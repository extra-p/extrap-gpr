from function_generator import FunctionGenerator
import copy
from multiprocessing import Manager
import multiprocessing as mp
from multiprocessing import Pool
from tqdm import tqdm
import math
from math import log2
import extrap
from extrap.entities.parameter import Parameter
from extrap.entities.callpath import Callpath
from extrap.entities.metric import Metric
from extrap.entities.coordinate import Coordinate
from extrap.entities.measurement import Measurement
from extrap.entities.experiment import Experiment
import random
from extrap.modelers import multi_parameter
from extrap.modelers import single_parameter
from extrap.modelers.abstract_modeler import MultiParameterModeler
from extrap.modelers.model_generator import ModelGenerator
from extrap.util.options_parser import SINGLE_PARAMETER_MODELER_KEY, SINGLE_PARAMETER_OPTIONS_KEY
from extrap.util.progress_bar import ProgressBar
import numpy as np
from plotting import plot_measurement_point_number, plot_model_accuracy, plot_costs
from generic_strategy import add_additional_point_generic, add_additional_point_random, add_additional_point_grid
from temp import add_measurements_to_gpr
from temp import add_measurement_to_gpr
from temp import add_measurement_to_gpr_test
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern
from sklearn.gaussian_process.kernels import WhiteKernel
import warnings
from sklearn.exceptions import ConvergenceWarning
import sys
import json

def create_experiment2(selected_coord_list, experiment, nr_parameters, parameter_placeholders, metric_id, callpath_id):
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

def calculate_selected_point_cost2(selected_points, experiment, callpath_id, metric_id):
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
                runtime = measurement_temp.values[k]
                nr_processes = coordinate.as_tuple()[0]
                core_hours = runtime * nr_processes
                coordinate_cost += core_hours
        selected_cost += coordinate_cost
    return selected_cost

class SyntheticBenchmark():

    def __init__(self, args):
        self.nr_parameters = args.nr_parameters
        self.nr_functions = args.nr_functions
        self.nr_repetitions = args.nr_repetitions
        self.normalization = args.normalization
        self.plot = args.plot
        self.mode = args.mode
        self.budget = args.budget
        self.args = args
        self.parameter_placeholders = ["a","b","c","d"]
        self.parameter_values_a = [4,8,16,32,64]
        self.parameter_values_b = [10,20,30,40,50]
        self.parameter_values_c = [1000,2000,3000,4000,5000]
        self.parameter_values_d = [10,12,14,16,18]
        self.noise_percent = args.noise
        self.parameter_values_a_val = [128, 256]
        self.parameter_values_b_val = [60, 70]
        self.parameter_values_c_val = [6000, 7000]
        self.parameter_values_d_val = [20, 22]
        self.grid_search = args.grid_search
        if args.base_values < self.nr_repetitions:
            self.base_values = args.base_values
        else:
            self.base_values = 2
        self.hybrid_switch = args.hybrid_switch
        if args.newonly == 0:
            self.newonly = False
        else:
            self.newonly = True

    def calculate_percentage_of_buckets(self, acurracy_bucket_counter):
        # calculate the percentages for each accuracy bucket
        percentage_bucket_counter = {}
        #print("DEBUG:",acurracy_bucket_counter)
        for key, value in acurracy_bucket_counter.items():
            if value > 0:
                percentage = (value / acurracy_bucket_counter["rest"]) * 100
            else:
                percentage = 0
            percentage_bucket_counter[key] = percentage
        return percentage_bucket_counter
    
    def create_experiment_base(self, selected_coord_list, experiment, nr_parameters, parameter_placeholders, metric_id, callpath_id, nr_base_points):
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
                    values.append(measurement_temp.values[counter])
                    counter += 1
                #value = selected_measurement_values[selected_coord_list[j]] 
                #experiment_generic.add_measurement(Measurement(coordinate, callpath, metric, value))
                experiment_new.add_measurement(Measurement(coordinate, callpath, metric, values))
        return experiment_new
    
    def create_experiment(self, cord, experiment, new_value):
        # only append the new measurement value to experiment
        cord_found = False
        for i in range(len(experiment.measurements[(Callpath("main"), Metric("runtime"))])):
            if cord == experiment.measurements[(Callpath("main"), Metric("runtime"))][i].coordinate:
                experiment.measurements[(Callpath("main"), Metric("runtime"))][i].add_value(new_value)
                #x = np.append(x, new_value)
                #experiment.measurements[(Callpath("main"), Metric("runtime"))][i].values = x
                cord_found = True
                break
        if cord_found == False:
            # add new coordinate to experiment and then add a new measurement object with the new value to the experiment
            experiment.add_coordinate(cord)
            new_measurement = Measurement(cord, Callpath("main"), Metric("runtime"), [new_value])
            experiment.add_measurement(new_measurement)
        return experiment
    
    def calculate_selected_point_cost_base(self, selected_points, experiment, callpath_id, metric_id, nr_base_points):
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
                counter = 0
                while counter < nr_base_points:
                #for k in range(len(measurement_temp.values)):
                    runtime = measurement_temp.values[counter]
                    nr_processes = coordinate.as_tuple()[0]
                    core_hours = runtime * nr_processes
                    coordinate_cost += core_hours
                    counter += 1
            selected_cost += coordinate_cost
        return selected_cost
    
    def calculate_selected_point_cost(self, experiment):
        selected_cost = 0
        for i in range(len(experiment.measurements[(Callpath("main"), Metric("runtime"))])):
            x = experiment.measurements[(Callpath("main"), Metric("runtime"))][i]
            coordinate_cost = 0
            for k in range(len(x.values)):
                runtime = x.values[k]
                nr_processes = x.coordinate.as_tuple()[0]
                core_hours = runtime * nr_processes
                coordinate_cost += core_hours
            selected_cost += coordinate_cost
        return selected_cost

    def increment_accuracy_bucket(self, acurracy_bucket_counter, percentage_error):
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

    def percentage_error(self, true_value, measured_value):
        error = abs(true_value - measured_value)
        percentage_error = (error / true_value) * 100
        return percentage_error

    def get_extrap_model(self, experiment):
        # initialize model generator
        model_generator = ModelGenerator(
            experiment, modeler=self.args.modeler)

        # apply modeler options
        modeler = model_generator.modeler
        if isinstance(modeler, MultiParameterModeler) and self.args.modeler_options:
            # set single-parameter modeler of multi-parameter modeler
            single_modeler = self.args.modeler_options[SINGLE_PARAMETER_MODELER_KEY]
            if single_modeler is not None:
                modeler.single_parameter_modeler = single_parameter.all_modelers[single_modeler]()
            # apply options of single-parameter modeler
            if modeler.single_parameter_modeler is not None:
                for name, value in self.args.modeler_options[SINGLE_PARAMETER_OPTIONS_KEY].items():
                    if value is not None:
                        setattr(modeler.single_parameter_modeler, name, value)

        for name, value in self.args.modeler_options.items():
            if value is not None:
                setattr(modeler, name, value)

        # create models from data
        with ProgressBar(desc='Generating models', disable=True) as pbar:
            model_generator.model_all(pbar)

        modeler = experiment.modelers[0]
        models = modeler.models
        extrap_function_string = ""
        for model in models.values():
            hypothesis = model.hypothesis
            function = hypothesis.function
            function_string = function.to_string(*experiment.parameters)
            extrap_function_string += function_string + "\n"
        
        return extrap_function_string, models

    def generate_synthetic_functions(self):
        generator = FunctionGenerator(self.parameter_values_a, 
                                      self.parameter_values_b, 
                                      self.parameter_values_c, 
                                      self.parameter_values_d, 
                                      nr_parameters=self.nr_parameters)
        
        # parallelize reading all measurement_files in one folder
        manager = Manager()
        shared_dict = manager.dict()
        cpu_count = mp.cpu_count()
        cpu_count -= 4
        if self.nr_functions < cpu_count:
            cpu_count = self.nr_functions

        inputs = []
        for i in range(self.nr_functions):
            inputs.append([i, shared_dict])

        with Pool(cpu_count) as pool:
            _ = list(tqdm(pool.imap(generator.generate_function, inputs), total=self.nr_functions, disable=True))

        function_dict = copy.deepcopy(shared_dict)
        
        return function_dict
    
    def simulate(self, inputs):

        # disable deprecation warnings...
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=ConvergenceWarning)

        # get the values from the parallel input dict
        counter = inputs[0]
        shared_dict = inputs[1]
        basline_function = inputs[2]
        result_container = {}

        # prepare dicts for saving the accuracy analysis data
        acurracy_bucket_counter_full = {}
        acurracy_bucket_counter_full["rest"] = 0
        acurracy_bucket_counter_full["5"] = 0
        acurracy_bucket_counter_full["10"] = 0
        acurracy_bucket_counter_full["15"] = 0
        acurracy_bucket_counter_full["20"] = 0

        acurracy_bucket_counter_generic = {}
        acurracy_bucket_counter_generic["rest"] = 0
        acurracy_bucket_counter_generic["5"] = 0
        acurracy_bucket_counter_generic["10"] = 0
        acurracy_bucket_counter_generic["15"] = 0
        acurracy_bucket_counter_generic["20"] = 0

        percentage_cost_generic_container = []
        add_points_generic_container = []

        acurracy_bucket_counter_gpr = {}
        acurracy_bucket_counter_gpr["rest"] = 0
        acurracy_bucket_counter_gpr["5"] = 0
        acurracy_bucket_counter_gpr["10"] = 0
        acurracy_bucket_counter_gpr["15"] = 0
        acurracy_bucket_counter_gpr["20"] = 0

        percentage_cost_gpr_container = []
        add_points_gpr_container = []

        acurracy_bucket_counter_hybrid = {}
        acurracy_bucket_counter_hybrid["rest"] = 0
        acurracy_bucket_counter_hybrid["5"] = 0
        acurracy_bucket_counter_hybrid["10"] = 0
        acurracy_bucket_counter_hybrid["15"] = 0
        acurracy_bucket_counter_hybrid["20"] = 0

        percentage_cost_hybrid_container = []
        add_points_hybrid_container = []

        acurracy_bucket_counter_random = {}
        acurracy_bucket_counter_random["rest"] = 0
        acurracy_bucket_counter_random["5"] = 0
        acurracy_bucket_counter_random["10"] = 0
        acurracy_bucket_counter_random["15"] = 0
        acurracy_bucket_counter_random["20"] = 0

        percentage_cost_random_container = []
        add_points_random_container = []

        acurracy_bucket_counter_grid = {}
        acurracy_bucket_counter_grid["rest"] = 0
        acurracy_bucket_counter_grid["5"] = 0
        acurracy_bucket_counter_grid["10"] = 0
        acurracy_bucket_counter_grid["15"] = 0
        acurracy_bucket_counter_grid["20"] = 0

        percentage_cost_grid_container = []
        add_points_grid_container = []

        # logic for setting the number of min points required by the modeler
        if self.nr_parameters == 2:
            min_points = 9
        elif self.nr_parameters == 3:
            min_points = 13
        elif self.nr_parameters == 4:
            min_points = 17
        else:
            return 1
        
        cost = {}
        total_cost = 0

        # create a new extra-p experiment
        experiment = Experiment()
        
        # add the parameters to the experiment
        for j in range(self.nr_parameters):
            experiment.add_parameter(Parameter(self.parameter_placeholders[j]))
        
        # add a dummy callpath to the experiment
        callpath = Callpath("main")
        experiment.add_callpath(callpath)
        
        # add a dummy metric to the experiment
        metric = Metric("runtime")
        experiment.add_metric(metric)

        # set a random seed so that the amount of noise generated is the same for experiment with different budgets
        random.seed(10)

        if self.nr_parameters == 2:
            # create and add the coordinates and measurements to experiment
            for j in range(len(self.parameter_values_a)):
                for k in range(len(self.parameter_values_b)):
                    coordinate = Coordinate(self.parameter_values_a[j], self.parameter_values_b[k])
                    experiment.add_coordinate(coordinate)
                    a = self.parameter_values_a[j]
                    b = self.parameter_values_b[k]
                    result = eval(basline_function)
                    values = []
                    if coordinate not in cost:
                        cost[coordinate] = []
                    for _ in range(self.nr_repetitions):
                        if random.randint(1, 2) == 1:
                            noise = random.uniform(0, self.noise_percent/2)
                            result *= ((100-noise)/100)
                        else:
                            noise = random.uniform(0, self.noise_percent/2)
                            result *= ((100+noise)/100)
                        runtime = result
                        nr_processes = self.parameter_values_a[j]
                        core_hours = runtime * nr_processes
                        total_cost += core_hours
                        cost[coordinate].append(core_hours)
                        values.append(result)
                    experiment.add_measurement(Measurement(coordinate, callpath, metric, values))

        elif self.nr_parameters == 3:
            # create and add the coordinates and measurements to experiment
            for j in range(len(self.parameter_values_a)):
                for k in range(len(self.parameter_values_b)):
                    for o in range(len(self.parameter_values_c)):
                        coordinate = Coordinate(self.parameter_values_a[j], self.parameter_values_b[k], self.parameter_values_c[o])
                        experiment.add_coordinate(coordinate)
                        a = self.parameter_values_a[j]
                        b = self.parameter_values_b[k]
                        c = self.parameter_values_c[o]
                        result = eval(basline_function)
                        values = []
                        if coordinate not in cost:
                            cost[coordinate] = []
                        for _ in range(self.nr_repetitions):
                            if random.randint(1, 2) == 1:
                                noise = random.uniform(0, self.noise_percent/2)
                                result *= ((100-noise)/100)
                            else:
                                noise = random.uniform(0, self.noise_percent/2)
                                result *= ((100+noise)/100)
                            runtime = result
                            nr_processes = self.parameter_values_a[j]
                            core_hours = runtime * nr_processes
                            total_cost += core_hours
                            cost[coordinate].append(core_hours)
                            values.append(result)
                        experiment.add_measurement(Measurement(coordinate, callpath, metric, values))
                
        elif self.nr_parameters == 4:
            # create and add the coordinates and measurements to experiment
            for j in range(len(self.parameter_values_a)):
                for k in range(len(self.parameter_values_b)):
                    for o in range(len(self.parameter_values_c)):
                        for l in range(len(self.parameter_values_d)):
                            coordinate = Coordinate(self.parameter_values_a[j], self.parameter_values_b[k], self.parameter_values_c[o], self.parameter_values_d[l])
                            experiment.add_coordinate(coordinate)
                            a = self.parameter_values_a[j]
                            b = self.parameter_values_b[k]
                            c = self.parameter_values_c[o]
                            d = self.parameter_values_d[l]
                            result = eval(basline_function)
                            values = []
                            if coordinate not in cost:
                                cost[coordinate] = []
                            for _ in range(self.nr_repetitions):
                                if random.randint(1, 2) == 1:
                                    noise = random.uniform(0, self.noise_percent/2)
                                    result *= ((100-noise)/100)
                                else:
                                    noise = random.uniform(0, self.noise_percent/2)
                                    result *= ((100+noise)/100)
                                runtime = result
                                nr_processes = self.parameter_values_a[j]
                                core_hours = runtime * nr_processes
                                total_cost += core_hours
                                cost[coordinate].append(core_hours)
                                values.append(result)
                            experiment.add_measurement(Measurement(coordinate, callpath, metric, values))

        else:
            return 1
        
        ##########################
        ## Base point selection ##
        ##########################

        # create copy of the cost dict
        remaining_points = copy.deepcopy(cost)
        
        # create copy of the cost dict for the minimum experiment with gpr and hybrid strategies
        remaining_points_min = copy.deepcopy(cost)
        
        if self.grid_search == 2 or self.grid_search == 3:
            measurements_gpr = copy.deepcopy(experiment.measurements)
            measurements_hybrid = copy.deepcopy(experiment.measurements)
            measurements_random = copy.deepcopy(experiment.measurements)
            measurements_grid = copy.deepcopy(experiment.measurements)
    
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
                    
                    if self.grid_search == 2 or self.grid_search == 3:
                        for x in measurements_gpr[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_hybrid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_random[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_grid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        # also delete the cost values from the remaining min dict
                        for i in range(self.base_values):
                            remaining_points_min[cord].pop(0)
                    
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
                    
                    if self.grid_search == 2 or self.grid_search == 3:
                        for x in measurements_gpr[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_hybrid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_random[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_grid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                            
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
                    
                    if self.grid_search == 2 or self.grid_search == 3:
                        for x in measurements_gpr[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_hybrid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_random[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_grid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        # also delete the cost values from the remaining min dict
                        for i in range(self.base_values):
                            remaining_points_min[cord].pop(0)
                    
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
                    
                    if self.grid_search == 2 or self.grid_search == 3:
                        for x in measurements_gpr[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_hybrid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_random[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_grid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        # also delete the cost values from the remaining min dict
                        for i in range(self.base_values):
                            remaining_points_min[cord].pop(0)
                    
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
                    
                    if self.grid_search == 2 or self.grid_search == 3:
                        for x in measurements_gpr[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_hybrid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_random[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_grid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        # also delete the cost values from the remaining min dict
                        for i in range(self.base_values):
                            remaining_points_min[cord].pop(0)
                    
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

        elif len(experiment.parameters) == 4:
            
            # find the cheapest line of 5 points for x1
            x1_lines = {}
            for i in range(len(experiment.coordinates)):
                cord_values = experiment.coordinates[i].as_tuple()
                x1 = []
                x2 = cord_values[1]
                x3 = cord_values[2]
                x4 = cord_values[3]
                for j in range(len(experiment.coordinates)):
                    cord_values2 = experiment.coordinates[j].as_tuple()
                    if cord_values2[1] == x2 and cord_values2[2] == x3 and cord_values2[3] == x4:
                        x1.append(cord_values2[0])
                if len(x1) >= 5:
                    if (x2,x3,x4) not in x1_lines:
                        x1_lines[(x2,x3,x4)] = x1
            # calculate the cost of each of the lines
            line_costs = {}
            #print("x1_lines:",x1_lines)

            for key, value in x1_lines.items():
                line_cost = 0
                for i in range(len(value)):
                    point_cost = sum(cost[Coordinate(value[i], key[0], key[1], key[2])])
                    line_cost += point_cost
                line_costs[key] = line_cost
            x2_value, x3_value, x4_value = min(line_costs, key=line_costs.get)
            x1_values = x1_lines[min(line_costs, key=line_costs.get)]

            # remove these points from the list of remaining points
            for j in range(len(x1_values)):
                try:
                    cord = Coordinate(x1_values[j], x2_value, x3_value, x4_value)
                    remaining_points.pop(cord)
                    
                    if self.grid_search == 2 or self.grid_search == 3:
                        for x in measurements_gpr[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_hybrid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_random[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_grid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        # also delete the cost values from the remaining min dict
                        for i in range(self.base_values):
                            remaining_points_min[cord].pop(0)
                    
                except KeyError:
                    pass

            # add these points to the list of selected points
            selected_points = []
            for i in range(len(x1_values)):
                cord = Coordinate(x1_values[i], x2_value, x3_value, x4_value)
                selected_points.append(cord)

            #print("selected_points:",selected_points)

            # find the cheapest line of 5 points for x2
            x2_lines = {}
            for i in range(len(experiment.coordinates)):
                cord_values = experiment.coordinates[i].as_tuple()
                x1 = cord_values[0]
                x2 = []
                x3 = cord_values[2]
                x4 = cord_values[3]
                for j in range(len(experiment.coordinates)):
                    cord_values2 = experiment.coordinates[j].as_tuple()
                    if cord_values2[0] == x1 and cord_values2[2] == x3 and cord_values2[3] == x4:
                        x2.append(cord_values2[1])
                if len(x2) >= 5:
                    if (x1,x3,x4) not in x2_lines:
                        x2_lines[(x1,x3,x4)] = x2
            # calculate the cost of each of the lines
            line_costs = {}
            for key, value in x2_lines.items():
                line_cost = 0
                for i in range(len(value)):
                    point_cost = sum(cost[Coordinate(key[0], value[i], key[1], key[2])])
                    line_cost += point_cost
                line_costs[key] = line_cost
            x1_value, x3_value, x4_value = min(line_costs, key=line_costs.get)
            x2_values = x2_lines[min(line_costs, key=line_costs.get)]

            # remove these points from the list of remaining points
            for j in range(len(x2_values)):
                try:
                    cord = Coordinate(x1_value, x2_values[j], x3_value, x4_value)
                    remaining_points.pop(cord)
                    
                    if self.grid_search == 2 or self.grid_search == 3:
                        for x in measurements_gpr[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_hybrid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_random[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_grid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        # also delete the cost values from the remaining min dict
                        for i in range(self.base_values):
                            remaining_points_min[cord].pop(0)
                    
                except KeyError:
                    pass

            # add these points to the list of selected points
            for i in range(len(x2_values)):
                cord = Coordinate(x1_value, x2_values[i], x3_value, x4_value)
                exists = False
                for j in range(len(selected_points)):
                    if selected_points[j] == cord:
                        exists = True
                        break
                if exists == False:
                    selected_points.append(cord)

            #print("selected_points:",selected_points)

            # find the cheapest line of 5 points for x3
            x3_lines = {}
            for i in range(len(experiment.coordinates)):
                cord_values = experiment.coordinates[i].as_tuple()
                x1 = cord_values[0]
                x2 = cord_values[1]
                x3 = []
                x4 = cord_values[3]
                for j in range(len(experiment.coordinates)):
                    cord_values2 = experiment.coordinates[j].as_tuple()
                    if cord_values2[0] == x1 and cord_values2[1] == x2 and cord_values2[3] == x4:
                        x3.append(cord_values2[2])
                if len(x3) >= 5:
                    if (x1,x2,x4) not in x3_lines:
                        x3_lines[(x1,x2,x4)] = x3
            # calculate the cost of each of the lines
            line_costs = {}
            for key, value in x3_lines.items():
                line_cost = 0
                for i in range(len(value)):
                    point_cost = sum(cost[Coordinate(key[0], key[1], value[i], key[2])])
                    line_cost += point_cost
                line_costs[key] = line_cost
            x1_value, x2_value, x4_value = min(line_costs, key=line_costs.get)
            x3_values = x3_lines[min(line_costs, key=line_costs.get)]

            # remove these points from the list of remaining points
            for j in range(len(x3_values)):
                try:
                    cord = Coordinate(x1_value, x2_value, x3_values[j], x4_value)
                    remaining_points.pop(cord)
                    
                    if self.grid_search == 2 or self.grid_search == 3:
                        for x in measurements_gpr[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_hybrid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_random[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_grid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        # also delete the cost values from the remaining min dict
                        for i in range(self.base_values):
                            remaining_points_min[cord].pop(0)
                    
                except KeyError:
                    pass

            # add these points to the list of selected points
            for i in range(len(x3_values)):
                cord = Coordinate(x1_value, x2_value, x3_values[i], x4_value)
                exists = False
                for j in range(len(selected_points)):
                    if selected_points[j] == cord:
                        exists = True
                        break
                if exists == False:
                    selected_points.append(cord)

            #print("selected_points:",selected_points)

            # find the cheapest line of 5 points for x4
            x4_lines = {}
            for i in range(len(experiment.coordinates)):
                cord_values = experiment.coordinates[i].as_tuple()
                x1 = cord_values[0]
                x2 = cord_values[1]
                x3 = cord_values[2]
                x4 = []
                for j in range(len(experiment.coordinates)):
                    cord_values2 = experiment.coordinates[j].as_tuple()
                    if cord_values2[0] == x1 and cord_values2[1] == x2 and cord_values2[2] == x3:
                        x4.append(cord_values2[3])
                if len(x4) >= 5:
                    if (x1,x2,x3) not in x4_lines:
                        x4_lines[(x1,x2,x3)] = x4
            # calculate the cost of each of the lines
            line_costs = {}
            for key, value in x4_lines.items():
                line_cost = 0
                for i in range(len(value)):
                    point_cost = sum(cost[Coordinate(key[0], key[1], key[2], value[i])])
                    line_cost += point_cost
                line_costs[key] = line_cost
            x1_value, x2_value, x3_value = min(line_costs, key=line_costs.get)
            x4_values = x4_lines[min(line_costs, key=line_costs.get)]

            # remove these points from the list of remaining points
            for j in range(len(x4_values)):
                try:
                    cord = Coordinate(x1_value, x2_value, x3_value, x4_values[j])
                    remaining_points.pop(cord)
                    
                    if self.grid_search == 2 or self.grid_search == 3:
                        for x in measurements_gpr[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_hybrid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_random[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        for x in measurements_grid[(Callpath("main"), Metric("runtime"))]:
                            if x.coordinate == cord:
                                temp = x.values
                                for i in range(self.base_values):
                                    temp = np.delete(temp, 0)
                                x.values = temp
                        # also delete the cost values from the remaining min dict
                        for i in range(self.base_values):
                            remaining_points_min[cord].pop(0)
                    
                except KeyError:
                    pass

            # add these points to the list of selected points
            for i in range(len(x4_values)):
                cord = Coordinate(x1_value, x2_value, x3_value, x4_values[i])
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

        # create a map to store which data points where selected after each other
        point_map_generic = {}
        selection_point_counter = 1
        #print("DEBUG:",len(experiment.coordinates))
        for cord in experiment.coordinates:
            point_map_generic[cord] = -1
            #print("cord:",cord)
        #print("point_map_generic:",point_map_generic)
        copy_point_map_generic = {}
        for cord in experiment.coordinates:
            copy_point_map_generic[cord] = 0
            #print("cord:",cord)

        # update the map with the numbers of already selected points
        for point in selected_points:
            point_map_generic[point] = selection_point_counter
            selection_point_counter += 1
            #print("point:",point)
        #print("point_map_generic:",point_map_generic)

        # calculate the cost for the selected base points
        if self.grid_search == 2 or self.grid_search == 3:
            base_point_cost = self.calculate_selected_point_cost_base(selected_points, experiment, 0, 0, self.base_values)
        elif self.grid_search == 1 or self.grid_search == 4:
            base_point_cost = calculate_selected_point_cost2(selected_points, experiment, 0, 0)
        base_point_cost = base_point_cost / (total_cost / 100)
        #print("base_point_cost %:",base_point_cost)

        added_points_generic = len(selected_points) * (self.nr_repetitions)
        added_points_random = len(selected_points) * (self.nr_repetitions)
        added_points_grid = len(selected_points) * (self.nr_repetitions)

        #print("len selected_points:",len(selected_points))
        
        if self.nr_parameters == 2:
            parameters = ["a", "b"]
        elif self.nr_parameters == 3:
            parameters = ["a", "b", "c"]
        elif self.nr_parameters == 4:
            parameters = ["a", "b", "c", "d"]
        else:
            return 1
        
        #############
        ## Generic ##
        #############

        remaining_points_generic = copy.deepcopy(remaining_points)
        selected_points_generic = copy.deepcopy(selected_points)
        
        # create base model for generic
        #if self.grid_search == 2 or self.grid_search == 3:
        #    experiment_generic_base = self.create_experiment_base(selected_points_generic, experiment, len(experiment.parameters), parameters, 0, 0, self.base_values)
        #else:
        #   experiment_generic_base = create_experiment2(selected_points_generic, experiment, len(experiment.parameters), parameters, 0, 0)
        
        #for x in experiment_generic_base.measurements[(Callpath("main"), Metric("runtime"))]:
        #    print(x.coordinate, x.values)

        # create first model
        experiment_generic_base = create_experiment2(selected_points_generic, experiment, len(experiment.parameters), parameters, 0, 0)
        
        _, models = self.get_extrap_model(experiment_generic_base)
        hypothesis = None
        for model in models.values():
            hypothesis = model.hypothesis

        # calculate selected point cost
        current_cost = calculate_selected_point_cost2(selected_points_generic, experiment, 0, 0)
        current_cost_percent = current_cost / (total_cost / 100)
        
        if self.mode == "budget":

            if current_cost_percent <= self.budget:
                if self.newonly == False:
                    while True:
                        # find another point for selection
                        remaining_points_new, selected_coord_list_new, new_point = add_additional_point_generic(remaining_points_generic, selected_points_generic)

                        # calculate selected point cost
                        current_cost = calculate_selected_point_cost2(selected_coord_list_new, experiment, 0, 0)
                        current_cost_percent = current_cost / (total_cost / 100)

                        # current cost exceeds budget so break the loop
                        #print("current_cost_percent > self.budget", current_cost_percent, self.budget)
                        # to make sure no mistakes occur here
                        # sometimes the numbers do not perfectly add up to the target budget
                        # but to 100.00001
                        # this is the fix for this case
                        current_cost_percent = float("{0:.2f}".format(current_cost_percent))
                        #print("current_cost_percent:",current_cost_percent)

                        if current_cost_percent > self.budget:
                            break

                        # add the new found point
                        else:

                            # update the map with the numbers of already selected points
                            point_map_generic[new_point] = selection_point_counter
                            selection_point_counter += 1
                            #print("point:",point)
                            #print("point_map_generic:",point_map_generic)

                            # increment counter value, because a new measurement point was added
                            #added_points_generic += 1
                            added_points_generic += self.nr_repetitions

                            # create new model
                            experiment_generic_base = create_experiment2(selected_coord_list_new, experiment, len(experiment.parameters), parameters, 0, 0)

                            selected_points_generic = selected_coord_list_new
                            remaining_points_generic = remaining_points_new

                        # if there are no points remaining that can be selected break the loop
                        if len(remaining_points_generic) == 0:
                            break

            else:
                pass

        elif self.mode == "free":
            pass

        else:
            return 1

        # calculate selected point cost
        selected_cost = calculate_selected_point_cost2(selected_points_generic, experiment, 0, 0)
        
        # calculate the percentage of cost of the selected points compared to the total cost of the full matrix
        percentage_cost_generic = selected_cost / (total_cost / 100)
        if percentage_cost_generic >= 99.9:
            percentage_cost_generic = 100
        #print("percentage_cost_generic:",percentage_cost_generic)
        percentage_cost_generic_container.append(percentage_cost_generic)

        # calculate number of additionally used data points (exceeding the base requirement of the sparse modeler)
        #add_points_generic = len(selected_points_generic) - min_points
        #if percentage_cost_generic > self.budget:
        #    added_points_generic = math.nan
        add_points_generic_container.append(added_points_generic)
        add_points_generic = added_points_generic
        #if percentage_cost_generic < 100:
        #    print("add_points_generic:",add_points_generic)
        
        # create model using point selection of generic strategy
        model_generic, _ = self.get_extrap_model(experiment_generic_base)
        
        #for x in experiment_generic_base.measurements[(Callpath("main"),Metric("runtime"))]:
        #    print(x, x.values)
        #print("Model generic:",model_generic)

        # create model using full matrix of points
        model_full, _ = self.get_extrap_model(experiment)
        #print("model_full:",model_full)

        # set the measurement point values for the evaluation of the prediction
        if self.nr_parameters == 2:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
        elif self.nr_parameters == 3:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
            c = self.parameter_values_c_val[0]
        elif self.nr_parameters == 4:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
            c = self.parameter_values_c_val[0]
            d = self.parameter_values_d_val[0]
        else:
            return 1

        # evaluate model accuracy against the first point in each direction of the parameter set for each parameter
        prediction_full = eval(model_full)
        #print("prediction_full:",prediction_full)
        prediction_generic = eval(model_generic)
        #print("prediction_generic:",prediction_generic)

        #basline_function = function_dict[i].function
        actual = eval(basline_function)
        #print("actual:",actual)

        # get the percentage error for the full matrix of points
        error_full = abs(self.percentage_error(actual, prediction_full))
        #print("error_full:",error_full)

        # get the percentage error for the generic strategy
        if percentage_cost_generic <= self.budget:
            error_generic = abs(self.percentage_error(actual, prediction_generic))
        else:
            error_generic = 100
        #print("error_generic:",error_generic)

        # increment accuracy bucket for full matrix of points
        acurracy_bucket_counter_full = self.increment_accuracy_bucket(acurracy_bucket_counter_full, error_full)

        # increment accuracy bucket for generic strategy
        acurracy_bucket_counter_generic = self.increment_accuracy_bucket(acurracy_bucket_counter_generic, error_generic)

        ##################
        ## GPR strategy ##
        ##################    

        # GPR parameter-value normalization for each measurement point
        normalization_factors = {}

        if self.normalization:
            
            for i in range(len(experiment.parameters)):

                param_value_max = -1

                for coord in experiment.coordinates:

                    temp = coord.as_tuple()[i]

                    if param_value_max < temp:
                        param_value_max = temp
                    
                param_value_max = 100 / param_value_max
                normalization_factors[experiment.parameters[i]] = param_value_max
                
            #print("normalization_factors:",normalization_factors)
        
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
        #print("Detected noise level from measurements:",mean_noise,"%")

        # nu should be [0.5, 1.5, 2.5, inf], everything else has 10x overhead
        # matern kernel + white kernel to simulate actual noise found in the measurements
        kernel = 1.0 * Matern(length_scale=1.0, length_scale_bounds=(1e-5, 1e5), nu=1.5) + WhiteKernel(noise_level=mean_noise)

        # create a gaussian process regressor
        gaussian_process = GaussianProcessRegressor(
            kernel=kernel, n_restarts_optimizer=20
        )

        eval_point = []
        if self.nr_parameters == 2:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
            eval_point.append(a)
            eval_point.append(b)
        elif self.nr_parameters == 3:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
            c = self.parameter_values_c_val[0]
            eval_point.append(a)
            eval_point.append(b)
            eval_point.append(c)
        elif self.nr_parameters == 4:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
            c = self.parameter_values_c_val[0]
            d = self.parameter_values_d_val[0]
            eval_point.append(a)
            eval_point.append(b)
            eval_point.append(c)
            eval_point.append(d)
        else:
            return 1

        # add additional measurement points until break criteria is met
        add_points_gpr = 0
        
        budget_core_hours = self.budget * (total_cost / 100)
        
        if self.grid_search == 1 or self.grid_search == 4:
            add_points_gpr = len(selected_points) * self.nr_repetitions
            remaining_points_gpr = copy.deepcopy(remaining_points)
            # entails all measurement points and their values
            measurements_gpr = copy.deepcopy(experiment.measurements)
        elif self.grid_search == 2 or self.grid_search == 3:
            add_points_gpr = len(selected_points) * self.base_values
            remaining_points_gpr = copy.deepcopy(remaining_points_min)
        selected_points_gpr = copy.deepcopy(selected_points)

        # add all of the selected measurement points to the gaussian process
        # as training data and train it for these points
        gaussian_process = add_measurements_to_gpr(gaussian_process, 
                        selected_points_gpr, 
                        measurements_gpr, 
                        callpath,
                        metric,
                        normalization_factors,
                        experiment.parameters, eval_point)

        # create base model for gpr
        if self.grid_search == 2 or self.grid_search == 3:
            experiment_gpr_base = self.create_experiment_base(selected_points_gpr, experiment, len(experiment.parameters), parameters, 0, 0, self.base_values)
        else:
            experiment_gpr_base = create_experiment2(selected_points_gpr, experiment, len(experiment.parameters), parameters, 0, 0)
        
        if base_point_cost <= self.budget:
            if self.newonly == False:
                while True:
                    
                    # identify all possible next points that would 
                    # still fit into the modeling budget in core hours
                    fitting_measurements = []
                    for key, value in remaining_points_gpr.items():
                        
                        #current_cost = calculate_selected_point_cost2(selected_points_gpr, experiment_gpr_base, 0, 0)
                        current_cost = self.calculate_selected_point_cost(experiment_gpr_base)
                        
                        # always take the first value in the list, until none left
                        #new_cost = current_cost + np.sum(value)
                        new_cost = current_cost + value[0]
                        cost_percent = new_cost / (total_cost / 100)
                        
                        #if new_cost > budget_core_hours:
                        #    print("new_cost <= budget_core_hours:", new_cost, budget_core_hours)
                        #if cost_percent > 100:
                        #    print("cost percent <= budget percent:", cost_percent, self.budget)
                        # to make sure no mistakes occur here
                        # sometimes the numbers do not perfectly add up to the target budget
                        # but to 100.00001
                        # this is the fix for this case
                        cost_percent = float("{0:.3f}".format(cost_percent))
                        if cost_percent > 100.0:
                            cost_percent = 100.0

                        if cost_percent <= self.budget:
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
                                x.append(parameter_values[j] * normalization_factors[experiment_gpr_base.parameters[j]])
                        
                            else:
                                x.append(parameter_values[j])
                                
                        #NOTE: should recalculate the noise level here... but is already done on all measurements before so not needed here....
                        # but in real extra-P implementation needs to be done...
                                
                        #print("DEBUG3 remaining_points_gpr:",remaining_points_gpr[fitting_measurements[i]][0])
                        
                        # term_1 is cost(t)^2
                        term_1 = math.pow(remaining_points_gpr[fitting_measurements[i]][0], 2)
                        # predict variance of input vector x with the gaussian process
                        x = [x]
                        _, y_cov = gaussian_process.predict(x, return_cov=True)
                        y_cov = abs(y_cov)
                        # term_2 is gp_cov(t,t)^2
                        term_2 = math.pow(y_cov, 2)
                        # rated is h(t)
                        
                        if self.grid_search == 3 or self.grid_search == 4:
                            rep = 1
                            for j in range(len(measurements_gpr[(Callpath("main"), Metric("runtime"))])):
                                if measurements_gpr[(Callpath("main"), Metric("runtime"))][j].coordinate == fitting_measurements[i]:
                                    rep = (self.nr_repetitions - len(measurements_gpr[(Callpath("main"), Metric("runtime"))][j].values)) + 1
                                    break
                            rep_func = 2**((1/2)*rep-(1/2))
                            noise_func = -math.tanh((1/4)*mean_noise-2.5)
                            cost_multiplier = rep_func + noise_func
                            rated = (term_1 * cost_multiplier) / term_2
                        else:
                            rated = term_1 / term_2

                        if rated <= best_rated:
                            best_rated = rated
                            best_index = i    

                    # if there has been a point found that is suitable
                    if best_index != -1:

                        # add the identified measurement point to the selected point list
                        parameter_values = fitting_measurements[best_index].as_tuple()
                        cord = Coordinate(parameter_values)
                        #selected_points_gpr.append(cord)
                        
                        # only add coordinate to selected points list if not already in there (because of reps)
                        if cord not in selected_points_gpr:
                            selected_points_gpr.append(cord)
                        
                        # add the new point to the gpr and call fit()
                        gaussian_process = add_measurement_to_gpr(gaussian_process, 
                                cord, 
                                measurements_gpr,
                                callpath, 
                                metric,
                                normalization_factors,
                                experiment_gpr_base.parameters)
                        
                        new_value = 0
                        
                        # remove the identified measurement point from the remaining point list
                        try:
                            # only pop cord when there are no values left in the measurement
                            
                            # if that's not the case pop the value from the measurement of the cord
                            measurement = None
                            cord_id = None
                            for i in range(len(measurements_gpr[(Callpath("main"), Metric("runtime"))])):
                                if measurements_gpr[(Callpath("main"), Metric("runtime"))][i].coordinate == cord:
                                    cord_id = i
                                    x = measurements_gpr[(Callpath("main"), Metric("runtime"))][i].values
                                    if len(x) > 0:
                                        new_value = x[0]
                                        x = np.delete(x, 0)
                                        measurements_gpr[(Callpath("main"), Metric("runtime"))][i].values = x
                                    break
                            
                            # pop value from cord in remaining points list that has been selected as best next point
                            remaining_points_gpr[cord].pop(0)
                            
                            # pop cord from remaining points when no value left anymore
                            if len(measurements_gpr[(Callpath("main"), Metric("runtime"))][cord_id].values) == 0:
                                remaining_points_gpr.pop(cord)
                            
                        except KeyError:
                            pass

                        # update the number of additional points used
                        add_points_gpr += 1

                        # add this point to the gpr experiment
                        #experiment_gpr_base = create_experiment2(selected_points_gpr, experiment_gpr_base, len(experiment_gpr_base.parameters), parameters, 0, 0)
                        experiment_gpr_base = self.create_experiment(cord, experiment_gpr_base, new_value)

                    # if there are no suitable measurement points found
                    # break the while True loop
                    else:
                        break
                
        # cost used of the gpr strategy
        current_cost = calculate_selected_point_cost2(selected_points_gpr, experiment_gpr_base, 0, 0)
        #current_cost = self.calculate_selected_point_cost(experiment_gpr_base)
        percentage_cost_gpr = current_cost / (total_cost / 100)
        if percentage_cost_gpr >= 99.9:
            percentage_cost_gpr = 100
        #print("percentage_cost_gpr:",percentage_cost_gpr)
        
        # additionally used data points (exceeding the base requirement of the sparse modeler)
        add_points_gpr_container.append(add_points_gpr)
        
        # create model using point selection of gpr strategy
        model_gpr, _ = self.get_extrap_model(experiment_gpr_base)
        #print("Model GPR:",model_gpr)

        # set the measurement point values for the evaluation of the prediction
        if self.nr_parameters == 2:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
        elif self.nr_parameters == 3:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
            c = self.parameter_values_c_val[0]
        elif self.nr_parameters == 4:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
            c = self.parameter_values_c_val[0]
            d = self.parameter_values_d_val[0]
        else:
            return 1

        prediction_gpr = eval(model_gpr)
        #print("prediction_gpr:",prediction_gpr)

        # get the percentage error for the gpr strategy
        if percentage_cost_gpr <= self.budget:
            error_gpr = abs(self.percentage_error(actual, prediction_gpr))
        else:
            error_gpr = 100
        #print("error_gpr:",error_gpr)

        # increment accuracy bucket for gpr strategy
        acurracy_bucket_counter_gpr = self.increment_accuracy_bucket(acurracy_bucket_counter_gpr, error_gpr)

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
            kernel=kernel, alpha=0.75**2, n_restarts_optimizer=20
        )

        # add additional measurement points until break criteria is met
        add_points_hybrid = 0
        budget_core_hours = self.budget * (total_cost / 100)
        
        if self.grid_search == 1 or self.grid_search == 4:
            add_points_hybrid = len(selected_points) * self.nr_repetitions
            remaining_points_hybrid = copy.deepcopy(remaining_points)
            # entails all measurement points and their values
            measurements_hybrid = copy.deepcopy(experiment.measurements)
        elif self.grid_search == 2 or self.grid_search == 3:
            add_points_hybrid = len(selected_points) * self.base_values
            remaining_points_hybrid = copy.deepcopy(remaining_points_min)
        selected_points_hybrid = copy.deepcopy(selected_points)
        
        #print("DEBUG add_points_hybrid:",add_points_hybrid)

        # add all of the selected measurement points to the gaussian process
        # as training data and train it for these points
        gaussian_process_hybrid = add_measurements_to_gpr(gaussian_process_hybrid, 
                        selected_points_hybrid, 
                        measurements_hybrid,
                        callpath, 
                        metric,
                        normalization_factors,
                        experiment.parameters, eval_point)

        # create base model for gpr hybrid
        if self.grid_search == 2 or self.grid_search == 3:
            experiment_hybrid_base = self.create_experiment_base(selected_points_hybrid, experiment, len(experiment.parameters), parameters, 0, 0, self.base_values)
        else:
            experiment_hybrid_base = create_experiment2(selected_points_hybrid, experiment, len(experiment.parameters), parameters, 0, 0)

        if self.mode == "budget":
            if self.newonly == False:

                while True:
                    # identify all possible next points that would 
                    # still fit into the modeling budget in core hours
                    fitting_measurements = []
                    for key, value in remaining_points_hybrid.items():

                        #current_cost = calculate_selected_point_cost2(selected_points_hybrid, experiment, 0, 0)
                        current_cost = self.calculate_selected_point_cost(experiment_hybrid_base)
                        
                        #new_cost = current_cost + np.sum(value)
                        new_cost = current_cost + value[0]
                        cost_percent = new_cost / (total_cost / 100)
                        
                        #if new_cost > budget_core_hours:
                        #    print("new_cost <= budget_core_hours:", new_cost, budget_core_hours)
                        #if cost_percent > 100:
                        #    print("cost percent <= budget percent:", cost_percent, self.budget)
                        # to make sure no mistakes occur here
                        # sometimes the numbers do not perfectly add up to the target budget
                        # but to 100.00001
                        # this is the fix for this case
                        cost_percent = float("{0:.3f}".format(cost_percent))
                        if cost_percent > 100.0:
                            cost_percent = 100.0

                        if cost_percent <= self.budget:
                            fitting_measurements.append(key)

                    #print("fitting_measurements:",fitting_measurements)

                    # determine the switching point between gpr and hybrid strategy
                    swtiching_point = 0
                    if len(experiment.parameters) == 2:
                        if self.grid_search == 1 or self.grid_search == 4:
                            swtiching_point = self.nr_repetitions * min_points + self.hybrid_switch
                        elif self.grid_search == 2 or self.grid_search == 3:
                            swtiching_point = self.base_values * min_points + self.hybrid_switch
                    elif len(experiment.parameters) == 3:
                        if self.grid_search == 1 or self.grid_search == 4:
                            swtiching_point = self.nr_repetitions * min_points + self.hybrid_switch
                        elif self.grid_search == 2 or self.grid_search == 3:
                            swtiching_point = self.base_values * min_points + self.hybrid_switch
                    elif len(experiment.parameters) == 4:
                        if self.grid_search == 1 or self.grid_search == 4:
                            swtiching_point = self.nr_repetitions * min_points + self.hybrid_switch
                        elif self.grid_search == 2 or self.grid_search == 3:
                            swtiching_point = self.base_values * min_points + self.hybrid_switch
                    else:
                        if self.grid_search == 1 or self.grid_search == 4:
                            swtiching_point = self.nr_repetitions * min_points + self.hybrid_switch
                        elif self.grid_search == 2 or self.grid_search == 3:
                            swtiching_point = self.base_values * min_points + self.hybrid_switch

                    best_index = -1
                    
                    #print("DEBUG: add_points_hybrid, swtiching_point", add_points_hybrid, swtiching_point)
                    
                    # find the next best additional measurement point using the gpr strategy
                    if add_points_hybrid > swtiching_point:
                        #print("Using gpr strategy")
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
                            #term_1 = math.pow(np.sum(remaining_points_hybrid[fitting_measurements[i]]), 2)
                            term_1 = math.pow(remaining_points_hybrid[fitting_measurements[i]][0], 2)
                            # predict variance of input vector x with the gaussian process
                            x = [x]
                            _, y_cov = gaussian_process_hybrid.predict(x, return_cov=True)
                            y_cov = abs(y_cov)
                            # term_2 is gp_cov(t,t)^2
                            term_2 = math.pow(y_cov, 2)
                            # rated is h(t)
                            
                            if self.grid_search == 3 or self.grid_search == 4:
                                rep = 1
                                for j in range(len(measurements_hybrid[(Callpath("main"), Metric("runtime"))])):
                                    if measurements_hybrid[(Callpath("main"), Metric("runtime"))][j].coordinate == fitting_measurements[i]:
                                        rep = (self.nr_repetitions - len(measurements_hybrid[(Callpath("main"), Metric("runtime"))][j].values)) + 1
                                        break
                                rep_func = 2**((1/2)*rep-(1/2))
                                noise_func = -math.tanh((1/4)*mean_noise-2.5)
                                cost_multiplier = rep_func + noise_func
                                rated = (term_1 * cost_multiplier) / term_2
                            else:
                                rated = term_1 / term_2

                            if rated <= best_rated:
                                best_rated = rated
                                best_index = i 

                    # find the next best additional measurement point using the generic strategy
                    else:
                        #print("Using generic strategy")
                        lowest_cost = sys.float_info.max
                        for i in range(len(fitting_measurements)):
                            
                            # get the cost of the measurement point
                            #cost = np.sum(remaining_points_hybrid[fitting_measurements[i]])
                            cost = remaining_points_hybrid[fitting_measurements[i]][0]

                            if cost < lowest_cost:
                                lowest_cost = cost
                                best_index = i

                    # if there has been a point found that is suitable
                    if best_index != -1:

                        # add the identified measurement point to the experiment, selected point list
                        parameter_values = fitting_measurements[best_index].as_tuple()
                        cord = Coordinate(parameter_values)
                        #selected_points_hybrid.append(cord)
                        
                        # only add coordinate to selected points list if not already in there (because of reps)
                        if cord not in selected_points_hybrid:
                            selected_points_hybrid.append(cord)
                        
                        # add the new point to the gpr and call fit()
                        gaussian_process_hybrid = add_measurement_to_gpr(gaussian_process_hybrid, 
                                cord, 
                                measurements_hybrid, 
                                callpath, 
                                metric,
                                normalization_factors,
                                experiment_hybrid_base.parameters)
                        
                        # remove the identified measurement point from the remaining point list
                        #try:
                        #    remaining_points_hybrid.pop(cord)
                        #except KeyError:
                        #    pass
                        
                        new_value = 0

                        # remove the identified measurement point from the remaining point list
                        try:
                            # only pop cord when there are no values left in the measurement
                            
                            # if that's not the case pop the value from the measurement of the cord
                            measurement = None
                            cord_id = None
                            for i in range(len(measurements_hybrid[(Callpath("main"), Metric("runtime"))])):
                                if measurements_hybrid[(Callpath("main"), Metric("runtime"))][i].coordinate == cord:
                                    cord_id = i
                                    x = measurements_hybrid[(Callpath("main"), Metric("runtime"))][i].values
                                    if len(x) > 0:
                                        new_value = x[0]
                                        x = np.delete(x, 0)
                                        measurements_hybrid[(Callpath("main"), Metric("runtime"))][i].values = x
                                    break
                                
                            # pop value from cord in remaining points list that has been selected as best next point
                            remaining_points_hybrid[cord].pop(0)
                            
                            # pop cord from remaining points when no value left anymore
                            if len(measurements_hybrid[(Callpath("main"), Metric("runtime"))][cord_id].values) == 0:
                                remaining_points_hybrid.pop(cord)
                            
                        except KeyError:
                            pass


                        # update the number of additional points used
                        add_points_hybrid += 1

                        # add this point to the hybrid experiment
                        #experiment_hybrid_base = create_experiment2(selected_points_hybrid, experiment, len(experiment.parameters), parameters, 0, 0)
                        experiment_hybrid_base = self.create_experiment(cord, experiment_hybrid_base, new_value)


                    # if there are no suitable measurement points found
                    # break the while True loop
                    else:
                        break

        elif self.mode == "free":
            pass

        else:
            return 1

        # cost used of the gpr strategy
        #current_cost = calculate_selected_point_cost2(selected_points_hybrid, experiment, 0, 0)
        current_cost = self.calculate_selected_point_cost(experiment_hybrid_base)
        current_cost_percent = current_cost / (total_cost / 100)

        percentage_cost_hybrid = current_cost_percent
        if percentage_cost_hybrid >= 99.9:
            percentage_cost_hybrid = 100
        #print("percentage_cost_hybrid:",percentage_cost_hybrid)

        # additionally used data points (exceeding the base requirement of the sparse modeler)
        add_points_hybrid_container.append(add_points_hybrid)
        #print("DEBUG add_points_hybrid:",add_points_hybrid)

        # create model using point selection of hybrid strategy
        model_hybrid, _ = self.get_extrap_model(experiment_hybrid_base)
        
        # set the measurement point values for the evaluation of the prediction
        if self.nr_parameters == 2:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
        elif self.nr_parameters == 3:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
            c = self.parameter_values_c_val[0]
        elif self.nr_parameters == 4:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
            c = self.parameter_values_c_val[0]
            d = self.parameter_values_d_val[0]
        else:
            return 1

        prediction_hybrid = eval(model_hybrid)
        #print("prediction_hybrid:",prediction_hybrid)

        # get the percentage error for the hybrid strategy
        if percentage_cost_hybrid <= self.budget:
            error_hybrid = abs(self.percentage_error(actual, prediction_hybrid))
        else:
            error_hybrid = 100
        #print("error_hybrid:",error_hybrid)
        
        # increment accuracy bucket for hybrid strategy
        acurracy_bucket_counter_hybrid = self.increment_accuracy_bucket(acurracy_bucket_counter_hybrid, error_hybrid)



        ############
        ## Random ##
        ############

        remaining_points_random = copy.deepcopy(remaining_points)
        selected_points_random = copy.deepcopy(selected_points)
        
        # create base model for generic
        #if self.grid_search == 2 or self.grid_search == 3:
        #    experiment_generic_base = self.create_experiment_base(selected_points_generic, experiment, len(experiment.parameters), parameters, 0, 0, self.base_values)
        #else:
        #   experiment_generic_base = create_experiment2(selected_points_generic, experiment, len(experiment.parameters), parameters, 0, 0)
        
        #for x in experiment_generic_base.measurements[(Callpath("main"), Metric("runtime"))]:
        #    print(x.coordinate, x.values)

        # create first model
        experiment_random_base = create_experiment2(selected_points_random, experiment, len(experiment.parameters), parameters, 0, 0)
        
        _, models = self.get_extrap_model(experiment_random_base)
        hypothesis = None
        for model in models.values():
            hypothesis = model.hypothesis

        # calculate selected point cost
        current_cost = calculate_selected_point_cost2(selected_points_random, experiment, 0, 0)
        current_cost_percent = current_cost / (total_cost / 100)
        
        if self.mode == "budget":

            if current_cost_percent <= self.budget:
                while True:
                    # find another point for selection
                    remaining_points_new, selected_coord_list_new, new_point = add_additional_point_random(remaining_points_random, selected_points_random)

                    # calculate selected point cost
                    current_cost = calculate_selected_point_cost2(selected_coord_list_new, experiment, 0, 0)
                    current_cost_percent = current_cost / (total_cost / 100)

                    # current cost exceeds budget so break the loop
                    #print("current_cost_percent > self.budget", current_cost_percent, self.budget)
                    # to make sure no mistakes occur here
                    # sometimes the numbers do not perfectly add up to the target budget
                    # but to 100.00001
                    # this is the fix for this case
                    current_cost_percent = float("{0:.2f}".format(current_cost_percent))
                    #print("current_cost_percent:",current_cost_percent)

                    if current_cost_percent > self.budget:
                        break

                    # add the new found point
                    else:

                        # update the map with the numbers of already selected points
                        #point_map_generic[new_point] = selection_point_counter
                        selection_point_counter += 1
                        #print("point:",point)
                        #print("point_map_generic:",point_map_generic)

                        # increment counter value, because a new measurement point was added
                        #added_points_generic += 1
                        added_points_random += self.nr_repetitions

                        # create new model
                        experiment_random_base = create_experiment2(selected_coord_list_new, experiment, len(experiment.parameters), parameters, 0, 0)

                        selected_points_random = selected_coord_list_new
                        remaining_points_random = remaining_points_new

                    # if there are no points remaining that can be selected break the loop
                    if len(remaining_points_random) == 0:
                        break

            else:
                pass

        elif self.mode == "free":
            pass

        else:
            return 1

        # calculate selected point cost
        selected_cost = calculate_selected_point_cost2(selected_points_random, experiment, 0, 0)
        
        # calculate the percentage of cost of the selected points compared to the total cost of the full matrix
        percentage_cost_random = selected_cost / (total_cost / 100)
        if percentage_cost_random >= 99.9:
            percentage_cost_random = 100
        #print("percentage_cost_random:",percentage_cost_random)
        percentage_cost_random_container.append(percentage_cost_random)

        # calculate number of additionally used data points (exceeding the base requirement of the sparse modeler)
        #add_points_random = len(selected_points_random) - min_points
        #if percentage_cost_random > self.budget:
        #    added_points_random = math.nan
        add_points_random_container.append(added_points_random)
        add_points_random = added_points_random
        #if percentage_cost_random < 100:
        #    print("add_points_random:",add_points_random)
        
        # create model using point selection of generic strategy
        model_random, _ = self.get_extrap_model(experiment_random_base)
        
        #for x in experiment_random_base.measurements[(Callpath("main"),Metric("runtime"))]:
        #    print(x, x.values)
        #print("Model generic:",model_random)

        # create model using full matrix of points
        model_full, _ = self.get_extrap_model(experiment)
        #print("model_full:",model_full)

        # set the measurement point values for the evaluation of the prediction
        if self.nr_parameters == 2:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
        elif self.nr_parameters == 3:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
            c = self.parameter_values_c_val[0]
        elif self.nr_parameters == 4:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
            c = self.parameter_values_c_val[0]
            d = self.parameter_values_d_val[0]
        else:
            return 1

        # evaluate model accuracy against the first point in each direction of the parameter set for each parameter
        prediction_full = eval(model_full)
        #print("prediction_full:",prediction_full)
        prediction_random = eval(model_random)
        #print("prediction_generic:",prediction_generic)

        #basline_function = function_dict[i].function
        actual = eval(basline_function)
        #print("actual:",actual)

        # get the percentage error for the full matrix of points
        error_full = abs(self.percentage_error(actual, prediction_full))
        #print("error_full:",error_full)

        # get the percentage error for the generic strategy
        if percentage_cost_random <= self.budget:
            error_random = abs(self.percentage_error(actual, prediction_random))
        else:
            error_random = 100
        #print("error_generic:",error_generic)

        # increment accuracy bucket for full matrix of points
        acurracy_bucket_counter_full = self.increment_accuracy_bucket(acurracy_bucket_counter_full, error_full)

        # increment accuracy bucket for generic strategy
        acurracy_bucket_counter_random = self.increment_accuracy_bucket(acurracy_bucket_counter_random, error_random)



        ############
        ## Grid ##
        ############

        remaining_points_grid = copy.deepcopy(remaining_points)
        selected_points_grid = copy.deepcopy(selected_points)
        
        # create base model for generic
        #if self.grid_search == 2 or self.grid_search == 3:
        #    experiment_generic_base = self.create_experiment_base(selected_points_generic, experiment, len(experiment.parameters), parameters, 0, 0, self.base_values)
        #else:
        #   experiment_generic_base = create_experiment2(selected_points_generic, experiment, len(experiment.parameters), parameters, 0, 0)
        
        #for x in experiment_generic_base.measurements[(Callpath("main"), Metric("runtime"))]:
        #    print(x.coordinate, x.values)

        # create first model
        experiment_grid_base = create_experiment2(selected_points_grid, experiment, len(experiment.parameters), parameters, 0, 0)
        
        _, models = self.get_extrap_model(experiment_grid_base)
        hypothesis = None
        for model in models.values():
            hypothesis = model.hypothesis

        # calculate selected point cost
        current_cost = calculate_selected_point_cost2(selected_points_grid, experiment, 0, 0)
        current_cost_percent = current_cost / (total_cost / 100)
        
        if self.mode == "budget":

            if current_cost_percent <= self.budget:
                while True:
                    # find another point for selection
                    remaining_points_new, selected_coord_list_new, new_point = add_additional_point_grid(remaining_points_grid, selected_points_grid)

                    # calculate selected point cost
                    current_cost = calculate_selected_point_cost2(selected_coord_list_new, experiment, 0, 0)
                    current_cost_percent = current_cost / (total_cost / 100)

                    # current cost exceeds budget so break the loop
                    #print("current_cost_percent > self.budget", current_cost_percent, self.budget)
                    # to make sure no mistakes occur here
                    # sometimes the numbers do not perfectly add up to the target budget
                    # but to 100.00001
                    # this is the fix for this case
                    current_cost_percent = float("{0:.2f}".format(current_cost_percent))
                    #print("current_cost_percent:",current_cost_percent)

                    if current_cost_percent > self.budget:
                        break

                    # add the new found point
                    else:

                        # update the map with the numbers of already selected points
                        #point_map_generic[new_point] = selection_point_counter
                        selection_point_counter += 1
                        #print("point:",point)
                        #print("point_map_generic:",point_map_generic)

                        # increment counter value, because a new measurement point was added
                        #added_points_generic += 1
                        added_points_grid += self.nr_repetitions

                        # create new model
                        experiment_grid_base = create_experiment2(selected_coord_list_new, experiment, len(experiment.parameters), parameters, 0, 0)

                        selected_points_grid = selected_coord_list_new
                        remaining_points_grid = remaining_points_new

                    # if there are no points remaining that can be selected break the loop
                    if len(remaining_points_grid) == 0:
                        break

            else:
                pass

        elif self.mode == "free":
            pass

        else:
            return 1

        # calculate selected point cost
        selected_cost = calculate_selected_point_cost2(selected_points_grid, experiment, 0, 0)
        
        # calculate the percentage of cost of the selected points compared to the total cost of the full matrix
        percentage_cost_grid = selected_cost / (total_cost / 100)
        if percentage_cost_grid >= 99.9:
            percentage_cost_grid = 100
        #print("percentage_cost_grid:",percentage_cost_grid)
        percentage_cost_grid_container.append(percentage_cost_grid)

        # calculate number of additionally used data points (exceeding the base requirement of the sparse modeler)
        #add_points_grid = len(selected_points_grid) - min_points
        #if percentage_cost_grid > self.budget:
        #    added_points_grid = math.nan
        add_points_grid_container.append(added_points_grid)
        add_points_grid = added_points_grid
        #if percentage_cost_grid < 100:
        #    print("add_points_grid:",add_points_grid)
        
        # create model using point selection of generic strategy
        model_grid, _ = self.get_extrap_model(experiment_grid_base)
        
        #for x in experiment_grid_base.measurements[(Callpath("main"),Metric("runtime"))]:
        #    print(x, x.values)
        #print("Model generic:",model_grid)

        # create model using full matrix of points
        model_full, _ = self.get_extrap_model(experiment)
        #print("model_full:",model_full)

        # set the measurement point values for the evaluation of the prediction
        if self.nr_parameters == 2:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
        elif self.nr_parameters == 3:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
            c = self.parameter_values_c_val[0]
        elif self.nr_parameters == 4:
            a = self.parameter_values_a_val[0]
            b = self.parameter_values_b_val[0]
            c = self.parameter_values_c_val[0]
            d = self.parameter_values_d_val[0]
        else:
            return 1

        # evaluate model accuracy against the first point in each direction of the parameter set for each parameter
        prediction_full = eval(model_full)
        #print("prediction_full:",prediction_full)
        prediction_grid = eval(model_grid)
        #print("prediction_generic:",prediction_generic)

        #basline_function = function_dict[i].function
        actual = eval(basline_function)
        #print("actual:",actual)

        # get the percentage error for the full matrix of points
        error_full = abs(self.percentage_error(actual, prediction_full))
        #print("error_full:",error_full)

        # get the percentage error for the generic strategy
        if percentage_cost_grid <= self.budget:
            error_grid = abs(self.percentage_error(actual, prediction_grid))
        else:
            error_grid = 100
        #print("error_generic:",error_generic)

        # increment accuracy bucket for full matrix of points
        acurracy_bucket_counter_full = self.increment_accuracy_bucket(acurracy_bucket_counter_full, error_full)

        # increment accuracy bucket for generic strategy
        acurracy_bucket_counter_grid = self.increment_accuracy_bucket(acurracy_bucket_counter_grid, error_grid)




        ###############
        ### results ###
        ###############

        # save the results of this worker to return them to the main process
        result_container["acurracy_bucket_counter_full"] = acurracy_bucket_counter_full

        result_container["add_points_generic"] = add_points_generic
        #print("add_points_generic:",add_points_generic)
        result_container["percentage_cost_generic"] = percentage_cost_generic
        #print("DEBUG percentage_cost_generic:",percentage_cost_generic)
        result_container["acurracy_bucket_counter_generic"] = acurracy_bucket_counter_generic

        result_container["add_points_gpr"] = add_points_gpr
        result_container["percentage_cost_gpr"] = percentage_cost_gpr
        #print("DEBUG percentage_cost_gpr:",percentage_cost_gpr)
        result_container["acurracy_bucket_counter_gpr"] = acurracy_bucket_counter_gpr

        result_container["add_points_hybrid"] = add_points_hybrid
        result_container["percentage_cost_hybrid"] = percentage_cost_hybrid
        result_container["acurracy_bucket_counter_hybrid"] = acurracy_bucket_counter_hybrid

        result_container["add_points_random"] = add_points_random
        result_container["percentage_cost_random"] = percentage_cost_random
        result_container["acurracy_bucket_counter_random"] = acurracy_bucket_counter_random

        result_container["add_points_grid"] = add_points_grid
        result_container["percentage_cost_grid"] = percentage_cost_grid
        result_container["acurracy_bucket_counter_grid"] = acurracy_bucket_counter_grid

        result_container["base_point_cost"] = base_point_cost

        result_container["len_coordinates"] = len(experiment.coordinates)

        result_container["point_map_generic"] = point_map_generic
        result_container["copy_point_map_generic"] = copy_point_map_generic
        
        if percentage_cost_generic <= self.budget:
            result_container["generic_possible"] = True
        else:
            result_container["generic_possible"] = False
        
        if percentage_cost_gpr <= self.budget:
            result_container["gpr_possible"] = True
        else:
            result_container["gpr_possible"] = False
            
        if percentage_cost_hybrid <= self.budget:
            result_container["hybrid_possible"] = True
        else:
            result_container["hybrid_possible"] = False
        
        if percentage_cost_random <= self.budget:
            result_container["random_possible"] = True
        else:
            result_container["random_possible"] = False

        if percentage_cost_grid <= self.budget:
            result_container["grid_possible"] = True
        else:
            result_container["grid_possible"] = False
        
        shared_dict[counter] = result_container

    def run(self):

        import pickle
        #function_dict = self.generate_synthetic_functions()
        #file = open("functions", "wb")
        #pickle.dump(function_dict, file)
        #file.close()

        file = open("functions", "rb")
        function_dict = pickle.load(file)
        file.close()
        
        #for key, value in function_dict.items():
        #    print(key, value.function)
        #return 0

        # set the minimum number of points required for modeling with the sparse modeler
        min_points = 0
        if self.nr_parameters == 1:
            min_points = 5
        elif self.nr_parameters == 2:
            min_points = 9
        elif self.nr_parameters == 3:
            min_points = 13
        elif self.nr_parameters == 4:
            min_points = 17
        else:
            min_points = 5
        
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
        copy_point_map_generic = None

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

        # random
        acurracy_bucket_counter_random = {}
        acurracy_bucket_counter_random["rest"] = 0
        acurracy_bucket_counter_random["5"] = 0
        acurracy_bucket_counter_random["10"] = 0
        acurracy_bucket_counter_random["15"] = 0
        acurracy_bucket_counter_random["20"] = 0

        percentage_cost_random_container = []
        add_points_random_container = []

        # grid
        acurracy_bucket_counter_grid = {}
        acurracy_bucket_counter_grid["rest"] = 0
        acurracy_bucket_counter_grid["5"] = 0
        acurracy_bucket_counter_grid["10"] = 0
        acurracy_bucket_counter_grid["15"] = 0
        acurracy_bucket_counter_grid["20"] = 0

        percentage_cost_grid_container = []
        add_points_grid_container = []

        base_point_costs = []
        
        gpr_functions_modeled = []
        generic_functions_modeled = []
        hybrid_functions_modeled = []
        random_functions_modeled = []
        grid_functions_modeled = []
        
        len_coordinates = None
       
        # parallelize reading all measurement_files in one folder
        manager = Manager()
        shared_dict = manager.dict()
        cpu_count = mp.cpu_count()
        cpu_count -= 2
        if self.nr_functions < cpu_count:
            cpu_count = self.nr_functions

        inputs = []
        for i in range(self.nr_functions):
            inputs.append([i, shared_dict, function_dict[i].function])

        with Pool(cpu_count) as pool:
            _ = list(tqdm(pool.imap(self.simulate, inputs), total=self.nr_functions))

        result_dict = copy.deepcopy(shared_dict)

        # analyze results
        for i in range(len(result_dict)):
            
            add_points_generic_container.append(result_dict[i]["add_points_generic"])
            percentage_cost_generic_container.append(result_dict[i]["percentage_cost_generic"])

            add_points_gpr_container.append(result_dict[i]["add_points_gpr"])
            percentage_cost_gpr_container.append(result_dict[i]["percentage_cost_gpr"])

            add_points_hybrid_container.append(result_dict[i]["add_points_hybrid"])
            percentage_cost_hybrid_container.append(result_dict[i]["percentage_cost_hybrid"])

            add_points_random_container.append(result_dict[i]["add_points_random"])
            percentage_cost_random_container.append(result_dict[i]["percentage_cost_random"])

            add_points_grid_container.append(result_dict[i]["add_points_grid"])
            percentage_cost_grid_container.append(result_dict[i]["percentage_cost_grid"])

            base_point_costs.append(result_dict[i]["base_point_cost"])
            
            generic_functions_modeled.append(result_dict[i]["generic_possible"])
            gpr_functions_modeled.append(result_dict[i]["gpr_possible"])
            hybrid_functions_modeled.append(result_dict[i]["hybrid_possible"])
            random_functions_modeled.append(result_dict[i]["random_possible"])
            grid_functions_modeled.append(result_dict[i]["grid_possible"])

            if i == 0:
                len_coordinates = result_dict[i]["len_coordinates"]
                copy_point_map_generic = result_dict[i]["copy_point_map_generic"]
            
            b_full = result_dict[i]["acurracy_bucket_counter_full"]
            b_generic = result_dict[i]["acurracy_bucket_counter_generic"]
            b_gpr = result_dict[i]["acurracy_bucket_counter_gpr"]
            b_hybrid = result_dict[i]["acurracy_bucket_counter_hybrid"]
            b_random = result_dict[i]["acurracy_bucket_counter_random"]
            b_grid = result_dict[i]["acurracy_bucket_counter_grid"]

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

        #print("acurracy_bucket_counter_full:",acurracy_bucket_counter_full)
        #print("acurracy_bucket_counter_generic:",acurracy_bucket_counter_generic)
        #print("acurracy_bucket_counter_gpr:",acurracy_bucket_counter_gpr)
        #print("acurracy_bucket_counter_hybrid:",acurracy_bucket_counter_hybrid)

        # analyze results
        selected_copy_point_map_generic = copy.deepcopy(copy_point_map_generic)
        for i in range(len(result_dict)):
            point_map_generic = result_dict[i]["point_map_generic"]

            for key, value in point_map_generic.items():
                if value != -1:
                    copy_point_map_generic[key] += value
                    selected_copy_point_map_generic[key] += 1
        #print("selected_copy_point_map_generic:",selected_copy_point_map_generic)
        for key, value in copy_point_map_generic.items():
            if value != -1:
                if selected_copy_point_map_generic[key] != 0:
                    value = value / selected_copy_point_map_generic[key]
                    #print(value)
                    #value = '{0:.0f}'.format(value)
                    #print(value)
                    copy_point_map_generic[key] = value
        #print("copy_point_map_generic:",copy_point_map_generic)
        point_map_generic = {}
        for key, value in copy_point_map_generic.items():
            point_map_generic[str(key)] = value

        #TODO: do update this point map
        #print("point_map_generic:",point_map_generic)

        json_out = {}

        # calculate the percentages for each accuracy bucket
        percentage_bucket_counter_full = self.calculate_percentage_of_buckets(acurracy_bucket_counter_full)
        print("percentage_bucket_counter_full:",percentage_bucket_counter_full)
        print("")
        json_out["percentage_bucket_counter_full"] = percentage_bucket_counter_full
        
        ###############
        ### Generic ###
        ###############
        
        percentage_bucket_counter_generic = self.calculate_percentage_of_buckets(acurracy_bucket_counter_generic)
        print("percentage_bucket_counter_generic:",percentage_bucket_counter_generic)
        json_out["percentage_bucket_counter_generic"] = percentage_bucket_counter_generic
        
        #print("percentage_cost_generic_container:",percentage_cost_generic_container)
        percentage_cost_generic_container_filtered = []
        add_points_generic_container_filtered = []
        for i in range(len(percentage_cost_generic_container)):
            if percentage_cost_generic_container[i] <= self.budget:
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
        
        percentage_bucket_counter_gpr = self.calculate_percentage_of_buckets(acurracy_bucket_counter_gpr)
        print("percentage_bucket_counter_gpr:",percentage_bucket_counter_gpr)
        json_out["percentage_bucket_counter_gpr"] = percentage_bucket_counter_gpr

        #print("percentage_cost_gpr_container:",percentage_cost_gpr_container)
        percentage_cost_gpr_container_filtered = []
        add_points_gpr_container_filtered = []
        for i in range(len(percentage_cost_gpr_container)):
            if percentage_cost_gpr_container[i] <= self.budget:
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
        
        percentage_bucket_counter_hybrid = self.calculate_percentage_of_buckets(acurracy_bucket_counter_hybrid)
        print("percentage_bucket_counter_hybrid:",percentage_bucket_counter_hybrid)
        json_out["percentage_bucket_counter_hybrid"] = percentage_bucket_counter_hybrid

        percentage_cost_hybrid_container_filtered = []
        add_points_hybrid_container_filtered = []
        for i in range(len(percentage_cost_hybrid_container)):
            if percentage_cost_hybrid_container[i] <= self.budget:
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
        
        json_out["nr_func_modeled_hybrid"] = nr_func_modeled_hybrid

        ##############
        ### Random ###
        ##############
        
        percentage_bucket_counter_random = self.calculate_percentage_of_buckets(acurracy_bucket_counter_random)
        print("percentage_bucket_counter_random:",percentage_bucket_counter_random)
        json_out["percentage_bucket_counter_random"] = percentage_bucket_counter_random

        percentage_cost_random_container_filtered = []
        add_points_random_container_filtered = []
        for i in range(len(percentage_cost_random_container)):
            if percentage_cost_random_container[i] <= self.budget:
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

        ############
        ### Grid ###
        ############
        
        percentage_bucket_counter_grid = self.calculate_percentage_of_buckets(acurracy_bucket_counter_grid)
        print("percentage_bucket_counter_grid:",percentage_bucket_counter_grid)
        json_out["percentage_bucket_counter_grid"] = percentage_bucket_counter_grid

        percentage_cost_grid_container_filtered = []
        add_points_grid_container_filtered = []
        for i in range(len(percentage_cost_grid_container)):
            if percentage_cost_grid_container[i] <= self.budget:
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
        
        json_out["nr_func_modeled_grid"] = nr_func_modeled_grid

        ###################
        ### Base Points ###
        ###################

        base_point_costs_filtered = []
        for x in base_point_costs:
            if x <= self.budget:
                base_point_costs_filtered.append(x)
        #mean_base_point_cost = np.nanmean(base_point_costs)
        mean_base_point_cost = np.nanmean(base_point_costs_filtered)
        print("")
        print("mean_base_point_cost:",mean_base_point_cost)

        json_out["point_map_generic"] = point_map_generic

        ####################
        # Plot the results #
        ####################

        # plot the results of the model accuracy analysis
        if self.plot == True and self.newonly == False:
            plot_model_accuracy(percentage_bucket_counter_full, percentage_bucket_counter_generic, percentage_bucket_counter_gpr, percentage_bucket_counter_hybrid, self.budget)
        
        used_costs = {
            "Base points": np.array([mean_base_point_cost, mean_base_point_cost, mean_base_point_cost, mean_base_point_cost]),
            "Additional points": np.array([100-mean_base_point_cost, mean_budget_generic-mean_base_point_cost, mean_budget_gpr-mean_base_point_cost, mean_budget_hybrid-mean_base_point_cost]),
        }
        json_out["base_point_cost"] = mean_base_point_cost
        json_out["min_points"] = min_points
        json_out["budget"] = self.budget

        # plot the analysis result for the costs and budgets
        if self.plot == True and self.newonly == False:
            plot_costs(used_costs, mean_base_point_cost, self.budget)

        add_points = {
            "Base points": np.array([min_points, min_points, min_points, min_points]),
            "Additional points": np.array([len_coordinates*self.nr_repetitions, mean_add_points_generic, mean_add_points_gpr, mean_add_points_hybrid]),
        }

        # plot the analysis result for the additional measurement point numbers
        if self.plot == True and self.newonly == False:
            plot_measurement_point_number(add_points, min_points, self.budget)

        ##############################
        # Write results to json file #
        ##############################

        # write results to file
        json_object = json.dumps(json_out, indent=4)

        budget_string = "{:0.1f}".format(self.budget)
        with open("result.budget."+str(budget_string)+".json", "w") as outfile:
            outfile.write(json_object)
        
