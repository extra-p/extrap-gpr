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

def plot_accuracy(x_values, y_values_list_acc, labels, bucket):
    ls=["-",'dotted','--',':','-']
    lw = [1,2,2,5,2]
    #plt.rc('text', usetex=True)
    #plt.rcParams["font.size"] = 9.5
    plt.xscale("symlog")
    plt.xlim(0.1, 120)
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc, labels, colors):
        if style_counter == 0:
            plt.scatter(100, y_values[len(y_values)-1], label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            plt.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    plt.fill_between(x_values, y_values_list_acc[1], y_values_list_acc[2], color="green", where=np.array(y_values_list_acc[2]) > np.array(y_values_list_acc[1]), alpha=0.4, label='GPR better than CPF', hatch="x", interpolate=True)
    plt.fill_between(x_values, y_values_list_acc[2], y_values_list_acc[1], color="red", where=np.array(y_values_list_acc[2]) < np.array(y_values_list_acc[1]), alpha=0.4, label='GPR worse than CPF', hatch="+", zorder=5, interpolate=True)
    plt.grid(alpha=0.3)
    plt.yticks(np.arange(0, 100, 10))
    plt.xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    plt.xlabel('Allowed modeling budget $b$ [%]')
    plt.ylabel('Models in '+str(bucket)+'% accuracy bucket [%]')
    plt.legend(loc="lower right")
    plt.savefig('accuracy_'+str(bucket)+'.png')
    plt.show()
    plt.close()

def plot_cost(x_values, y_values_list_acc, labels, bucket):
    min_y_values = []
    max_y_values = []
    ls=['dotted','--',':','dashdot']
    lw = [3,3,6,3]
    colors = ["blue", "red", "orange", "dimgray"]
    zorders=[4,3,2,1]
    style_counter = 0
    #plt.xscale("symlog")
    for y_values, label in zip(y_values_list_acc, labels):
        plt.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, zorder=zorders[style_counter], color=colors[style_counter])
        min_y_values.append(np.min(y_values))
        max_y_values.append(np.max(y_values))
        style_counter += 1
    plt.plot(x_values, x_values, label="Optimal budget usage", linestyle='-', color="black", linewidth=2, alpha=1, zorder=3)
    plt.fill_between(x_values, y_values_list_acc[1], y_values_list_acc[0], color="green", where=np.array(y_values_list_acc[0]) < np.array(y_values_list_acc[1]), alpha=0.3, label='GPR better than CPF', zorder=1, hatch="x", interpolate=True)
    plt.fill_between(x_values, y_values_list_acc[1], y_values_list_acc[0], color="red", where=np.array(y_values_list_acc[1]) < np.array(y_values_list_acc[0]), alpha=0.3, label='GPR worse than CPF', zorder=0, hatch="+", interpolate=True)
    plt.grid(alpha=0.3)
    min_y_value = np.min(min_y_values)
    max_y_value = np.max(max_y_values)
    temp = list(plt.yticks()[0])
    temp.append(min_y_value)
    temp.append(max_y_value)
    plt.yticks(temp)
    temp = list(plt.xticks()[0])
    temp.append(1)
    plt.yticks(np.arange(0, 110, 10))
    plt.xticks([1,10,20,30,40,50,60,70,80,90,100])
    plt.ylim(0,100)
    plt.xlim(0,100)
    plt.xlabel('Allowed modeling budget $b$ [%]')
    plt.ylabel('Mean used modeling budget $\\bar{b}_{u}$ [%]')
    plt.legend(loc='upper left').set_zorder(2)
    #plt.savefig('cost.pdf')
    plt.savefig('cost.png')
    plt.show()
    plt.close()

def plot_selected_points(x_values, y_values_list_acc, labels, bucket):
    ls=["-",'dotted','--',':','dashdot']
    lw = [1,2,2,5,2]
    #plt.rc('text', usetex=True)
    #plt.rcParams["font.size"] = 9.5
    #plt.xlim(0.1, 120)
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "dimgray"]
    plt.xscale("symlog")
    for y_values, label in zip(y_values_list_acc, labels):
        if style_counter == 0:
            plt.scatter(100, y_values[len(y_values)-1], label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            plt.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    plt.ylabel('Mean number of points used for modelnig $\\bar{p}$')
    plt.xlabel('Allowed modeling budget $b$ [%]')
    plt.grid(alpha=0.3)
    plt.yticks(np.arange(0, 110, 10))
    plt.xticks([1,10,20,30,40,50,60,70,80,90,100])
    plt.xlim(0,120)
    plt.legend(loc='upper left')
    plt.savefig('additional_points.png')
    plt.show()
    plt.close()

def main():
    
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Plotting tool for analysis.')

    # Add the argument
    parser.add_argument('--bucket', type=str, help='The bucket type.', choices=["5","10","15","20"], default="20", required=False)

    # Add the argument
    parser.add_argument('--path', type=str, help='The path to the results.', required=False)

    # Parse the command-line arguments
    args = parser.parse_args()

    # Extract the argument value
    bucket = args.bucket
    
    if args.path:
        folder_path = args.path
    else:
        folder_path = "analysis_results/"
    
    #folder_path = "analysis_results/"
    files = find_files(folder_path)
    #print("DEBUG:",len(files))

    x_values = []
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
    
    all_points = []

    files = natsorted(files)
    #print("DEBUG:",len(files))

    for i in range(len(files)):
        json_file_path = files[i]
        json_data = read_json_file(json_file_path)

        x_values.append(json_data["budget"])
        full_values.append(json_data["percentage_bucket_counter_full"][bucket])
        generic_values.append(json_data["percentage_bucket_counter_generic"][bucket])
        gpr_values.append(json_data["percentage_bucket_counter_gpr"][bucket])
        hybrid_values.append(json_data["percentage_bucket_counter_hybrid"][bucket])

        generic_costs.append(json_data["mean_budget_generic"])
        gpr_costs.append(json_data["mean_budget_gpr"])
        hybrid_costs.append(json_data["mean_budget_hybrid"])

        points_generic.append(json_data["mean_add_points_generic"]+json_data["min_points"])
        points_gpr.append(json_data["mean_add_points_gpr"]+json_data["min_points"])
        points_hybrid.append(json_data["mean_add_points_hybrid"]+json_data["min_points"])
        
        all_points.append(100)

        base_point_costs.append(json_data["base_point_cost"])

        base_points.append(json_data["min_points"])
        
    # Example usage
    y_values_list_acc = [
        full_values,
        generic_values,
        gpr_values,
        hybrid_values
    ]
    y_values_list_cost = [
        generic_costs,
        gpr_costs,
        hybrid_costs,
        base_point_costs
    ]
    y_values_list_points = [
        all_points,
        points_generic,
        points_gpr,
        points_hybrid,
        base_points
    ]

    labels_acc = ['Full matrix', 'CPF strategy', 'GPR strategy', 'Hybrid strategy']
    labels_cost = ['CPF strategy', 'GPR strategy', 'Hybrid strategy', 'Min. modeling requirement $\\bar{b}_{min}$']
    labels_points = ['All available points', 'CPF strategy', 'GPR strategy', 'Hybrid strategy', 'Min. points required $\\bar{p}_{min}$']

    # create the figure environment including subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(6, 12))
    fig.suptitle("Evaluation results 1% noise")
    
    # plot the accuracy
    ls=["-",'dotted','--',':','-']
    lw = [1,2,2,5,2]
    ax1.set_xscale("symlog")
    ax1.set_xlim(0.1, 120)
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc, labels_acc, colors):
        if style_counter == 0:
            ax1.scatter(100, y_values[len(y_values)-1], label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax1.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax1.fill_between(x_values, y_values_list_acc[1], y_values_list_acc[2], color="green", where=np.array(y_values_list_acc[2]) > np.array(y_values_list_acc[1]), alpha=0.4, label='GPR better than CPF', hatch="x", interpolate=True)
    ax1.fill_between(x_values, y_values_list_acc[2], y_values_list_acc[1], color="red", where=np.array(y_values_list_acc[2]) < np.array(y_values_list_acc[1]), alpha=0.4, label='GPR worse than CPF', hatch="+", zorder=5, interpolate=True)
    ax1.grid(alpha=0.3)
    ax1.set_yticks(np.arange(0, 100, 10))
    ax1.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    ax1.set_xlabel('Allowed modeling budget $b$ [%]')
    ax1.set_ylabel('Models in '+str(bucket)+'% accuracy bucket [%]')
    ax1.legend(loc="lower right")
    
    # plot the cost
    ls=['dotted','--',':','dashdot']
    lw = [3,3,6,3]
    colors = ["blue", "red", "orange", "dimgray"]
    zorders=[4,3,2,1]
    style_counter = 0
    #ax2.xscale("symlog")
    for y_values, label in zip(y_values_list_cost, labels_cost):
        ax2.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, zorder=zorders[style_counter], color=colors[style_counter])
        style_counter += 1
    ax2.plot(x_values, x_values, label="Optimal budget usage", linestyle='-', color="black", linewidth=2, alpha=1, zorder=3)
    ax2.fill_between(x_values, y_values_list_cost[1], y_values_list_cost[0], color="green", where=np.array(y_values_list_cost[0]) < np.array(y_values_list_cost[1]), alpha=0.3, label='GPR better than CPF', zorder=1, hatch="x", interpolate=True)
    ax2.fill_between(x_values, y_values_list_cost[1], y_values_list_cost[0], color="red", where=np.array(y_values_list_cost[1]) < np.array(y_values_list_cost[0]), alpha=0.3, label='GPR worse than CPF', zorder=0, hatch="+", interpolate=True)
    ax2.grid(alpha=0.3)
    ax2.set_yticks(np.arange(0, 110, 10))
    ax2.set_xticks([1,10,20,30,40,50,60,70,80,90,100])
    ax2.set_ylim(0,100)
    ax2.set_xlim(0,100)
    ax2.set_xlabel('Allowed modeling budget $b$ [%]')
    ax2.set_ylabel('Mean used modeling budget $\\bar{b}_{u}$ [%]')
    ax2.legend(loc='upper left').set_zorder(2)
    
    # plot the points
    ls=["-",'dotted','--',':','dashdot']
    lw = [1,2,2,5,2]
    #ax3.xlim(0.1, 120)
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "dimgray"]
    ax3.set_xscale("symlog")
    for y_values, label in zip(y_values_list_points, labels_points):
        if style_counter == 0:
            ax3.scatter(100, y_values[len(y_values)-1], label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax3.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax3.set_ylabel('Mean number of points used for modelnig $\\bar{p}$')
    ax3.set_xlabel('Allowed modeling budget $b$ [%]')
    ax3.grid(alpha=0.3)
    ax3.set_yticks(np.arange(0, 110, 10))
    ax3.set_xticks([1,10,20,30,40,50,60,70,80,90,100])
    ax3.set_xlim(0,120)
    ax3.legend(loc='upper left')
    
    plt.savefig('single_plot.png')
    plt.show()
    plt.close()

if __name__ == '__main__':
    main()