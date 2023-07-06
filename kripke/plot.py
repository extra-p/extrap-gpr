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

def plot_lines(x_values, y_values_list, labels, bucket):
    for y_values, label in zip(y_values_list, labels):
        plt.plot(x_values, y_values, label=label)
    plt.xlabel('Modeling Budget [%]')
    plt.ylabel('Models in '+str(bucket)+'% accuracy bucket [%]')
    plt.legend()
    plt.savefig('accuracy.png')
    plt.show()

def plot_lines2(x_values, y_values_list, labels):
    for y_values, label in zip(y_values_list, labels):
        plt.plot(x_values, y_values, label=label)
    plt.xlabel('Modeling Budget [%]')
    plt.ylabel('Used Budget [%]')
    plt.legend()
    plt.savefig('cost.png')
    plt.show()

def plot_lines3(x_values, y_values_list, labels):
    for y_values, label in zip(y_values_list, labels):
        plt.plot(x_values, y_values, label=label)
        #print("DEBUG:",label)
    plt.xlabel('Number of additional points used for modelnig')
    plt.ylabel('Used Budget [%]')
    plt.legend()
    plt.savefig('additional_points.png')
    plt.show()

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

        points_generic.append(json_data["mean_add_points_generic"])
        points_gpr.append(json_data["mean_add_points_gpr"])
        points_hybrid.append(json_data["mean_add_points_hybrid"])

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
        hybrid_costs
    ]
    y_values_list3 = [
        points_generic,
        points_gpr,
        points_hybrid
    ]
    labels = ['full', 'generic', 'gpr', 'hybrid']
    labels2 = ['generic', 'gpr', 'hybrid']

    plot_lines(budget_values, y_values_list, labels, bucket)
    plot_lines2(budget_values, y_values_list2, labels2)
    plot_lines3(budget_values, y_values_list3, labels2)

    #print("DEBUG:",labels2)

    

if __name__ == '__main__':
    main()