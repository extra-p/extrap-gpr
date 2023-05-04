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
from extrap.entities.coordinate import Coordinate


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

        # TODO: 

        print(experiment.parameters)

        metric_id = -1
        for i in range(len(experiment.metrics)):
            if str(experiment.metrics[i]) == "time":
                metric_id = i
                break
        metric = experiment.metrics[metric_id]
        metric_string = metric.name

        smapes = []
        cost = {}
        total_costs = []
        
        modeler = experiment.modelers[0]
        for callpath_id in range(len(experiment.callpaths)):
            callpath = experiment.callpaths[callpath_id]
            callpath_string = callpath.name
            
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

                total_cost = 0

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
                    runtime = measurement_temp.mean
                    #print("measurement_temp:",measurement_temp.mean)
                    core_hours = runtime * nr_processes
                    cost[experiment.coordinates[i]].append(core_hours)
                    total_cost += core_hours

            else:
                smape = 0
                ar2 = 0
                function_string = "None"
                total_cost = 0

            smapes.append(smape)
            total_costs.append(total_cost)

            print(callpath_string, metric_string, function_string, total_cost)

        # create copy of the cost dict
        remaining_points = copy.deepcopy(cost)
        
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
        print("y_lines:",y_lines)
        # calculate the cost of each of the lines
        line_costs = {}
        for key, value in y_lines.items():
            line_cost = 0
            for i in range(len(value)):
                point_cost = sum(cost[Coordinate(key, value[i])])
                line_cost += point_cost
            line_costs[key] = line_cost
        print("line_costs:",line_costs)
        x_value = min(line_costs, key=line_costs.get)
        y_values = y_lines[min(line_costs, key=line_costs.get)]
        print("y_values:",y_values)

        selected_points = []
        for i in range(len(y_values)):
            cord = Coordinate(x_value, y_values[i])
            selected_points.append(cord)

        print("selected_points:",selected_points)

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
        print("x_lines:",x_lines)
        # calculate the cost of each of the lines
        line_costs = {}
        for key, value in x_lines.items():
            line_cost = 0
            for i in range(len(value)):
                point_cost = sum(cost[Coordinate(value[i], key)])
                line_cost += point_cost
            line_costs[key] = line_cost
        print("line_costs:",line_costs)
        y_value = min(line_costs, key=line_costs.get)
        x_values = x_lines[min(line_costs, key=line_costs.get)]
        print("x_values:",x_values)

        for i in range(len(x_values)):
            cord = Coordinate(x_values[i], y_value)
            exists = False
            for j in range(len(selected_points)):
                if selected_points[j] == cord:
                    exists = True
                    break
            if exists == False:
                selected_points.append(cord)

        print("selected_points:",selected_points)

        #TODO: add some additional single points

        



            



        




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

