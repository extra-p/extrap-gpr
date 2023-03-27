import argparse
from synthetic_benchmark import SyntheticBenchmark


def main():
    """
    Runs a synthetic benchmark with a specified number of parameters.

    Command line arguments:
    --nr-parameters: Number of parameters for the benchmark. Must be a positive integer.
    --nr-functions: Number of functions used for the synthetic evaluation. Must be a positive integer.

    Returns:
    None
    """
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run synthetic benchmark.")
    parser.add_argument("--nr-parameters", type=int, choices=[1, 2, 3, 4], required=True,
                        help="Number of parameters for the synthetic benchmark. Must be 1, 2, 3, or 4.")
    parser.add_argument("--nr-functions", type=int, default=1000, required=True,
                        help="Number of synthetic functions used for the evaluation. Must be an integer value.")
    args = parser.parse_args()

    # Run the benchmark
    benchmark = SyntheticBenchmark(args.nr_parameters, args.nr_functions)
    benchmark.run()


if __name__ == "__main__":
    main()

