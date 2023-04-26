import argparse
from synthetic_benchmark import SyntheticBenchmark
from itertools import chain
from extrap.modelers import multi_parameter
from extrap.modelers import single_parameter
from extrap.util.options_parser import ModelerOptionsAction, ModelerHelpAction
from extrap.util.options_parser import SINGLE_PARAMETER_MODELER_KEY, SINGLE_PARAMETER_OPTIONS_KEY


def main():
    """
    Runs an evaluation for a case study based on the cube files loaded from the specified directory.

    Command line arguments:
    --nr-parameters: Number of parameters for the benchmark. Must be a positive integer.
    --nr-functions: Number of functions used for the synthetic evaluation. Must be a positive integer.
    --noise: Set the percentage of noise induced to the created measurements. Must be a positive integer.

    Returns:
    None
    """

    #TODO: add command line arguments and method to read data from cube files... remove not needed arguments...
    
    # Parse command line arguments
    modelers_list = list(set(k.lower() for k in
                             chain(single_parameter.all_modelers.keys(), multi_parameter.all_modelers.keys())))
    parser = argparse.ArgumentParser(description="Run synthetic benchmark.")

    parser.add_argument("--nr-parameters", type=int, choices=[1, 2, 3, 4], required=True,
                        help="Number of parameters for the synthetic benchmark. Must be 2, 3, or 4.")
    

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

    # TODO: code for case study analysis

    #TODO: need to be able to read data from cube files: FASTEST, Kripke, MILC
    #TODO: need to make measurements for MILC with 2 and three parameters
    #TODO: need to create, read input files for Relearn somehow...

    #NOTE: -> for case studies... I need the percentage of models where the prediction is within +-5, +-10, +-15, +-20 % of the actual measurements
    # using a total budget of 15, 20, 30 % of all available points, for the point selection
    # mit +-1, +-2.5, +-5, +-7.5, +-10 % noise on the measurements for synthetic stuff

    


if __name__ == "__main__":
    main()

