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
from generic_strategy import add_additional_point_generic
from case_study import calculate_selected_point_cost


class SyntheticBenchmark():

    def __init__(self, args):
        self.nr_parameters = args.nr_parameters
        self.nr_functions = args.nr_functions
        self.nr_repetitions = args.nr_repetitions
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
        self.parameter_values_a_val = [128]
        self.parameter_values_b_val = [60]
        self.parameter_values_c_val = [6000]
        self.parameter_values_d_val = [20]

    def create_experiment(self, selected_coord_list, experiment):
        # create new experiment with only the selected measurements and points as coordinates and measurements
        experiment_generic = Experiment()
        for j in range(self.nr_parameters):
            experiment_generic.add_parameter(Parameter(self.parameter_placeholders[j]))
        callpath = Callpath("main")
        experiment_generic.add_callpath(callpath)
        metric = Metric("runtime")
        experiment_generic.add_metric(metric)
        for j in range(len(selected_coord_list)):
            coordinate = selected_coord_list[j]
            experiment_generic.add_coordinate(coordinate)

            coordinate_id = -1
            for k in range(len(experiment.coordinates)):
                if coordinate == experiment.coordinates[k]:
                    coordinate_id = k
            measurement_temp = experiment.get_measurement(coordinate_id, 0, 0)
            #print("haha:",measurement_temp.values)

            #value = selected_measurement_values[selected_coord_list[j]] 
            #experiment_generic.add_measurement(Measurement(coordinate, callpath, metric, value))
            experiment_generic.add_measurement(Measurement(coordinate, callpath, metric, measurement_temp.values))
        return experiment_generic

    """def add_additional_point_generic(self, remaining_points, selected_coord_list):
        while True:
            point_costs = {}
            for key, value in remaining_points.items():
                try:
                    min_value = min(value)
                except ValueError:
                    min_value = math.inf
                point_costs[key] = min_value
            try:
                temp = min(point_costs, key=point_costs.get)
            except Exception as e:
                print(e)
                #print("point_costs:",point_costs)
                #print("remaining_points:",remaining_points)
                return remaining_points, selected_coord_list
        
            # check if point was already selected
            # make sure this point was not selected yet
            exists = False
            for k in range(len(selected_coord_list)):
                if temp == selected_coord_list[k]:
                    exists = True
                    break
            # if point was selected already, delete it
            if exists == True:
                try:
                    #remaining_points[temp].remove(point_costs[temp])
                    del remaining_points[temp]
                except ValueError as e:
                    print(e)
                    print("temp:",temp)
                    print("selected_coord_list:",selected_coord_list)
                    print("remaining_points:",remaining_points)
                    return 0
            # if point was not selected yet, break the loop and add this point
            else:
                break

        # if point was not selected yet, use it
        # add the point to the selected list
        selected_coord_list.append(temp)

        # remove this point from the remaining points list
        try:
            #remaining_points[temp].remove(point_costs[temp])
            del remaining_points[temp]
        except ValueError as e:
            print(e)

        return remaining_points, selected_coord_list"""

    def calculate_percentage_of_buckets(self, acurracy_bucket_counter):
        # calculate the percentages for each accuracy bucket
        percentage_bucket_counter = {}
        for key, value in acurracy_bucket_counter.items():
            percentage = (value / self.nr_functions) * 100
            percentage_bucket_counter[key] = percentage
        return percentage_bucket_counter

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
            experiment, modeler=self.args.modeler, use_median=True)

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

    def generate_synthetic_functions(self):
        generator = FunctionGenerator(self.parameter_values_a, self.parameter_values_b, self.parameter_values_c, self.parameter_values_d, nr_parameters=self.nr_parameters)
        
        # parallelize reading all measurement_files in one folder
        manager = Manager()
        shared_dict = manager.dict()
        cpu_count = mp.cpu_count()

        inputs = []
        for i in range(self.nr_functions):
            inputs.append([i, shared_dict])

        with Pool(cpu_count) as pool:
            _ = list(tqdm(pool.imap(generator.generate_function, inputs), total=self.nr_functions))

        function_dict = copy.deepcopy(shared_dict)
        
        return function_dict
    
    #TODO
    def simulate(self, inputs):

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

        acurracy_bucket_counter_gpr = {}
        acurracy_bucket_counter_gpr["rest"] = 0
        acurracy_bucket_counter_gpr["5"] = 0
        acurracy_bucket_counter_gpr["10"] = 0
        acurracy_bucket_counter_gpr["15"] = 0
        acurracy_bucket_counter_gpr["20"] = 0

        acurracy_bucket_counter_hybrid = {}
        acurracy_bucket_counter_hybrid["rest"] = 0
        acurracy_bucket_counter_hybrid["5"] = 0
        acurracy_bucket_counter_hybrid["10"] = 0
        acurracy_bucket_counter_hybrid["15"] = 0
        acurracy_bucket_counter_hybrid["20"] = 0

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

        for j in range(len(self.parameter_values_a)):
            
            function = basline_function
            for k in range(len(self.parameter_values_b)):

                coordinate = Coordinate(self.parameter_values_a[j], self.parameter_values_b[k])
                experiment.add_coordinate(coordinate)
                
                a = self.parameter_values_a[j]
                b = self.parameter_values_b[k]
                result = eval(function)
                values = []
                if coordinate not in cost:
                    cost[coordinate] = []
                for _ in range(5):
                    if random.randint(1, 2) == 1:
                        noise = random.uniform(0, self.noise_percent)
                        result *= ((100-noise)/100)
                    else:
                        noise = random.uniform(0, self.noise_percent)
                        result *= ((100+noise)/100)
                    runtime = result
                    nr_processes = self.parameter_values_a[j]
                    core_hours = runtime * nr_processes
                    total_cost += core_hours
                    cost[coordinate].append(core_hours)
                    values.append(result)
                experiment.add_measurement(Measurement(coordinate, callpath, metric, values))

        #experiments.append(experiment)

        #print("len measurements:",len(experiment.coordinates))

        #container["experiment"] = experiment

        #print("cost:",cost)
        #print("total_cost:",total_cost)

        #container["cost_dict"] = cost
        #container["total_cost"] = total_cost

        # create copy of the cost dict
        remaining_points = copy.deepcopy(cost)

        # dict to store the measurement points values for later use for modeling
        #selected_measurement_values = {}

        # find the cheapest line of 5 points for x
        row_costs = []
        cord_lists = []
        values_list = []
        for k in range(len(self.parameter_values_b)):
            row_cost = 0
            cord_list = []
            values = []
            for j in range(len(self.parameter_values_a)):
                y = self.parameter_values_b[k]
                x = self.parameter_values_a[j]
                temp = cost[Coordinate(self.parameter_values_a[j], self.parameter_values_b[k])]
                temp = min(temp)
                #print("point cost:",temp)
                row_cost += temp
                values.append(temp)
                cord_list.append(Coordinate(self.parameter_values_a[j], self.parameter_values_b[k]))
            row_costs.append(row_cost)
            values_list.append(values)
            #print("row cost:",row_cost)
            cord_lists.append(cord_list)
        #print("row_costs:",row_costs)
        #print(min(row_costs))
        row_id = row_costs.index(min(row_costs))
        #print(row_id)
        cheapest_points_x = cord_lists[row_id]
        # delete all points of this row from remaining point list
        #print("remaining before:",remaining_points)
        values = values_list[row_id]
        #print(values)
        for j in range(len(cheapest_points_x)):
            try:
                remaining_points[cheapest_points_x[j]].remove(values[j])
            except ValueError:
                pass
            """# add measurement value to the list
            coordinate_id = -1
            for k in range(len(experiment.coordinates)):
                if cheapest_points_x[j] == experiment.coordinates[k]:
                    coordinate_id = k
            measurement_temp = experiment.get_measurement(coordinate_id, 0, 0)
            value_id = -1
            for k in range(len(measurement_temp.values)):
                runtime = measurement_temp.values[k]
                nr_processes = cheapest_points_x[j].as_tuple()[0]
                core_hours = runtime * nr_processes
                if core_hours == values[k]:
                    value_id = k
                    break
            #print("measurement_temp:",measurement_temp.values[value_id])
            selected_measurement_values[cheapest_points_x[j]] = measurement_temp.values[value_id]"""
        #print("remaining after:",remaining_points)
        #print(cheapest_points_x)

        # find the cheapest line of 5 points for y
        row_costs = []
        cord_lists = []
        values_list = []
        for k in range(len(self.parameter_values_a)):
            row_cost = 0
            cord_list = []
            values = []
            for j in range(len(self.parameter_values_b)):
                y = self.parameter_values_a[k]
                x = self.parameter_values_b[j]
                temp = cost[Coordinate(self.parameter_values_a[k], self.parameter_values_b[j])]
                temp = min(temp)
                #print("point cost:",temp)
                row_cost += temp
                values.append(temp)
                cord_list.append(Coordinate(self.parameter_values_a[k], self.parameter_values_b[j]))
            row_costs.append(row_cost)
            values_list.append(values)
            #print("row cost:",row_cost)
            cord_lists.append(cord_list)
        #print("row_costs:",row_costs)
        #print(min(row_costs))
        row_id = row_costs.index(min(row_costs))
        #print(row_id)
        cheapest_points_y = cord_lists[row_id]
        #print(cheapest_points_y)
        # delete all points of this row from remaining point list
        #print("remaining before:",remaining_points)
        values = values_list[row_id]
        #print(values)
        for j in range(len(cheapest_points_y)):
            try:
                remaining_points[cheapest_points_y[j]].remove(values[j])
            except ValueError:
                pass
            """# add measurement value to the list
            coordinate_id = -1
            for k in range(len(experiment.coordinates)):
                if cheapest_points_y[j] == experiment.coordinates[k]:
                    coordinate_id = k
            measurement_temp = experiment.get_measurement(coordinate_id, 0, 0)
            value_id = -1
            for k in range(len(measurement_temp.values)):
                runtime = measurement_temp.values[k]
                nr_processes = cheapest_points_y[j].as_tuple()[0]
                core_hours = runtime * nr_processes
                if core_hours == values[k]:
                    value_id = k
                    break
            #print("measurement_temp:",measurement_temp.values[value_id])
            selected_measurement_values[cheapest_points_y[j]] = measurement_temp.values[value_id]"""
        #print("remaining after:",remaining_points)
        #print(cheapest_points_y)

        # put both lines in a new list
        selected_coord_list = []
        for j in range(len(cheapest_points_x)):
            if len(selected_coord_list)==0:
                selected_coord_list.append(cheapest_points_x[j])
            else:
                exists = False
                for k in range(len(selected_coord_list)):
                    if cheapest_points_x[j] == selected_coord_list[k]:
                        exists = True
                if exists == False:
                    selected_coord_list.append(cheapest_points_x[j])
        for j in range(len(cheapest_points_y)):
            if len(selected_coord_list)==0:
                selected_coord_list.append(cheapest_points_y[j])
            else:
                exists = False
                for k in range(len(selected_coord_list)):
                    if cheapest_points_y[j] == selected_coord_list[k]:
                        exists = True
                if exists == False:
                    selected_coord_list.append(cheapest_points_y[j])

        #print("Selected points:",selected_coord_list)

        # calculate the cost for the selected base points
        base_point_cost = calculate_selected_point_cost(selected_coord_list, experiment, 0, 0)
        base_point_cost = base_point_cost / (total_cost / 100)
        #print("base_point_cost %:",base_point_cost)



        #NOTE: (generic, RL-strategy...)
        # select x cheapest measurement(s) that are not part of the list so far
        # continue doing this until there is no improvement in smape value on measured points for a delta of X iterations
        added_points = 0

        #print("len selected_coord_list:",len(selected_coord_list))

        # add the first additional point, this is mandatory for the generic strategy
        remaining_points_base, selected_coord_list_base = add_additional_point_generic(remaining_points, selected_coord_list)
        # increment counter value, because a new measurement point was added
        added_points += 1

        #print("len selected_coord_list_base:",len(selected_coord_list_base))

        #print("added_points:",added_points)

        # create first model
        experiment_generic_base = self.create_experiment(selected_coord_list_base, experiment)
        _, models = self.get_extrap_model(experiment_generic_base)
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
            experiment_generic_new = self.create_experiment(selected_coord_list_new, experiment)
            model_generic_new, models = self.get_extrap_model(experiment_generic_new)
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
        for j in range(len(selected_coord_list)):
            coordinate = selected_coord_list[j]
            coordinate_id = -1
            for k in range(len(experiment.coordinates)):
                if coordinate == experiment.coordinates[k]:
                    coordinate_id = k
            measurement_temp = experiment.get_measurement(coordinate_id, 0, 0)
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
        add_points_generic = len(selected_coord_list) - min_points
        #print("add_points_generic:",add_points_generic)

        # create model using full matrix of points
        model_full, _ = self.get_extrap_model(experiment)
        #print("model_full:",model_full)

        # create model using point selection of generic strategy
        model_generic, _ = self.get_extrap_model(experiment_generic_new)
        #print("model_generic:",model_generic)

        # create model using point selection of generic strategy
        model_gpr, _ = self.get_extrap_model(experiment_gpr_new)
        #print("model_gpr:",model_gpr)

        # create model using point selection of generic strategy
        model_hybrid, _ = self.get_extrap_model(experiment_hybrid_new)
        #print("model_hybrid:",model_hybrid)

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
        prediction_gpr = eval(model_gpr)
        #print("prediction_gpr:",prediction_gpr)
        prediction_hybrid = eval(model_hybrid)
        #print("prediction_hybrid:",prediction_hybrid)

        #basline_function = function_dict[i].function
        actual = eval(basline_function)
        #print("actual:",actual)

        # get the percentage error for the full matrix of points
        error_full = abs(self.percentage_error(actual, prediction_full))
        #print("error_full:",error_full)

        # get the percentage error for the generic strategy
        error_generic = abs(self.percentage_error(actual, prediction_generic))
        #print("error_generic:",error_generic)

        # get the percentage error for the gpr strategy
        error_gpr = abs(self.percentage_error(actual, prediction_gpr))
        #print("error_gpr:",error_gpr)

        # get the percentage error for the hybrid strategy
        error_hybrid = abs(self.percentage_error(actual, prediction_hybrid))
        #print("error_hybrid:",error_hybrid)

        # increment accuracy bucket for full matrix of points
        acurracy_bucket_counter_full = self.increment_accuracy_bucket(acurracy_bucket_counter_full, error_full)

        # increment accuracy bucket for generic strategy
        acurracy_bucket_counter_generic = self.increment_accuracy_bucket(acurracy_bucket_counter_generic, error_generic)

        # increment accuracy bucket for gpr strategy
        acurracy_bucket_counter_gpr = self.increment_accuracy_bucket(acurracy_bucket_counter_gpr, error_gpr)

        # increment accuracy bucket for hybrid strategy
        acurracy_bucket_counter_hybrid = self.increment_accuracy_bucket(acurracy_bucket_counter_hybrid, error_hybrid)

        result_container["acurracy_bucket_counter_full"] = acurracy_bucket_counter_full

        result_container["add_points_generic"] = add_points_generic
        result_container["percentage_cost_generic"] = percentage_cost_generic
        result_container["acurracy_bucket_counter_generic"] = acurracy_bucket_counter_generic

        result_container["add_points_gpr"] = add_points_gpr
        result_container["percentage_cost_gpr"] = percentage_cost_gpr
        result_container["acurracy_bucket_counter_gpr"] = acurracy_bucket_counter_gpr

        result_container["add_points_hybrid"] = add_points_hybrid
        result_container["percentage_cost_hybrid"] = percentage_cost_hybrid
        result_container["acurracy_bucket_counter_hybrid"] = acurracy_bucket_counter_hybrid

        result_container["base_point_cost"] = base_point_cost

        shared_dict[counter] = result_container

    def run(self):

        function_dict = self.generate_synthetic_functions()

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

        base_point_costs = []
       
        # parallelize reading all measurement_files in one folder
        manager = Manager()
        shared_dict = manager.dict()
        cpu_count = mp.cpu_count()

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
            base_point_costs.append(result_dict[i]["base_point_cost"])
            
            b_full = result_dict[i]["acurracy_bucket_counter_full"]
            b_generic = result_dict[i]["acurracy_bucket_counter_generic"]
            b_gpr = result_dict[i]["acurracy_bucket_counter_gpr"]
            b_hybrid = result_dict[i]["acurracy_bucket_counter_hybrid"]

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

        #print("acurracy_bucket_counter_full:",acurracy_bucket_counter_full)
        #print("acurracy_bucket_counter_generic:",acurracy_bucket_counter_generic)
        #print("acurracy_bucket_counter_gpr:",acurracy_bucket_counter_gpr)
        #print("acurracy_bucket_counter_hybrid:",acurracy_bucket_counter_hybrid)

        json_out = {}

        # calculate the percentages for each accuracy bucket
        percentage_bucket_counter_full = self.calculate_percentage_of_buckets(acurracy_bucket_counter_full)
        print("percentage_bucket_counter_full:",percentage_bucket_counter_full)
        json_out["percentage_bucket_counter_full"] = percentage_bucket_counter_full

        percentage_bucket_counter_generic = self.calculate_percentage_of_buckets(acurracy_bucket_counter_generic)
        print("percentage_bucket_counter_generic:",percentage_bucket_counter_generic)
        json_out["percentage_bucket_counter_generic"] = percentage_bucket_counter_generic
        
        percentage_bucket_counter_gpr = self.calculate_percentage_of_buckets(acurracy_bucket_counter_gpr)
        print("percentage_bucket_counter_gpr:",percentage_bucket_counter_gpr)
        json_out["percentage_bucket_counter_gpr"] = percentage_bucket_counter_gpr
        
        percentage_bucket_counter_hybrid = self.calculate_percentage_of_buckets(acurracy_bucket_counter_hybrid)
        print("percentage_bucket_counter_hybrid:",percentage_bucket_counter_hybrid)
        json_out["percentage_bucket_counter_hybrid"] = percentage_bucket_counter_hybrid

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

        mean_base_point_cost = np.nanmean(base_point_costs)
        print("mean_base_point_cost:",mean_base_point_cost)

        ####################
        # Plot the results #
        ####################

        # plot the results of the model accuracy analysis
        if self.plot == True:
            plot_model_accuracy(percentage_bucket_counter_full, percentage_bucket_counter_generic, percentage_bucket_counter_gpr, percentage_bucket_counter_hybrid)
        
        used_costs = {
            "base points": np.array([mean_base_point_cost, mean_base_point_cost, mean_base_point_cost, mean_base_point_cost]),
            "additional points": np.array([100-mean_base_point_cost, mean_budget_generic-mean_base_point_cost, mean_budget_gpr-mean_base_point_cost, mean_budget_hybrid-mean_base_point_cost]),
        }
        json_out["base_point_cost"] = mean_base_point_cost
        json_out["min_points"] = min_points
        json_out["budget"] = self.budget

        # plot the analysis result for the costs and budgets
        if self.plot == True:
            plot_costs(used_costs, mean_base_point_cost)

        add_points = {
            "base points": np.array([min_points, min_points, min_points, min_points]),
            "additional points": np.array([len(experiment.coordinates)-min_points, mean_add_points_generic, mean_add_points_gpr, mean_add_points_hybrid]),
        }

        # plot the analysis result for the additional measurement point numbers
        if self.plot == True:
            plot_measurement_point_number(add_points, min_points)

        ##############################
        # Write results to json file #
        ##############################

        # write results to file
        #TODO: need to same stuff differently based on the mode...
        import json
        json_object = json.dumps(json_out, indent=4)

        with open("result.budget."+str(self.budget)+".json", "w") as outfile:
            outfile.write(json_object)
        

       
        #TODO: check which functions I generate, compared to old evaluation approach
        # check exponents coefficients, function types, how I checked the term contribution...
        # check modeler configuration, number of terms, exponents available, ...
        