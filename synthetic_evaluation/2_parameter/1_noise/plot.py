import json
import os
from matplotlib import pyplot as plt
import numpy as np
import argparse
from natsort import natsorted

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def find_files(folder_path):
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(file_path)
    return file_list

def plot_accuracy(x_values, y_values_list, labels, bucket):
    ls=['-','--',':','-']
    lw = [2,3,5,2]
    plt.xscale("symlog")
    #plt.xlim(0.1, 25)
    style_counter = 0
    for y_values, label in zip(y_values_list, labels):
        if style_counter == 0:
            plt.plot(100, y_values[len(y_values)-1], label=label, marker="D", linestyle = 'None',)
        else:
            plt.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7)
        style_counter += 1
    plt.xlabel('Allowed Modeling Budget [%]')
    plt.ylabel('Models in '+str(bucket)+'% accuracy bucket [%]')
    plt.legend()
    plt.savefig('accuracy_'+str(bucket)+'.png')
    plt.show()
    plt.close()

def plot_cost(x_values, y_values_list, labels, bucket):
    min_y_values = []
    max_y_values = []
    ls=['-','--',':','-']
    lw = [2,3,5,3]
    style_counter = 0
    for y_values, label in zip(y_values_list, labels):
        plt.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7)
        min_y_values.append(np.min(y_values))
        max_y_values.append(np.max(y_values))
        style_counter += 1
    min_y_value = np.min(min_y_values)
    max_y_value = np.max(max_y_values)
    temp = list(plt.yticks()[0])
    temp.append(min_y_value)
    temp.append(max_y_value)
    plt.yticks(temp)
    #plt.yticks(list(plt.yticks()[0]) + max_y_value)
    temp = list(plt.xticks()[0])
    temp.append(1)
    plt.xticks(temp)
    plt.ylim(min_y_value-3,100)
    plt.xlim(1,100)
    plt.xlabel('Allowed Modeling Budget [%]')
    plt.ylabel('Mean Used Modeling Budget [%]')
    plt.legend(loc='upper left')
    plt.savefig('cost.png')
    plt.show()
    plt.close()

def plot_selected_points(x_values, y_values_list, labels, bucket):
    ls=['-','--',':','-']
    lw = [2,3,5,2]
    style_counter = 0
    for y_values, label in zip(y_values_list, labels):
        plt.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7)
        style_counter += 1
    plt.ylabel('Mean Number of Points Used for Modelnig')
    plt.xlabel('Allowed Modeling Budget [%]')
    temp = list(plt.yticks()[0])
    temp.append(9)
    temp.append(25)
    plt.yticks(temp)
    temp = list(plt.xticks()[0])
    temp.append(1)
    plt.xticks(temp)
    plt.xlim(1,100)
    plt.ylim(8.5,25)
    plt.legend(loc='center right')
    plt.savefig('additional_points.png')
    plt.show()
    plt.close()

def main():

    # Create the argument parser
    parser = argparse.ArgumentParser(description='Plotting tool for analysis.')

    # Add the argument
    parser.add_argument('--bucket', type=str, help='The bucket type.', choices=["5","10","15","20"], default="20", required=False)

    # Parse the command-line arguments
    args = parser.parse_args()

    # Extract the argument value
    bucket = args.bucket
    
    folder_path = "analysis_results/"
    files = find_files(folder_path)
    #print("DEBUG:",len(files))

    budget_values = []
    full_values = []
    generic_values = []
    gpr_values = []
    hybrid_values = []

    generic_costs = []
    gpr_costs = []
    hybrid_costs = []

    points_generic = []
    points_gpr = []
    points_hybrid = []

    base_point_costs = []
    base_points = []

    files = natsorted(files)
    #print("DEBUG:",len(files))

    for i in range(len(files)):
        json_file_path = files[i]
        json_data = read_json_file(json_file_path)

        budget_values.append(json_data["budget"])
        full_values.append(json_data["percentage_bucket_counter_full"][bucket])
        generic_values.append(json_data["percentage_bucket_counter_generic"][bucket])
        gpr_values.append(json_data["percentage_bucket_counter_gpr"][bucket])
        hybrid_values.append(json_data["percentage_bucket_counter_hybrid"][bucket])

        generic_costs.append(json_data["mean_budget_gpr"])
        gpr_costs.append(json_data["mean_budget_gpr"])
        hybrid_costs.append(json_data["mean_budget_hybrid"])

        points_generic.append(json_data["mean_add_points_generic"]+json_data["min_points"])
        points_gpr.append(json_data["mean_add_points_gpr"]+json_data["min_points"])
        points_hybrid.append(json_data["mean_add_points_hybrid"]+json_data["min_points"])

        base_point_costs.append(json_data["base_point_cost"])

        base_points.append(json_data["min_points"])

    # Example usage
    y_values_list = [
        full_values,
        generic_values,
        gpr_values,
        hybrid_values
    ]
    y_values_list2 = [
        generic_costs,
        gpr_costs,
        hybrid_costs,
        base_point_costs
    ]
    y_values_list3 = [
        points_generic,
        points_gpr,
        points_hybrid,
        base_points
    ]

    # points
    #print(np.max(points_generic))
    #print(np.max(points_gpr))
    #print(np.max(points_hybrid))

    # costs
    #print(np.max(generic_costs))
    #print(np.max(gpr_costs))
    #print(np.max(hybrid_costs))

    labels = ['full', 'generic', 'gpr', 'hybrid']
    labels2 = ['generic', 'gpr', 'hybrid', 'base point cost']
    labels3 = ['generic', 'gpr', 'hybrid', 'base points']

    plot_accuracy(budget_values, y_values_list, labels, bucket)
    plot_cost(budget_values, y_values_list2, labels2, bucket)
    plot_selected_points(budget_values, y_values_list3, labels3, bucket)

    #print("DEBUG:",labels2)

    

if __name__ == '__main__':
    main()