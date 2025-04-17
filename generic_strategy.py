import math
import copy
import random
import extrap
from extrap.entities.callpath import Callpath
from extrap.entities.metric import Metric
from extrap.entities.coordinate import Coordinate
import numpy as np

def add_additional_point_generic(remaining_points, selected_coord_list):
    remaining_points = copy.deepcopy(remaining_points)
    selected_coord_list = copy.deepcopy(selected_coord_list)
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

    return remaining_points, selected_coord_list, temp

def add_additional_point_random(remaining_points, selected_coord_list, measurements_random, nr_reps):
    remaining_points = copy.deepcopy(remaining_points)
    selected_coord_list = copy.deepcopy(selected_coord_list)

    # choose a random point from the remaining point list
    random_key = random.choice(list(remaining_points.keys()))
    random_value = remaining_points[random_key]

    # get the cost of the new measurement value
    new_point_cost = random_value[0]

    index_measurement_value = nr_reps - len(random_value)

    # get the actual measurement value
    for i in range(len(measurements_random[(Callpath("main"), Metric("runtime"))])):
        if measurements_random[(Callpath("main"), Metric("runtime"))][i].coordinate == random_key:
            new_measurement_value = measurements_random[(Callpath("main"), Metric("runtime"))][i].values[index_measurement_value]
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


def add_additional_point_grid(remaining_points, selected_coord_list, new_point):
    remaining_points = copy.deepcopy(remaining_points)
    selected_coord_list = copy.deepcopy(selected_coord_list)

    #print("old:",selected_coord_list)
    selected_coord_list.append(Coordinate(new_point))
    #print("new:",selected_coord_list)

    # calc the cost of the new point
    cost_values = remaining_points[Coordinate(new_point)]
    #print("DEBUG cost_values:", cost_values)
    new_point_cost = np.sum(cost_values)
    #print("DEBUG new_point_cost:", new_point_cost)

    #print("old:", remaining_points)
    # remove this point from the remaining points list
    try:
        del remaining_points[Coordinate(new_point)]
    except ValueError as e:
        print(e)
    #print("new:", remaining_points)

    return remaining_points, selected_coord_list, new_point_cost