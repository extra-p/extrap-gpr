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
    Runs an evaluation for a case study based on the cube files loaded from the specified directory.

    Command line args:
    --budget: Percentage of total cost of all points that can be used by the selection strategies. Positive integer value between 0-100.

    Returns:
    None
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

    parser.add_argument("--budget", type=int, required=True,
                        help="Percentage of total cost of all points that can be used by the selection strategies. Positive integer value between 0-100.")
    
    parser.add_argument("--processes", type=int, required=True,
                        help="Set which number in the list of parameters is the number of processes/MPI ranks. Positive integer value between 0-x.")
    
    parser.add_argument("--parameters", type=str, required=True,
                        help="Set the parameters of the experiments, used for eval(). String list of the parameter names.")
    
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

    # check scaling type
    scaling_type = args.scaling_type

    # set log level
    loglevel = logging.getLevelName(args.log_level.upper())

    # set output print type
    printtype = args.print_type.upper()

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

    #TODO: FASTEST, Kripke, MILC
    #TODO: need to make measurements for MILC with 2 and three parameters
    #TODO: need to create, read input files for Relearn somehow...

    #NOTE: -> for case studies... I need the percentage of models where the prediction is within +-5, +-10, +-15, +-20 % of the actual measurements
    # using a total budget of 15, 20, 30 % of all available points, for the point selection
    # mit +-1, +-2.5, +-5, +-7.5, +-10 % noise on the measurements for synthetic stuff

    #TODO: use only kernels > 1 % runtime from total???

    budget = args.budget
    print("budget:",budget)

    processes = args.processes
    print("processes:",processes)

    parameters = args.parameters
    print("parameters:",parameters)

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

        experiment.debug()

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

        for name, value in args.modeler_options.items():
            if value is not None:
                setattr(modeler, name, value)

        with ProgressBar(desc='Generating models') as pbar:
            # create models from data
            model_generator.model_all(pbar)

        if args.save_experiment:
            try:
                with ProgressBar(desc='Saving experiment') as pbar:
                    if not os.path.splitext(args.save_experiment)[1]:
                        args.save_experiment += '.extra-p'
                    experiment_io.write_experiment(experiment, args.save_experiment, pbar)
            except RecoverableError as err:
                logging.error('Saving experiment: ' + str(err))
                sys.exit(1)

        # TODO: code for case study analysis

        
        #print(experiment.parameters)

        metric_id = -1
        for i in range(len(experiment.metrics)):
            if str(experiment.metrics[i]) == "time":
                metric_id = i
                break
        metric = experiment.metrics[metric_id]
        metric_string = metric.name

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

        smapes = []
        cost_container = {}
        total_costs_container = {}
        all_points_functions_strings = {}
        
        modeler = experiment.modelers[0]
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
                smape = hypothesis.SMAPE
                ar2 = hypothesis.AR2
                function_string = function.to_string(*experiment.parameters)
                function_string = function_string.replace(" ","")
                function_string = function_string.replace("^","**")
                function_string = function_string.replace("log2","math.log2")
                function_string = function_string.replace("+-","-")
                all_points_functions_strings[callpath_string] = function_string

                #total_cost = 0

                for i in range(len(experiment.coordinates)):
                    if experiment.coordinates[i] not in cost:
                        cost[experiment.coordinates[i]] = []
                    values = experiment.coordinates[i].as_tuple()
                    #print("values:",values)
                    nr_processes = values[processes]
                    coordinate_id = -1
                    for k in range(len(experiment.coordinates)):
                        if experiment.coordinates[i] == experiment.coordinates[k]:
                            coordinate_id = k
                    measurement_temp = experiment.get_measurement(coordinate_id, callpath_id, metric_id)
                    # should calculate with all values not just mean
                    coordinate_cost = 0
                    for k in range(len(measurement_temp.values)):
                        runtime = measurement_temp.values[k]
                        core_hours = runtime * nr_processes
                        coordinate_cost += core_hours
                    total_cost += coordinate_cost

                    """runtime = measurement_temp.mean
                    #print("measurement_temp:",measurement_temp.mean)
                    core_hours = runtime * nr_processes
                    cost[experiment.coordinates[i]].append(core_hours)
                    total_cost += core_hours"""

            else:
                smape = 0
                ar2 = 0
                function_string = "None"
                total_cost = 0

            smapes.append(smape)
            #total_costs.append(total_cost)

            cost_container[callpath_string] = cost
            total_costs_container[callpath_string] = total_cost

            #print(callpath_string, metric_string, function_string, total_cost)



        for callpath_id in range(len(experiment.callpaths)):
            callpath = experiment.callpaths[callpath_id]
            callpath_string = callpath.name

            # get the cost values for this particular callpath
            cost = cost_container[callpath_string]
            total_cost = total_costs_container[callpath_string]

            # create copy of the cost dict
            remaining_points = copy.deepcopy(cost)
        
            # select points with generic strategy
            
            # find the cheapest line of 5 points for x
            #TODO: works only for 2 parameters like that...
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

            #print("DEBUG:",remaining_points)
            # remove these points from the list of remaining points
            for j in range(len(y_lines)):
                try:
                    cord = Coordinate(x_value, y_values[i])
                    #remaining_points[y_lines[j]].remove(y_values[j])
                    remaining_points.pop(cord)
                except KeyError:
                    pass
            #print("DEBUG_2:",remaining_points)

            # add these points to the list of selected points
            selected_points = []
            for i in range(len(y_values)):
                cord = Coordinate(x_value, y_values[i])
                selected_points.append(cord)

            #print("selected_points:",selected_points)

            # find the cheapest line of 5 points for y
            #TODO: works only for 2 parameters like that...
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
            for j in range(len(x_lines)):
                try:
                    cord = Coordinate(x_values[i], y_value)
                    #remaining_points[x_lines[j]].remove(x_values[j])
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

            #print("selected_points:",selected_points)

            # add some additional single points

            # select x cheapest measurement(s) that are not part of the list so far
            # continue doing this until there is no improvement in smape value on measured points for a delta of X iterations
            added_points = 0

            #print("len selected_coord_list:",len(selected_coord_list))

            # add the first additional point, this is mandatory for the generic strategy
            remaining_points_base, selected_coord_list_base = add_additional_point_generic(remaining_points, selected_points)
            # increment counter value, because a new measurement point was added
            added_points += 1

            #print("len selected_coord_list_base:",len(selected_coord_list_base))

            #print("added_points:",added_points)

            # create first model
            experiment_generic_base = create_experiment(selected_coord_list_base, experiment, len(experiment.parameters), parameters, metric_id, callpath_id)
            #print("DEBUG:", len(experiment_generic_base.callpaths))
            _, models = get_extrap_model(experiment_generic_base, args)
            hypothesis = None
            for model in models.values():
                hypothesis = model.hypothesis
            rss_base = hypothesis.SMAPE
            #ar2_base = hypothesis.AR2
            #print("rss_base:",rss_base)
            #print("ar2_base:",ar2_base)

            stall_counter = 1
            #TODO: find the best delta for 2,3,4 parameters...
            delta = 1
            while True:

                # add another point
                remaining_points_new, selected_coord_list_new = add_additional_point_generic(remaining_points_base, selected_coord_list_base)
                # increment counter value, because a new measurement point was added
                added_points += 1

                if len(remaining_points_new) == 0:
                    #print("remaining_points_new:",len(remaining_points_new))
                    break

                # create new model
                experiment_generic_new = create_experiment(selected_coord_list_new, experiment, len(experiment.parameters), parameters, metric_id, callpath_id)
                #print("DEBUG:", len(experiment_generic_new.callpaths))
                model_generic_new, models = get_extrap_model(experiment_generic_new, args)
                hypothesis = None
                for model in models.values():
                    hypothesis = model.hypothesis
                rss_new = hypothesis.SMAPE
                #ar2_new = hypothesis.AR2
                #print("rss_new:",rss_new)
                #print("ar2_new:",ar2_new)

                # if better continue, else stop after x steps without improvement...
                if rss_new <= rss_base:
                    #print("new rss is smaller")
                    stall_counter = 1
                    rss_base = rss_new
                    selected_coord_list_base = selected_coord_list_new
                    remaining_points_base = remaining_points_new
                else:
                    #print("new rss is larger")
                    if stall_counter == delta:
                        break
                    stall_counter += 1

            #print("added_points:",added_points)
            #print("len selected_coord_list_new:",len(selected_coord_list_base),len(selected_coord_list_new),added_points)

            
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
                for k in range(len(measurement_temp.values)):
                    runtime = measurement_temp.values[k]
                    nr_processes = coordinate.as_tuple()[0]
                    core_hours = runtime * nr_processes
                    coordinate_cost += core_hours
                selected_cost += coordinate_cost
            #print("selected_cost:",selected_cost)

            # calculate the percentage of cost of the selected points compared to the total cost of the full matrix
            percentage_cost_generic = selected_cost / (total_cost / 100)
            #print("percentage_cost_generic:",percentage_cost_generic)

            # calculate number of additionally used data points (exceeding the base requirement of the sparse modeler)
            add_points_generic = len(selected_points) - min_points
            #add_points_generic_container.append(add_points_generic)
            #print("add_points_generic:",add_points_generic)

            # create model using point selection of generic strategy
            #print("DEBUG:", len(experiment_generic_new.callpaths))
            model_generic, _ = get_extrap_model(experiment_generic_new, args)
            #print("model_generic:",model_generic)
            #container["model_generic"] = model_generic

            # create model using full matrix of points
            #model_full, _ = get_extrap_model(experiment, args)
            #TODO: use this instead here:   all_points_functions_strings[callpath_string]
            #print("model_full:",model_full)
            #container["model_full"] = model_full

            



            



        




        # format modeler output into text
        #text = format_output(experiment, printtype)

        # print formatted output to command line
        #print(text)

        # save formatted output to text file
        #if print_output:
        #    save_output(text, print_path)

    else:
        logging.error("No file path given to load files.")
        sys.exit(1)
    


if __name__ == "__main__":
    main()

