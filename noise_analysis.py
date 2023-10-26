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
    
    total_runtime = 0
    noise_levels = []
    for callpath in experiment.callpaths:
        measurement_runtime = 0
        # do an noise analysis on the existing points
        mm = experiment.measurements
        nn = mm[(callpath, metric)]
        nns = []
        for meas in nn:
            mean_mes = np.mean(meas.values)
            measurement_runtime += mean_mes
            pps = []
            for val in meas.values:
                if mean_mes == 0.0:
                    pp = 0.0
                else:
                    pp = abs((np.mean(val) / (mean_mes / 100)) - 100)
                pps.append(pp)
            nn = np.mean(pps)
            nns.append(nn)
        mean_noise = np.mean(nns)
        #print("mean_noise:",mean_noise,"%")
        noise_levels.append(mean_noise)
        total_runtime += measurement_runtime
        #(callpath, measurement_runtime)

    #print("\n\n")

    #print("total_runtime:",total_runtime)
    
    pecentage_runtimes = []
    for callpath in experiment.callpaths:
        measurement_runtime = 0
        # do an noise analysis on the existing points
        mm = experiment.measurements
        nn = mm[(callpath, metric)]
        nns = []
        for meas in nn:
            mean_mes = np.mean(meas.values)
            measurement_runtime += mean_mes
        #print(callpath, measurement_runtime)
        if args.total_runtime:
            pecentage_runtime = measurement_runtime / (args.total_runtime / 100)
        else:
            pecentage_runtime = measurement_runtime / (total_runtime / 100)
        pecentage_runtimes.append(pecentage_runtime)
            
    #print("pecentage_runtimes:",len(pecentage_runtimes))
    #print("noise_levels:",len(noise_levels))
    
    print(noise_levels)
    print(pecentage_runtimes)
    
    # create the different datasets
    dataset = None
    
    plot_noise(dataset)

   
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


def plot_noise(dataset):
    dataset = [
        ('Kripke\n(Vulcan)',
         [106.46, 20.7704, 117.542, 42.12, 121.95, 19.5687, 4.04765,
          3.66188, 8.37047, 28.0125, 27.0589, 15.7071, 53.6656, 61.7834],
         [0.00961309, 9.18522e-05, 1.69763e-05, 0.0137028, 0.0967781, 0.0944576,
          33.8806, 28.2083, 21.0661, 0.00928349, 0.323763, 0.430711, 15.7499, 0.11666]
         ),
        ('FASTEST\n(SuperMUC)',
         [270.676, 124.047, 5356.82, 2374.17, 195.602, 139.877, 5.91974, 95.8298, 47.6668, 158.933, 41.5688, 187.108, 30.4956, 26.8158, 49.7486, 31.4918,
          141.876, 37.014, 50.1385, 8604.76, 535.216, 1174.87, 1565.67, 53.9129, 78.7595, 7441.15, 31.1575, 169.022, 6651.73, 6237.62, 177.164, 108.718, 11.008, 42.1664, 52.6782,
          159.689, 4883.81, 13612.7, 1373.39, 159.744, 387.974, 151.975, 823.591, 200.832, 388.124, 67.8585, 59.436, 27.5334, 16.1084, 60.6686, 23.3738, 36.1089, 23.1263,
          28.9553, 114.205, 32.9436, 29.5253, 27.8151, 39.4051, 15.963, 37.9413, 95.28, 18.2127, 24.2014, 23.873, 38.8866, 13.5393, 793.553, 495.511, 129.954, 39.8244, 141.263,
          57.7992, 45.1964, 37.7121, 29.8241, 43.8234, 33.7841, 29.4745, 137.481, 133.225, 47.0505, 35.0237, 132.236, 217.106, 523.02, 137.487, 27.5661, 939.819, 256.955,
          70.4579, 47.836, 666.569, 159.988, 106.473, 28.9354, 54.6417, 28.4705, 45.3028, 139.564, 42.2256, 25.5625, 61.8783, 92.6572, 37.6675, 307.144, 20.6374, 37.2737, 102.873,
          51.7158, 343.319, 26.5638, 160.174, 29.9164, 34.9284, 129.722, 53.0537, 28.9137, 45.3951, 42.8436, 32.2816, 36.8952, 59.736, 55.095, 65.6586, 30.5582,
          178.908, 38.208, 128.248, 809.074, 50.5547, 107.461, 165.231, 34.9818, 213.564, 206.876, 88.6031, 123.721, 417.758, 283.179, 812.513, 440.109, 38.4316, 39.5636,
          794.374, 554.644, 43.5814, 31.5298, 104.734, 84.5644, 64.035, 85.7747, 41.0277, 47.0261, 132.71, 206.273, 22.6257, 87.2132, 76.5232, 89.2956, 26.1243, 33.9447,
          24.9656, 35.4778, 20.8379, 120.942, 132.644, 41.2452, 75.4485, 8603.02, 5995.22, 5999.89, 6018.57, 6003.51, 6027.57, 6016.2, 5998.63, 6021.09, 6002.74, 6019.98, 8935.48,
          6020.7, 265.806, 52.1607, 748.759, 129.006, 36.4917, 219.419, 24.7683, 129.257, 32.7755, 58.8767, 41.45, 33.965, 29.3478, 245.738, 171.57, 63.0494, 99.0229, 115.791,
          62.2991, 30.0675, 90.5033, 2320.14, 536.252, 36.6742, 6055.45, 6010.51, 6007.97, 8025.06, 5998.82, 13567.1, 6009.9, 5996.06, 6006.25, 6027.35, 5999.44, 5998.94,
          5500.14, 28.696, 18.5032, 44.8512, 227.465, 6011.29, 8775.39, 6415.1, 6009.6, 6003.19, 771.15, 11.0322, 23.0196, 23.1513, 6007.81, 6005.09, 6013.26, 6009.26,
          998.365, 109.199, 56.845, 784.517, 801.521, 405.087, 734.03, 4431.67, 32.1015, 305.382, 32.8702, 1189.21, 992.002, 19.4076, 185.441, 6120.91, 27.5443, 966.555,
          35.143, 105.774, 8958.07, 418.417, 63.8123, 2.49133, 13.4606, 46.2588, 12.4046, 323.593, 6.67019, 13.7242, 35.4034, 5.78062, 17.2978, 27.4927, 5.1736, 26.8675,
          6.66052, 3.72953, 41.2866, 7.26595, 20.4842, 9.45022, 251.13, 16.9593, 17.626, 44.1301, 6484.88, 6009.95, 22.6141, 15.4511, 77.7938, 6.63725, 34.4216, 67.2589,
          27.1815, 17.8833, 48.0549, 26.4292, 6.3286, 7.87244, 11.0569, 8.22575, 28.224, 9.88796, 10.0833, 22.8522, 15.6055, 4.06889, 21.5644, 6.39728, 18.265, 15.8098,
          47.5341, 17.9171, 20.5945, 13.626, 22.9149, 8.66662, 31.9078, 9.5235, 13.8287, 25.2251, 7.80251, 18.586, 16.4615, 166.754, 20.6294, 17.5404, 17.328, 16.789, 28.9545,
          15.7846, 49.8173, 35.5316, 18.359, 35.3873, 27.8588, 7.66515, 53.006, 8.49755, 22.5381, 31.5225, 141.041, 12.705, 18.1708, 23.0351, 135.157, 17.3598, 26.5967, 25.8049,
          9.15707, 39.578, 4.98684, 22.0385, 132.408, 131.116, 9.10078, 63.7843, 6.27971, 9.46364, 99.5039, 12.0419, 210.345, 26.2415, 21.5089, 26.9366, 41.3916, 20.6502,
          30.9353, 26.8124, 13.0826, 28.4426, 28.449, 13.4425, 28.5074, 15.6155, 16.62, 28.8141, 12.148, 18.3379, 20.7757, 160.265, 37.2725, 43.106, 123.952, 22.762, 18.9787,
          15.7691, 4.43961, 11.1837, 23.4144, 3.78502, 24.1229, 5.29418, 4.51906, 10.1916, 6.71774, 14.3651, 7.20311, 73.1521, 22.0911, 25.2104, 32.979, 14.0347, 25.8491,
          48.8541, 25.1615, 39.5211, 41.0742, 23.7799, 62.6296, 24.9557, 18.6068, 29.5044, 18.5835, 34.5238, 26.2772, 141.715, 38.0501, 18.0244, 20.4834, 29.8188, 17.5738,
          42.3685, 30.1886, 16.7292, 53.8533, 10.7632, 32.6085, 28.108, 147.564, 30.7849, 23.6718, 8.81968, 31.6855, 24.3621, 50.6112, 29.7602, 33.524, 21.9918, 28.4946,
          30.273, 33.1406, 138.143, 16.399, 30.7099, 28.9703, 16.3912, 29.7615, 11.5489, 22.5998, 137.214, 133.109, 21.9185, 116.645, 36.3286, 23.5801, 117.548, 16.7931,
          21.0685, 19.4017, 8.14483, 9.08898, 13.3815, 4.03967, 11.0997, 12.7165, 4.18127, 21.1348, 5.47151, 4.54725, 19.3019, 6.23602, 12.0968, 9.14111, 209.286, 7.51113,
          7.94258, 19.059, 21.0207, 19.0103, 13.1647, 37.9308, 12.2034, 18.851, 41.0729, 431.815, 6014.46, 62.6286, 4.05648, 28.8539, 274.812, 37.6839, 20.3058, 34.1592,
          13.822, 30.4216, 21.4417, 26.7085, 43.7597, 40.5496, 27.4082, 34.2261, 27.945, 25.0431, 28.6841, 20.81, 28.5812, 39.7713, 200.187, 31.721, 19.7384, 20.5253,
          28.1465, 13.4908, 36.0893, 18.0627, 18.514, 46.3568, 7.30469, 31.4164, 25.8085, 150.229, 45.4334, 20.5, 8.27453, 21.5804, 111.408, 22.4523, 35.725, 13.7616,
          13.8636, 15.438, 8.10428, 7.28418, 12.3321, 3.97891, 8.34387, 11.7277, 3.93924, 18.4702, 4.36795, 7.76774, 23.2269, 5.45839, 11.6943, 10.1351, 194.335, 7.41785,
          7.64184, 29.1454, 26.1259, 27.6184, 22.5724, 134.362, 10.2734, 36.1864, 9.4993, 18.1939, 29.2723, 31.5371, 28.1213, 133.615, 129.907, 25.5361, 178.695, 21.7372,
          11.0097, 80.932, 566.203, 6018.4, 182.085, 11.9519, 37.3884, 590.91, 114.782, 6.72299, 6.524, 4.99876, 7.2319, 9.89737, 548.039, 6014.3, 83.7945, 19.8684, 18.7886, 1247.99, 750.997],
         [7.42423e-05, 0.0023699, 2.31682e-05, 1.1959e-07, 0.0243175, 2.06515e-08, 9.67329e-07, 0.000130825, 2.55147e-07, 0.000516456, 1.10166e-07, 4.61956e-08, 2.33626e-06, 1.76984e-06,
          0.0010899, 1.19758e-06, 0.00910307, 1.17572e-06, 0.0138823, 1.80029e-08, 2.69183e-05, 6.36429e-06, 4.30182e-06, 1.16479e-07, 4.88376e-08, 1.36644e-07, 9.513e-08, 0.000895202,
          5.61127e-07, 7.15978e-10, 8.47825e-05, 4.69827e-08, 1.67769e-07, 0.269694, 1.92096e-07, 3.91424e-08, 4.31895e-07, 1.50568e-06, 5.89004e-06, 0.000701813, 2.78804e-05, 0.000203491,
          1.52264e-06, 3.35794e-08, 4.37535e-06, 4.83004e-08, 1.28913e-07, 6.51251e-05, 6.96777e-07, 2.98891e-08, 1.04115e-06, 2.53783e-06, 2.41685e-06, 1.06362e-07, 2.23125e-08, 9.36558e-08,
          1.66577e-07, 1.77737e-06, 1.89383e-07, 2.31318e-06, 9.07757e-08, 0.000410131, 2.24824e-07, 6.15407e-05, 8.11099e-07, 0.00357963, 8.29371e-07, 4.83689e-05, 1.04189e-05, 6.64213e-08,
          5.01146e-05, 8.33083e-08, 6.21981e-07, 6.96518e-08, 3.9341e-07, 4.98953e-07, 4.75413e-06, 6.73486e-07, 9.38682e-06, 4.22388e-08, 5.88183e-08, 2.11736e-07, 0.00054307, 3.96274e-08,
          3.07769e-05, 6.39535e-07, 2.34586e-08, 2.21582e-07, 3.53298e-06, 1.29122e-05, 8.21629e-07, 0.00180861, 6.32427e-07, 0.00341106, 3.7017e-05, 2.54656e-07, 0.00144468, 1.50318e-07,
          4.2249e-07, 0.0187625, 0.00106067, 6.84119e-07, 9.06679e-08, 2.02007e-05, 1.68507e-07, 0.000310787, 3.48013e-07, 5.01884e-08, 4.01673e-08, 8.1853e-08, 2.3585e-08, 4.35737e-07,
          2.01747e-06, 1.61686e-06, 9.3422e-08, 1.47373e-08, 7.89503e-08, 1.3899e-07, 8.60974e-07, 1.53204e-07, 1.50323e-06, 5.27236e-08, 9.07227e-05, 9.69742e-08, 2.21242e-08,
          1.19434e-05, 2.61064e-08, 9.43137e-08, 1.84424e-08, 3.04459e-07, 1.54019e-07, 1.653e-06, 1.97313e-07, 3.01084e-06, 1.74583e-08, 1.99738e-08, 7.14587e-08, 0.000110434,
          2.81525e-05, 0.000125947, 2.12675e-05, 1.3689e-05, 2.42047e-06, 5.26907e-06, 4.88733e-07, 1.85923e-05, 2.20748e-07, 3.21729e-07, 3.86356e-08, 1.22551e-07, 2.79097e-05,
          6.4051e-08, 0.000463203, 9.96035e-08, 3.29572e-08, 1.00084e-06, 2.93368e-06, 2.29045e-06, 1.64931e-07, 3.46432e-08, 1.43711e-07, 2.93529e-07, 1.4687e-06, 3.18729e-07,
          2.95264e-06, 9.92123e-08, 0.000287531, 0.000208317, 0.000226193, 1.84088e-05, 1.5591e-10, 1.56066e-10, 2.01873e-10, 1.59139e-10, 9.81858e-10, 1.47107e-10, 2.77023e-10,
          1.32685e-10, 1.07331e-09, 4.50681e-08, 3.60864e-06, 1.90961e-09, 3.50318e-07, 1.40534e-07, 2.96135e-07, 4.53373e-08, 1.96056e-05, 2.94551e-08, 1.15902e-07, 3.30642e-08,
          1.35455e-07, 1.88296e-07, 1.45973e-06, 2.45388e-07, 4.34693e-06, 2.22982e-08, 2.02225e-08, 9.1382e-08, 0.000177648, 6.37751e-08, 4.58227e-08, 0.000183481, 3.82726e-08,
          1.09508e-06, 1.10352e-06, 0.18727, 1.33617e-07, 1.93303e-09, 1.35068e-09, 1.44168e-09, 1.84524e-09, 1.01127e-06, 2.8674e-07, 4.33848e-09, 1.34961e-08, 1.36415e-09,
          8.38211e-09, 3.6413e-09, 7.42639e-05, 5.44215e-07, 0.127712, 5.20759e-08, 2.41566e-07, 1.10898e-07, 1.17451e-07, 3.12391e-06, 2.92877e-05, 4.62915e-06, 7.34323e-07,
          0.117904, 2.02444e-07, 0.000121378, 4.22624e-07, 5.49876e-05, 1.19196e-07, 0.000129484, 1.46238e-07, 6.82736e-08, 3.80858e-06, 2.34789e-06, 1.8748e-06, 3.77679e-05,
          6.62821e-07, 5.5437e-07, 4.63038e-08, 1.67095e-07, 3.19702e-07, 4.72863e-06, 3.67786e-06, 2.71652e-07, 0.00329695, 2.93501e-10, 1.38048e-05, 2.61759e-07, 2.27624e-06,
          2.74855e-08, 1.91023e-07, 5.47149e-05, 0.000805637, 0.0317096, 3.69129e-05, 0.00638338, 1.35041e-05, 0.00617089, 0.000468307, 9.50991e-06, 3.17543e-06, 9.88413e-05,
          0.000495007, 0.000622328, 1.7504e-05, 1.4944e-05, 1.46042e-05, 3.34468e-05, 0.000141981, 3.61366e-05, 0.000337654, 8.34971e-06, 0.0123684, 9.71942e-06, 0.00092802,
          2.29068, 1.09138e-05, 5.45755e-06, 0.00164817, 2.41294e-05, 0.0365125, 0.00730644, 0.000767857, 0.00316376, 2.05374, 0.00112521, 0.955091, 0.568108, 0.0171634,
          0.000355806, 0.000134535, 0.0036833, 0.0137343, 0.00891864, 0.000664993, 0.000444476, 0.000547575, 0.0012511, 0.00609265, 0.00133019, 0.0136052, 0.000321143,
          0.129036, 0.000392076, 0.0010847, 0.000374436, 0.184822, 0.000803152, 0.00059202, 0.000966523, 0.00137003, 0.00823397, 0.00196976, 0.0375185, 0.000427509, 0.186254,
          0.000332174, 0.948185, 6.90201, 0.00055846, 0.000192691, 0.00401915, 0.0251615, 0.0195753, 0.000719471, 0.000769609, 0.000608194, 0.00129101, 0.00597656, 0.00138367,
          0.0144644, 0.000364448, 0.211684, 0.00447576, 0.00117202, 0.654034, 0.000452145, 0.00302383, 0.00176005, 0.0034714, 0.00455204, 0.0333735, 0.00658728, 0.119611,
          0.00025546, 0.000282388, 0.00163026, 0.793662, 0.107313, 0.00447306, 2.85882, 0.00446314, 0.0250872, 0.0970875, 0.000446964, 0.0033042, 0.384052, 16.2715, 0.0195923,
          0.00566529, 0.0980948, 0.440215, 0.337184, 0.0180007, 0.0103049, 0.0148731, 0.035971, 0.195991, 0.0361354, 0.449572, 0.0101286, 3.9183, 0.218267, 0.00169447, 1.00344,
          3.27923, 0.0119371, 0.00336198, 0.0989702, 0.384155, 0.320372, 0.0178061, 0.00556, 0.0144788, 0.0342203, 0.153604, 0.0364083, 0.372032, 0.00830845, 2.48238, 0.00114078,
          1.95008, 0.734661, 0.0187599, 0.000545204, 0.000251246, 0.00449114, 0.0262888, 0.0463458, 0.000760169, 0.000829217, 0.000620409, 0.00151774, 0.00981914, 0.00166353,
          0.0251289, 0.000476029, 0.372338, 0.00058772, 0.00116039, 0.000301216, 0.21584, 0.00084421, 0.000462154, 0.00107102, 0.00139583, 0.00878619, 0.00201537, 0.0409282,
          0.000473257, 0.337825, 0.000410908, 1.04424, 6.99099, 1.26121, 0.000436748, 0.000556017, 0.00399936, 0.592591, 13.1882, 0.017204, 0.0057548, 2.82766, 0.00377508,
          0.0128856, 0.00801241, 0.0155051, 0.0227515, 0.141281, 0.0296376, 0.576095, 0.00182545, 0.00250091, 0.0071282, 3.04233, 0.609503, 0.00501732, 4.4833, 0.00161906,
          0.000501573, 0.00037677, 3.96386, 0.000705894, 0.000223702, 0.00732958, 0.0262097, 0.0206866, 0.00130166, 0.000691229, 0.00106972, 0.00249571, 0.0109207, 0.00271081,
          0.0249837, 0.000626562, 0.848283, 1.91292, 2.03416, 0.00134337, 0.000950875, 0.369875, 0.000727686, 0.380805, 0.00156032, 7.17302e-06, 0.000302358, 0.00100856,
          3.72595e-06, 4.6357e-05, 3.7339e-05, 0.00381208, 1.52728e-05, 0.0163122, 0.0296469, 0.019666, 0.000511242, 1.87417e-05, 8.60686e-06, 0.000130756, 0.000760143,
          0.0013113, 2.34576e-05, 2.33137e-05, 1.80463e-05, 4.83935e-05, 0.000380353, 5.03633e-05, 0.000858827, 1.65515e-05, 0.00652534, 1.07431e-05, 3.07831e-05, 1.03827e-05,
          0.00560815, 2.21511e-05, 1.14518e-05, 2.6916e-05, 3.67951e-05, 0.000235534, 5.23644e-05, 0.00115682, 1.24207e-05, 0.00766848, 1.0956e-05, 0.0280458, 0.193501,
          9.84394e-06, 1.35542e-05, 3.03858e-05, 0.0154908, 2.80021e-05, 1.03022e-05, 7.98378e-06, 0.108463, 2.15414e-05, 8.04169e-06, 0.000199102, 0.000713039, 0.000560272,
          3.59836e-05, 1.98434e-05, 2.97361e-05, 6.91665e-05, 0.000339175, 7.29391e-05, 0.000753803, 1.87263e-05, 0.0541734, 0.0523353, 0.0558444, 2.42607e-05, 3.17314e-05,
          1.46327e-05, 0.0059432, 8.09059e-06, 2.80127e-05, 2.82484e-05, 2.95567e-05, 5.34428e-05, 0.000451678, 6.69286e-05, 0.00119081, 3.2267e-06, 5.96862e-06, 1.60813e-05,
          0.0259137, 7.0588e-05, 2.08513e-05, 0.073129, 3.26333e-05, 1.35123e-07, 2.447e-05, 3.07181e-05, 0.0100353, 1.02037e-07, 9.25426e-05, 2.43718e-05, 1.41236e-05,
          0.00145415, 2.08663e-05, 0.00167927, 7.86695e-06, 7.27216e-08, 2.48759e-08, 1.20678e-05, 6.04124e-06, 3.25558e-08, 1.21735e-05]),
        ('RELeARN\n(Lichtenberg)',
         [0.13565720928481795, 0.4598420350040482, 0.13567263577317676, 5.030727437570446, 3.5714676711443225, 0.135688130000498, 0.0, 4.349318934963172, 19.83543363125717, 14.647046741373813, 9.120721510982676, 0.135796773837086, 0.7754740276754604, 0.13544423403396025],
         [100.0, 0.061983908155317104, 99.93836988221186, 4.0573903559443026e-09, 3.325652904467642e-09, 99.93831828534027, 0.0, 0.00010693404259331131, 0.0005127204738231404, 4.55163835233615e-06, 1.3034792583546987e-06, 99.90828421545692, 0.006742453089766081, 90.99592531687438]
         ),
        ('LULESH\n(Lichtenberg)',
         [0.6439731745302313,
          122.70011876867557,
          91.00109911021991,
          0.644774929455935,
          8.61981102364483,
          0.6745866151125853,
          2.0173365155585175,
          0.6446367601568742,
          30.08965026325741,
          38.75992726504036,
          0.6446367601568742,
          47.94546895815047,
          107.02350302205137, ],
         [100.0, 1.0565487551688383e-06, 7.478345676154262e-07, 99.8991476188248, 0.008415226123598966, 86.6591632823448, 0.0769332502542859,
          99.92328323141373, 1.034383396668793e-08, 1.0466974847243738e-08, 99.92316009053317, 0.00021076928570900826, 0.00040452887530508154, 100]
         ),
        ('MiniFE\n(Lichtenberg)',
         [0.6439731745302313,
          122.70011876867557,
          91.00109911021991,
          0.644774929455935,
          8.61981102364483,
          0.6745866151125853,
          2.0173365155585175,
          0.6446367601568742,
          30.08965026325741,
          38.75992726504036,
          0.6446367601568742,
          47.94546895815047,
          107.02350302205137, ],
         [100.0, 1.0565487551688383e-06, 7.478345676154262e-07, 99.8991476188248, 0.008415226123598966, 86.6591632823448, 0.0769332502542859,
          99.92328323141373, 1.034383396668793e-08, 1.0466974847243738e-08, 99.92316009053317, 0.00021076928570900826, 0.00040452887530508154, 100]
         ),
        ('Quicksilver\n(Lichtenberg)',
         [0.6439731745302313,
          122.70011876867557,
          91.00109911021991,
          0.644774929455935,
          8.61981102364483,
          0.6745866151125853,
          2.0173365155585175,
          0.6446367601568742,
          30.08965026325741,
          38.75992726504036,
          0.6446367601568742,
          47.94546895815047,
          107.02350302205137, ],
         [100.0, 1.0565487551688383e-06, 7.478345676154262e-07, 99.8991476188248, 0.008415226123598966, 86.6591632823448, 0.0769332502542859,
          99.92328323141373, 1.034383396668793e-08, 1.0466974847243738e-08, 99.92316009053317, 0.00021076928570900826, 0.00040452887530508154, 100]
         )
    ]

    data = []
    names = []
    for i, (name, values, percentages) in enumerate(dataset):
        x = []
        y = []

        cutoffrate = 1

        for i in range(len(values)):
            if percentages[i] > cutoffrate:
                x.append(values[i])
                y.append(percentages[i])
        data.append(x)
        names.append(name)
        
    plt.figure(figsize=(6.8, 1.5), dpi=300)
    # print(str(len(y))+" kernels used from "+str(len(values)))
    ylabel = plt.ylabel("Noise $n$ [$\%$]\nRange of relative deviation")
    x, y = ylabel.get_position()
    ylabel.set_position((x, y-0.05))
    # plt.ylabel("percentage of total runtime of the kernel")
    arrowstyle = {'arrowstyle': '-',
                  'relpos': (0, 0.5), 'shrinkA': 0, 'shrinkB': 5, 'linewidth': 0.4}

    violins = plt.violinplot(data, [1, 2, 3, 4, 5, 6])
    for b in violins['bodies']:
        b.set_facecolor((0, 0, 255 / 255, 1))
        b.set_alpha(0.2)
    for l in [violins['cbars'], violins['cmins'], violins['cmaxes']]:
        l.set_color((0.3, 0.3, 255 / 255, 1))
        l.set_linewidth(0.8)
    for x, y in zip([1, 2, 3, 4, 5, 6], [np.max(d) for d in data]):
        xy = (x + 0.15, y)
        va = 'center'
        if x == 2:
            va = 'top'
        if x == 3:
            xy = (x + 0.15, 52)
        if x == 4:
            xy = (x + 5.55, 52)
        plt.annotate(r"$n_{\mathrm{max}}="+f"{y: .2f}$", (x, y), xytext=xy,
                     arrowprops=arrowstyle if x == 3 else None, va=va)
    mean_hndl = plt.plot([1, 2, 3, 4, 5, 6], [np.mean(d)
                                     for d in data], 'x', color=(1, 0.1, 0.1, 1))
    for x, y in zip([1, 2, 3, 4, 5, 6], [np.mean(d) for d in data]):
        xy = (x + 0.15, y)
        if x == 1:
            xy = (x + 0.15, y+18)
        if x == 3:
            xy = (x + 0.15, 37)
        plt.annotate(fr"$\bar{{n}}={y:.2f}$", (x, y), xytext=xy,
                     arrowprops=arrowstyle if x != 2 else None, va='center')
    median_hndl = plt.plot([1, 2, 3, 4, 5, 6], [np.median(d)
                                       for d in data], '_', color=(1, 0.55, 0.1, 1))
    for x, y in zip([1, 2, 3, 4, 5, 6], [np.median(d) for d in data]):
        xy = (x + 0.15, y)
        if x == 1:
            xy = (x + 0.15, y+14)
        if x == 3:
            xy = (x + 0.15, 22)
        plt.annotate(fr"$\tilde{{n}}={y:.2f}$", (x, y), xytext=xy,
                     arrowprops=arrowstyle if x != 2 else None, va='center')
    for x, y in zip([1, 2, 3, 4, 5, 6], [np.min(d) for d in data]):
        xy = (x + 0.15, y)
        if x != 2:
            xy = (x + 0.15, 7)
        plt.annotate(r"$n_{\mathrm{min}}="+f"{y:.2f}$", (x, y), xytext=xy,
                     va='center')
    plt.xticks([1, 2, 3, 4, 5, 6], names)
    plt.xlim(0.7, 3.75)
    plt.ylim(0, 165)
    plt.tight_layout(pad=0)

    max_hndl = Line2D([0, 1], [0, 1], marker=3, color=(
        0.3, 0.3, 255 / 255, 1), linewidth=0.8)
    min_hndl = Line2D([0, 1], [0, 1], marker=2, color=(
        0.3, 0.3, 255 / 255, 1), linewidth=0.8)
    leg = plt.legend([max_hndl, mean_hndl[0], median_hndl[0], min_hndl],
                     [r'maximum $n_{\mathrm{max}}$', r'mean $\bar{n}$',
                      r'median $\tilde{n}$', r'minimum $n_{\mathrm{min}}$'],
                     loc='upper left', bbox_to_anchor=(0.02, 0.98), markerscale=0.6, handlelength=1.2, handletextpad=0.4, labelspacing=0.2, fancybox=False, borderpad=0.2)
    leg.get_frame().set_linewidth(0.4)
    plt.grid(axis='y', linewidth=0.4, color=(0.8, 0.8, 0.8, 1))

    plt.savefig("noise_level_dist.pdf")
    plt.show()
    plt.close()


if __name__ == "__main__":
    main()