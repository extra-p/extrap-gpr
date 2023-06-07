from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
import numpy as np
import matplotlib.pyplot as plt
from synthetic_benchmark import SyntheticBenchmark
import argparse
import math
from math import log2
import random
from extrap.util.progress_bar import ProgressBar
from extrap.fileio.cube_file_reader2 import read_cube_file
from extrap.fileio.experiment_io import read_experiment
from extrap.fileio.json_file_reader import read_json_file
from extrap.fileio.talpas_file_reader import read_talpas_file
from extrap.fileio.text_file_reader import read_text_file
import os
import sys
import logging
from extrap.modelers.model_generator import ModelGenerator
from extrap.modelers.abstract_modeler import MultiParameterModeler
from itertools import chain
from extrap.modelers import multi_parameter
from extrap.modelers import single_parameter
from extrap.util.options_parser import ModelerOptionsAction, ModelerHelpAction
from extrap.util.options_parser import SINGLE_PARAMETER_MODELER_KEY, SINGLE_PARAMETER_OPTIONS_KEY
from case_study import get_eval_string
import copy
from case_study import calculate_selected_point_cost
from extrap.entities.coordinate import Coordinate
from temp import add_measurements_to_gpr
from temp import add_measurement_to_gpr


def main():

    # parse command line arguments
    # Parse command line args
    modelers_list = list(set(k.lower() for k in
                             chain(single_parameter.all_modelers.keys(), multi_parameter.all_modelers.keys())))
    parser = argparse.ArgumentParser(description="GPR TEST.")
    parser.add_argument("--mode", type=str, choices=["synth", "case"], default="case", required=True,
                        help="Percentage of induced noise. Must be an integer value.")
    """parser.add_argument("--nr-parameters", type=int, choices=[1, 2, 3, 4], required=True,
                        help="Number of parameters for the synthetic benchmark. Must be 2, 3, or 4.")
    parser.add_argument("--nr-functions", type=int, default=1000, required=True,
                        help="Number of synthetic functions used for the evaluation. Must be an integer value.")
    parser.add_argument("--nr-repetitions", type=int, default=5, required=True,
                        help="Number of repetitions for each measurement point. Must be an integer value.")"""
    parser.add_argument("--noise", type=int, default=1,
                        help="Percentage of induced noise. Must be an integer value.")
    
    positional_args = parser.add_argument_group("Positional args")
    positional_args.add_argument("path", metavar="FILEPATH", type=str, action="store",
                                      help="Specify a file path for Extra-P to work with")

    parser.add_argument("--budget", type=int, required=True, default=100,
                        help="Percentage of total cost of all points that can be used by the selection strategies. Positive integer value between 0-100.")
    
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
    
    args = parser.parse_args()

    normalization = args.normalization
    print("Use normalization?:",normalization)

    # set use mean or median for computation
    use_median = args.median

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

    if args.mode == "case":

        # check scaling type
        scaling_type = args.scaling_type

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

        runtime_sums = {}
        smapes = []
        cost_container = {}
        total_costs_container = {}
        all_points_functions_strings = {}

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
                smape = hypothesis.SMAPE
                
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
                    for k in range(len(measurement_temp.values)):
                        runtime = measurement_temp.values[k]
                        core_hours = runtime * nr_processes
                        cost[experiment.coordinates[i]].append(core_hours)
                        coordinate_cost += core_hours
                        overall_runtime += runtime
                    total_cost += coordinate_cost
            else:
                smape = 0
                function_string = "None"
                total_cost = 0
                overall_runtime = 0

            smapes.append(smape)
           
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

            kernels_used += 1
            print("callpath_cost_percent_from_total:",callpath_cost)

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
            #print("y_values:",y_values,"x_value:",x_value)

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

            print("selected_points:",selected_points)

            # calculate the cost for the selected base points
            base_point_cost = calculate_selected_point_cost(selected_points, experiment, callpath_id, metric_id)
            base_point_cost_core_hours = base_point_cost
            base_point_cost = base_point_cost / (total_cost / 100)

            print("base_point_cost %:",base_point_cost)

            ##################################

            # GPR code...

            ##################################

            # parameter-value normalization for each measurement point
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

            ##################################
            #//Setup GPR
            #std::string cov = "CovMatern5iso";
            #GaussianProcess gp( dim, cov );
            #Eigen::VectorXd gpr_params( gp.covf().get_param_dim() );
            #gpr_params << 5.0, 0.0;
            #gp.covf().set_loghyper( gpr_params );

            # ell = 5.0
            #sf2 = 0.0
            ####################################

            # create a gaussian process regressor
            #TODO: need to make sure this is correct
            #TODO: what hyper parameter values to choose?
            #TODO: should not use alpha I guess...
            #TODO: should use RBF or something else???


            from sklearn.gaussian_process.kernels import Matern
            # nu should be [0.5, 1.5, 2.5, inf], everything else has 10x overhead
            kernel = 1.0 * Matern(length_scale=1.0, length_scale_bounds=(1e-5, 1e5), nu=1.5)


            #kernel = 1 * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e3))
            gaussian_process = GaussianProcessRegressor(
                kernel=kernel, alpha=0.75**2, n_restarts_optimizer=9
            )

            # add all of the selected measurement points to the gaussian process
            # as training data and train it for these points
            gaussian_process = add_measurements_to_gpr(gaussian_process, 
                            selected_points, 
                            experiment.measurements, 
                            callpath, 
                            metric,
                            normalization_factors,
                            experiment.parameters)
            
            #DEBUG
            #print("remaining_points:",remaining_points)

            # add additional measurement points until break criteria is met
            add_points = 0
            budget_core_hours = budget * (total_cost / 100)
                
            while True:

                # identify all possible next points that would 
                # still fit into the modeling budget in core hours
                fitting_measurements = []
                for key, value in remaining_points.items():

                    current_cost = calculate_selected_point_cost(selected_points, experiment, callpath_id, metric_id)
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
                    term_1 = math.pow(np.sum(remaining_points[fitting_measurements[i]]), 2)
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

                    # add the identified measurement point to the experiment, selected point list
                    parameter_values = fitting_measurements[best_index].as_tuple()
                    cord = Coordinate(parameter_values)
                    selected_points.append(cord)
                    
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
                        remaining_points.pop(cord)
                    except KeyError:
                        pass

                    # update the number of additional points used
                    add_points += 1

                # if there are no suitable measurement points found
                # break the while True loop
                else:
                    break
                #TODO: for use in extra-p later could also go by accuracy improvement with a certain threshold

            #DEBUG print outs
            print("selected_points:",selected_points)
            current_cost = calculate_selected_point_cost(selected_points, experiment, callpath_id, metric_id)
            print("Cost used in core hours: {:.2f}".format(current_cost))
            current_cost_percent = current_cost / (total_cost / 100)
            current_cost_percent_string = "{:.2f}".format(current_cost_percent)
            print("Used",current_cost_percent_string,"% of the",budget,"% budget.")
            print("Additinal points used:",add_points)
            #print("remaining_points:",remaining_points)






    else:

        random.seed(10)

        # create a syntethic function
        benchmark = SyntheticBenchmark(args)
        nr_parameters = benchmark.nr_parameters
        functions = benchmark.generate_synthetic_functions()
        function = functions[0].function

        function = "1.5+2.3*a**2*math.log2(a)**1*2.75*b**1*math.log2(b)**1"

        print("function:",function)
        
        # x1 is the number of processes
        x1_min = 1
        x1_max = benchmark.parameter_values_a_val[0]+1
        # x2 is the problem size
        x2_min = 1
        x2_max = benchmark.parameter_values_b_val[0]+1

        X1 = np.linspace(start=x1_min, stop=x1_max, num=1_000).reshape(-1, 1)
        X2 = np.linspace(start=x2_min, stop=x2_max, num=1_000).reshape(-1, 1)

        runtime = []
        for i in range(len(X1)):
            a = X1[i]
            b = X2[i]
            result = eval(function)
            runtime.append(result[0])
        runtime = np.array(runtime)


        ###############################################################################

        # define the parameter value sets for the input
        # parameters x1,x2,...,xn
        xn = [
            [4,8,16,32,64],
            [10,20,30,40,50],
            [2,4,6,8,10]
        ]

        # create a full measurement matrix based on the 
        # set of parameter values of all input parameters x1,x2,...,xn
        for i in range(len(xn)):
            for j in range(len(xn[i])):
                xn[i][j]
            if i+1 == nr_parameters:
                break
        
        print("test:",)



        # get the parameter values from the measurement points
        # into the input parameters x1,x2,...,xn
        if nr_parameters == 1:

            x1_train = benchmark.parameter_values_a
            x1_train = np.array(x1_train)
            x1_train = x1_train.reshape(-1, 1)
            print("x1_train:",x1_train)
            
        elif nr_parameters == 2:
            
            x1_train = benchmark.parameter_values_a
            x1_train = np.array(x1_train)
            x1_train = x1_train.reshape(-1, 1)
            print("x1_train:",x1_train)

            x2_train = benchmark.parameter_values_b
            x2_train = np.array(x2_train)
            x2_train = x2_train.reshape(-1, 1)
            print("x2_train:",x2_train)

        else:

            return 1

        # get the target parameter by calculating its value
        # using the baseline function and the input parameters x1,x2,...xn
        y_train = []

        #TODO: how many measurement points should I use???


        y_train2 = []
        for i in range(len(x1_train)):
            a = x1_train[i]
            b = x2_train[i]
            result = eval(function)



            values = []
            for _ in range(5):
                if random.randint(1, 2) == 1:
                    noise = random.uniform(0, args.noise)
                    result *= ((100-noise)/100)
                else:
                    noise = random.uniform(0, args.noise)
                    result *= ((100+noise)/100)
                values.append(result)
            y_train2.append(np.mean(values))
        
        y_train2 = np.array(y_train2)
        x_train_plot = x1_train
        y_train2_plot = y_train2
        #x_train = x_train.reshape(-1, 1)
        y_train2 = y_train2.reshape(-1, 1)
        #print("x_train:",x_train)
        print("y_train2:",y_train2)

        # calculate the costs of each of these training points
        nr_cores = 8
        costs = []
        for i in range(len(x1_train)):
            nr_processes = x1_train[i]
            core_hours = nr_processes * y_train2[i] * nr_cores
            costs.append(core_hours)

        # calculate cost of a not yet conducted experiment


        #rng = np.random.RandomState(1)
        #training_indices = rng.choice(np.arange(y.size), size=6, replace=False)
        #X_train, y_train = X[training_indices], y[training_indices]

        #print(" X_train, y_train:", X_train, y_train)


        #noise_std = 0.75
        noise_std = 1 - (args.noise/100)
        #y_train_noisy = y_train + rng.normal(loc=0.0, scale=noise_std, size=y_train.shape)
        #print("y_train_noisy:",y_train_noisy)

        #TODO: could use the noise level extracted from the measurements for the alpha value here...
        kernel = 1 * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e2))
        gaussian_process = GaussianProcessRegressor(
            kernel=kernel, alpha=noise_std**2, n_restarts_optimizer=9
        )
        gaussian_process.fit(x1_train, y_train2)
        mean_prediction, std_prediction = gaussian_process.predict(X1, return_std=True)

        #print("X_train, y_train_noisy:",X_train[2], y_train_noisy[2])

        target = [benchmark.parameter_values_a_val[0]]

        #nr_processes = (X_train[2])
        XX = [target]
        predicted_y, _ = gaussian_process.predict(XX, return_std=True)
        #y_sample = gaussian_process.sample_y(XX, n_samples=1, random_state=0)
        #print("y_sample:",y_sample[0])
        #predicted_y = y_sample[0]







        # plot the baseline function
        plt.plot(X1, runtime, label=r"$f(a)="+str(function)+"$", linestyle="dotted")

        # plot the training points
        plt.errorbar(x_train_plot, y_train2_plot, noise_std, linestyle="None", color="tab:blue", marker=".", markersize=10, label="Observations")

        # plot mean prediction model created by gpr
        #plt.plot(X1, mean_prediction, label="Mean prediction")

        # plot the 95% confidence interval
        """plt.fill_between(
            X1.ravel(),
            mean_prediction - 1.96 * std_prediction,
            mean_prediction + 1.96 * std_prediction,
            color="tab:orange",
            alpha=0.5,
            label=r"95% confidence interval",
        )"""

        # visualize the prediction of the target evaluation point
        #plt.plot(XX, predicted_y, marker="X")
        
        #plt.plot(XX, predicted_y[0], marker="X", label="target point")


        plt.legend()
        plt.xlabel("number of processes $a$")
        plt.ylabel("$f(a)$")
        _ = plt.title("Gaussian process regression on a noisy dataset")
        plt.tight_layout()
        plt.show()

        #print("mean_prediction:",mean_prediction)



        #double rated = std::pow( costForIndex[current_index].second, 2 ) / ( std::pow( std::abs( gp.var( x )), 2 ));



if __name__ == "__main__":
    main()
