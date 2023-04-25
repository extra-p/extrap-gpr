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


class SyntheticBenchmark():

    def __init__(self, args):
        self.nr_parameters = args.nr_parameters
        self.nr_functions = args.nr_functions
        self.args = args
        self.parameter_placeholders = ["a","b","c","d"]
        self.parameter_values_a = [4,8,16,32,64]
        self.parameter_values_b = [10,20,30,40,50]
        self.parameter_values_c = [1000,2000,3000,4000,5000]
        self.parameter_values_d = [10,12,14,16,18]
        self.noise_percent = args.noise

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
        return extrap_function_string

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

        
    def run(self):

        function_dict = self.generate_synthetic_functions()
       
        data = {}

        if self.nr_parameters == 2:

            min_points = 9

            experiments = []
            for i in range(self.nr_functions):

                container = {}

                container["baseline_function"] = function_dict[i].function

                cost = {}
                total_cost = 0

                experiment = Experiment()
                for j in range(self.nr_parameters):
                    experiment.add_parameter(Parameter(self.parameter_placeholders[j]))
                callpath = Callpath("main")
                experiment.add_callpath(callpath)
                metric = Metric("runtime")
                experiment.add_metric(metric)
                for j in range(len(self.parameter_values_a)):
                    
                    function = function_dict[i]
                    for k in range(len(self.parameter_values_b)):

                        coordinate = Coordinate(self.parameter_values_a[j], self.parameter_values_b[k])
                        experiment.add_coordinate(coordinate)
                        
                        a = self.parameter_values_a[j]
                        b = self.parameter_values_b[k]
                        result = eval(function.function)
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
                            #print("runtime:",runtime)
                            core_hours = runtime * nr_processes
                            total_cost += core_hours
                            cost[coordinate].append(core_hours)
                            values.append(result)
                        experiment.add_measurement(Measurement(coordinate, callpath, metric, values))

                experiments.append(experiment)

                print("len measurements:",len(experiment.coordinates))

                container["experiment"] = experiment

                print("cost:",cost)
                print("total_cost:",total_cost)

                container["cost_dict"] = cost
                container["total_cost"] = total_cost

                # create copy of the cost dict
                remaining_points = copy.deepcopy(cost)

                # dict to store the measurement points values for later use for modeling
                selected_measurement_values = {}

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
                    # add measurement value to the list
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
                    selected_measurement_values[cheapest_points_x[j]] = measurement_temp.values[value_id]
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
                    # add measurement value to the list
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
                    selected_measurement_values[cheapest_points_y[j]] = measurement_temp.values[value_id]
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

                # select x cheapest measurement(s) that are not part of the list so far
                # TODO: how to decide how many extra points should be taken???
                add_measurements = 1
                added_points = 0
                while True:
                    if added_points == add_measurements:
                        break

                    point_costs = {}
                    for key, value in remaining_points.items():
                        try:
                            min_value = min(value)
                        except ValueError:
                            min_value = math.inf
                        #print("min_value:",min_value)
                        point_costs[key] = min_value
                    temp = min(point_costs, key=point_costs.get)
                    #print("x:",temp)
                    #print("x2:",point_costs[temp])

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
                            remaining_points[temp].remove(point_costs[temp])
                        except ValueError:
                            pass
                    
                    # if point was not selected yet, use it
                    else:
                        # add the point to the selected list
                        selected_coord_list.append(temp)

                        # add measurement value to the list
                        coordinate_id = -1
                        for j in range(len(experiment.coordinates)):
                            if temp == experiment.coordinates[j]:
                                coordinate_id = j
                        measurement_temp = experiment.get_measurement(coordinate_id, 0, 0)
                        value_id = -1
                        for j in range(len(measurement_temp.values)):
                            runtime = measurement_temp.values[j]
                            nr_processes = temp.as_tuple()[0]
                            core_hours = runtime * nr_processes
                            if core_hours == point_costs[temp]:
                                value_id = j
                                break
                        #print("measurement_temp:",measurement_temp.values[value_id])
                        selected_measurement_values[temp] = measurement_temp.values[value_id]

                        # remove this point from the remaining points list
                        try:
                            remaining_points[temp].remove(point_costs[temp])
                        except ValueError:
                            pass
            
                        # increment counter value, because a new measurement point was added
                        added_points += 1

                    
                #print(remaining_points)

                    

                print("Selected points:",selected_coord_list)

                print("selected measurement values:", selected_measurement_values)


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
                    value = selected_measurement_values[selected_coord_list[j]] 
                    experiment_generic.add_measurement(Measurement(coordinate, callpath, metric, value))

                # calculate selected point cost
                selected_cost = 0
                for key, value in selected_measurement_values.items():
                    runtime = value
                    nr_processes = key.as_tuple()[0]
                    core_hours = runtime * nr_processes
                    #print(nr_processes, runtime, core_hours)
                    selected_cost += core_hours
                print("selected_cost:",selected_cost)

                # calculate number of additionally used data points (exceeding the base requirement of the sparse modeler)
                add_points = len(selected_coord_list) - min_points
                print("add_points:",add_points)

                # create model using point selection of generic strategy
                generic_function_string = self.get_extrap_model(experiment_generic)
                print("generic_function_string:",generic_function_string)

                
                extrap_function_string = self.get_extrap_model(experiment)
                print("extrap_function_string:",extrap_function_string)

                container["extrap_function_string"] = extrap_function_string

                
                
                #TODO: add other code here...

                data[i] = container


                break 

        elif self.nr_parameters == 3:
            pass
        elif self.nr_parameters == 4:
            pass


        #print(data)


        
        #TODO: evaluate the accuracy and predictive power of the models as described in the paper...


        ######################################################################################

        #TODO: create models using the gpr strategy

        #TODO: calculate the cost of the points used by the gpr strategy and the number of additional points

        #TODO: create models using the hybrid strategy

        #TODO: calculate the cost of the points used by the hybrid strategy and the number of additional points

        #TODO: calculate the model error of all strategies

        #TODO: parallelize all of these steps (the outer loop that iterates through the functions)

        #TODO: save the results in a csv table

        #TODO: plot the results using matplotlib or plotly
       
    
        
        
    
