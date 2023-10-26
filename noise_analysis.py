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
import sys
import warnings
from extrap.fileio.cube_file_reader2 import read_cube_file
from extrap.fileio.experiment_io import read_experiment
from extrap.fileio.json_file_reader import read_json_file
from extrap.fileio.talpas_file_reader import read_talpas_file
from extrap.fileio.text_file_reader import read_text_file
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
plt.rc('font', **{'family': 'serif', 'size': 7.5})
#plt.rc('text', usetex=True)
plt.rc('axes', edgecolor='black', linewidth=0.4, axisbelow=True)
plt.rc('xtick', **{'direction': 'out', 'major.width': 0.4})
plt.rc('ytick', **{'direction': 'in', 'major.width': 0.4})


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

    parser.add_argument("--plot", type=bool, required=False, default=False,
                        help="Set if the plots should be shown after running the anlysis.")
    
    parser.add_argument("--name", type=str, required=True,
                        help="Set the name for the output file where the results will be saved.")
    
    parser.add_argument("--total-runtime", type=float, required=False,
                        help="Set a total runtime value for measurements where the metric was not measured exclusively, e.g., Relearn.")

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

    # check scaling type
    scaling_type = args.scaling_type

    # set log level
    loglevel = logging.getLevelName(args.log_level.upper())

    # set output print type
    printtype = args.print_type.upper()

    # set show plots
    plot = args.plot

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
    
    # load the measurements from files
    experiment = load_measurements(args)
    
    # get metric id and string of runtime/time metric
    metric_id = -1
    for i in range(len(experiment.metrics)):
        if str(experiment.metrics[i]) == "time" or str(experiment.metrics[i]) == "runtime":
            metric_id = i
            break
    metric = experiment.metrics[metric_id]
    metric_string = metric.name
    #print("Metric:",metric_string)
    
    # calc only total runtime first
    total_runtime = 0
    for callpath in experiment.callpaths:
        measurement_runtime = 0
        mm = experiment.measurements
        nn = mm[(callpath, metric)]
        for meas in nn:
            means = []
            for x in meas.values:
                means.append(np.mean(x))
            mean_mes = np.mean(means)
            measurement_runtime += mean_mes
        total_runtime += measurement_runtime
    
    noise_levels = []
    pecentage_runtimes = []
    for callpath in experiment.callpaths:
        measurement_runtime = 0
        # do an noise analysis on the existing points
        mm = experiment.measurements
        nn = mm[(callpath, metric)]
        nns = []
        for meas in nn:
            rep_values = []
            for x in meas.values:
                rep_values.append(np.mean(x))
            mean_mes = np.mean(rep_values)
            measurement_runtime += mean_mes
            pps = []
            for val in rep_values:
                if mean_mes == 0.0:
                    pp = 0.0
                else:
                    pp = abs((val / (mean_mes / 100)) - 100)
                pps.append(pp)
            nn = np.mean(pps)
            nns.append(nn)
        mean_noise = np.mean(nns)
        #print("mean_noise:",mean_noise,"%")
        if args.total_runtime:
            pecentage_runtime = measurement_runtime / (args.total_runtime / 100)
        else:
            pecentage_runtime = measurement_runtime / (total_runtime / 100)
        pecentage_runtimes.append(pecentage_runtime)
        noise_levels.append(mean_noise)
    
    # probability is calculated by the runtime percentage * the prob of the value in the list of samples
    import scipy.stats
    kde = scipy.stats.gaussian_kde(noise_levels)
    probabilities = []
    for i in range(len(noise_levels)):
        probability = kde.pdf(noise_levels[i])[0]
        probability = probability * pecentage_runtimes[i]
        #print(noise_levels[i], probability)
        probabilities.append(probability)
    #print(probability)
    
    x = {}
    x["noise"] = noise_levels
    x["probability"] = probabilities
    
    import json
    with open(args.name+'.json', 'w', encoding='utf-8') as f:
        json.dump(x, f, ensure_ascii=False, indent=4)
    
   
def load_measurements(args):
    if args.path is not None:
        with ProgressBar(desc='Loading file') as pbar:
            if args.cube:
                # load data from cube files
                if os.path.isdir(args.path):
                    experiment = read_cube_file(args.path, args.scaling_type)
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
    return experiment

if __name__ == "__main__":
    main()