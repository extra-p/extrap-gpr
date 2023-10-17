import json
import os
import matplotlib
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

def main():
    
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Plotting tool for analysis.')

    # Add the argument
    parser.add_argument('--path', type=str, help='The path to the results.', required=False)
    parser.add_argument('--name', type=str, help='Set name of the plot.', required=False)
    parser.add_argument('--reps', type=int, default=4, help='Set the number of repetitions per measurement point.', required=False)

    # Parse the command-line arguments
    args = parser.parse_args()
    
    reps = args.reps

    if args.path:
        folder_path = args.path
    else:
        folder_path = "analysis_results/"
        
    if args.name:
        plot_name = args.name+".png"
    else:
        plot_name = "single_plot.png"
    
    #folder_path = "analysis_results/"
    files = find_files(folder_path)
    #print("DEBUG:",len(files))

    x_values = []

    generic_costs = []
    gpr_costs = []
    hybrid_costs = []

    base_point_costs = []
    base_points = []
    
    all_points = []

    files = natsorted(files)
    #print("DEBUG:",len(files))

    for i in range(len(files)):
        json_file_path = files[i]
        json_data = read_json_file(json_file_path)

        x_values.append(json_data["budget"])
        
        generic_costs.append(json_data["budget"]-json_data["mean_budget_generic"])
        gpr_costs.append(json_data["budget"]-json_data["mean_budget_gpr"])
        hybrid_costs.append(json_data["budget"]-json_data["mean_budget_hybrid"])
        
        base_point_costs.append(json_data["base_point_cost"])
        
    y_values_list_cost = [
        generic_costs,
        gpr_costs,
        hybrid_costs,
    ]

    labels_cost = ['CPF strategy', 'GPR strategy', 'Hybrid strategy']
    
    # create the figure environment including subplots
    fig, ax1 = plt.subplots(1,1, figsize=(6,4))
    fig.suptitle("Evaluation results $m=4, n=\\pm1\\%$")
    
    # plot the cost
    ls=['dotted','--',':','dashdot']
    lw = [2,2,5,2]
    colors = ["blue", "red", "orange", "dimgray"]
    zorders=[7,6,5,4]
    style_counter = 0
    #ax1.yscale("symlog")
    for y_values, label in zip(y_values_list_cost, labels_cost):
        ax1.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, zorder=zorders[style_counter], color=colors[style_counter])
        style_counter += 1
    #ax1.plot(x_values, x_values, label="Optimal budget usage", linestyle='-', color="black", linewidth=2, alpha=1, zorder=4)
    #ax1.fill_between(x_values, y_values_list_cost[1], y_values_list_cost[0], color="green", where=np.array(y_values_list_cost[0]) < np.array(y_values_list_cost[1]), alpha=0.3, label='GPR better than CPF', zorder=3, hatch="x", interpolate=True)
    #ax1.fill_between(x_values, y_values_list_cost[1], y_values_list_cost[0], color="red", where=np.array(y_values_list_cost[1]) < np.array(y_values_list_cost[0]), alpha=0.3, label='GPR worse than CPF', zorder=3, hatch="+", interpolate=True)
    ax1.grid(alpha=0.3)
    #ax1.set_yticks(np.arange(0, 110, 10))
    ax1.set_xticks([1,10,20,30,40,50,60,70,80,90,100])
    #ax1.set_ylim(0,100)
    ax1.set_xlim(0,100)
    ax1.set_xlabel('Allowed modeling budget $b$ [%]')
    ax1.set_ylabel('Mean unused modeling budget $\\bar{b}_{nu}$ [%]')
    ax1.legend(loc='upper left', prop={'size': 8}).set_zorder(2)

    fig.tight_layout(pad=2.0)
    plt.savefig(plot_name)
    plt.show()
    plt.close()

if __name__ == '__main__':
    main()