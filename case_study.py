import argparse
from itertools import chain
from extrap.modelers import multi_parameter
from extrap.modelers import single_parameter
from extrap.util.options_parser import ModelerOptionsAction, ModelerHelpAction
from extrap.util.options_parser import SINGLE_PARAMETER_MODELER_KEY, SINGLE_PARAMETER_OPTIONS_KEY
from extrap.util.progress_bar import ProgressBar
from extrap.modelers.abstract_modeler import MultiParameterModeler
from extrap.modelers.model_generator import ModelGenerator
import logging
import os
from extrap.fileio.cube_file_reader2 import read_cube_file
from extrap.fileio.experiment_io import read_experiment
from extrap.fileio.json_file_reader import read_json_file
from extrap.fileio.talpas_file_reader import read_talpas_file
from extrap.fileio.text_file_reader import read_text_file
import sys
from extrap.util.exceptions import RecoverableError
from extrap.fileio import experiment_io
from extrap.fileio.io_helper import format_output
from extrap.fileio.io_helper import save_output
import math
from math import log2
import copy
import extrap
from extrap.entities.coordinate import Coordinate
from generic_strategy import add_additional_point_generic
from extrap.entities.experiment import Experiment
from extrap.entities.parameter import Parameter
from extrap.entities.callpath import Callpath
from extrap.entities.metric import Metric
from extrap.entities.measurement import Measurement
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from plotting import plot_measurement_point_number, plot_model_accuracy, plot_costs
from temp import add_measurements_to_gpr
from temp import add_measurement_to_gpr
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern
from sklearn.gaussian_process.kernels import WhiteKernel
import warnings
from sklearn.exceptions import ConvergenceWarning
import pickle
from parallel import analyze_callpath
import json
import time


def create_experiment2(cord, experiment, new_value, callpath, metric):
    # only append the new measurement value to experiment
    cord_found = False
    for i in range(len(experiment.measurements[(callpath, metric)])):
        if cord == experiment.measurements[(callpath, metric)][i].coordinate:
            experiment.measurements[(callpath, metric)][i].add_value(new_value)
            #x = np.append(x, new_value)
            #experiment.measurements[(callpath, metric)][i].values = x
            cord_found = True
            break
    if cord_found == False:
        # add new coordinate to experiment and then add a new measurement object with the new value to the experiment
        experiment.add_coordinate(cord)
        new_measurement = Measurement(cord, callpath, metric, [new_value])
        experiment.add_measurement(new_measurement)
    return experiment

def create_experiment_base(selected_coord_list, experiment, nr_parameters, parameter_placeholders, metric_id, callpath_id, nr_base_points):
    # create new experiment with only the selected measurements and points as coordinates and measurements
    experiment_new = Experiment()
    for j in range(nr_parameters):
        experiment_new.add_parameter(Parameter(parameter_placeholders[j]))

    callpath = experiment.callpaths[callpath_id]
    experiment_new.add_callpath(callpath)

    metric = experiment.metrics[metric_id]
    experiment_new.add_metric(metric)

    for j in range(len(selected_coord_list)):
        coordinate = selected_coord_list[j]
        experiment_new.add_coordinate(coordinate)

        coordinate_id = -1
        for k in range(len(experiment.coordinates)):
            if coordinate == experiment.coordinates[k]:
                coordinate_id = k
        measurement_temp = experiment.get_measurement(coordinate_id, callpath_id, metric_id)
        #print("haha:",measurement_temp.median)

        if measurement_temp != None:
            values = []
            counter = 0
            while counter < nr_base_points:
                values.append(np.mean(measurement_temp.values[counter]))
                counter += 1
            #value = selected_measurement_values[selected_coord_list[j]] 
            #experiment_generic.add_measurement(Measurement(coordinate, callpath, metric, value))
            experiment_new.add_measurement(Measurement(coordinate, callpath, metric, values))
    return experiment_new

def percentage_error(true_value, measured_value):
    error = abs(true_value - measured_value)
    percentage_error = (error / true_value) * 100
    return percentage_error

def get_eval_string(function_string):
    function_string = function_string.replace(" ","")
    function_string = function_string.replace("^","**")
    function_string = function_string.replace("log2","math.log2")
    function_string = function_string.replace("+-","-")
    return function_string

def calculate_selected_point_cost2(experiment, callpath, metric):
        selected_cost = 0
        for i in range(len(experiment.measurements[(callpath, metric)])):
            x = experiment.measurements[(callpath, metric)][i]
            coordinate_cost = 0
            for k in range(len(x.values)):
                runtime = np.mean(x.values[k])
                nr_processes = x.coordinate.as_tuple()[0]
                core_hours = runtime * nr_processes
                coordinate_cost += core_hours
            selected_cost += coordinate_cost
        return selected_cost

def calculate_selected_point_cost(selected_points, experiment, callpath_id, metric_id):
    # calculate selected point cost
    selected_cost = 0
    for j in range(len(selected_points)):
        coordinate = selected_points[j]
        coordinate_id = -1
        for k in range(len(experiment.coordinates)):
            if coordinate == experiment.coordinates[k]:
                coordinate_id = k
        counter = 0
        for metric in experiment.metrics:
            if str(metric) == "runtime" or str(metric) == "time":
                break
            else:
                counter += 1

        measurement_temp = experiment.get_measurement(coordinate_id, callpath_id, counter)
        
        #print("measurement_temp:",measurement_temp)
        coordinate_cost = 0
        if measurement_temp != None:
            for k in range(len(measurement_temp.values)):
                runtime = np.mean(measurement_temp.values[k])
                nr_processes = coordinate.as_tuple()[0]
                core_hours = runtime * nr_processes
                coordinate_cost += core_hours
        selected_cost += coordinate_cost
    return selected_cost

def increment_accuracy_bucket(acurracy_bucket_counter, percentage_error):
    # increase the counter of the accuracy bucket the error falls into for strategy
    if percentage_error <= 5:
        acurracy_bucket_counter["5"] = acurracy_bucket_counter["5"] + 1
        acurracy_bucket_counter["10"] = acurracy_bucket_counter["10"] + 1
        acurracy_bucket_counter["15"] = acurracy_bucket_counter["15"] + 1
        acurracy_bucket_counter["20"] = acurracy_bucket_counter["20"] + 1
        acurracy_bucket_counter["rest"] = acurracy_bucket_counter["rest"] + 1
    elif percentage_error <= 10:
        acurracy_bucket_counter["10"] = acurracy_bucket_counter["10"] + 1
        acurracy_bucket_counter["15"] = acurracy_bucket_counter["15"] + 1
        acurracy_bucket_counter["20"] = acurracy_bucket_counter["20"] + 1
        acurracy_bucket_counter["rest"] = acurracy_bucket_counter["rest"] + 1
    elif percentage_error <= 15:
        acurracy_bucket_counter["15"] = acurracy_bucket_counter["15"] + 1
        acurracy_bucket_counter["20"] = acurracy_bucket_counter["20"] + 1
        acurracy_bucket_counter["rest"] = acurracy_bucket_counter["rest"] + 1
    elif percentage_error <= 20:
        acurracy_bucket_counter["20"] = acurracy_bucket_counter["20"] + 1
        acurracy_bucket_counter["rest"] = acurracy_bucket_counter["rest"] + 1
    else:
        acurracy_bucket_counter["rest"] = acurracy_bucket_counter["rest"] + 1
    return acurracy_bucket_counter


def calculate_percentage_of_buckets(acurracy_bucket_counter, nr_callpaths):
    # calculate the percentages for each accuracy bucket
    percentage_bucket_counter = {}
    for key, value in acurracy_bucket_counter.items():
        percentage = (value / nr_callpaths) * 100
        percentage_bucket_counter[key] = percentage
    return percentage_bucket_counter

def get_extrap_model2(experiment, args, callpath, metric):
    # initialize model generator
    model_generator = ModelGenerator(
        experiment, modeler=args.modeler)

    # apply modeler options
    modeler = model_generator.modeler
    if isinstance(modeler, MultiParameterModeler) and args.modeler_options:
        # set single-parameter modeler of multi-parameter modeler
        single_modeler = args.modeler_options[SINGLE_PARAMETER_MODELER_KEY]
        if single_modeler is not None:
            modeler.single_parameter_modeler = single_parameter.all_modelers[single_modeler]()
        # apply options of single-parameter modeler
        if modeler.single_parameter_modeler is not None:
            for name, value in args.modeler_options[SINGLE_PARAMETER_OPTIONS_KEY].items():
                if value is not None:
                    setattr(modeler.single_parameter_modeler, name, value)

    for name, value in args.modeler_options.items():
        if value is not None:
            setattr(modeler, name, value)

    # create models from data
    with ProgressBar(desc='Generating models', disable=True) as pbar:
        model_generator.model_all(pbar)

    modeler = experiment.modelers[0]
    models = modeler.models
    
    model = models[(callpath, metric)]
    hypothesis = model.hypothesis
    function = hypothesis.function
    function_string = function.to_string(*experiment.parameters)
    extrap_function_string = function_string
    """for model in models.values():
        hypothesis = model.hypothesis
        function = hypothesis.function
        function_string = function.to_string(*experiment.parameters)
        print("TAYLOR HAS BIG BOOBS:",function_string)
        extrap_function_string += function_string + "\n"""
    
    return extrap_function_string, model

def get_extrap_model(experiment, args, callpath, metric):
    # initialize model generator
    model_generator = ModelGenerator(
        experiment, modeler=args.modeler)

    # apply modeler options
    modeler = model_generator.modeler
    if isinstance(modeler, MultiParameterModeler) and args.modeler_options:
        # set single-parameter modeler of multi-parameter modeler
        single_modeler = args.modeler_options[SINGLE_PARAMETER_MODELER_KEY]
        if single_modeler is not None:
            modeler.single_parameter_modeler = single_parameter.all_modelers[single_modeler]()
        # apply options of single-parameter modeler
        if modeler.single_parameter_modeler is not None:
            for name, value in args.modeler_options[SINGLE_PARAMETER_OPTIONS_KEY].items():
                if value is not None:
                    setattr(modeler.single_parameter_modeler, name, value)

    for name, value in args.modeler_options.items():
        if value is not None:
            setattr(modeler, name, value)

    with ProgressBar(desc='Generating models', disable=True) as pbar:
        # create models from data
        model_generator.model_all(pbar)

    modeler = experiment.modelers[0]
    models = modeler.models
    extrap_function_string = ""
    model = models[(callpath, metric)]
    for model in models.values():
        hypothesis = model.hypothesis
        function = hypothesis.function
        function_string = function.to_string(*experiment.parameters)
        extrap_function_string += function_string + "\n"
    # convert into python interpretable function
    extrap_function_string = extrap_function_string.replace(" ","")
    extrap_function_string = extrap_function_string.replace("^","**")
    extrap_function_string = extrap_function_string.replace("log2","math.log2")
    extrap_function_string = extrap_function_string.replace("+-","-")
    return extrap_function_string, models


def create_experiment(selected_coord_list, experiment, nr_parameters, parameter_placeholders, metric_id, callpath_id):
    # create new experiment with only the selected measurements and points as coordinates and measurements
    experiment_generic = Experiment()
    for j in range(nr_parameters):
        experiment_generic.add_parameter(Parameter(parameter_placeholders[j]))

    callpath = experiment.callpaths[callpath_id]
    experiment_generic.add_callpath(callpath)

    metric = experiment.metrics[metric_id]
    experiment_generic.add_metric(metric)

    for j in range(len(selected_coord_list)):
        coordinate = selected_coord_list[j]
        experiment_generic.add_coordinate(coordinate)

        coordinate_id = -1
        for k in range(len(experiment.coordinates)):
            if coordinate == experiment.coordinates[k]:
                coordinate_id = k
        measurement_temp = experiment.get_measurement(coordinate_id, callpath_id, metric_id)
        #print("haha:",measurement_temp.median)

        if measurement_temp != None:
            #value = selected_measurement_values[selected_coord_list[j]] 
            #experiment_generic.add_measurement(Measurement(coordinate, callpath, metric, value))
            experiment_generic.add_measurement(Measurement(coordinate, callpath, metric, measurement_temp.values))
    return experiment_generic


def main():
    """
    Runs an evaluation for a case study based on the cube files loaded from the specified directory or another input file format.
    """

    # Parse command line args
    modelers_list = list(set(k.lower() for k in
                             chain(single_parameter.all_modelers.keys(), multi_parameter.all_modelers.keys())))
    parser = argparse.ArgumentParser(description="Run synthetic benchmark.")

    basic_args = parser.add_argument_group("Optional args")
    
    basic_args.add_argument("--log", action="store", dest="log_level", type=str.lower, default='warning',
                                 choices=['debug', 'info', 'warning', 'error', 'critical'],
                                 help="Set program's log level (default: warning)")

    positional_args = parser.add_argument_group("Positional args")

    parser.add_argument("--budget", type=float, required=True, default=100,
                        help="Percentage of total cost of all points that can be used by the selection strategies. Positive integer value between 0-100.")
    
    parser.add_argument("--plot", type=bool, required=False, default=False,
                        help="Set if the plots should be shown after running the anlysis.")

    parser.add_argument("--processes", type=int, required=True,
                        help="Set which number in the list of parameters is the number of processes/MPI ranks. Positive integer value between 0-x.")
    
    parser.add_argument("--parameters", type=str, required=True,
                        help="Set the parameters of the experiments, used for eval(). String list of the parameter names.")

    parser.add_argument("--eval_point", type=str, required=True,
                        help="Set the measurement point that will be used for the evaluation of the predictive power of the models. String list of the parameter values of the measurement point.")
    
    parser.add_argument("--filter", type=float, required=True,
                        help="Set a integer value as percentage filter for callpaths. Sets how much they need to contribute to ovarll runtime to be used for analysis.")
    
    parser.add_argument("--normalization", type=bool, default=False,
                        help="Set if normalization of the measurement points parameter values is used for the gpr approach.")

    parser.add_argument("--base-values", type=int, default=2, required=False,
                        help="Set the number of repetitions used for the minimal set of measurements for the GPR strategy.")
    
    parser.add_argument("--repetitions", type=int, default=5, required=False,
                        help="Set the number of repetitions thay are available from the measurements.")
    
    parser.add_argument("--hybrid-switch", type=int, default=5, required=False,
                        help="Set the switching point for the hybrid selection strategy.")
    
    parser.add_argument("--grid-search", type=int, default=1, required=False, choices=[1,2,3,4],
                        help="Set the evaluation mode. Used for grid search for best strategy setups.")

    parser.add_argument("--newonly", type=int, required=False, default=0, choices=[0, 1],
                        help="Run analysis only for random and grid search only.")

    input_options = parser.add_argument_group("Input options")
    group = input_options.add_mutually_exclusive_group(required=True)
    group.add_argument("--cube", action="store_true", default=False, dest="cube", help="Load data from CUBE files")
    group.add_argument("--text", action="store_true", default=False, dest="text", help="Load data from text files")
    group.add_argument("--talpas", action="store_true", default=False, dest="talpas",
                       help="Load data from Talpas data format")
    group.add_argument("--json", action="store_true", default=False, dest="json",
                       help="Load data from JSON or JSON Lines file")
    group.add_argument("--extra-p", action="store_true", default=False, dest="extrap",
                       help="Load data from Extra-P experiment")
    input_options.add_argument("--scaling", action="store", dest="scaling_type", default="weak", type=str.lower,
                               choices=["weak", "strong"],
                               help="Set weak or strong scaling when loading data from CUBE files (default: weak)")
    

    modeling_options = parser.add_argument_group("Modeling options")
    modeling_options.add_argument("--median", action="store_true", dest="median",
                                  help="Use median values for computation instead of mean values")
    modeling_options.add_argument("--modeler", action="store", dest="modeler", default='default', type=str.lower,
                                  choices=modelers_list,
                                  help="Selects the modeler for generating the performance models")
    modeling_options.add_argument("--options", dest="modeler_options", default={}, nargs='+', metavar="KEY=VALUE",
                                  action=ModelerOptionsAction,
                                  help="Options for the selected modeler")
    modeling_options.add_argument("--help-modeler", choices=modelers_list, type=str.lower,
                                  help="Show help for modeler options and exit",
                                  action=ModelerHelpAction)
    positional_args.add_argument("path", metavar="FILEPATH", type=str, action="store",
                                      help="Specify a file path for Extra-P to work with")
    
    output_options = parser.add_argument_group("Output options")
    output_options.add_argument("--out", action="store", metavar="OUTPUT_PATH", dest="out",
                                help="Specify the output path for Extra-P results")
    output_options.add_argument("--print", action="store", dest="print_type", default="all",
                                choices=["all", "callpaths", "metrics", "parameters", "functions"],
                                help="Set which information should be displayed after modeling "
                                     "(default: all)")
    output_options.add_argument("--save-experiment", action="store", metavar="EXPERIMENT_PATH", dest="save_experiment",
                                help="Saves the experiment including all models as Extra-P experiment "
                                     "(if no extension is specified, '.extra-p' is appended)")

    args = parser.parse_args()

    # disable deprecation warnings...
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=ConvergenceWarning)

    # check scaling type
    scaling_type = args.scaling_type

    # set log level
    loglevel = logging.getLevelName(args.log_level.upper())

    # set output print type
    printtype = args.print_type.upper()

    # set show plots
    plot = args.plot

    normalization = args.normalization
    print("Use normalization?:",normalization)

    # set use mean or median for computation
    use_median = args.median

    # save modeler output to file?
    print_path = None
    if args.out is not None:
        print_output = True
        print_path = args.out
    else:
        print_output = False

    # set log format location etc.
    if loglevel == logging.DEBUG:
        # import warnings
        # warnings.simplefilter('always', DeprecationWarning)
        # check if log file exists and create it if necessary
        # if not os.path.exists("../temp/extrap.log"):
        #    log_file = open("../temp/extrap.log","w")
        #    log_file.close()
        # logging.basicConfig(format="%(levelname)s - %(asctime)s - %(filename)s:%(lineno)s - %(funcName)10s():
        # %(message)s", level=loglevel, datefmt="%m/%d/%Y %I:%M:%S %p", filename="../temp/extrap.log", filemode="w")
        logging.basicConfig(
            format="%(levelname)s - %(asctime)s - %(filename)s:%(lineno)s - %(funcName)10s(): %(message)s",
            level=loglevel, datefmt="%m/%d/%Y %I:%M:%S %p")
    else:
        logging.basicConfig(
            format="%(levelname)s: %(message)s", level=loglevel)
    
    budget = args.budget
    print("budget:",budget)

    processes = args.processes
    print("processes:",processes)

    parameters = args.parameters
    print("parameters:",parameters)

    eval_point = args.eval_point
    print("eval_point:",eval_point)
    
    base_values = args.base_values
    print("base_values:",base_values)
    
    hybrid_switch = args.hybrid_switch
    print("hybrid_switch:",hybrid_switch)
    
    grid_search = args.grid_search
    print("grid_search:",grid_search)
    
    nr_repetitions = args.repetitions
    print("nr_repetitions:",nr_repetitions)

    # set if to only run extended eval algorithms for random, grid search and bayesian optimization
    # disables plotting and algo execution for generic, gpr, hybrid method
    newonly = False
    if args.newonly == 0:
        newonly = False
    else:
        newonly = True

    parameters = parameters.split(",")

    eval_point = eval_point.split(",")

    filter = args.filter
    print("filter:",filter)
    
    if args.path is not None:
        with ProgressBar(desc='Loading file') as pbar:
            if args.cube:
                # load data from cube files
                if os.path.isdir(args.path):
                    experiment = read_cube_file(args.path, scaling_type)
                else:
                    logging.error("The given path is not valid. It must point to a directory.")
                    sys.exit(1)
            elif os.path.isfile(args.path):
                if args.text:
                    # load data from text files
                    experiment = read_text_file(args.path, pbar)
                elif args.talpas:
                    # load data from talpas format
                    experiment = read_talpas_file(args.path, pbar)
                elif args.json:
                    # load data from json file
                    experiment = read_json_file(args.path, pbar)
                elif args.extrap:
                    # load data from Extra-P file
                    experiment = read_experiment(args.path, pbar)
                else:
                    logging.error("The file format specifier is missing.")
                    sys.exit(1)
            else:
                logging.error("The given file path is not valid.")
                sys.exit(1)

        # find the runtime metric first
        temp_metric_id = -1
        for o in range(len(experiment.metrics)):
            if str(experiment.metrics[o]) == "runtime" or str(experiment.metrics[o]) == "time":
                temp_metric_id = o
                break

        # make sure the evaluation point is not used for modeling
        measurements_backup = copy.deepcopy(experiment.measurements)
        #print("DEBUG:",measurements_backup)
        #measurements_backup2 = []
        measurement_evaluation = copy.deepcopy(experiment.measurements)
        #coordinate_evaluation = copy.deepcopy(experiment.coordinates)
        experiment.measurements = None
        #print("len(experiment.coordinates):",len(experiment.coordinates))
        #print("experiment.coordinates:",experiment.coordinates)
        for k in range(len(experiment.callpaths)):
            temp = []
            for i in range(len(experiment.coordinates)):
                #print("measurements_backup:",measurements_backup[experiment.callpaths[k], experiment.metrics[temp_metric_id]])
                #print("i:",i)
                cord = measurements_backup[experiment.callpaths[k], experiment.metrics[temp_metric_id]][i].coordinate
                if cord == Coordinate(float(eval_point[0]),float(eval_point[1])):
                    pass
                    #measurements_backup2.append(measurements_backup[experiment.callpaths[k], experiment.metrics[temp_metric_id]][i])
                    #measurements_backup[experiment.callpaths[k], experiment.metrics[temp_metric_id]].pop(i)
                else:
                    temp.append(measurements_backup[experiment.callpaths[k], experiment.metrics[temp_metric_id]][i])
            measurements_backup[experiment.callpaths[k], experiment.metrics[temp_metric_id]] = temp
            #print("len(measurements_backup[experiment.callpaths[k], experiment.metrics[temp_metric_id]]):",len(measurements_backup[experiment.callpaths[k], experiment.metrics[temp_metric_id]]))
        """for k in range(len(experiment.callpaths)):
            for i in range(len(ids_to_delete)):
                id_to_delete = ids_to_delete[i]
                measurements_backup[experiment.callpaths[k], experiment.metrics[temp_metric_id]].pop(id_to_delete)"""
        #measurements_backup = measurements_backup2
        
        # make sure the number of base values is not equal to the number of total tepetitions available for modeling
        if base_values == nr_repetitions:
            base_values -= 1
        if base_values > nr_repetitions:
            base_values = nr_repetitions - 1
    
        experiment.measurements = measurements_backup
        coordinate_evaluation = []
        temp = []
        #print("experiment.coordinates:",experiment.coordinates)
        #print("len(experiment.coordinates):",len(experiment.coordinates))
        for i in range(len(experiment.coordinates)):
            coordinate_evaluation.append(experiment.coordinates[i])
        for i in range(len(experiment.coordinates)):
            if experiment.coordinates[i] == Coordinate(float(eval_point[0]),float(eval_point[1])):
                pass
                #experiment.coordinates.pop(i)
            else:
                temp.append(experiment.coordinates[i])
        experiment.coordinates = temp

        # initialize model generator
        model_generator = ModelGenerator(
            experiment, modeler=args.modeler)

        # apply modeler options
        modeler = model_generator.modeler
        if isinstance(modeler, MultiParameterModeler) and args.modeler_options:
            # set single-parameter modeler of multi-parameter modeler
            single_modeler = args.modeler_options[SINGLE_PARAMETER_MODELER_KEY]
            if single_modeler is not None:
                modeler.single_parameter_modeler = single_parameter.all_modelers[single_modeler]()
            # apply options of single-parameter modeler
            if modeler.single_parameter_modeler is not None:
                for name, value in args.modeler_options[SINGLE_PARAMETER_OPTIONS_KEY].items():
                    if value is not None:
                        setattr(modeler.single_parameter_modeler, name, value)

        # apply modeler options
        for name, value in args.modeler_options.items():
            if value is not None:
                setattr(modeler, name, value)

        # create models from data
        with ProgressBar(desc='Generating models', disable=False) as pbar:
            model_generator.model_all(pbar)

        # save experiment if set in command line options
        if args.save_experiment:
            try:
                with ProgressBar(desc='Saving experiment') as pbar:
                    if not os.path.splitext(args.save_experiment)[1]:
                        args.save_experiment += '.extra-p'
                    experiment_io.write_experiment(experiment, args.save_experiment, pbar)
            except RecoverableError as err:
                logging.error('Saving experiment: ' + str(err))
                sys.exit(1)
        
        # get metric id and string of runtime/time metric
        metric_id = -1
        for i in range(len(experiment.metrics)):
            if str(experiment.metrics[i]) == "time" or str(experiment.metrics[i]) == "runtime":
                metric_id = i
                break
        metric = experiment.metrics[metric_id]
        metric_string = metric.name
        print("Metric:",metric_string)

        # set the minimum number of points required for modeling with the sparse modeler
        min_points = 0
        if len(experiment.parameters) == 1:
            min_points = 5
        elif len(experiment.parameters) == 2:
            min_points = 9
        elif len(experiment.parameters) == 3:
            min_points = 13
        elif len(experiment.parameters) == 4:
            min_points = 17
        else:
            min_points = 5

        cost_container = {}
        total_costs_container = {}
        all_points_functions_strings = {}
        
        # full
        acurracy_bucket_counter_full = {}
        acurracy_bucket_counter_full["rest"] = 0
        acurracy_bucket_counter_full["5"] = 0
        acurracy_bucket_counter_full["10"] = 0
        acurracy_bucket_counter_full["15"] = 0
        acurracy_bucket_counter_full["20"] = 0

        # generic
        acurracy_bucket_counter_generic = {}
        acurracy_bucket_counter_generic["rest"] = 0
        acurracy_bucket_counter_generic["5"] = 0
        acurracy_bucket_counter_generic["10"] = 0
        acurracy_bucket_counter_generic["15"] = 0
        acurracy_bucket_counter_generic["20"] = 0

        percentage_cost_generic_container = []
        add_points_generic_container = []

        # gpr
        acurracy_bucket_counter_gpr = {}
        acurracy_bucket_counter_gpr["rest"] = 0
        acurracy_bucket_counter_gpr["5"] = 0
        acurracy_bucket_counter_gpr["10"] = 0
        acurracy_bucket_counter_gpr["15"] = 0
        acurracy_bucket_counter_gpr["20"] = 0

        percentage_cost_gpr_container = []
        add_points_gpr_container = []

        # hybrid
        acurracy_bucket_counter_hybrid = {}
        acurracy_bucket_counter_hybrid["rest"] = 0
        acurracy_bucket_counter_hybrid["5"] = 0
        acurracy_bucket_counter_hybrid["10"] = 0
        acurracy_bucket_counter_hybrid["15"] = 0
        acurracy_bucket_counter_hybrid["20"] = 0

        percentage_cost_hybrid_container = []
        add_points_hybrid_container = []

        # grid
        acurracy_bucket_counter_grid = {}
        acurracy_bucket_counter_grid["rest"] = 0
        acurracy_bucket_counter_grid["5"] = 0
        acurracy_bucket_counter_grid["10"] = 0
        acurracy_bucket_counter_grid["15"] = 0
        acurracy_bucket_counter_grid["20"] = 0

        percentage_cost_grid_container = []
        add_points_grid_container = []

        # random
        acurracy_bucket_counter_random = {}
        acurracy_bucket_counter_random["rest"] = 0
        acurracy_bucket_counter_random["5"] = 0
        acurracy_bucket_counter_random["10"] = 0
        acurracy_bucket_counter_random["15"] = 0
        acurracy_bucket_counter_random["20"] = 0

        percentage_cost_random_container = []
        add_points_random_container = []

        # bayesian
        acurracy_bucket_counter_bayesian = {}
        acurracy_bucket_counter_bayesian["rest"] = 0
        acurracy_bucket_counter_bayesian["5"] = 0
        acurracy_bucket_counter_bayesian["10"] = 0
        acurracy_bucket_counter_bayesian["15"] = 0
        acurracy_bucket_counter_bayesian["20"] = 0

        percentage_cost_bayesian_container = []
        add_points_bayesian_container = []
        
        generic_functions_modeled = []
        gpr_functions_modeled = []
        hybrid_functions_modeled = []
        grid_functions_modeled = []
        random_functions_modeled = []
        bayesian_functions_modeled = []

        runtime_sums = {}

        modeler = experiment.modelers[0]

        # calculate the overall runtime of the application and the cost of each kernel per measurement point
        for callpath_id in range(len(experiment.callpaths)):
            callpath = experiment.callpaths[callpath_id]
            callpath_string = callpath.name

            cost = {}
            total_cost = 0
            
            try:
                model = modeler.models[callpath, metric]
            except KeyError as e:
                model = None
            if model != None:
                hypothesis = model.hypothesis
                function = hypothesis.function
                
                # get the extrap function as a string
                function_string = function.to_string(*experiment.parameters)
                function_string = get_eval_string(function_string)
                all_points_functions_strings[callpath_string] = function_string

                overall_runtime = 0
                for i in range(len(experiment.coordinates)):
                    if experiment.coordinates[i] not in cost:
                        cost[experiment.coordinates[i]] = []
                    values = experiment.coordinates[i].as_tuple()
                    nr_processes = values[processes]
                    coordinate_id = -1
                    for k in range(len(experiment.coordinates)):
                        if experiment.coordinates[i] == experiment.coordinates[k]:
                            coordinate_id = k
                    measurement_temp = experiment.get_measurement(coordinate_id, callpath_id, metric_id)
                    coordinate_cost = 0
                    if measurement_temp != None:
                        for k in range(len(measurement_temp.values)):
                            runtime = np.mean(measurement_temp.values[k])
                            core_hours = runtime * nr_processes
                            cost[experiment.coordinates[i]].append(core_hours)
                            coordinate_cost += core_hours
                            overall_runtime += runtime
                    total_cost += coordinate_cost

            else:
                function_string = "None"
                total_cost = 0
                overall_runtime = 0

            cost_container[callpath_string] = cost
            total_costs_container[callpath_string] = total_cost

            runtime_sums[callpath_string] = overall_runtime

        total_runtime_sum = 0
        for key, value in runtime_sums.items():
            total_runtime_sum += value
        print("total_runtime_sum:",total_runtime_sum)
        
        # preselect all callpaths that are interesting for the analysis based on the set filter value
        filtered_callpaths = []
        filtered_callpaths_ids = []
        kernels_used = 0
        for i in range(len(experiment.callpaths)):
            callpath_string = experiment.callpaths[i].name

            # get the cost values for this particular callpath
            cost = cost_container[callpath_string]
            total_cost = total_costs_container[callpath_string]

            overall_runtime = runtime_sums[callpath_string]
            opc = total_runtime_sum / 100
            callpath_cost = overall_runtime / opc
            
            if callpath_cost >= filter:
                kernels_used += 1
                filtered_callpaths.append(experiment.callpaths[i])
                filtered_callpaths_ids.append(i)
        
        print("kernels_used:", kernels_used)

        base_point_costs = []
        
        from multiprocessing import Manager
        import multiprocessing as mp
        from multiprocessing import Pool
        from tqdm import tqdm
        
        # parallelize reading all measurement_files in one folder
        manager = Manager()
        shared_dict = manager.dict()
        cpu_count = mp.cpu_count()
        cpu_count -= 4
        if len(filtered_callpaths_ids) < cpu_count:
            cpu_count = len(filtered_callpaths_ids)

        inputs = []
        for i in range(len(filtered_callpaths_ids)):
            inputs.append([filtered_callpaths_ids[i], shared_dict, cost, 
                           filtered_callpaths[i], cost_container, total_costs_container, 
                           grid_search, experiment.measurements, len(experiment.parameters),
                           experiment.coordinates, metric, base_values,
                           metric_id, nr_repetitions, parameters,
                           args, budget, eval_point, all_points_functions_strings,
                           coordinate_evaluation, measurement_evaluation, normalization,
                           min_points, hybrid_switch, newonly])
            
        with Pool(cpu_count) as pool:
            _ = list(tqdm(pool.imap(analyze_callpath, inputs), total=len(filtered_callpaths_ids), disable=False))

        result_dict = copy.deepcopy(shared_dict)
        
        #print("DEBUG:",result_dict)
        
        
        # analyze results
        for i, _ in result_dict.items():
            
            add_points_generic_container.append(result_dict[i]["add_points_generic"])
            percentage_cost_generic_container.append(result_dict[i]["percentage_cost_generic"])
            add_points_gpr_container.append(result_dict[i]["add_points_gpr"])
            percentage_cost_gpr_container.append(result_dict[i]["percentage_cost_gpr"])
            add_points_hybrid_container.append(result_dict[i]["add_points_hybrid"])
            percentage_cost_hybrid_container.append(result_dict[i]["percentage_cost_hybrid"])
            add_points_grid_container.append(result_dict[i]["add_points_grid"])
            percentage_cost_grid_container.append(result_dict[i]["percentage_cost_grid"])
            add_points_random_container.append(result_dict[i]["add_points_random"])
            percentage_cost_random_container.append(result_dict[i]["percentage_cost_random"])
            add_points_bayesian_container.append(result_dict[i]["add_points_bayesian"])
            percentage_cost_bayesian_container.append(result_dict[i]["percentage_cost_bayesian"])
            base_point_costs.append(result_dict[i]["base_point_cost"])
            
            generic_functions_modeled.append(result_dict[i]["generic_possible"])
            gpr_functions_modeled.append(result_dict[i]["gpr_possible"])
            hybrid_functions_modeled.append(result_dict[i]["hybrid_possible"])
            grid_functions_modeled.append(result_dict[i]["grid_possible"])
            random_functions_modeled.append(result_dict[i]["random_possible"])
            bayesian_functions_modeled.append(result_dict[i]["bayesian_possible"])
            
            b_full = result_dict[i]["acurracy_bucket_counter_full"]
            b_generic = result_dict[i]["acurracy_bucket_counter_generic"]
            b_gpr = result_dict[i]["acurracy_bucket_counter_gpr"]
            b_hybrid = result_dict[i]["acurracy_bucket_counter_hybrid"]
            b_grid = result_dict[i]["acurracy_bucket_counter_grid"]
            b_random = result_dict[i]["acurracy_bucket_counter_random"]
            b_bayesian = result_dict[i]["acurracy_bucket_counter_bayesian"]

            if b_full["rest"] == 1:
                acurracy_bucket_counter_full["rest"] += 1
            if b_full["5"] == 1:
                acurracy_bucket_counter_full["5"] += 1
            if b_full["10"] == 1:
                acurracy_bucket_counter_full["10"] += 1
            if b_full["15"] == 1:
                acurracy_bucket_counter_full["15"] += 1
            if b_full["20"] == 1:
                acurracy_bucket_counter_full["20"] += 1
            
            if b_generic["rest"] == 1:
                acurracy_bucket_counter_generic["rest"] += 1
            if b_generic["5"] == 1:
                acurracy_bucket_counter_generic["5"] += 1
            if b_generic["10"] == 1:
                acurracy_bucket_counter_generic["10"] += 1
            if b_generic["15"] == 1:
                acurracy_bucket_counter_generic["15"] += 1
            if b_generic["20"] == 1:
                acurracy_bucket_counter_generic["20"] += 1

            if b_gpr["rest"] == 1:
                acurracy_bucket_counter_gpr["rest"] += 1
            if b_gpr["5"] == 1:
                acurracy_bucket_counter_gpr["5"] += 1
            if b_gpr["10"] == 1:
                acurracy_bucket_counter_gpr["10"] += 1
            if b_gpr["15"] == 1:
                acurracy_bucket_counter_gpr["15"] += 1
            if b_gpr["20"] == 1:
                acurracy_bucket_counter_gpr["20"] += 1
                
            if b_hybrid["rest"] == 1:
                acurracy_bucket_counter_hybrid["rest"] += 1
            if b_hybrid["5"] == 1:
                acurracy_bucket_counter_hybrid["5"] += 1
            if b_hybrid["10"] == 1:
                acurracy_bucket_counter_hybrid["10"] += 1
            if b_hybrid["15"] == 1:
                acurracy_bucket_counter_hybrid["15"] += 1
            if b_hybrid["20"] == 1:
                acurracy_bucket_counter_hybrid["20"] += 1

            if b_grid["rest"] == 1:
                acurracy_bucket_counter_grid["rest"] += 1
            if b_grid["5"] == 1:
                acurracy_bucket_counter_grid["5"] += 1
            if b_grid["10"] == 1:
                acurracy_bucket_counter_grid["10"] += 1
            if b_grid["15"] == 1:
                acurracy_bucket_counter_grid["15"] += 1
            if b_grid["20"] == 1:
                acurracy_bucket_counter_grid["20"] += 1

            if b_random["rest"] == 1:
                acurracy_bucket_counter_random["rest"] += 1
            if b_random["5"] == 1:
                acurracy_bucket_counter_random["5"] += 1
            if b_random["10"] == 1:
                acurracy_bucket_counter_random["10"] += 1
            if b_random["15"] == 1:
                acurracy_bucket_counter_random["15"] += 1
            if b_random["20"] == 1:
                acurracy_bucket_counter_random["20"] += 1

            if b_bayesian["rest"] == 1:
                acurracy_bucket_counter_bayesian["rest"] += 1
            if b_bayesian["5"] == 1:
                acurracy_bucket_counter_bayesian["5"] += 1
            if b_bayesian["10"] == 1:
                acurracy_bucket_counter_bayesian["10"] += 1
            if b_bayesian["15"] == 1:
                acurracy_bucket_counter_bayesian["15"] += 1
            if b_bayesian["20"] == 1:
                acurracy_bucket_counter_bayesian["20"] += 1

        #print("acurracy_bucket_counter_full:",acurracy_bucket_counter_full)
        #print("acurracy_bucket_counter_generic:",acurracy_bucket_counter_generic)
        #print("acurracy_bucket_counter_gpr:",acurracy_bucket_counter_gpr)
        #print("acurracy_bucket_counter_hybrid:",acurracy_bucket_counter_hybrid)
            

        print("Number of kernels used:",kernels_used,"of",len(experiment.callpaths),"callpaths.")
        print("Total number of measurement points:",len(experiment.coordinates))
        
        print("Min required modeling budget for most expensive callpath:",max(base_point_costs),"%")

        #print("acurracy_bucket_counter_full:",acurracy_bucket_counter_full)
        #print("acurracy_bucket_counter_generic:",acurracy_bucket_counter_generic)
        #print("acurracy_bucket_counter_gpr:",acurracy_bucket_counter_gpr)
        #print("acurracy_bucket_counter_hybrid:",acurracy_bucket_counter_hybrid)

        json_out = {}

        # calculate the percentages for each accuracy bucket
        percentage_bucket_counter_full = calculate_percentage_of_buckets(acurracy_bucket_counter_full, kernels_used)
        print("percentage_bucket_counter_full:",percentage_bucket_counter_full)
        print("")
        json_out["percentage_bucket_counter_full"] = percentage_bucket_counter_full
        
        ###############
        ### Generic ###
        ###############
        
        percentage_bucket_counter_generic = calculate_percentage_of_buckets(acurracy_bucket_counter_generic, kernels_used)
        print("percentage_bucket_counter_generic:",percentage_bucket_counter_generic)
        json_out["percentage_bucket_counter_generic"] = percentage_bucket_counter_generic
        
        #print("percentage_cost_generic_container:",percentage_cost_generic_container)
        percentage_cost_generic_container_filtered = []
        add_points_generic_container_filtered = []
        for i in range(len(percentage_cost_generic_container)):
            if percentage_cost_generic_container[i] <= budget:
                percentage_cost_generic_container_filtered.append(percentage_cost_generic_container[i])
                add_points_generic_container_filtered.append(add_points_generic_container[i])
        #mean_budget_generic = np.nanmean(percentage_cost_generic_container)
        mean_budget_generic = np.nanmean(percentage_cost_generic_container_filtered)
        #print("percentage_cost_generic_container_filtered:",percentage_cost_generic_container_filtered)
        print("mean_budget_generic:",mean_budget_generic)
        json_out["mean_budget_generic"] = mean_budget_generic

        #mean_add_points_generic = np.nanmean(add_points_generic_container)
        mean_add_points_generic = np.nanmean(add_points_generic_container_filtered)
        print("mean_add_points_generic:",mean_add_points_generic)
        json_out["mean_add_points_generic"] = mean_add_points_generic
        
        nr_func_modeled_generic = 0
        for i in range(len(generic_functions_modeled)):
            if generic_functions_modeled[i] == True:
                nr_func_modeled_generic += 1
        print("nr_func_modeled_generic:",nr_func_modeled_generic)
        
        print("")
        
        json_out["nr_func_modeled_generic"] = nr_func_modeled_generic

        ###########
        ### GPR ###
        ###########
        
        percentage_bucket_counter_gpr = calculate_percentage_of_buckets(acurracy_bucket_counter_gpr, kernels_used)
        print("percentage_bucket_counter_gpr:",percentage_bucket_counter_gpr)
        json_out["percentage_bucket_counter_gpr"] = percentage_bucket_counter_gpr

        #print("percentage_cost_gpr_container:",percentage_cost_gpr_container)
        percentage_cost_gpr_container_filtered = []
        add_points_gpr_container_filtered = []
        for i in range(len(percentage_cost_gpr_container)):
            if percentage_cost_gpr_container[i] <= budget:
                percentage_cost_gpr_container_filtered.append(percentage_cost_gpr_container[i])
                add_points_gpr_container_filtered.append(add_points_gpr_container[i])
                
        if len(add_points_gpr_container_filtered) > 0:
            mean_add_points_gpr = np.nanmean(add_points_gpr_container_filtered)
        else:
            mean_add_points_gpr = 0
        print("mean_add_points_gpr:",mean_add_points_gpr)
        json_out["mean_add_points_gpr"] = mean_add_points_gpr
                
        if len(percentage_cost_gpr_container_filtered) > 0:
            mean_budget_gpr = np.nanmean(percentage_cost_gpr_container_filtered)
        else:
            mean_budget_gpr = 0
        print("mean_budget_gpr:",mean_budget_gpr)
        json_out["mean_budget_gpr"] = mean_budget_gpr
        
        nr_func_modeled_gpr = 0
        for i in range(len(gpr_functions_modeled)):
            if gpr_functions_modeled[i] == True:
                nr_func_modeled_gpr += 1
        print("nr_func_modeled_gpr:",nr_func_modeled_gpr)
        
        print("")
        
        json_out["nr_func_modeled_gpr"] = nr_func_modeled_gpr
        
        ##############
        ### Hybrid ###
        ##############
        
        percentage_bucket_counter_hybrid = calculate_percentage_of_buckets(acurracy_bucket_counter_hybrid, kernels_used)
        print("percentage_bucket_counter_hybrid:",percentage_bucket_counter_hybrid)
        json_out["percentage_bucket_counter_hybrid"] = percentage_bucket_counter_hybrid

        percentage_cost_hybrid_container_filtered = []
        add_points_hybrid_container_filtered = []
        for i in range(len(percentage_cost_hybrid_container)):
            if percentage_cost_hybrid_container[i] <= budget:
                percentage_cost_hybrid_container_filtered.append(percentage_cost_hybrid_container[i])
                add_points_hybrid_container_filtered.append(add_points_hybrid_container[i])
        #print("percentage_cost_hybrid_container:",percentage_cost_hybrid_container)
        #mean_budget_hybrid = np.nanmean(percentage_cost_hybrid_container)
        
        if len(percentage_cost_hybrid_container_filtered) > 0:
            mean_budget_hybrid = np.nanmean(percentage_cost_hybrid_container_filtered)
        else:
            mean_budget_hybrid = 0
        print("mean_budget_hybrid:",mean_budget_hybrid)
        json_out["mean_budget_hybrid"] = mean_budget_hybrid

        if len(add_points_hybrid_container_filtered) > 0:
            mean_add_points_hybrid = np.nanmean(add_points_hybrid_container_filtered)
        else:
            mean_add_points_hybrid = 0
        print("mean_add_points_hybrid:",mean_add_points_hybrid)
        json_out["mean_add_points_hybrid"] = mean_add_points_hybrid
        
        nr_func_modeled_hybrid = 0
        for i in range(len(hybrid_functions_modeled)):
            if hybrid_functions_modeled[i] == True:
                nr_func_modeled_hybrid += 1
        print("nr_func_modeled_hybrid:",nr_func_modeled_hybrid)

        print("")
        
        json_out["nr_func_modeled_hybrid"] = nr_func_modeled_hybrid

        ##############
        ### Grid ###
        ##############
        
        percentage_bucket_counter_grid = calculate_percentage_of_buckets(acurracy_bucket_counter_grid, kernels_used)
        print("percentage_bucket_counter_grid:",percentage_bucket_counter_grid)
        json_out["percentage_bucket_counter_grid"] = percentage_bucket_counter_grid

        percentage_cost_grid_container_filtered = []
        add_points_grid_container_filtered = []
        for i in range(len(percentage_cost_grid_container)):
            if percentage_cost_grid_container[i] <= budget:
                percentage_cost_grid_container_filtered.append(percentage_cost_grid_container[i])
                add_points_grid_container_filtered.append(add_points_grid_container[i])
        #print("percentage_cost_grid_container:",percentage_cost_grid_container)
        #mean_budget_grid = np.nanmean(percentage_cost_grid_container)
        
        if len(percentage_cost_grid_container_filtered) > 0:
            mean_budget_grid = np.nanmean(percentage_cost_grid_container_filtered)
        else:
            mean_budget_grid = 0
        print("mean_budget_grid:",mean_budget_grid)
        json_out["mean_budget_grid"] = mean_budget_grid

        if len(add_points_grid_container_filtered) > 0:
            mean_add_points_grid = np.nanmean(add_points_grid_container_filtered)
        else:
            mean_add_points_grid = 0
        print("mean_add_points_grid:",mean_add_points_grid)
        json_out["mean_add_points_grid"] = mean_add_points_grid
        
        nr_func_modeled_grid = 0
        for i in range(len(grid_functions_modeled)):
            if grid_functions_modeled[i] == True:
                nr_func_modeled_grid += 1
        print("nr_func_modeled_grid:",nr_func_modeled_grid)

        print("")
        
        json_out["nr_func_modeled_grid"] = nr_func_modeled_grid

        ##############
        ### Random ###
        ##############
        
        percentage_bucket_counter_random = calculate_percentage_of_buckets(acurracy_bucket_counter_random, kernels_used)
        print("percentage_bucket_counter_random:",percentage_bucket_counter_random)
        json_out["percentage_bucket_counter_random"] = percentage_bucket_counter_random

        percentage_cost_random_container_filtered = []
        add_points_random_container_filtered = []
        for i in range(len(percentage_cost_random_container)):
            if percentage_cost_random_container[i] <= budget:
                percentage_cost_random_container_filtered.append(percentage_cost_random_container[i])
                add_points_random_container_filtered.append(add_points_random_container[i])
        #print("percentage_cost_random_container:",percentage_cost_random_container)
        #mean_budget_random = np.nanmean(percentage_cost_random_container)
        
        if len(percentage_cost_random_container_filtered) > 0:
            mean_budget_random = np.nanmean(percentage_cost_random_container_filtered)
        else:
            mean_budget_random = 0
        print("mean_budget_random:",mean_budget_random)
        json_out["mean_budget_random"] = mean_budget_random

        if len(add_points_random_container_filtered) > 0:
            mean_add_points_random = np.nanmean(add_points_random_container_filtered)
        else:
            mean_add_points_random = 0
        print("mean_add_points_random:",mean_add_points_random)
        json_out["mean_add_points_random"] = mean_add_points_random
        
        nr_func_modeled_random = 0
        for i in range(len(random_functions_modeled)):
            if random_functions_modeled[i] == True:
                nr_func_modeled_random += 1
        print("nr_func_modeled_random:",nr_func_modeled_random)
        
        json_out["nr_func_modeled_random"] = nr_func_modeled_random

        print("")

        ##############
        ### Bayesian ###
        ##############
        
        percentage_bucket_counter_bayesian = calculate_percentage_of_buckets(acurracy_bucket_counter_bayesian, kernels_used)
        print("percentage_bucket_counter_bayesian:",percentage_bucket_counter_bayesian)
        json_out["percentage_bucket_counter_bayesian"] = percentage_bucket_counter_bayesian

        percentage_cost_bayesian_container_filtered = []
        add_points_bayesian_container_filtered = []
        for i in range(len(percentage_cost_bayesian_container)):
            if percentage_cost_bayesian_container[i] <= budget:
                percentage_cost_bayesian_container_filtered.append(percentage_cost_bayesian_container[i])
                add_points_bayesian_container_filtered.append(add_points_bayesian_container[i])
        #print("percentage_cost_bayesian_container:",percentage_cost_bayesian_container)
        #mean_budget_bayesian = np.nanmean(percentage_cost_bayesian_container)
        
        if len(percentage_cost_bayesian_container_filtered) > 0:
            mean_budget_bayesian = np.nanmean(percentage_cost_bayesian_container_filtered)
        else:
            mean_budget_bayesian = 0
        print("mean_budget_bayesian:",mean_budget_bayesian)
        json_out["mean_budget_bayesian"] = mean_budget_bayesian

        if len(add_points_bayesian_container_filtered) > 0:
            mean_add_points_bayesian = np.nanmean(add_points_bayesian_container_filtered)
        else:
            mean_add_points_bayesian = 0
        print("mean_add_points_bayesian:",mean_add_points_bayesian)
        json_out["mean_add_points_bayesian"] = mean_add_points_bayesian
        
        nr_func_modeled_bayesian = 0
        for i in range(len(bayesian_functions_modeled)):
            if bayesian_functions_modeled[i] == True:
                nr_func_modeled_bayesian += 1
        print("nr_func_modeled_bayesian:",nr_func_modeled_bayesian)
        
        json_out["nr_func_modeled_bayesian"] = nr_func_modeled_bayesian

        ###################
        ### Base Points ###
        ###################

        base_point_costs_filtered = []
        for x in base_point_costs:
            if x <= budget:
                base_point_costs_filtered.append(x)
        #mean_base_point_cost = np.nanmean(base_point_costs)
        mean_base_point_cost = np.nanmean(base_point_costs_filtered)
        print("")
        print("mean_base_point_cost:",mean_base_point_cost)

        ####################
        # Plot the results #
        ####################

        # plot the results of the model accuracy analysis
        if plot == True and newonly == False:
            plot_model_accuracy(percentage_bucket_counter_full, percentage_bucket_counter_generic, percentage_bucket_counter_gpr, percentage_bucket_counter_hybrid, budget)
        
        used_costs = {
            "Base points": np.array([mean_base_point_cost, mean_base_point_cost, mean_base_point_cost, mean_base_point_cost]),
            "Additional points": np.array([100-mean_base_point_cost, mean_budget_generic-mean_base_point_cost, mean_budget_gpr-mean_base_point_cost, mean_budget_hybrid-mean_base_point_cost]),
        }
        json_out["base_point_cost"] = mean_base_point_cost
        json_out["min_points"] = min_points
        json_out["budget"] = budget

        # plot the analysis result for the costs and budgets
        if plot == True and newonly == False:
            plot_costs(used_costs, mean_base_point_cost, budget)

        len_coordinates = len(experiment.coordinates)
        add_points = {
            "Base points": np.array([min_points, min_points, min_points, min_points]),
            "Additional points": np.array([len_coordinates*nr_repetitions, mean_add_points_generic, mean_add_points_gpr, mean_add_points_hybrid]),
        }

        # plot the analysis result for the additional measurement point numbers
        if plot == True and newonly == False:
            plot_measurement_point_number(add_points, min_points, budget)
            
        ##############################
        # Write results to json file #
        ##############################

        # write results to file
        json_object = json.dumps(json_out, indent=4)

        budget_string = "{:0.1f}".format(budget)
        with open("result.budget."+str(budget_string)+".json", "w") as outfile:
            outfile.write(json_object)
    
    else:
        logging.error("No file path given to load files.")
        sys.exit(1)


def calculate_selected_point_cost_base(selected_points, experiment, callpath_id, metric_id, nr_base_points):
    # calculate selected point cost
    selected_cost = 0
    for j in range(len(selected_points)):
        coordinate = selected_points[j]
        coordinate_id = -1
        for k in range(len(experiment.coordinates)):
            if coordinate == experiment.coordinates[k]:
                coordinate_id = k
        #print("DEBUG3:", metric_id)
        #print(experiment.metrics)
        counter = 0
        for metric in experiment.metrics:
            if str(metric) == "runtime" or str(metric) == "time":
                break
            else:
                counter += 1
        #print(counter)
        measurement_temp = experiment.get_measurement(coordinate_id, callpath_id, counter)
        #print("measurement_temp:",measurement_temp)
        coordinate_cost = 0
        if measurement_temp != None:
            counter = 0
            while counter < nr_base_points:
            #for k in range(len(measurement_temp.values)):
                runtime = np.mean(measurement_temp.values[counter])
                nr_processes = coordinate.as_tuple()[0]
                core_hours = runtime * nr_processes
                coordinate_cost += core_hours
                counter += 1
        selected_cost += coordinate_cost
    return selected_cost

if __name__ == "__main__":
    starttime = time.time()
    os.environ["TQDM_DISABLE"] = "1"
    main()
    endtime = time.time()
    runtime = endtime - starttime
    print("runtime:",runtime)
