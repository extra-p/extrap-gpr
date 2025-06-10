import copy
from extrap.entities.coordinate import Coordinate
from extrap.entities.experiment import Experiment
from extrap.entities.parameter import Parameter
from extrap.entities.callpath import Callpath
from extrap.entities.metric import Metric
from extrap.entities.measurement import Measurement
from extrap.modelers.model_generator import ModelGenerator
from extrap.modelers.abstract_modeler import MultiParameterModeler
from extrap.util.progress_bar import ProgressBar
import numpy as np
import math
from math import log2
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern
from sklearn.gaussian_process.kernels import WhiteKernel
import warnings
from sklearn.exceptions import ConvergenceWarning
from temp import add_measurements_to_gpr
from temp import add_measurement_to_gpr
import sys
from generic_strategy import add_additional_point_generic, add_additional_point_grid
from extrap.util.options_parser import ModelerOptionsAction, ModelerHelpAction
from extrap.util.options_parser import SINGLE_PARAMETER_MODELER_KEY, SINGLE_PARAMETER_OPTIONS_KEY
from extrap.util.options_parser import ModelerOptionsAction, ModelerHelpAction
from extrap.modelers import multi_parameter
from extrap.modelers import single_parameter
import random


def add_additional_point_random(remaining_points, selected_coord_list, measurements_random, nr_reps, callpath, metric):
    remaining_points = copy.deepcopy(remaining_points)
    selected_coord_list = copy.deepcopy(selected_coord_list)

    # choose a random point from the remaining point list
    random_key = random.choice(list(remaining_points.keys()))
    random_value = remaining_points[random_key]

    # get the cost of the new measurement value
    new_point_cost = random_value[0]

    index_measurement_value = nr_reps - len(random_value)

    #print("DEBUG measurements_random:", measurements_random)

    # get the actual measurement value
    for i in range(len(measurements_random[(callpath, metric)])):
        if measurements_random[(callpath, metric)][i].coordinate == random_key:
            new_measurement_value = measurements_random[(callpath, metric)][i].values[index_measurement_value]
            break

    # pop new value from remaining points list
    remaining_points[random_key].pop(0)

    # check if point was already selected
    # make sure this point was not selected yet
    exists = False
    for k in range(len(selected_coord_list)):
        if random_key == selected_coord_list[k]:
            exists = True
            break
    # if point was selected already, delete it
    if exists == False:
        # add not yet selected cord to selected cord list
        selected_coord_list.append(random_key)
    else:
        # if there is no value left for this cord then delete it completely from the list
        if len(remaining_points[random_key]) == 0:
            del remaining_points[random_key]

    selected_cord_new = random_key

    return new_point_cost, selected_cord_new, remaining_points, selected_coord_list, new_measurement_value


def create_experiment2(cord, experiment, new_value, callpath, metric):
    # only append the new measurement value to experiment
    cord_found = False
    for i in range(len(experiment.measurements[(callpath, metric)])):
        if cord == experiment.measurements[(callpath, metric)][i].coordinate:
            experiment.measurements[(callpath, metric)][i].add_value(new_value)
            #x = np.append(x, new_value)
            #experiment.measurements[(callpath, metric)][i].values = x
            cord_found = True
            break
    if cord_found == False:
        # add new coordinate to experiment and then add a new measurement object with the new value to the experiment
        experiment.add_coordinate(cord)
        new_measurement = Measurement(cord, callpath, metric, [new_value])
        experiment.add_measurement(new_measurement)
    return experiment


def calculate_selected_point_cost2(experiment, callpath, metric):
        selected_cost = 0
        for i in range(len(experiment.measurements[(callpath, metric)])):
            x = experiment.measurements[(callpath, metric)][i]
            coordinate_cost = 0
            for k in range(len(x.values)):
                runtime = np.mean(x.values[k])
                nr_processes = x.coordinate.as_tuple()[0]
                core_hours = runtime * nr_processes
                coordinate_cost += core_hours
            selected_cost += coordinate_cost
        return selected_cost
    

def create_experiment_base(selected_coord_list, nr_parameters, parameter_placeholders, metric, callpath, nr_base_points, experiment_coordinates, experiment_measurements):
    # create new experiment with only the selected measurements and points as coordinates and measurements
    experiment_new = Experiment()
    for j in range(nr_parameters):
        experiment_new.add_parameter(Parameter(parameter_placeholders[j]))
        
    experiment_new.add_callpath(callpath)
    experiment_new.add_metric(metric)

    for j in range(len(selected_coord_list)):
        coordinate = selected_coord_list[j]
        experiment_new.add_coordinate(coordinate)

        coordinate_id = -1
        for k in range(len(experiment_coordinates)):
            if coordinate == experiment_coordinates[k]:
                coordinate_id = k
        measurement_temp = experiment_measurements[(callpath, metric)][coordinate_id]
        #print("haha:",measurement_temp.median)

        if measurement_temp != None:
            values = []
            counter = 0
            while counter < nr_base_points:
                values.append(np.mean(measurement_temp.values[counter]))
                counter += 1
            #value = selected_measurement_values[selected_coord_list[j]] 
            #experiment_generic.add_measurement(Measurement(coordinate, callpath, metric, value))
            experiment_new.add_measurement(Measurement(coordinate, callpath, metric, values))
    return experiment_new


def increment_accuracy_bucket(acurracy_bucket_counter, percentage_error):
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


def percentage_error(true_value, measured_value):
    error = abs(true_value - measured_value)
    if true_value == 0.0:
        percentage_error = 0.0
    else:
        percentage_error = (error / true_value) * 100
    return percentage_error

def calculate_selected_point_cost(selected_points, callpath, metric, experiment_coordinates, experiment_measurements):
    # calculate selected point cost
    selected_cost = 0
    for j in range(len(selected_points)):
        coordinate = selected_points[j]
        coordinate_id = -1
        for k in range(len(experiment_coordinates)):
            if coordinate == experiment_coordinates[k]:
                coordinate_id = k
        measurement_temp = experiment_measurements[(callpath, metric)][coordinate_id]
        coordinate_cost = 0
        if measurement_temp != None:
            for k in range(len(measurement_temp.values)):
                runtime = np.mean(measurement_temp.values[k])
                nr_processes = coordinate.as_tuple()[0]
                core_hours = runtime * nr_processes
                coordinate_cost += core_hours
        selected_cost += coordinate_cost
    return selected_cost


def get_extrap_model2(experiment, args, callpath, metric):
    # initialize model generator
    model_generator = ModelGenerator(
        experiment, modeler=args.modeler)

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

    # create models from data
    with ProgressBar(desc='Generating models', disable=True) as pbar:
        model_generator.model_all(pbar)

    modeler = experiment.modelers[0]
    models = modeler.models
    
    model = models[(callpath, metric)]
    hypothesis = model.hypothesis
    function = hypothesis.function
    function_string = function.to_string(*experiment.parameters)
    extrap_function_string = function_string
    
    return extrap_function_string, model


def create_experiment(selected_coord_list, nr_parameters, parameter_placeholders, callpath, metric, experiment_coordinates, experiment_measurements):
    # create new experiment with only the selected measurements and points as coordinates and measurements
    experiment_generic = Experiment()
    for j in range(nr_parameters):
        experiment_generic.add_parameter(Parameter(parameter_placeholders[j]))

    experiment_generic.add_callpath(callpath)
    experiment_generic.add_metric(metric)

    for j in range(len(selected_coord_list)):
        coordinate = selected_coord_list[j]
        experiment_generic.add_coordinate(coordinate)

        coordinate_id = -1
        for k in range(len(experiment_coordinates)):
            if coordinate == experiment_coordinates[k]:
                coordinate_id = k
        measurement_temp = experiment_measurements[(callpath, metric)][coordinate_id]

        if measurement_temp != None:
            experiment_generic.add_measurement(Measurement(coordinate, callpath, metric, measurement_temp.values))
    return experiment_generic


def calculate_selected_point_cost_base(selected_points, callpath, metric, nr_base_points, experiment_coordinates, experiment_measurements):
    selected_cost = 0
    for j in range(len(selected_points)):
        coordinate = selected_points[j]
        coordinate_id = -1
        for k in range(len(experiment_coordinates)):
            if coordinate == experiment_coordinates[k]:
                coordinate_id = k
     
        measurement_temp = experiment_measurements[(callpath, metric)][coordinate_id]
        coordinate_cost = 0
        if measurement_temp != None:
            counter = 0
            while counter < nr_base_points:
                runtime = np.mean(measurement_temp.values[counter])
                nr_processes = coordinate.as_tuple()[0]
                core_hours = runtime * nr_processes
                coordinate_cost += core_hours
                counter += 1
        selected_cost += coordinate_cost
    return selected_cost


def analyze_callpath(inputs):
    
    # get the values from the parallel input dict
    callpath_id = inputs[0]
    shared_dict = inputs[1]
    cost = inputs[2]
    callpath = inputs[3]
    cost_container = inputs[4]
    total_costs_container = inputs[5]
    grid_search = inputs[6]
    experiment_measurements = inputs[7]
    nr_parameters = inputs[8]
    experiment_coordinates = inputs[9]
    metric = inputs[10]
    base_values = inputs[11]
    metric_id = inputs[12]
    nr_repetitions = inputs[13]
    parameters = inputs[14]
    args = inputs[15]
    budget = inputs[16]
    eval_point = inputs[17]
    all_points_functions_strings = inputs[18]
    coordinate_evaluation = inputs[19]
    measurement_evaluation = inputs[20]
    normalization = inputs[21]
    min_points = inputs[22]
    hybrid_switch = inputs[23]
    newonly = inputs[24]
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

    # bayesian
    acurracy_bucket_counter_bayesian = {}
    acurracy_bucket_counter_bayesian["rest"] = 0
    acurracy_bucket_counter_bayesian["5"] = 0
    acurracy_bucket_counter_bayesian["10"] = 0
    acurracy_bucket_counter_bayesian["15"] = 0
    acurracy_bucket_counter_bayesian["20"] = 0

    percentage_cost_bayesian_container = []
    add_points_bayesian_container = []
    
    callpath_string = callpath.name

    # get the cost values for this particular callpath
    cost = cost_container[callpath_string]
    total_cost = total_costs_container[callpath_string]

    # create copy of the cost dict
    remaining_points = copy.deepcopy(cost)
    
    ##########################
    ## Base point selection ##
    ##########################

    # create copy of the cost dict
    remaining_points = copy.deepcopy(cost)
    
    # create copy of the cost dict for the minimum experiment with gpr and hybrid strategies
    remaining_points_min = copy.deepcopy(cost)
    
    if grid_search == 2 or grid_search == 3:
        measurements_gpr = copy.deepcopy(experiment_measurements)
        measurements_hybrid = copy.deepcopy(experiment_measurements)

    if nr_parameters == 2:
            
        # find the cheapest line of 5 points for y
        y_lines = {}
        for i in range(len(experiment_coordinates)):
            cord_values = experiment_coordinates[i].as_tuple()
            x = cord_values[0]
            y = []
            for j in range(len(experiment_coordinates)):
                cord_values2 = experiment_coordinates[j].as_tuple()
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
                
                if grid_search == 2 or grid_search == 3:
                    for x in measurements_gpr[(callpath, metric)]:
                        if x.coordinate == cord:
                            temp = x.values
                            for i in range(base_values):
                                temp = np.delete(temp, 0, 0)
                            x.values = temp
                    for x in measurements_hybrid[(callpath, metric)]:
                        if x.coordinate == cord:
                            temp = x.values
                            for i in range(base_values):
                                temp = np.delete(temp, 0, 0)
                            x.values = temp
                    # also delete the cost values from the remaining min dict
                    for i in range(base_values):
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
        for i in range(len(experiment_coordinates)):
            cord_values = experiment_coordinates[i].as_tuple()
            y = cord_values[1]
            x = []
            for j in range(len(experiment_coordinates)):
                cord_values2 = experiment_coordinates[j].as_tuple()
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
                
                if grid_search == 2 or grid_search == 3:
                    for x in measurements_gpr[(callpath, metric)]:
                        if x.coordinate == cord:
                            temp = x.values
                            for i in range(base_values):
                                temp = np.delete(temp, 0, 0)
                            x.values = temp
                    for x in measurements_hybrid[(callpath, metric)]:
                        if x.coordinate == cord:
                            temp = x.values
                            for i in range(base_values):
                                temp = np.delete(temp, 0, 0)
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

    elif nr_parameters == 3:
        
        # find the cheapest line of 5 points for y
        y_lines = {}
        for i in range(len(experiment_coordinates)):
            cord_values = experiment_coordinates[i].as_tuple()
            x = cord_values[0]
            y = []
            z = cord_values[2]
            for j in range(len(experiment_coordinates)):
                cord_values2 = experiment_coordinates[j].as_tuple()
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
                
                if grid_search == 2 or grid_search == 3:
                    for x in measurements_gpr[(callpath, metric)]:
                        if x.coordinate == cord:
                            temp = x.values
                            for i in range(base_values):
                                temp = np.delete(temp, 0, 0)
                            x.values = temp
                    for x in measurements_hybrid[(callpath, metric)]:
                        if x.coordinate == cord:
                            temp = x.values
                            for i in range(base_values):
                                temp = np.delete(temp, 0, 0)
                            x.values = temp
                    # also delete the cost values from the remaining min dict
                    for i in range(base_values):
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
        for i in range(len(experiment_coordinates)):
            cord_values = experiment_coordinates[i].as_tuple()
            y = cord_values[1]
            x = []
            z = cord_values[2]
            for j in range(len(experiment_coordinates)):
                cord_values2 = experiment_coordinates[j].as_tuple()
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
                
                if grid_search == 2 or grid_search == 3:
                    for x in measurements_gpr[(callpath, metric)]:
                        if x.coordinate == cord:
                            temp = x.values
                            for i in range(base_values):
                                temp = np.delete(temp, 0, 0)
                            x.values = temp
                    for x in measurements_hybrid[(callpath, metric)]:
                        if x.coordinate == cord:
                            temp = x.values
                            for i in range(base_values):
                                temp = np.delete(temp, 0, 0)
                            x.values = temp
                    # also delete the cost values from the remaining min dict
                    for i in range(base_values):
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
        for i in range(len(experiment_coordinates)):
            cord_values = experiment_coordinates[i].as_tuple()
            x = cord_values[0]
            z = []
            y = cord_values[1]
            for j in range(len(experiment_coordinates)):
                cord_values2 = experiment_coordinates[j].as_tuple()
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
                
                if grid_search == 2 or grid_search == 3:
                    for x in measurements_gpr[(callpath, metric)]:
                        if x.coordinate == cord:
                            temp = x.values
                            for i in range(base_values):
                                temp = np.delete(temp, 0, 0)
                            x.values = temp
                    for x in measurements_hybrid[(callpath, metric)]:
                        if x.coordinate == cord:
                            temp = x.values
                            for i in range(base_values):
                                temp = np.delete(temp, 0, 0)
                            x.values = temp
                    # also delete the cost values from the remaining min dict
                    for i in range(base_values):
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
        
    else:
        return 1

    # calculate the cost for the selected base points
    if grid_search == 2 or grid_search == 3:
        #print("DEBUG2:",metric_id)
        base_point_cost = calculate_selected_point_cost_base(selected_points, callpath, metric, base_values, experiment_coordinates, experiment_measurements)
    elif grid_search == 1 or grid_search == 4:
        base_point_cost = calculate_selected_point_cost(selected_points, callpath, metric, experiment_coordinates, experiment_measurements)
    if total_cost == 0.0:
        base_point_cost = 0.0
    else:
        base_point_cost = base_point_cost / (total_cost / 100)
    #print("base_point_cost %:",base_point_cost)
    result_container["base_point_cost"] = base_point_cost

    added_points_generic = len(selected_points) * (nr_repetitions)


    ######################
    ## Generic strategy ##
    ######################

    remaining_points_generic = copy.deepcopy(remaining_points)
    selected_points_generic = copy.deepcopy(selected_points)
    
    # create first model
    experiment_generic_base = create_experiment(selected_points_generic, nr_parameters, parameters, callpath, metric, experiment_coordinates, experiment_measurements)
    _, model = get_extrap_model2(experiment_generic_base, args, callpath, metric)
    hypothesis = model.hypothesis

    # calculate selected point cost
    current_cost = calculate_selected_point_cost(selected_points_generic, callpath, metric, experiment_coordinates, experiment_measurements)
    if total_cost == 0.0:
        current_cost_percent = 0.0
    else:
        current_cost_percent = current_cost / (total_cost / 100)
    
    if current_cost_percent <= budget:
        if newonly == False:
            while True:
                # find another point for selection
                remaining_points_new, selected_coord_list_new, new_point = add_additional_point_generic(remaining_points_generic, selected_points_generic)

                # calculate selected point cost
                current_cost = calculate_selected_point_cost(selected_coord_list_new, callpath, metric, experiment_coordinates, experiment_measurements)
                if total_cost == 0.0:
                    current_cost_percent = 0.0
                else:
                    current_cost_percent = current_cost / (total_cost / 100)

                # current cost exceeds budget so break the loop
                #print("current_cost_percent > budget", current_cost_percent, budget)
                # to make sure no mistakes occur here
                # sometimes the numbers do not perfectly add up to the target budget
                # but to 100.00001
                # this is the fix for this case
                current_cost_percent = float("{0:.2f}".format(current_cost_percent))
                #print("current_cost_percent:",current_cost_percent)

                if current_cost_percent > budget:
                    break

                # add the new found point
                else:

                    # increment counter value, because a new measurement point was added
                    #added_points_generic += 1
                    added_points_generic += nr_repetitions

                    # create new model
                    experiment_generic_base = create_experiment(selected_coord_list_new, nr_parameters, parameters, callpath, metric, experiment_coordinates, experiment_measurements)

                    selected_points_generic = selected_coord_list_new
                    remaining_points_generic = remaining_points_new

                # if there are no points remaining that can be selected break the loop
                if len(remaining_points_generic) == 0:
                    break

    else:
        pass

    # calculate selected point cost
    selected_cost = calculate_selected_point_cost(selected_points_generic, callpath, metric, experiment_coordinates, experiment_measurements)
    
    # calculate the percentage of cost of the selected points compared to the total cost of the full matrix
    if total_cost == 0.0:
        percentage_cost_generic = 0.0
    else:
        percentage_cost_generic = selected_cost / (total_cost / 100)
    if percentage_cost_generic >= 99.9:
        percentage_cost_generic = 100
    result_container["percentage_cost_generic"] = percentage_cost_generic

    # calculate number of additionally used data points (exceeding the base requirement of the sparse modeler)
    result_container["add_points_generic"] = added_points_generic
    #add_points_generic = added_points_generic
    
    # create model using point selection of generic strategy
    model_generic, _ = get_extrap_model2(experiment_generic_base, args, callpath, metric)     
    
    # evaluate model accuracy against the first point in each direction of the parameter set for each parameter
    if parameters[0] == "p" and parameters[1] == "size":
        p = int(eval_point[0])
        size = int(eval_point[1])
    elif parameters[0] == "p" and parameters[1] == "n":
        p = int(eval_point[0])
        n = int(eval_point[1])
    elif parameters[0] == "p" and parameters[1] == "s":
        p = int(eval_point[0])
        s = int(eval_point[1])
    elif parameters[0] == "p" and parameters[1] == "d" and parameters[2] == "g":
        p = int(eval_point[0])
        d = int(eval_point[1])
        g = int(eval_point[2])
    elif parameters[0] == "p" and parameters[1] == "m" and parameters[2] == "n":
        p = int(eval_point[0])
        m = int(eval_point[1])
        n = int(eval_point[2])

    prediction_full = eval(all_points_functions_strings[callpath_string])
    #print("prediction_full:",prediction_full)
    prediction_generic = eval(model_generic)
    #print("prediction_generic:",prediction_generic)

    # get the actual measured value
    eval_measurement = None
    if nr_parameters == 2:
        for o in range(len(coordinate_evaluation)):
            parameter_values = coordinate_evaluation[o].as_tuple()
            #print("parameter_values:",parameter_values)
            if parameter_values[0] == float(eval_point[0]) and parameter_values[1] == float(eval_point[1]):
                eval_measurement = measurement_evaluation[callpath, metric][o]
                break
    elif nr_parameters == 3:
        for o in range(len(coordinate_evaluation)):
            parameter_values = coordinate_evaluation[o].as_tuple()
            #print("parameter_values:",parameter_values)
            if parameter_values[0] == float(eval_point[0]) and parameter_values[1] == float(eval_point[1]) and parameter_values[2] == float(eval_point[2]):
                eval_measurement = measurement_evaluation[callpath, metric][o]
                break
    else:
        return 1

    #print("eval_measurement:",eval_measurement)
    actual = eval_measurement.mean
    #print("actual:",actual)

    # get the percentage error for the full matrix of points
    error_full = abs(percentage_error(actual, prediction_full))
    #print("error_full:",error_full)

    # get the percentage error for the full matrix of points
    #error_generic = abs(percentage_error(actual, prediction_generic))
    #print("error_generic:",error_generic)
    
    # get the percentage error for the generic strategy
    if percentage_cost_generic <= budget:
        error_generic = abs(percentage_error(actual, prediction_generic))
    else:
        error_generic = 100
    #print("error_generic:",error_generic)

    # increment accuracy bucket for full matrix of points
    acurracy_bucket_counter_full = increment_accuracy_bucket(acurracy_bucket_counter_full, error_full)

    # increment accuracy bucket for generic strategy
    acurracy_bucket_counter_generic = increment_accuracy_bucket(acurracy_bucket_counter_generic, error_generic)

    ##################
    ## GPR strategy ##
    ##################

    # GPR parameter-value normalization for each measurement point
    normalization_factors = {}

    if normalization:
        
        for i in range(nr_parameters):

            param_value_max = -1

            for coord in experiment_coordinates:

                temp = coord.as_tuple()[i]

                if param_value_max < temp:
                    param_value_max = temp
                
            param_value_max = 100 / param_value_max
            normalization_factors[Parameter(parameters[i])] = param_value_max
            
        #print("normalization_factors:",normalization_factors)
    
    # do an noise analysis on the existing points
    mm = experiment_measurements
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
            if mean_mes == 0.0:
                pp = 0
            else:
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
    gaussian_process = GaussianProcessRegressor(
        kernel=kernel, n_restarts_optimizer=20
    )

    # add additional measurement points until break criteria is met
    add_points_gpr = 0
    
    budget_core_hours = budget * (total_cost / 100)
    
    if grid_search == 1 or grid_search == 4:
        add_points_gpr = len(selected_points) * nr_repetitions
        remaining_points_gpr = copy.deepcopy(remaining_points)
        # entails all measurement points and their values
        measurements_gpr = copy.deepcopy(experiment_measurements)
    elif grid_search == 2 or grid_search == 3:
        add_points_gpr = len(selected_points) * base_values
        remaining_points_gpr = copy.deepcopy(remaining_points_min)
    selected_points_gpr = copy.deepcopy(selected_points)

    # add all of the selected measurement points to the gaussian process
    # as training data and train it for these points
    temp_params = []
    for x in parameters:
        temp_params.append(Parameter(x))
    gaussian_process = add_measurements_to_gpr(gaussian_process, 
                    selected_points_gpr, 
                    measurements_gpr, 
                    callpath,
                    metric,
                    normalization_factors,
                    temp_params, eval_point)

    # create base model for gpr
    if grid_search == 2 or grid_search == 3:
        experiment_gpr_base = create_experiment_base(selected_points_gpr, nr_parameters, parameters, metric, callpath, base_values, experiment_coordinates, experiment_measurements)
    else:
        experiment_gpr_base = create_experiment(selected_points_gpr, nr_parameters, parameters, callpath, metric, experiment_coordinates, experiment_measurements)
    
    if base_point_cost <= budget:
        if newonly == False:
            while True:
                
                # identify all possible next points that would 
                # still fit into the modeling budget in core hours
                fitting_measurements = []
                for key, value in remaining_points_gpr.items():
                    
                    #current_cost = calculate_selected_point_cost(selected_points_gpr, experiment_gpr_base, metric_id, callpath_id)
                    current_cost = calculate_selected_point_cost2(experiment_gpr_base, callpath, metric)
                    
                    # always take the first value in the list, until none left
                    #new_cost = current_cost + np.sum(value)
                    new_cost = current_cost + value[0]
                    if total_cost == 0.0:
                        cost_percent = 0.0
                    else:
                        cost_percent = new_cost / (total_cost / 100)
                    
                    #if new_cost > budget_core_hours:
                    #    print("new_cost <= budget_core_hours:", new_cost, budget_core_hours)
                    #if cost_percent > 100:
                    #    print("cost percent <= budget percent:", cost_percent, budget)
                    # to make sure no mistakes occur here
                    # sometimes the numbers do not perfectly add up to the target budget
                    # but to 100.00001
                    # this is the fix for this case
                    cost_percent = float("{0:.3f}".format(cost_percent))
                    if cost_percent > 100.0:
                        cost_percent = 100.0

                    if cost_percent <= budget:
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
                    
                    if grid_search == 3 or grid_search == 4:
                        rep = 1
                        for j in range(len(measurements_gpr[(callpath, metric)])):
                            if measurements_gpr[(callpath, metric)][j].coordinate == fitting_measurements[i]:
                                rep = (nr_repetitions - len(measurements_gpr[(callpath, metric)][j].values)) + 1
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
                        for i in range(len(measurements_gpr[(callpath, metric)])):
                            if measurements_gpr[(callpath, metric)][i].coordinate == cord:
                                cord_id = i
                                x = measurements_gpr[(callpath, metric)][i].values
                                #print("DEBUG 5:",len(x))
                                if len(x) > 0:
                                    new_value = np.mean(x[0])
                                    x = np.delete(x, 0, 0)
                                    measurements_gpr[(callpath, metric)][i].values = x
                                break
                        
                        # pop value from cord in remaining points list that has been selected as best next point
                        remaining_points_gpr[cord].pop(0)
                        
                        # pop cord from remaining points when no value left anymore
                        if len(measurements_gpr[(callpath, metric)][cord_id].values) == 0:
                            remaining_points_gpr.pop(cord)
                        
                    except KeyError:
                        pass

                    # update the number of additional points used
                    add_points_gpr += 1

                    # add this point to the gpr experiment
                    #experiment_gpr_base = create_experiment(selected_points_gpr, experiment_gpr_base, len(experiment_gpr_base.parameters), parameters, metric_id, callpath_id)
                    experiment_gpr_base = create_experiment2(cord, experiment_gpr_base, new_value, callpath, metric)

                # if there are no suitable measurement points found
                # break the while True loop
                else:
                    break

    # cost used of the gpr strategy
    #current_cost = calculate_selected_point_cost(selected_points_gpr, callpath, metric, experiment_coordinates, measurements_gpr)
    current_cost = calculate_selected_point_cost2(experiment_gpr_base, callpath, metric)
    if total_cost == 0.0:
        percentage_cost_gpr = 0.0
    else:
        percentage_cost_gpr = current_cost / (total_cost / 100)
    if percentage_cost_gpr >= 99.9:
        percentage_cost_gpr = 100
    #print("percentage_cost_gpr:",percentage_cost_gpr)
    #percentage_cost_gpr_container.append(percentage_cost_gpr)
    result_container["percentage_cost_gpr"] = percentage_cost_gpr
    
    # additionally used data points (exceeding the base requirement of the sparse modeler)
    #add_points_gpr_container.append(add_points_gpr)
    result_container["add_points_gpr"] = add_points_gpr
    
    # create model using point selection of gpr strategy
    model_gpr, _ = get_extrap_model2(experiment_gpr_base, args, callpath, metric)
    #print("Model GPR:",model_gpr)
    
    # create model using full matrix of points
    # evaluate model accuracy against the first point in each direction of the parameter set for each parameter
    if parameters[0] == "p" and parameters[1] == "size":
        p = int(eval_point[0])
        size = int(eval_point[1])
    elif parameters[0] == "p" and parameters[1] == "n":
        p = int(eval_point[0])
        n = int(eval_point[1])
    elif parameters[0] == "p" and parameters[1] == "s":
        p = int(eval_point[0])
        s = int(eval_point[1])
    elif parameters[0] == "p" and parameters[1] == "d" and parameters[2] == "g":
        p = int(eval_point[0])
        d = int(eval_point[1])
        g = int(eval_point[2])
    elif parameters[0] == "p" and parameters[1] == "m" and parameters[2] == "n":
        p = int(eval_point[0])
        m = int(eval_point[1])
        n = int(eval_point[2])

    prediction_full = eval(all_points_functions_strings[callpath_string])
    #print("prediction_full:",prediction_full)
    prediction_gpr = eval(model_gpr)
    #print("prediction_gpr:",prediction_gpr)

    # get the actual measured value
    eval_measurement = None
    if nr_parameters == 2:
        for o in range(len(coordinate_evaluation)):
            parameter_values = coordinate_evaluation[o].as_tuple()
            #print("parameter_values:",parameter_values)
            if parameter_values[0] == float(eval_point[0]) and parameter_values[1] == float(eval_point[1]):
                eval_measurement = measurement_evaluation[callpath, metric][o]
                break
    elif nr_parameters == 3:
        for o in range(len(coordinate_evaluation)):
            parameter_values = coordinate_evaluation[o].as_tuple()
            #print("parameter_values:",parameter_values)
            if parameter_values[0] == float(eval_point[0]) and parameter_values[1] == float(eval_point[1]) and parameter_values[2] == float(eval_point[2]):
                eval_measurement = measurement_evaluation[callpath, metric][o]
                break
    else:
        return 1

    #print("eval_measurement:",eval_measurement)
    actual = eval_measurement.mean
    #print("actual:",actual)
    
    # get the percentage error for the gpr strategy
    if percentage_cost_gpr <= budget:
        error_gpr = abs(percentage_error(actual, prediction_gpr))
    else:
        error_gpr = 100
    #print("error_gpr:",error_gpr)

    # increment accuracy bucket for gpr strategy
    acurracy_bucket_counter_gpr = increment_accuracy_bucket(acurracy_bucket_counter_gpr, error_gpr)

    #####################
    ## Hybrid strategy ##
    #####################

    # do an noise analysis on the existing points
    mm = experiment_measurements
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
            if mean_mes == 0.0:
                pp = 0.0
            else:
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
    budget_core_hours = budget * (total_cost / 100)
    
    if grid_search == 1 or grid_search == 4:
        add_points_hybrid = len(selected_points) * nr_repetitions
        remaining_points_hybrid = copy.deepcopy(remaining_points)
        # entails all measurement points and their values
        measurements_hybrid = copy.deepcopy(experiment_measurements)
    elif grid_search == 2 or grid_search == 3:
        add_points_hybrid = len(selected_points) * base_values
        remaining_points_hybrid = copy.deepcopy(remaining_points_min)
    selected_points_hybrid = copy.deepcopy(selected_points)
    
    #print("DEBUG add_points_hybrid:",add_points_hybrid)

    # add all of the selected measurement points to the gaussian process
    # as training data and train it for these points
    temp_params = []
    for x in parameters:
        temp_params.append(Parameter(x))
    gaussian_process_hybrid = add_measurements_to_gpr(gaussian_process_hybrid, 
                    selected_points_hybrid, 
                    measurements_hybrid,
                    callpath, 
                    metric,
                    normalization_factors,
                    temp_params, eval_point)

    # create base model for gpr hybrid
    if grid_search == 2 or grid_search == 3:
        experiment_hybrid_base = create_experiment_base(selected_points_hybrid, nr_parameters, parameters, metric, callpath, base_values, experiment_coordinates, experiment_measurements)
    else:
        experiment_hybrid_base = create_experiment(selected_points_hybrid, nr_parameters, parameters, callpath, metric, experiment_coordinates, experiment_measurements)

    if newonly == False:
        while True:
            
            # identify all possible next points that would 
            # still fit into the modeling budget in core hours
            fitting_measurements = []
            for key, value in remaining_points_hybrid.items():

                current_cost = calculate_selected_point_cost2(experiment_hybrid_base, callpath, metric)
                
                #new_cost = current_cost + np.sum(value)
                new_cost = current_cost + value[0]
                if total_cost == 0.0:
                    cost_percent = 0.0
                else:
                    cost_percent = new_cost / (total_cost / 100)
                
                #if new_cost > budget_core_hours:
                #    print("new_cost <= budget_core_hours:", new_cost, budget_core_hours)
                #if cost_percent > 100:
                #    print("cost percent <= budget percent:", cost_percent, budget)
                # to make sure no mistakes occur here
                # sometimes the numbers do not perfectly add up to the target budget
                # but to 100.00001
                # this is the fix for this case
                cost_percent = float("{0:.3f}".format(cost_percent))
                if cost_percent > 100.0:
                    cost_percent = 100.0

                if cost_percent <= budget:
                    fitting_measurements.append(key)

            #print("fitting_measurements:",fitting_measurements)

            # determine the switching point between gpr and hybrid strategy
            swtiching_point = 0
            if nr_parameters == 2:
                if grid_search == 1 or grid_search == 4:
                    swtiching_point = nr_repetitions * min_points + hybrid_switch
                elif grid_search == 2 or grid_search == 3:
                    swtiching_point = base_values * min_points + hybrid_switch
            elif nr_parameters == 3:
                if grid_search == 1 or grid_search == 4:
                    swtiching_point = nr_repetitions * min_points + hybrid_switch
                elif grid_search == 2 or grid_search == 3:
                    swtiching_point = base_values * min_points + hybrid_switch
            elif nr_parameters == 4:
                if grid_search == 1 or grid_search == 4:
                    swtiching_point = nr_repetitions * min_points + hybrid_switch
                elif grid_search == 2 or grid_search == 3:
                    swtiching_point = base_values * min_points + hybrid_switch
            else:
                if grid_search == 1 or grid_search == 4:
                    swtiching_point = nr_repetitions * min_points + hybrid_switch
                elif grid_search == 2 or grid_search == 3:
                    swtiching_point = base_values * min_points + hybrid_switch

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
                            x.append(parameter_values[j] * normalization_factors[experiment_hybrid_base.parameters[j]])
                    
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
                    
                    if grid_search == 3 or grid_search == 4:
                        rep = 1
                        for j in range(len(measurements_hybrid[(callpath, metric)])):
                            if measurements_hybrid[(callpath, metric)][j].coordinate == fitting_measurements[i]:
                                rep = (nr_repetitions - len(measurements_hybrid[(callpath, metric)][j].values)) + 1
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
                    for i in range(len(measurements_hybrid[(callpath, metric)])):
                        if measurements_hybrid[(callpath, metric)][i].coordinate == cord:
                            cord_id = i
                            x = measurements_hybrid[(callpath, metric)][i].values
                            if len(x) > 0:
                                new_value = np.mean(x[0])
                                x = np.delete(x, 0, 0)
                                measurements_hybrid[(callpath, metric)][i].values = x
                            break
                        
                    # pop value from cord in remaining points list that has been selected as best next point
                    remaining_points_hybrid[cord].pop(0)
                    
                    # pop cord from remaining points when no value left anymore
                    if len(measurements_hybrid[(callpath, metric)][cord_id].values) == 0:
                        remaining_points_hybrid.pop(cord)
                    
                except KeyError:
                    pass


                # update the number of additional points used
                add_points_hybrid += 1

                # add this point to the hybrid experiment
                experiment_hybrid_base = create_experiment2(cord, experiment_hybrid_base, new_value, callpath, metric)


            # if there are no suitable measurement points found
            # break the while True loop
            else:
                break

    # cost used of the gpr strategy
    current_cost = calculate_selected_point_cost2(experiment_hybrid_base, callpath, metric)
    if total_cost == 0.0:
        current_cost_percent = 0.0
    else:
        current_cost_percent = current_cost / (total_cost / 100)

    percentage_cost_hybrid = current_cost_percent
    if percentage_cost_hybrid >= 99.9:
        percentage_cost_hybrid = 100
    #print("percentage_cost_hybrid:",percentage_cost_hybrid)
    #percentage_cost_hybrid_container.append(percentage_cost_hybrid)
    result_container["percentage_cost_hybrid"] = percentage_cost_hybrid

    # additionally used data points (exceeding the base requirement of the sparse modeler)
    #add_points_hybrid_container.append(add_points_hybrid)
    #print("DEBUG add_points_hybrid:",add_points_hybrid)
    result_container["add_points_hybrid"] = add_points_hybrid

    # create model using point selection of hybrid strategy
    model_hybrid, _ = get_extrap_model2(experiment_hybrid_base, args, callpath, metric)
    
    # create model using full matrix of points
    # evaluate model accuracy against the first point in each direction of the parameter set for each parameter
    if parameters[0] == "p" and parameters[1] == "size":
        p = int(eval_point[0])
        size = int(eval_point[1])
    elif parameters[0] == "p" and parameters[1] == "n":
        p = int(eval_point[0])
        n = int(eval_point[1])
    elif parameters[0] == "p" and parameters[1] == "s":
        p = int(eval_point[0])
        s = int(eval_point[1])
    elif parameters[0] == "p" and parameters[1] == "d" and parameters[2] == "g":
        p = int(eval_point[0])
        d = int(eval_point[1])
        g = int(eval_point[2])
    elif parameters[0] == "p" and parameters[1] == "m" and parameters[2] == "n":
        p = int(eval_point[0])
        m = int(eval_point[1])
        n = int(eval_point[2])

    prediction_full = eval(all_points_functions_strings[callpath_string])
    #print("prediction_full:",prediction_full)
    prediction_hybrid = eval(model_hybrid)
    #print("prediction_hybrid:",prediction_hybrid)

    # get the actual measured value
    eval_measurement = None
    if nr_parameters == 2:
        for o in range(len(coordinate_evaluation)):
            parameter_values = coordinate_evaluation[o].as_tuple()
            #print("parameter_values:",parameter_values)
            if parameter_values[0] == float(eval_point[0]) and parameter_values[1] == float(eval_point[1]):
                eval_measurement = measurement_evaluation[callpath, metric][o]
                break
    elif nr_parameters == 3:
        for o in range(len(coordinate_evaluation)):
            parameter_values = coordinate_evaluation[o].as_tuple()
            #print("parameter_values:",parameter_values)
            if parameter_values[0] == float(eval_point[0]) and parameter_values[1] == float(eval_point[1]) and parameter_values[2] == float(eval_point[2]):
                eval_measurement = measurement_evaluation[callpath, metric][o]
                break
    else:
        return 1

    #print("eval_measurement:",eval_measurement)
    actual = eval_measurement.mean
    #print("actual:",actual)

    # get the percentage error for the full matrix of points
    #error_hybrid = abs(percentage_error(actual, prediction_hybrid))
    #print("error_hybrid:",error_hybrid)

    # get the percentage error for the hybrid strategy
    if percentage_cost_hybrid <= budget:
        error_hybrid = abs(percentage_error(actual, prediction_hybrid))
    else:
        error_hybrid = 100
    #print("error_hybrid:",error_hybrid)

    # increment accuracy bucket for hybrid strategy
    acurracy_bucket_counter_hybrid = increment_accuracy_bucket(acurracy_bucket_counter_hybrid, error_hybrid)

    ############
    ## Random ##
    ############

    added_points_random = len(selected_points) * (nr_repetitions)

    remaining_points_random = copy.deepcopy(remaining_points)
    selected_points_random = copy.deepcopy(selected_points)

    # create first model
    experiment_random_base = create_experiment(selected_points_random, nr_parameters, parameters, callpath, metric, experiment_coordinates, experiment_measurements)
    
    _, model = get_extrap_model2(experiment_random_base, args, callpath, metric)
    hypothesis = model.hypothesis

    # calculate selected point cost
    current_cost = calculate_selected_point_cost(selected_points_random, callpath, metric, experiment_coordinates, experiment_measurements)
    if total_cost == 0.0:
        current_cost_percent = 0.0
    else:
        current_cost_percent = current_cost / (total_cost / 100)

    #print("remaining_points_random:", remaining_points_random)
    #print("selected_points_random:", selected_points_random)
    #print("DEBUG measurements_random:", measurements_random)

    if current_cost_percent <= budget:
        while True:
            # find another point for selection
            new_point_cost, selected_cord_new, remaining_points_new, selected_coord_list_new, new_measurement_value = add_additional_point_random(remaining_points_random, selected_points_random, experiment_measurements, nr_repetitions, callpath, metric)

            #print("DEBUG:", new_point_cost, selected_cord_new, remaining_points_new, selected_coord_list_new, new_measurement_value)

            # calculate new selected point cost
            new_cost = current_cost + new_point_cost
            new_cost_percent = new_cost / (total_cost / 100)

            # current cost exceeds budget so break the loop
            # to make sure no mistakes occur here
            # sometimes the numbers do not perfectly add up to the target budget
            # but to 100.00001
            # this is the fix for this case
            new_cost_percent = float("{0:.2f}".format(new_cost_percent))
            #print("new_cost_percent:",new_cost_percent)

            if new_cost_percent > budget:
                break

            # add the new found point
            else:
                # increment counter value, because a new measurement point was added
                added_points_random += 1

                # create new model
                experiment_random_base = create_experiment2(selected_cord_new, experiment_random_base, new_measurement_value, callpath, metric)
                
                selected_points_random = selected_coord_list_new
                remaining_points_random = remaining_points_new
                current_cost = new_cost
                current_cost_percent = new_cost_percent

            # if there are no points remaining that can be selected break the loop
            if len(remaining_points_random) == 0:
                break

    else:
        pass

    # calculate the percentage of cost of the selected points compared to the total cost of the full matrix
    current_cost = calculate_selected_point_cost2(experiment_hybrid_base, callpath, metric)
    if total_cost == 0.0:
        percentage_cost_random = 0.0
    else:
        percentage_cost_random = current_cost / (total_cost / 100)
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
    
    # create model using point selection of random strategy
    model_random, _ = get_extrap_model2(experiment_random_base, args, callpath, metric)     

    # evaluate model accuracy against the first point in each direction of the parameter set for each parameter
    if parameters[0] == "p" and parameters[1] == "size":
        p = int(eval_point[0])
        size = int(eval_point[1])
    elif parameters[0] == "p" and parameters[1] == "n":
        p = int(eval_point[0])
        n = int(eval_point[1])
    elif parameters[0] == "p" and parameters[1] == "s":
        p = int(eval_point[0])
        s = int(eval_point[1])
    elif parameters[0] == "p" and parameters[1] == "d" and parameters[2] == "g":
        p = int(eval_point[0])
        d = int(eval_point[1])
        g = int(eval_point[2])
    elif parameters[0] == "p" and parameters[1] == "m" and parameters[2] == "n":
        p = int(eval_point[0])
        m = int(eval_point[1])
        n = int(eval_point[2])

    prediction_full = eval(all_points_functions_strings[callpath_string])
    #print("prediction_full:",prediction_full)
    prediction_random = eval(model_random)
    #print("prediction_random:",prediction_random)

    # get the actual measured value
    eval_measurement = None
    if nr_parameters == 2:
        for o in range(len(coordinate_evaluation)):
            parameter_values = coordinate_evaluation[o].as_tuple()
            #print("parameter_values:",parameter_values)
            if parameter_values[0] == float(eval_point[0]) and parameter_values[1] == float(eval_point[1]):
                eval_measurement = measurement_evaluation[callpath, metric][o]
                break
    elif nr_parameters == 3:
        for o in range(len(coordinate_evaluation)):
            parameter_values = coordinate_evaluation[o].as_tuple()
            #print("parameter_values:",parameter_values)
            if parameter_values[0] == float(eval_point[0]) and parameter_values[1] == float(eval_point[1]) and parameter_values[2] == float(eval_point[2]):
                eval_measurement = measurement_evaluation[callpath, metric][o]
                break
    else:
        return 1

    #print("eval_measurement:",eval_measurement)
    actual = eval_measurement.mean
    #print("actual:",actual)
    
    # get the percentage error for the gpr strategy
    if percentage_cost_random <= budget:
        error_random = abs(percentage_error(actual, prediction_random))
    else:
        error_random = 100
    #print("error_random:",error_random)

    # increment accuracy bucket for gpr strategy
    acurracy_bucket_counter_random = increment_accuracy_bucket(acurracy_bucket_counter_random, error_random)


    ##########
    ## Grid ##
    ##########

    remaining_points_grid = copy.deepcopy(remaining_points)
    selected_points_grid = copy.deepcopy(selected_points)

    # setup the grid for the grid search
    combinations = None
    parameter_values_a = self.parameter_values_a[::-1]
    if self.nr_parameters == 2:
        combinations = list(itertools.product(
            parameter_values_a,
            self.parameter_values_b,
        ))

    elif self.nr_parameters == 3:
        combinations = list(itertools.product(
            parameter_values_a,
            self.parameter_values_b,
            self.parameter_values_c
        ))

    elif self.nr_parameters == 4:
        combinations = list(itertools.product(
            parameter_values_a,
            self.parameter_values_b,
            self.parameter_values_c,
            self.parameter_values_d
        ))

    else:
        return 1

    # filter the combinations so that the base points do not need to be iterated over again...
    if self.nr_parameters == 2:
        remaining_combinations = [
            (a, b) for (a, b) in combinations if Coordinate(a, b) not in selected_points_grid
        ]
    elif self.nr_parameters == 3:
        remaining_combinations = [
            (a, b, c) for (a, b, c) in combinations if Coordinate(a, b, c) not in selected_points_grid
        ]
    elif self.nr_parameters == 4:
        remaining_combinations = [
            (a, b, c, d) for (a, b, c, d) in combinations if Coordinate(a, b, c, d) not in selected_points_grid
        ]
    else:
        return 1
    #print("DEBUG:", len(combinations))
    #print("DEBUG:", selected_points_grid, len(selected_points_grid))
    #print("DEBUG:", remaining_combinations, len(remaining_combinations)) 

    # create first model
    experiment_grid_base = create_experiment2(selected_points_grid, experiment, len(experiment.parameters), parameters, 0, 0)
    
    _, models = self.get_extrap_model(experiment_grid_base)
    hypothesis = None
    for model in models.values():
        hypothesis = model.hypothesis

    # calculate selected point cost
    current_cost = calculate_selected_point_cost2(selected_points_grid, experiment, 0, 0)
    current_cost_percent = current_cost / (total_cost / 100)

    from collections import defaultdict
    
    if self.mode == "budget":

        if current_cost_percent <= self.budget:
            
            # loop through all remaining_combinations of the grid
            if self.nr_parameters == 2:

                for i, (a, b) in enumerate(remaining_combinations):
                        
                    # get the new selected point from grid
                    new_point = Coordinate(a, b)
                    #print("DEBUG: ", new_point)

                    # update remaining point list and selected point list
                    remaining_points_new, selected_coord_list_new, new_point_cost = add_additional_point_grid(remaining_points_grid, selected_points_grid, new_point)

                    # calculate selected point cost
                    current_cost = current_cost + new_point_cost
                    current_cost_percent = current_cost / (total_cost / 100)
                    #print(current_cost_percent)

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


            elif self.nr_parameters == 3:
                for i, (a, b, c) in enumerate(remaining_combinations):
                    new_point = Coordinate(a, b, c)
                    #print("DEBUG new_point:", new_point)

                    # update remaining point list and selected point list
                    remaining_points_new, selected_coord_list_new, new_point_cost = add_additional_point_grid(remaining_points_grid, selected_points_grid, new_point)

                    # calculate selected point cost
                    current_cost = current_cost + new_point_cost
                    current_cost_percent = current_cost / (total_cost / 100)
                    #print(current_cost_percent)

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


            elif self.nr_parameters == 4:
                for i, (a, b, c, d) in enumerate(remaining_combinations):
                    new_point = Coordinate(a, b, c, d)
                    #print("DEBUG new_point:", new_point)

                    # update remaining point list and selected point list
                    remaining_points_new, selected_coord_list_new, new_point_cost = add_additional_point_grid(remaining_points_grid, selected_points_grid, new_point)

                    # calculate selected point cost
                    current_cost = current_cost + new_point_cost
                    current_cost_percent = current_cost / (total_cost / 100)
                    #print(current_cost_percent)

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
                return 1
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

    # increment accuracy bucket for generic strategy
    acurracy_bucket_counter_grid = self.increment_accuracy_bucket(acurracy_bucket_counter_grid, error_grid)

    #######################
    ## Bayesian strategy ##
    #######################

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
    add_points_bayesian = 0
    
    budget_core_hours = self.budget * (total_cost / 100)
    
    if self.grid_search == 1 or self.grid_search == 4:
        add_points_bayesian = len(selected_points) * self.nr_repetitions
        remaining_points_bayesian = copy.deepcopy(remaining_points)
        # entails all measurement points and their values
        measurements_bayesian = copy.deepcopy(experiment.measurements)
    elif self.grid_search == 2 or self.grid_search == 3:
        add_points_bayesian = len(selected_points) * self.base_values
        remaining_points_bayesian = copy.deepcopy(remaining_points_min)
    selected_points_bayesian = copy.deepcopy(selected_points)

    # add all of the selected measurement points to the gaussian process
    # as training data and train it for these points
    gaussian_process = add_measurements_to_gpr(gaussian_process, 
                    selected_points_bayesian, 
                    measurements_bayesian, 
                    callpath,
                    metric,
                    normalization_factors,
                    experiment.parameters, eval_point)

    # create base model for gpr
    if self.grid_search == 2 or self.grid_search == 3:
        experiment_bayesian_base = self.create_experiment_base(selected_points_bayesian, experiment, len(experiment.parameters), parameters, 0, 0, self.base_values)
    else:
        experiment_bayesian_base = create_experiment2(selected_points_bayesian, experiment, len(experiment.parameters), parameters, 0, 0)
    
    # Precompute normalization values only once for performance
    norm_factors = [normalization_factors.get(param, 1.0) 
                    for param in experiment_bayesian_base.parameters]

    if base_point_cost <= self.budget:
        while True:
            
            # identify all possible next points that would 
            # still fit into the modeling budget in core hours
            fitting_measurements = []
            for key, value in remaining_points_bayesian.items():
                
                #current_cost = calculate_selected_point_cost2(selected_points_bayesian, experiment_bayesian_base, 0, 0)
                current_cost = self.calculate_selected_point_cost(experiment_bayesian_base)
                
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
            #print("selected_points_bayesian:", selected_points_bayesian)

            # Propose next sampling point using BO
            #X_candidates = np.array([c.as_tuple() for c in fitting_measurements])
            #print("X_candidates:", X_candidates)

            """X_candidates_list = []
            for fm in fitting_measurements:
                parameter_values = fm.as_tuple()
                x = []
                for j in range(len(parameter_values)):
                    if len(normalization_factors) != 0:
                        x.append(parameter_values[j] * normalization_factors[experiment_bayesian_base.parameters[j]])
                    else:
                        x.append(parameter_values[j])
                #x = [x]
                X_candidates_list.append(x)
                #print("DEBUG x:", x)
            X_candidates = np.array(X_candidates_list)"""
            X_candidates_list = [
                [val * norm_factors[j] if normalization_factors else val
                for j, val in enumerate(fm.as_tuple())]
                for fm in fitting_measurements
            ]

            # Convert to NumPy array
            X_candidates = np.array(X_candidates_list)
            #print("X_candidates:", X_candidates)

            """y_train = []
            for i in range(len(selected_points_bayesian)):
                for j in range(len(measurements_bayesian[(Callpath("main"), Metric("runtime"))])):
                    if measurements_bayesian[(Callpath("main"), Metric("runtime"))][j].coordinate == selected_points_bayesian[i]:
                        y_train.append(measurements_bayesian[(Callpath("main"), Metric("runtime"))][j].mean)
            y_train = np.array(y_train)"""
            measurement_key = (Callpath("main"), Metric("runtime"))
            measurements_by_coord = {
                m.coordinate: m.mean
                for m in measurements_bayesian[measurement_key]
            }

            y_train = np.array([
                measurements_by_coord[coord]
                for coord in selected_points_bayesian
                if coord in measurements_by_coord  # Optional: safety check
            ])
            #print("y_train:", y_train)

            if len(X_candidates) == 0:
                break

            ei = expected_improvement(X_candidates, gaussian_process, y_train)
            best_idx = np.argmax(ei)
            X_next = X_candidates[best_idx].reshape(1, -1)
            best_coordinate = fitting_measurements[best_idx]
            #print("X_next:",X_next)
            #print("best_coordinate:", best_coordinate)

            # find the next best additional measurement point using the gpr
            best_index = -1
            for i in range(len(fitting_measurements)):
                parameter_values = fitting_measurements[i].as_tuple()
                cord = Coordinate(parameter_values)
                #print(best_coordinate, cord)
                if best_coordinate == cord:
                    best_index = i
                    break
            #print("best_index:", best_index)

            # if there has been a point found that is suitable
            if best_index != -1:

                # add the identified measurement point to the selected point list
                parameter_values = fitting_measurements[best_index].as_tuple()
                cord = Coordinate(parameter_values)
                #print("DEBUG cord:", cord)
                #selected_points_bayesian.append(cord)
                
                # only add coordinate to selected points list if not already in there (because of reps)
                if cord not in selected_points_bayesian:
                    selected_points_bayesian.append(cord)
                
                # add the new point to the gpr and call fit()
                gaussian_process = add_measurement_to_gpr(gaussian_process, 
                        cord, 
                        measurements_bayesian,
                        callpath, 
                        metric,
                        normalization_factors,
                        experiment_bayesian_base.parameters)
                
                new_value = 0
                
                # remove the identified measurement point from the remaining point list
                try:
                    # only pop cord when there are no values left in the measurement
                    
                    # if that's not the case pop the value from the measurement of the cord
                    measurement = None
                    cord_id = None
                    for i in range(len(measurements_bayesian[(Callpath("main"), Metric("runtime"))])):
                        if measurements_bayesian[(Callpath("main"), Metric("runtime"))][i].coordinate == cord:
                            cord_id = i
                            x = measurements_bayesian[(Callpath("main"), Metric("runtime"))][i].values
                            if len(x) > 0:
                                new_value = x[0]
                                x = np.delete(x, 0)
                                measurements_bayesian[(Callpath("main"), Metric("runtime"))][i].values = x
                            break
                    
                    # pop value from cord in remaining points list that has been selected as best next point
                    remaining_points_bayesian[cord].pop(0)
                    
                    # pop cord from remaining points when no value left anymore
                    if len(measurements_bayesian[(Callpath("main"), Metric("runtime"))][cord_id].values) == 0:
                        remaining_points_bayesian.pop(cord)
                    
                except KeyError:
                    pass

                # update the number of additional points used
                add_points_bayesian += 1

                # add this point to the gpr experiment
                #experiment_bayesian_base = create_experiment2(selected_points_bayesian, experiment_bayesian_base, len(experiment_bayesian_base.parameters), parameters, 0, 0)
                experiment_bayesian_base = self.create_experiment(cord, experiment_bayesian_base, new_value)

            # if there are no suitable measurement points found
            # break the while True loop
            else:
                break
        
    # cost used of the gpr strategy
    current_cost = calculate_selected_point_cost2(selected_points_bayesian, experiment_bayesian_base, 0, 0)
    #current_cost = self.calculate_selected_point_cost(experiment_bayesian_base)
    percentage_cost_bayesian = current_cost / (total_cost / 100)
    if percentage_cost_bayesian >= 99.9:
        percentage_cost_bayesian = 100
    #print("percentage_cost_bayesian:",percentage_cost_bayesian)
    
    # additionally used data points (exceeding the base requirement of the sparse modeler)
    add_points_bayesian_container.append(add_points_bayesian)
    
    # create model using point selection of gpr strategy
    model_bayesian, _ = self.get_extrap_model(experiment_bayesian_base)
    #print("Model GPR:",model_bayesian)

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

    prediction_bayesian = eval(model_bayesian)
    #print("prediction_bayesian:",prediction_bayesian)

    # get the percentage error for the gpr strategy
    if percentage_cost_bayesian <= self.budget:
        error_bayesian = abs(self.percentage_error(actual, prediction_bayesian))
    else:
        error_bayesian = 100
    #print("error_bayesian:",error_bayesian)

    # increment accuracy bucket for gpr strategy
    acurracy_bucket_counter_bayesian = self.increment_accuracy_bucket(acurracy_bucket_counter_bayesian, error_bayesian)






    # save the results of this worker to return them to the main process
    result_container["acurracy_bucket_counter_full"] = acurracy_bucket_counter_full
    result_container["acurracy_bucket_counter_generic"] = acurracy_bucket_counter_generic
    result_container["acurracy_bucket_counter_gpr"] = acurracy_bucket_counter_gpr
    result_container["acurracy_bucket_counter_hybrid"] = acurracy_bucket_counter_hybrid

    result_container["base_point_cost"] = base_point_cost

        
    if percentage_cost_generic <= budget:
        result_container["generic_possible"] = True
    else:
        result_container["generic_possible"] = False
    
    if percentage_cost_gpr <= budget:
        result_container["gpr_possible"] = True
    else:
        result_container["gpr_possible"] = False
        
    if percentage_cost_hybrid <= budget:
        result_container["hybrid_possible"] = True
    else:
        result_container["hybrid_possible"] = False
        
        
    shared_dict[callpath_id] = result_container
    