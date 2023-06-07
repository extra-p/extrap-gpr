import math
import copy

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

    return remaining_points, selected_coord_list
