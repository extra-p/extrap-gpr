import argparse
from synthetic_benchmark import SyntheticBenchmark
from itertools import chain
from extrap.modelers import multi_parameter
from extrap.modelers import single_parameter
from extrap.util.options_parser import ModelerOptionsAction, ModelerHelpAction
from extrap.util.options_parser import SINGLE_PARAMETER_MODELER_KEY, SINGLE_PARAMETER_OPTIONS_KEY
import os

def main():
    """
    Runs a synthetic benchmark with a specified number of parameters.

    Command line arguments:
    --nr-parameters: Number of parameters for the benchmark. Must be a positive integer.
    --nr-functions: Number of functions used for the synthetic evaluation. Must be a positive integer.
    --nr-repetitions: Number of repetitions for each measurement point. Must be a positive integer.
    --noise: Set the percentage of noise induced to the created measurements. Must be a positive integer.

    Returns:
    None
    """
    
    # Parse command line arguments
    modelers_list = list(set(k.lower() for k in
                             chain(single_parameter.all_modelers.keys(), multi_parameter.all_modelers.keys())))
    parser = argparse.ArgumentParser(description="Run synthetic benchmark.")
    parser.add_argument("--newonly", type=int, required=False, default=0, choices=[0, 1],
                        help="Run analysis only for random and grid search only.")
    parser.add_argument("--plot", type=bool, required=False, default=False,
                        help="Set if the plots should be shown after running the anlysis.")
    parser.add_argument("--mode", type=str, required=False, default="free", choices=["free", "budget"],
                        help="Set the analysis mode. If budget is used, strategies are only allowed to add more points until budget is reached. If free is set they choose until no improvement is made anymore.")
    parser.add_argument("--normalization", type=bool, default=False,
                        help="Set if normalization of the measurement points parameter values is used for the gpr approach.")
    parser.add_argument("--budget", type=float, required=False, default=30,
                        help="Set the allowed budget for the measurement points of the anlysis.")
    parser.add_argument("--nr-parameters", type=int, choices=[2, 3, 4], required=True,
                        help="Number of parameters for the synthetic benchmark. Must be 2, 3, or 4.")
    parser.add_argument("--nr-functions", type=int, default=1000, required=True,
                        help="Number of synthetic functions used for the evaluation. Must be an integer value.")
    parser.add_argument("--nr-repetitions", type=int, default=4, required=True,
                        help="Number of repetitions for each measurement point. Must be an integer value.")
    parser.add_argument("--noise", type=float, default=1, required=True,
                        help="Percentage of induced noise. Must be an integer value.")
    parser.add_argument("--grid-search", type=int, default=1, required=False, choices=[1,2,3,4],
                        help="Set the evaluation mode. Used for grid search for best strategy setups.")
    parser.add_argument("--base-values", type=int, default=2, required=False,
                        help="Set the number of repetitions used for the minimal set of measurements for the GPR strategy.")
    parser.add_argument("--hybrid-switch", type=int, default=5, required=False,
                        help="Set the switching point for the hybrid selection strategy.")
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
    args = parser.parse_args()

    # Run the benchmark
    benchmark = SyntheticBenchmark(args)
    benchmark.run()


if __name__ == "__main__":
    os.environ["TQDM_DISABLE"] = "1"
    main()

