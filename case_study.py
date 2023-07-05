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

def calculate_selected_point_cost(selected_points, experiment, callpath_id, metric_id):
    # calculate selected point cost
    selected_cost = 0
    for j in range(len(selected_points)):
        coordinate = selected_points[j]
        coordinate_id = -1
        for k in range(len(experiment.coordinates)):
            if coordinate == experiment.coordinates[k]:
                coordinate_id = k
        measurement_temp = experiment.get_measurement(coordinate_id, callpath_id, metric_id)
        #print("measurement_temp:",measurement_temp)
        coordinate_cost = 0
        if measurement_temp != None:
            for k in range(len(measurement_temp.values)):
                runtime = measurement_temp.values[k]
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


def get_extrap_model(experiment, args):
    # initialize model generator
    model_generator = ModelGenerator(
        experiment, modeler=args.modeler, use_median=True)

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

    with ProgressBar(desc='Generating models') as pbar:
        # create models from data
        model_generator.model_all(pbar)

    modeler = experiment.modelers[0]
    models = modeler.models
    extrap_function_string = ""
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

    parser.add_argument("--budget", type=int, required=True, default=100,
                        help="Percentage of total cost of all points that can be used by the selection strategies. Positive integer value between 0-100.")
    
    parser.add_argument("--plot", type=bool, required=False, default=False,
                        help="Set if the plots should be shown after running the anlysis.")

    parser.add_argument("--processes", type=int, required=True,
                        help="Set which number in the list of parameters is the number of processes/MPI ranks. Positive integer value between 0-x.")
    
    parser.add_argument("--parameters", type=str, required=True,
                        help="Set the parameters of the experiments, used for eval(). String list of the parameter names.")

    parser.add_argument("--eval_point", type=str, required=True,
                        help="Set the measurement point that will be used for the evaluation of the predictive power of the models. String list of the parameter values of the measurement point.")
    
    parser.add_argument("--filter", type=int, required=True,
                        help="Set a integer value as percentage filter for callpaths. Sets how much they need to contribute to ovarll runtime to be used for analysis.")
    
    parser.add_argument("--normalization", type=bool, default=False,
                        help="Set if normalization of the measurement points parameter values is used for the gpr approach.")

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

    #TODO: make sure the code works for all case studies: Quicksilver
    
    budget = int(args.budget)
    print("budget:",budget)

    processes = args.processes
    print("processes:",processes)

    parameters = args.parameters
    print("parameters:",parameters)

    eval_point = args.eval_point
    print("eval_point:",eval_point)

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
            experiment, modeler=args.modeler, use_median=use_median)

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
        with ProgressBar(desc='Generating models') as pbar:
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
                            runtime = measurement_temp.values[k]
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

        kernels_used = 0

        for callpath_id in range(len(experiment.callpaths)):
            callpath = experiment.callpaths[callpath_id]
            callpath_string = callpath.name

            # get the cost values for this particular callpath
            cost = cost_container[callpath_string]
            total_cost = total_costs_container[callpath_string]

            overall_runtime = runtime_sums[callpath_string]
            opc = total_runtime_sum / 100
            callpath_cost = overall_runtime / opc
            
            if callpath_cost >= filter:
                kernels_used += 1
                #print("callpath_cost_percent_from_total:",callpath_cost)

                # create copy of the cost dict
                remaining_points = copy.deepcopy(cost)
            
                # select points with generic strategy

                if len(experiment.parameters) == 2:
                
                    # find the cheapest line of 5 points for y
                    y_lines = {}
                    for i in range(len(experiment.coordinates)):
                        cord_values = experiment.coordinates[i].as_tuple()
                        x = cord_values[0]
                        y = []
                        for j in range(len(experiment.coordinates)):
                            cord_values2 = experiment.coordinates[j].as_tuple()
                            if cord_values2[0] == x:
                                y.append(cord_values2[1])
                        if len(y) == 5:
                            #print("x:",x)
                            #print("y:",y)
                            if x not in y_lines:
                                y_lines[x] = y
                    #print("y_lines:",y_lines)
                    # calculate the cost of each of the lines
                    line_costs = {}
                    for key, value in y_lines.items():
                        line_cost = 0
                        for i in range(len(value)):
                            point_cost = sum(cost[Coordinate(key, value[i])])
                            line_cost += point_cost
                        line_costs[key] = line_cost
                    #print("line_costs:",line_costs)
                    x_value = min(line_costs, key=line_costs.get)
                    y_values = y_lines[min(line_costs, key=line_costs.get)]
                    #print("y_values:",y_values)

                    # remove these points from the list of remaining points
                    for j in range(len(y_values)):
                        try:
                            cord = Coordinate(x_value, y_values[j])
                            remaining_points.pop(cord)
                        except KeyError:
                            pass

                    # add these points to the list of selected points
                    selected_points = []
                    for i in range(len(y_values)):
                        cord = Coordinate(x_value, y_values[i])
                        selected_points.append(cord)

                    #print("selected_points:",selected_points)

                    # find the cheapest line of 5 points for x
                    x_lines = {}
                    for i in range(len(experiment.coordinates)):
                        cord_values = experiment.coordinates[i].as_tuple()
                        y = cord_values[1]
                        x = []
                        for j in range(len(experiment.coordinates)):
                            cord_values2 = experiment.coordinates[j].as_tuple()
                            if cord_values2[1] == y:
                                x.append(cord_values2[0])
                        if len(x) == 5:
                            #print("x:",x)
                            #print("y:",y)
                            if y not in x_lines:
                                x_lines[y] = x
                    #print("x_lines:",x_lines)
                    # calculate the cost of each of the lines
                    line_costs = {}
                    for key, value in x_lines.items():
                        line_cost = 0
                        for i in range(len(value)):
                            point_cost = sum(cost[Coordinate(value[i], key)])
                            line_cost += point_cost
                        line_costs[key] = line_cost
                    #print("line_costs:",line_costs)
                    y_value = min(line_costs, key=line_costs.get)
                    x_values = x_lines[min(line_costs, key=line_costs.get)]
                    #print("x_values:",x_values)

                    # remove these points from the list of remaining points
                    for j in range(len(x_values)):
                        try:
                            cord = Coordinate(x_values[j], y_value)
                            remaining_points.pop(cord)
                        except KeyError:
                            pass

                    # add these points to the list of selected points
                    for i in range(len(x_values)):
                        cord = Coordinate(x_values[i], y_value)
                        exists = False
                        for j in range(len(selected_points)):
                            if selected_points[j] == cord:
                                exists = True
                                break
                        if exists == False:
                            selected_points.append(cord)

                elif len(experiment.parameters) == 3:
                    
                    # find the cheapest line of 5 points for y
                    y_lines = {}
                    for i in range(len(experiment.coordinates)):
                        cord_values = experiment.coordinates[i].as_tuple()
                        x = cord_values[0]
                        y = []
                        z = cord_values[2]
                        for j in range(len(experiment.coordinates)):
                            cord_values2 = experiment.coordinates[j].as_tuple()
                            if cord_values2[0] == x and cord_values2[2] == z:
                                y.append(cord_values2[1])
                        #print("y:",y)
                        if len(y) >= 5:
                            #print("x:",x)
                            #print("y:",y)
                            #print("z:",z)
                            if (x,z) not in y_lines:
                                y_lines[(x,z)] = y
                    #print("y_lines:",y_lines)
                    # calculate the cost of each of the lines
                    line_costs = {}
                    for key, value in y_lines.items():
                        line_cost = 0
                        for i in range(len(value)):
                            point_cost = sum(cost[Coordinate(key[0], value[i], key[1])])
                            line_cost += point_cost
                        line_costs[key] = line_cost
                    #print("line_costs:",line_costs)
                    x_value, z_value = min(line_costs, key=line_costs.get)
                    y_values = y_lines[min(line_costs, key=line_costs.get)]
                    #print("values:",x_value, z_value)
                    #print("y_values:",y_values)

                    # remove these points from the list of remaining points
                    for j in range(len(y_values)):
                        try:
                            cord = Coordinate(x_value, y_values[j], z_value)
                            remaining_points.pop(cord)
                        except KeyError:
                            pass

                    # add these points to the list of selected points
                    selected_points = []
                    for i in range(len(y_values)):
                        cord = Coordinate(x_value, y_values[i], z_value)
                        selected_points.append(cord)

                    #print("selected_points:",selected_points)

                    # find the cheapest line of 5 points for x
                    x_lines = {}
                    for i in range(len(experiment.coordinates)):
                        cord_values = experiment.coordinates[i].as_tuple()
                        y = cord_values[1]
                        x = []
                        z = cord_values[2]
                        for j in range(len(experiment.coordinates)):
                            cord_values2 = experiment.coordinates[j].as_tuple()
                            if cord_values2[1] == y and cord_values2[2] == z:
                                x.append(cord_values2[0])
                        if len(x) >= 5:
                            #print("x:",x)
                            #print("y:",y)
                            if (y,z) not in x_lines:
                                x_lines[(y,z)] = x
                    #print("x_lines:",x_lines)
                    # calculate the cost of each of the lines
                    line_costs = {}
                    for key, value in x_lines.items():
                        line_cost = 0
                        for i in range(len(value)):
                            point_cost = sum(cost[Coordinate(value[i], key[0], key[1])])
                            line_cost += point_cost
                        line_costs[key] = line_cost
                    #print("line_costs:",line_costs)
                    y_value, z_value = min(line_costs, key=line_costs.get)
                    x_values = x_lines[min(line_costs, key=line_costs.get)]
                    #print("x_values:",x_values)

                    # remove these points from the list of remaining points
                    for j in range(len(x_values)):
                        try:
                            cord = Coordinate(x_values[j], y_value, z_value)
                            remaining_points.pop(cord)
                        except KeyError:
                            pass

                    # add these points to the list of selected points
                    for i in range(len(x_values)):
                        cord = Coordinate(x_values[i], y_value, z_value)
                        exists = False
                        for j in range(len(selected_points)):
                            if selected_points[j] == cord:
                                exists = True
                                break
                        if exists == False:
                            selected_points.append(cord)

                    #print("selected_points:",selected_points)

                    # find the cheapest line of 5 points for z
                    z_lines = {}
                    for i in range(len(experiment.coordinates)):
                        cord_values = experiment.coordinates[i].as_tuple()
                        x = cord_values[0]
                        z = []
                        y = cord_values[1]
                        for j in range(len(experiment.coordinates)):
                            cord_values2 = experiment.coordinates[j].as_tuple()
                            if cord_values2[0] == x and cord_values2[1] == y:
                                z.append(cord_values2[2])
                        if len(z) >= 5:
                            #print("z:",z)
                            #print("y:",y)
                            #print("x:",x)
                            if (x,y) not in z_lines:
                                z_lines[(x,y)] = z
                    #print("z_lines:",z_lines)
                    # calculate the cost of each of the lines
                    line_costs = {}
                    for key, value in z_lines.items():
                        line_cost = 0
                        for i in range(len(value)):
                            point_cost = sum(cost[Coordinate(key[0], key[1], value[i])])
                            line_cost += point_cost
                        line_costs[key] = line_cost
                    #print("line_costs:",line_costs)
                    x_value, y_value = min(line_costs, key=line_costs.get)
                    z_values = z_lines[min(line_costs, key=line_costs.get)]
                    #print("z_values:",z_values)

                    # remove these points from the list of remaining points
                    for j in range(len(z_values)):
                        try:
                            cord = Coordinate(x_value, y_value, z_values[j])
                            remaining_points.pop(cord)
                        except KeyError:
                            pass

                    # add these points to the list of selected points
                    for i in range(len(z_values)):
                        cord = Coordinate(x_value, y_value, z_values[i])
                        exists = False
                        for j in range(len(selected_points)):
                            if selected_points[j] == cord:
                                exists = True
                                break
                        if exists == False:
                            selected_points.append(cord)

                    #print("selected_points:",selected_points)

                else:
                    return 1

                #print("selected_points:",selected_points)

                # calculate the cost for the selected base points
                base_point_cost = calculate_selected_point_cost(selected_points, experiment, callpath_id, metric_id)
                base_point_cost = base_point_cost / (total_cost / 100)
                #print("base_point_cost %:",base_point_cost)

                # add some additional single points

                # select x cheapest measurement(s) that are not part of the list so far
                # continue doing this until there is no improvement in smape value on measured points for a delta of X iterations
                added_points_generic = 0

                #print("len selected_coord_list:",len(selected_coord_list))

                # add the first additional point, this is mandatory for the generic strategy
                remaining_points_base, selected_coord_list_base = add_additional_point_generic(remaining_points, selected_points)
                # increment counter value, because a new measurement point was added
                added_points_generic += 1

                # create first model
                experiment_generic_base = create_experiment(selected_coord_list_base, experiment, len(experiment.parameters), parameters, metric_id, callpath_id)
                _, models = get_extrap_model(experiment_generic_base, args)
                hypothesis = None
                for model in models.values():
                    hypothesis = model.hypothesis

                # calculate selected point cost
                current_cost = calculate_selected_point_cost(selected_coord_list_base, experiment, callpath_id, metric_id)
                current_cost_percent = current_cost / (total_cost / 100)
                
                if current_cost_percent <= budget:
                    while True:
                        # find another point for selection
                        remaining_points_new, selected_coord_list_new = add_additional_point_generic(remaining_points_base, selected_coord_list_base)

                        # calculate selected point cost
                        current_cost = calculate_selected_point_cost(selected_coord_list_new, experiment, callpath_id, metric_id)
                        current_cost_percent = current_cost / (total_cost / 100)

                        # current cost exceeds budget so break the loop
                        if current_cost_percent >= budget:
                            break

                        # add the new found point
                        else:

                            # increment counter value, because a new measurement point was added
                            added_points_generic += 1

                            # create new model
                            experiment_generic_base = create_experiment(selected_coord_list_new, experiment, len(experiment.parameters), parameters, metric_id, callpath_id)
                            #_, models = get_extrap_model(experiment_generic_base, args)
                            #hypothesis = None
                            #for model in models.values():
                            #    hypothesis = model.hypothesis

                            selected_coord_list_base = selected_coord_list_new
                            remaining_points_base = remaining_points_new

                        # if there are no points remaining that can be selected break the loop
                        if len(remaining_points_base) == 0:
                            break

                else:
                    pass

                # calculate selected point cost
                selected_cost = calculate_selected_point_cost(selected_coord_list_base, experiment, callpath_id, metric_id)

                # calculate the percentage of cost of the selected points compared to the total cost of the full matrix
                percentage_cost_generic = selected_cost / (total_cost / 100)
                percentage_cost_generic_container.append(percentage_cost_generic)

                # calculate number of additionally used data points (exceeding the base requirement of the sparse modeler)
                #add_points_generic = len(selected_coord_list_base) - min_points
                add_points_generic_container.append(added_points_generic)
                
                # create model using point selection of generic strategy
                model_generic, _ = get_extrap_model(experiment_generic_base, args)
                
                # create model using full matrix of points
                # evaluate model accuracy against the first point in each direction of the parameter set for each parameter
                if parameters[0] == "p" and parameters[1] == "size":
                    p = int(eval_point[0])
                    size = int(eval_point[1])
                elif parameters[0] == "p" and parameters[1] == "n":
                    p = int(eval_point[0])
                    n = int(eval_point[1])
                elif parameters[0] == "p" and parameters[1] == "s":
                    p = int(eval_point[0])
                    s = int(eval_point[1])
                elif parameters[0] == "p" and parameters[1] == "d" and parameters[2] == "g":
                    p = int(eval_point[0])
                    d = int(eval_point[1])
                    g = int(eval_point[2])
                elif parameters[0] == "p" and parameters[1] == "m" and parameters[2] == "n":
                    p = int(eval_point[0])
                    m = int(eval_point[1])
                    n = int(eval_point[2])

                prediction_full = eval(all_points_functions_strings[callpath_string])
                #print("prediction_full:",prediction_full)
                prediction_generic = eval(model_generic)
                #print("prediction_generic:",prediction_generic)

                # get the actual measured value
                eval_measurement = None
                if len(experiment.parameters) == 2:
                    for o in range(len(coordinate_evaluation)):
                        parameter_values = coordinate_evaluation[o].as_tuple()
                        #print("parameter_values:",parameter_values)
                        if parameter_values[0] == float(eval_point[0]) and parameter_values[1] == float(eval_point[1]):
                            eval_measurement = measurement_evaluation[experiment.callpaths[callpath_id], experiment.metrics[metric_id]][o]
                            break
                elif len(experiment.parameters) == 3:
                    for o in range(len(coordinate_evaluation)):
                        parameter_values = coordinate_evaluation[o].as_tuple()
                        #print("parameter_values:",parameter_values)
                        if parameter_values[0] == float(eval_point[0]) and parameter_values[1] == float(eval_point[1]) and parameter_values[2] == float(eval_point[2]):
                            eval_measurement = measurement_evaluation[experiment.callpaths[callpath_id], experiment.metrics[metric_id]][o]
                            break
                else:
                    return 1

                #print("eval_measurement:",eval_measurement)
                actual = eval_measurement.mean
                #print("actual:",actual)

                # get the percentage error for the full matrix of points
                error_full = abs(percentage_error(actual, prediction_full))
                #print("error_full:",error_full)

                # get the percentage error for the full matrix of points
                error_generic = abs(percentage_error(actual, prediction_generic))
                #print("error_generic:",error_generic)

                # increment accuracy bucket for full matrix of points
                acurracy_bucket_counter_full = increment_accuracy_bucket(acurracy_bucket_counter_full, error_full)

                # increment accuracy bucket for generic strategy
                acurracy_bucket_counter_generic = increment_accuracy_bucket(acurracy_bucket_counter_generic, error_generic)

                ##################
                ## GPR strategy ##
                ##################

                # GPR parameter-value normalization for each measurement point
                normalization_factors = {}

                if normalization:
                    
                    for i in range(len(experiment.parameters)):

                        param_value_max = -1

                        for coord in experiment.coordinates:

                            temp = coord.as_tuple()[i]

                            if param_value_max < temp:
                                param_value_max = temp
                            
                        param_value_max = 100 / param_value_max
                        normalization_factors[experiment.parameters[i]] = param_value_max
                        
                    print("normalization_factors:",normalization_factors)
                
                # do an noise analysis on the existing points
                mm = experiment.measurements
                #print("DEBUG:",mm)
                nn = mm[(callpath, metric)]
                #print("DEBUG:",nn)
                temp = []
                for cord in selected_points:
                    for meas in nn:
                        if meas.coordinate == cord:
                            temp.append(meas)
                            break
                #print("temp:",temp)
                nns = []
                for meas in temp:
                    #print("DEBUG:",meas.values)
                    mean_mes = np.mean(meas.values)
                    pps = []
                    for val in meas.values:
                        pp = abs((val / (mean_mes / 100)) - 100)
                        pps.append(pp)
                        #print(pp,"%")
                    nn = np.mean(pps)
                    nns.append(nn)
                mean_noise = np.mean(nns)
                #print("mean_noise:",mean_noise,"%")

                # nu should be [0.5, 1.5, 2.5, inf], everything else has 10x overhead
                # matern kernel + white kernel to simulate actual noise found in the measurements
                kernel = 1.0 * Matern(length_scale=1.0, length_scale_bounds=(1e-5, 1e5), nu=1.5) + WhiteKernel(noise_level=mean_noise)

                # create a gaussian process regressor
                gaussian_process = GaussianProcessRegressor(
                    kernel=kernel, n_restarts_optimizer=20
                )

                # add all of the selected measurement points to the gaussian process
                # as training data and train it for these points
                gaussian_process = add_measurements_to_gpr(gaussian_process, 
                                selected_points, 
                                experiment.measurements, 
                                callpath, 
                                metric,
                                normalization_factors,
                                experiment.parameters, eval_point)
                
                # add additional measurement points until break criteria is met
                add_points_gpr = 0
                budget_core_hours = budget * (total_cost / 100)

                remaining_points_gpr = copy.deepcopy(remaining_points)
                selected_points_gpr = copy.deepcopy(selected_points)

                # create base model for gpr
                experiment_gpr_base = create_experiment(selected_points_gpr, experiment, len(experiment.parameters), parameters, metric_id, callpath_id)
                    
                while True:

                    # identify all possible next points that would 
                    # still fit into the modeling budget in core hours
                    fitting_measurements = []
                    for key, value in remaining_points_gpr.items():

                        current_cost = calculate_selected_point_cost(selected_points_gpr, experiment, callpath_id, metric_id)
                        new_cost = current_cost + np.sum(value)
                        
                        if new_cost <= budget_core_hours:
                            fitting_measurements.append(key)

                    #print("fitting_measurements:",fitting_measurements)

                    # find the next best additional measurement point using the gpr
                    best_index = -1
                    best_rated = sys.float_info.max

                    for i in range(len(fitting_measurements)):
                    
                        parameter_values = fitting_measurements[i].as_tuple()
                        x = []
                        
                        for j in range(len(parameter_values)):
                        
                            if len(normalization_factors) != 0:
                                x.append(parameter_values[j] * normalization_factors[experiment.parameters[j]])
                        
                            else:
                                x.append(parameter_values[j])
                        
                        # term_1 is cost(t)^2
                        term_1 = math.pow(np.sum(remaining_points_gpr[fitting_measurements[i]]), 2)
                        # predict variance of input vector x with the gaussian process
                        x = [x]
                        _, y_cov = gaussian_process.predict(x, return_cov=True)
                        y_cov = abs(y_cov)
                        # term_2 is gp_cov(t,t)^2
                        term_2 = math.pow(y_cov, 2)
                        # rated is h(t)
                        rated = term_1 / term_2

                        if rated <= best_rated:
                            best_rated = rated
                            best_index = i    

                    # if there has been a point found that is suitable
                    if best_index != -1:

                        # add the identified measurement point to the selected point list
                        parameter_values = fitting_measurements[best_index].as_tuple()
                        cord = Coordinate(parameter_values)
                        selected_points_gpr.append(cord)
                        
                        # add the new point to the gpr and call fit()
                        gaussian_process = add_measurement_to_gpr(gaussian_process, 
                                cord, 
                                experiment.measurements, 
                                callpath, 
                                metric,
                                normalization_factors,
                                experiment.parameters)
                        
                        # remove the identified measurement point from the remaining point list
                        try:
                            remaining_points_gpr.pop(cord)
                        except KeyError:
                            pass

                        # update the number of additional points used
                        add_points_gpr += 1

                        # add this point to the gpr experiment
                        experiment_gpr_base = create_experiment(selected_points_gpr, experiment, len(experiment.parameters), parameters, metric_id, callpath_id)

                    # if there are no suitable measurement points found
                    # break the while True loop
                    else:
                        break

                current_cost = calculate_selected_point_cost(selected_points_gpr, experiment, callpath_id, metric_id)
                current_cost_percent = current_cost / (total_cost / 100)
                
                # cost used of the gpr strategy
                percentage_cost_gpr_container.append(current_cost_percent)

                # additionally used data points (exceeding the base requirement of the sparse modeler)
                add_points_gpr_container.append(add_points_gpr)

                # create model using point selection of gpr strategy
                model_generic, _ = get_extrap_model(experiment_gpr_base, args)
                
                # create model using full matrix of points
                # evaluate model accuracy against the first point in each direction of the parameter set for each parameter
                if parameters[0] == "p" and parameters[1] == "size":
                    p = int(eval_point[0])
                    size = int(eval_point[1])
                elif parameters[0] == "p" and parameters[1] == "n":
                    p = int(eval_point[0])
                    n = int(eval_point[1])
                elif parameters[0] == "p" and parameters[1] == "s":
                    p = int(eval_point[0])
                    s = int(eval_point[1])
                elif parameters[0] == "p" and parameters[1] == "d" and parameters[2] == "g":
                    p = int(eval_point[0])
                    d = int(eval_point[1])
                    g = int(eval_point[2])
                elif parameters[0] == "p" and parameters[1] == "m" and parameters[2] == "n":
                    p = int(eval_point[0])
                    m = int(eval_point[1])
                    n = int(eval_point[2])

                prediction_full = eval(all_points_functions_strings[callpath_string])
                #print("prediction_full:",prediction_full)
                prediction_gpr = eval(model_generic)
                #print("prediction_gpr:",prediction_gpr)

                # get the actual measured value
                eval_measurement = None
                if len(experiment.parameters) == 2:
                    for o in range(len(coordinate_evaluation)):
                        parameter_values = coordinate_evaluation[o].as_tuple()
                        #print("parameter_values:",parameter_values)
                        if parameter_values[0] == float(eval_point[0]) and parameter_values[1] == float(eval_point[1]):
                            eval_measurement = measurement_evaluation[experiment.callpaths[callpath_id], experiment.metrics[metric_id]][o]
                            break
                elif len(experiment.parameters) == 3:
                    for o in range(len(coordinate_evaluation)):
                        parameter_values = coordinate_evaluation[o].as_tuple()
                        #print("parameter_values:",parameter_values)
                        if parameter_values[0] == float(eval_point[0]) and parameter_values[1] == float(eval_point[1]) and parameter_values[2] == float(eval_point[2]):
                            eval_measurement = measurement_evaluation[experiment.callpaths[callpath_id], experiment.metrics[metric_id]][o]
                            break
                else:
                    return 1

                #print("eval_measurement:",eval_measurement)
                actual = eval_measurement.mean
                #print("actual:",actual)

                # get the percentage error for the full matrix of points
                error_gpr = abs(percentage_error(actual, prediction_gpr))
                #print("error_gpr:",error_gpr)

                # increment accuracy bucket for gpr strategy
                acurracy_bucket_counter_gpr = increment_accuracy_bucket(acurracy_bucket_counter_gpr, error_gpr)

                #####################
                ## Hybrid strategy ##
                #####################

                # do an noise analysis on the existing points
                mm = experiment.measurements
                #print("DEBUG:",mm)
                nn = mm[(callpath, metric)]
                #print("DEBUG:",nn)
                temp = []
                for cord in selected_points:
                    for meas in nn:
                        if meas.coordinate == cord:
                            temp.append(meas)
                            break
                #print("temp:",temp)
                nns = []
                for meas in temp:
                    #print("DEBUG:",meas.values)
                    mean_mes = np.mean(meas.values)
                    pps = []
                    for val in meas.values:
                        pp = abs((val / (mean_mes / 100)) - 100)
                        pps.append(pp)
                        #print(pp,"%")
                    nn = np.mean(pps)
                    nns.append(nn)
                mean_noise = np.mean(nns)
                #print("mean_noise:",mean_noise,"%")

                # nu should be [0.5, 1.5, 2.5, inf], everything else has 10x overhead
                # matern kernel + white kernel to simulate actual noise found in the measurements
                kernel = 1.0 * Matern(length_scale=1.0, length_scale_bounds=(1e-5, 1e5), nu=1.5) + WhiteKernel(noise_level=mean_noise)

                # create a gaussian process regressor
                gaussian_process_hybrid = GaussianProcessRegressor(
                    kernel=kernel, alpha=0.75**2, n_restarts_optimizer=9
                )

                # add all of the selected measurement points to the gaussian process
                # as training data and train it for these points
                gaussian_process_hybrid = add_measurements_to_gpr(gaussian_process_hybrid, 
                                selected_points, 
                                experiment.measurements, 
                                callpath, 
                                metric,
                                normalization_factors,
                                experiment.parameters, eval_point)
                
                # add additional measurement points until break criteria is met
                add_points_hybrid = 0
                budget_core_hours = budget * (total_cost / 100)

                remaining_points_hybrid = copy.deepcopy(remaining_points)
                selected_points_hybrid = copy.deepcopy(selected_points)

                # create base model for gpr hybrid
                experiment_hybrid_base = create_experiment(selected_points_hybrid, experiment, len(experiment.parameters), parameters, metric_id, callpath_id)
                 
                while True:

                    # identify all possible next points that would 
                    # still fit into the modeling budget in core hours
                    fitting_measurements = []
                    for key, value in remaining_points_hybrid.items():

                        current_cost = calculate_selected_point_cost(selected_points_hybrid, experiment, callpath_id, metric_id)
                        new_cost = current_cost + np.sum(value)
                        
                        if new_cost <= budget_core_hours:
                            fitting_measurements.append(key)

                    #print("fitting_measurements:",fitting_measurements)

                    # determine the switching point between gpr and hybrid strategy
                    swtiching_point = 0
                    if len(experiment.parameters) == 2:
                        swtiching_point = 11
                    elif len(experiment.parameters) == 3:
                        swtiching_point = 18
                    elif len(experiment.parameters) == 4:
                        swtiching_point = 25
                    else:
                        swtiching_point = 11

                    best_index = -1
                    
                    # find the next best additional measurement point using the gpr strategy
                    if add_points_hybrid + min_points > swtiching_point:
                        best_rated = sys.float_info.max

                        for i in range(len(fitting_measurements)):
                    
                            parameter_values = fitting_measurements[i].as_tuple()
                            x = []
                            
                            for j in range(len(parameter_values)):
                            
                                if len(normalization_factors) != 0:
                                    x.append(parameter_values[j] * normalization_factors[experiment.parameters[j]])
                            
                                else:
                                    x.append(parameter_values[j])
                            
                            # term_1 is cost(t)^2
                            term_1 = math.pow(np.sum(remaining_points_hybrid[fitting_measurements[i]]), 2)
                            # predict variance of input vector x with the gaussian process
                            x = [x]
                            _, y_cov = gaussian_process_hybrid.predict(x, return_cov=True)
                            y_cov = abs(y_cov)
                            # term_2 is gp_cov(t,t)^2
                            term_2 = math.pow(y_cov, 2)
                            # rated is h(t)
                            rated = term_1 / term_2

                            if rated <= best_rated:
                                best_rated = rated
                                best_index = i 

                    # find the next best additional measurement point using the generic strategy
                    else:
                        lowest_cost = sys.float_info.max
                        for i in range(len(fitting_measurements)):
                            
                            # get the cost of the measurement point
                            cost = np.sum(remaining_points_hybrid[fitting_measurements[i]])
                        
                            if cost < lowest_cost:
                                lowest_cost = cost
                                best_index = i

                    # if there has been a point found that is suitable
                    if best_index != -1:

                        # add the identified measurement point to the experiment, selected point list
                        parameter_values = fitting_measurements[best_index].as_tuple()
                        cord = Coordinate(parameter_values)
                        selected_points_hybrid.append(cord)
                        
                        # add the new point to the gpr and call fit()
                        gaussian_process_hybrid = add_measurement_to_gpr(gaussian_process_hybrid, 
                                cord, 
                                experiment.measurements, 
                                callpath, 
                                metric,
                                normalization_factors,
                                experiment.parameters)
                        
                        # remove the identified measurement point from the remaining point list
                        try:
                            remaining_points_hybrid.pop(cord)
                        except KeyError:
                            pass

                        # update the number of additional points used
                        add_points_hybrid += 1

                        # add this point to the hybrid experiment
                        experiment_hybrid_base = create_experiment(selected_points_hybrid, experiment, len(experiment.parameters), parameters, metric_id, callpath_id)

                    # if there are no suitable measurement points found
                    # break the while True loop
                    else:
                        break

                current_cost = calculate_selected_point_cost(selected_points_hybrid, experiment, callpath_id, metric_id)
                current_cost_percent = current_cost / (total_cost / 100)

                # cost used of the hybrid strategy
                percentage_cost_hybrid_container.append(current_cost_percent)

                # additionally used data points (exceeding the base requirement of the sparse modeler)
                add_points_hybrid_container.append(add_points_hybrid)

                # create model using point selection of hybrid strategy
                model_generic, _ = get_extrap_model(experiment_hybrid_base, args)
                
                # create model using full matrix of points
                # evaluate model accuracy against the first point in each direction of the parameter set for each parameter
                if parameters[0] == "p" and parameters[1] == "size":
                    p = int(eval_point[0])
                    size = int(eval_point[1])
                elif parameters[0] == "p" and parameters[1] == "n":
                    p = int(eval_point[0])
                    n = int(eval_point[1])
                elif parameters[0] == "p" and parameters[1] == "s":
                    p = int(eval_point[0])
                    s = int(eval_point[1])
                elif parameters[0] == "p" and parameters[1] == "d" and parameters[2] == "g":
                    p = int(eval_point[0])
                    d = int(eval_point[1])
                    g = int(eval_point[2])
                elif parameters[0] == "p" and parameters[1] == "m" and parameters[2] == "n":
                    p = int(eval_point[0])
                    m = int(eval_point[1])
                    n = int(eval_point[2])

                prediction_full = eval(all_points_functions_strings[callpath_string])
                #print("prediction_full:",prediction_full)
                prediction_hybrid = eval(model_generic)
                #print("prediction_hybrid:",prediction_hybrid)

                # get the actual measured value
                eval_measurement = None
                if len(experiment.parameters) == 2:
                    for o in range(len(coordinate_evaluation)):
                        parameter_values = coordinate_evaluation[o].as_tuple()
                        #print("parameter_values:",parameter_values)
                        if parameter_values[0] == float(eval_point[0]) and parameter_values[1] == float(eval_point[1]):
                            eval_measurement = measurement_evaluation[experiment.callpaths[callpath_id], experiment.metrics[metric_id]][o]
                            break
                elif len(experiment.parameters) == 3:
                    for o in range(len(coordinate_evaluation)):
                        parameter_values = coordinate_evaluation[o].as_tuple()
                        #print("parameter_values:",parameter_values)
                        if parameter_values[0] == float(eval_point[0]) and parameter_values[1] == float(eval_point[1]) and parameter_values[2] == float(eval_point[2]):
                            eval_measurement = measurement_evaluation[experiment.callpaths[callpath_id], experiment.metrics[metric_id]][o]
                            break
                else:
                    return 1

                #print("eval_measurement:",eval_measurement)
                actual = eval_measurement.mean
                #print("actual:",actual)

                # get the percentage error for the full matrix of points
                error_hybrid = abs(percentage_error(actual, prediction_hybrid))
                #print("error_hybrid:",error_hybrid)

                # increment accuracy bucket for hybrid strategy
                acurracy_bucket_counter_hybrid = increment_accuracy_bucket(acurracy_bucket_counter_hybrid, error_hybrid)

            else:
                pass

        print("Number of kernels used:",kernels_used,"of",len(experiment.callpaths),"callpaths.")
        print("Total number of measurement points:",len(experiment.coordinates))

        #print("acurracy_bucket_counter_full:",acurracy_bucket_counter_full)
        #print("acurracy_bucket_counter_generic:",acurracy_bucket_counter_generic)
        #print("acurracy_bucket_counter_gpr:",acurracy_bucket_counter_gpr)
        #print("acurracy_bucket_counter_hybrid:",acurracy_bucket_counter_hybrid)

        json_out = {}

        # calculate the percentages for each accuracy bucket
        percentage_bucket_counter_full = calculate_percentage_of_buckets(acurracy_bucket_counter_full, kernels_used)
        print("percentage_bucket_counter_full:",percentage_bucket_counter_full)
        json_out["percentage_bucket_counter_full"] = percentage_bucket_counter_full
        percentage_bucket_counter_generic = calculate_percentage_of_buckets(acurracy_bucket_counter_generic, kernels_used)
        print("percentage_bucket_counter_generic:",percentage_bucket_counter_generic)
        json_out["percentage_bucket_counter_generic"] = percentage_bucket_counter_generic
        percentage_bucket_counter_gpr = calculate_percentage_of_buckets(acurracy_bucket_counter_gpr, kernels_used)
        print("percentage_bucket_counter_gpr:",percentage_bucket_counter_gpr)
        json_out["percentage_bucket_counter_gpr"] = percentage_bucket_counter_gpr
        percentage_bucket_counter_hybrid = calculate_percentage_of_buckets(acurracy_bucket_counter_hybrid, kernels_used)
        print("percentage_bucket_counter_hybrid:",percentage_bucket_counter_hybrid)
        json_out["percentage_bucket_counter_hybrid"] = percentage_bucket_counter_hybrid

        # plot the results of the model accuracy analysis
        if plot == True:
            plot_model_accuracy(percentage_bucket_counter_full, percentage_bucket_counter_generic, percentage_bucket_counter_gpr, percentage_bucket_counter_hybrid)
        
        print("budget:",budget,"%")
        json_out["budget"] = budget

        mean_budget_generic = np.nanmean(percentage_cost_generic_container)
        print("mean_budget_generic:",mean_budget_generic)
        json_out["mean_budget_generic"] = mean_budget_generic

        mean_add_points_generic = np.nanmean(add_points_generic_container)
        print("mean_add_points_generic:",mean_add_points_generic)
        json_out["mean_add_points_generic"] = mean_add_points_generic

        mean_budget_gpr = np.nanmean(percentage_cost_gpr_container)
        print("mean_budget_gpr:",mean_budget_gpr)
        json_out["mean_budget_gpr"] = mean_budget_gpr

        mean_add_points_gpr = np.nanmean(add_points_gpr_container)
        print("mean_add_points_gpr:",mean_add_points_gpr)
        json_out["mean_add_points_gpr"] = mean_add_points_gpr

        mean_budget_hybrid = np.nanmean(percentage_cost_hybrid_container)
        print("mean_budget_hybrid:",mean_budget_hybrid)
        json_out["mean_budget_hybrid"] = mean_budget_hybrid

        mean_add_points_hybrid = np.nanmean(add_points_hybrid_container)
        print("mean_add_points_hybrid:",mean_add_points_hybrid)
        json_out["mean_add_points_hybrid"] = mean_add_points_hybrid

        used_costs = {
            "base points": np.array([base_point_cost, base_point_cost, base_point_cost, base_point_cost]),
            "additional points": np.array([100-base_point_cost, mean_budget_generic-base_point_cost, mean_budget_gpr-base_point_cost, mean_budget_hybrid-base_point_cost]),
        }
        json_out["base_point_cost"] = base_point_cost

        # plot the analysis result for the costs and budgets
        if plot == True:
            plot_costs(used_costs, base_point_cost)

        add_points = {
            "base points": np.array([min_points, min_points, min_points, min_points]),
            "additional points": np.array([len(experiment.coordinates)-min_points, mean_add_points_generic, mean_add_points_gpr, mean_add_points_hybrid]),
        }
        json_out["min_points"] = min_points
        json_out["filter"] = filter

        # plot the analysis result for the additional measurement point numbers
        if plot == True:
            plot_measurement_point_number(add_points, min_points)

        # write results to file
        import json
        json_object = json.dumps(json_out, indent=4)
 
        with open("result.budget."+str(budget)+".json", "w") as outfile:
            outfile.write(json_object)

    else:
        logging.error("No file path given to load files.")
        sys.exit(1)

if __name__ == "__main__":
    main()
