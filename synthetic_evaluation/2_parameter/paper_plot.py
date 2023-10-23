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
    parser.add_argument('--name', type=str, help='Set name of the plot.', required=False)
    parser.add_argument('--reps', type=int, default=4, help='Set the number of repetitions per measurement point.', required=False)

    # Parse the command-line arguments
    args = parser.parse_args()
    
    reps = args.reps
        
    if args.name:
        plot_name = args.name+".pdf"
    else:
        plot_name = "paper_plot.pdf"
    
    path_1 = "1_noise/final/analysis_results"
    path_2 = "2_noise/final/analysis_results"
    path_5 = "5_noise/final/analysis_results"
    path_10 = "10_noise/final/analysis_results"
    
    files_1 = find_files(path_1)
    files_2 = find_files(path_2)
    files_5 = find_files(path_5)
    files_10 = find_files(path_10)
    
    x_values = []
    full_values_1 = []
    generic_values_1 = []
    gpr_values_1 = []
    hybrid_values_1 = []
    
    full_values_2 = []
    generic_values_2 = []
    gpr_values_2 = []
    hybrid_values_2 = []
    
    full_values_5 = []
    generic_values_5 = []
    gpr_values_5 = []
    hybrid_values_5 = []
    
    full_values_10 = []
    generic_values_10 = []
    gpr_values_10 = []
    hybrid_values_10 = []

    generic_costs = []
    gpr_costs = []
    hybrid_costs = []

    points_generic = []
    points_gpr = []
    points_hybrid = []

    base_point_costs = []
    base_points = []
    
    all_points = []

    files_1 = natsorted(files_1)
    files_2 = natsorted(files_2)
    files_5 = natsorted(files_5)
    files_10 = natsorted(files_10)
    #print("DEBUG:",len(files))

    for i in range(len(files_1)):
        json_file_path = files_1[i]
        json_data = read_json_file(json_file_path)

        x_values.append(json_data["budget"])
        full_values_1.append(json_data["percentage_bucket_counter_full"]["5"])
        generic_values_1.append(json_data["percentage_bucket_counter_generic"]["5"])
        gpr_values_1.append(json_data["percentage_bucket_counter_gpr"]["5"])
        hybrid_values_1.append(json_data["percentage_bucket_counter_hybrid"]["5"])

        generic_costs.append(json_data["mean_budget_generic"])
        gpr_costs.append(json_data["mean_budget_gpr"])
        hybrid_costs.append(json_data["mean_budget_hybrid"])

        points_generic.append(json_data["mean_add_points_generic"])
        points_gpr.append(json_data["mean_add_points_gpr"])
        points_hybrid.append(json_data["mean_add_points_hybrid"])
        
        all_points.append(25*reps)

        base_point_costs.append(json_data["base_point_cost"])

        base_points.append(json_data["min_points"])
        
    for i in range(len(files_2)):
        json_file_path = files_2[i]
        json_data = read_json_file(json_file_path)

        #x_values.append(json_data["budget"])
        full_values_2.append(json_data["percentage_bucket_counter_full"]["5"])
        generic_values_2.append(json_data["percentage_bucket_counter_generic"]["5"])
        gpr_values_2.append(json_data["percentage_bucket_counter_gpr"]["5"])
        hybrid_values_2.append(json_data["percentage_bucket_counter_hybrid"]["5"])

        generic_costs.append(json_data["mean_budget_generic"])
        gpr_costs.append(json_data["mean_budget_gpr"])
        hybrid_costs.append(json_data["mean_budget_hybrid"])

        points_generic.append(json_data["mean_add_points_generic"])
        points_gpr.append(json_data["mean_add_points_gpr"])
        points_hybrid.append(json_data["mean_add_points_hybrid"])
        
        #all_points.append(25*reps)
        #base_point_costs.append(json_data["base_point_cost"])
        #base_points.append(json_data["min_points"])
        
    for i in range(len(files_5)):
        json_file_path = files_5[i]
        json_data = read_json_file(json_file_path)

        #x_values.append(json_data["budget"])
        full_values_5.append(json_data["percentage_bucket_counter_full"]["5"])
        generic_values_5.append(json_data["percentage_bucket_counter_generic"]["5"])
        gpr_values_5.append(json_data["percentage_bucket_counter_gpr"]["5"])
        hybrid_values_5.append(json_data["percentage_bucket_counter_hybrid"]["5"])

        generic_costs.append(json_data["mean_budget_generic"])
        gpr_costs.append(json_data["mean_budget_gpr"])
        hybrid_costs.append(json_data["mean_budget_hybrid"])

        points_generic.append(json_data["mean_add_points_generic"])
        points_gpr.append(json_data["mean_add_points_gpr"])
        points_hybrid.append(json_data["mean_add_points_hybrid"])
        
        #all_points.append(25*reps)
        #base_point_costs.append(json_data["base_point_cost"])
        #base_points.append(json_data["min_points"])
        
    for i in range(len(files_10)):
        json_file_path = files_10[i]
        json_data = read_json_file(json_file_path)

        #x_values.append(json_data["budget"])
        full_values_10.append(json_data["percentage_bucket_counter_full"]["5"])
        generic_values_10.append(json_data["percentage_bucket_counter_generic"]["5"])
        gpr_values_10.append(json_data["percentage_bucket_counter_gpr"]["5"])
        hybrid_values_10.append(json_data["percentage_bucket_counter_hybrid"]["5"])

        generic_costs.append(json_data["mean_budget_generic"])
        gpr_costs.append(json_data["mean_budget_gpr"])
        hybrid_costs.append(json_data["mean_budget_hybrid"])

        points_generic.append(json_data["mean_add_points_generic"])
        points_gpr.append(json_data["mean_add_points_gpr"])
        points_hybrid.append(json_data["mean_add_points_hybrid"])
        
        #all_points.append(25*reps)
        #base_point_costs.append(json_data["base_point_cost"])
        #base_points.append(json_data["min_points"])
    
    y_values_list_acc_1 = [
        full_values_1 ,
        generic_values_1 ,
        gpr_values_1 ,
        hybrid_values_1
    ]
    y_values_list_acc_2 = [
        full_values_2,
        generic_values_2,
        gpr_values_2,
        hybrid_values_2
    ]
    y_values_list_acc_5 = [
        full_values_5,
        generic_values_5,
        gpr_values_5,
        hybrid_values_5
    ]
    y_values_list_acc_10 = [
        full_values_10,
        generic_values_10,
        gpr_values_10,
        hybrid_values_10
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

    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": "Helvetica",
    })

    # create the figure environment including subplots
    cm = 1/2.54 
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(18.415*cm, 5*cm), sharex=True, sharey=True)
    
    # plot the accuracy of bucket 5 and n=1%
    ls=["-",'dotted','--',':','-']
    lw = [1,2,2,5,2]
    ax1.set_xscale("symlog")
    ax1.set_xlim(0.1, 120)
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc_1, labels_acc, colors):
        if style_counter == 0:
            ax1.scatter(100, y_values[len(y_values)-1], label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax1.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    #ax1.fill_between(x_values, y_values_list_acc_1[1], y_values_list_acc_1[2], color="green", where=np.array(y_values_list_acc_1[2]) > np.array(y_values_list_acc_1[1]), alpha=0.4, label='GPR better than CPF', hatch="x", interpolate=True)
    #ax1.fill_between(x_values, y_values_list_acc_1[2], y_values_list_acc_1[1], color="red", where=np.array(y_values_list_acc_1[2]) < np.array(y_values_list_acc_1[1]), alpha=0.4, label='GPR worse than CPF', hatch="+", zorder=5, interpolate=True)
    ax1.grid(alpha=0.3)
    ax1.set_yticks(np.arange(0, 100, 10))
    ax1.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    ax1.set_xlabel('$n=1\%$')
    ax1.set_ylabel('Models within\n $\pm5\%$ at $P_{eval}$ [%]')
    #ax1.legend(loc="lower right", prop={'size': 8})
    
    # plot the accuracy of bucket 5 and n=2%
    ls=["-",'dotted','--',':','-']
    lw = [1,2,2,5,2]
    ax2.set_xscale("symlog")
    ax2.set_xlim(0.1, 120)
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc_2, labels_acc, colors):
        if style_counter == 0:
            ax2.scatter(100, y_values[len(y_values)-1], label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax2.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    #ax2.fill_between(x_values, y_values_list_acc_2[1], y_values_list_acc_2[2], color="green", where=np.array(y_values_list_acc_2[2]) > np.array(y_values_list_acc_2[1]), alpha=0.4, label='GPR better than CPF', hatch="x", interpolate=True)
    #ax2.fill_between(x_values, y_values_list_acc_2[2], y_values_list_acc_2[1], color="red", where=np.array(y_values_list_acc_2[2]) < np.array(y_values_list_acc_2[1]), alpha=0.4, label='GPR worse than CPF', hatch="+", zorder=5, interpolate=True)
    ax2.grid(alpha=0.3)
    ax2.set_yticks(np.arange(0, 100, 10))
    ax2.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    ax2.set_xlabel('$n=2\%$')
    #ax2.set_ylabel('Models within $\pm10\%$ at $P_{eval}$ [%]')
    #ax2.legend(loc="lower right", prop={'size': 8})
    
    # plot the accuracy of bucket 15
    ls=["-",'dotted','--',':','-']
    lw = [1,2,2,5,2]
    ax3.set_xscale("symlog")
    ax3.set_xlim(0.1, 120)
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc_5, labels_acc, colors):
        if style_counter == 0:
            ax3.scatter(100, y_values[len(y_values)-1], label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax3.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    #ax3.fill_between(x_values, y_values_list_acc_5[1], y_values_list_acc_5[2], color="green", where=np.array(y_values_list_acc_5[2]) > np.array(y_values_list_acc_5[1]), alpha=0.4, label='GPR better than CPF', hatch="x", interpolate=True)
    #ax3.fill_between(x_values, y_values_list_acc_5[2], y_values_list_acc_5[1], color="red", where=np.array(y_values_list_acc_5[2]) < np.array(y_values_list_acc_5[1]), alpha=0.4, label='GPR worse than CPF', hatch="+", zorder=5, interpolate=True)
    ax3.grid(alpha=0.3)
    ax3.set_yticks(np.arange(0, 100, 10))
    ax3.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    ax3.set_xlabel('$n=5\%$')
    #ax3.set_ylabel('Models within $\pm15\%$ at $P_{eval}$ [%]')
    #ax3.legend(loc="lower right", prop={'size': 8})
    
    # plot the accuracy of bucket 20
    ls=["-",'dotted','--',':','-']
    lw = [1,2,2,5,2]
    ax4.set_xscale("symlog")
    ax4.set_xlim(0.1, 120)
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc_10, labels_acc, colors):
        if style_counter == 0:
            ax4.scatter(100, y_values[len(y_values)-1], label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax4.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    #ax4.fill_between(x_values, y_values_list_acc_10[1], y_values_list_acc_10[2], color="green", where=np.array(y_values_list_acc_10[2]) > np.array(y_values_list_acc_10[1]), alpha=0.4, label='GPR better than CPF', hatch="x", interpolate=True)
    #ax4.fill_between(x_values, y_values_list_acc_10[2], y_values_list_acc_10[1], color="red", where=np.array(y_values_list_acc_10[2]) < np.array(y_values_list_acc_10[1]), alpha=0.4, label='GPR worse than CPF', hatch="+", zorder=5, interpolate=True)
    ax4.grid(alpha=0.3)
    ax4.set_yticks(np.arange(0, 100, 10))
    ax4.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    ax4.set_xlabel('$n=10\%$')
    #ax4.set_ylabel('Models within $\pm20\%$ at $P_{eval}$ [%]')
    #ax4.legend(loc="lower right", prop={'size': 8})
    
    """# plot the cost
    ls=['dotted','--',':','dashdot']
    lw = [2,2,5,2]
    colors = ["blue", "red", "orange", "dimgray"]
    zorders=[7,6,5,4]
    style_counter = 0
    #ax5.xscale("symlog")
    for y_values, label in zip(y_values_list_cost, labels_cost):
        ax5.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, zorder=zorders[style_counter], color=colors[style_counter])
        style_counter += 1
    ax5.plot(x_values, x_values, label="Optimal budget usage", linestyle='-', color="black", linewidth=2, alpha=1, zorder=4)
    #ax5.fill_between(x_values, y_values_list_cost[1], y_values_list_cost[0], color="green", where=np.array(y_values_list_cost[0]) < np.array(y_values_list_cost[1]), alpha=0.3, label='GPR better than CPF', zorder=3, hatch="x", interpolate=True)
    #ax5.fill_between(x_values, y_values_list_cost[1], y_values_list_cost[0], color="red", where=np.array(y_values_list_cost[1]) < np.array(y_values_list_cost[0]), alpha=0.3, label='GPR worse than CPF', zorder=3, hatch="+", interpolate=True)
    ax5.grid(alpha=0.3)
    ax5.set_yticks(np.arange(0, 110, 10))
    ax5.set_xticks([1,10,20,30,40,50,60,70,80,90,100])
    ax5.set_ylim(0,100)
    ax5.set_xlim(0,100)
    ax5.set_xlabel('Allowed modeling budget $b$ [%]')
    ax5.set_ylabel('Mean used modeling budget $\\bar{b}_{u}$ [%]')
    ax5.legend(loc='upper left', prop={'size': 8}).set_zorder(2)
    
    # plot the points
    ls=["-",'dotted','--',':','dashdot']
    lw = [1,2,2,5,2]
    #ax6.xlim(0.1, 120)
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "dimgray"]
    ax6.set_xscale("symlog")
    for y_values, label in zip(y_values_list_points, labels_points):
        if style_counter == 0:
            ax6.scatter(100, y_values[len(y_values)-1], label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax6.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax6.set_ylabel('Mean number of points used for modelnig $\\bar{p}$')
    ax6.set_xlabel('Allowed modeling budget $b$ [%]')
    ax6.grid(alpha=0.3)
    #ax6.set_yticks(np.arange(0, 110, 10))
    #ax6.set_xticks([1,10,20,30,40,50,60,70,80,90,100])
    ax6.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    ax6.set_yticks(np.arange(0, 25*reps+10, 10))
    ax6.set_xlim(0,120)
    ax6.legend(loc='lower right', prop={'size': 8})"""
    
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', prop={'size': 8}, ncol=4, bbox_to_anchor=(0.5, 1.15), frameon=False)
    
    fig.text(0.5, -0.1, 'Allowed modeling budget $b$ [%]', ha='center')
    
    fig.tight_layout(pad=-0.2)
    plt.savefig(plot_name, bbox_inches="tight")
    plt.show()
    plt.close()

if __name__ == '__main__':
    main()