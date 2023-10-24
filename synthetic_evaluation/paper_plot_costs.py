import json
import os
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import argparse
from natsort import natsorted
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import AutoMinorLocator, MultipleLocator

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
        plot_name = "paper_plot_costs.pdf"
    
    #path_1 = "2_parameter/1_noise/final/analysis_results"
    #path_2 = "2_parameter/2_noise/final/analysis_results"
    path_5 = "2_parameter/5_noise/final/analysis_results"
    #path_10 = "2_parameter/10_noise/final/analysis_results"
    
    #path_1_3 = "3_parameter/1_noise/final/analysis_results"
    #path_2_3 = "3_parameter/2_noise/final/analysis_results"
    path_5_3 = "3_parameter/5_noise/final/analysis_results"
    #path_10_3 = "3_parameter/10_noise/final/analysis_results"
    
    #path_1_4 = "4_parameter/1_noise/final/analysis_results"
    #path_2_4 = "4_parameter/2_noise/final/analysis_results"
    path_5_4 = "4_parameter/5_noise/final/analysis_results"
    #path_10_4 = "4_parameter/10_noise/final/analysis_results"
    
    #files_1 = find_files(path_1)
    #files_2 = find_files(path_2)
    files_5 = find_files(path_5)
    #files_10 = find_files(path_10)
    
    #files_1_3 = find_files(path_1_3)
    #files_2_3 = find_files(path_2_3)
    files_5_3 = find_files(path_5_3)
    #files_10_3 = find_files(path_10_3)
    
    #files_1_4 = find_files(path_1_4)
    #files_2_4 = find_files(path_2_4)
    files_5_4 = find_files(path_5_4)
    #files_10_4 = find_files(path_10_4)
    
    x_values = []

    generic_costs_2 = []
    gpr_costs_2 = []
    hybrid_costs_2 = []
    
    generic_costs_3 = []
    gpr_costs_3 = []
    hybrid_costs_3 = []
    
    generic_costs_4 = []
    gpr_costs_4 = []
    hybrid_costs_4 = []

    base_point_costs_2 = []
    base_point_costs_3 = []
    base_point_costs_4 = []

    #files_1 = natsorted(files_1)
    #files_2 = natsorted(files_2)
    files_5 = natsorted(files_5)
    #files_10 = natsorted(files_10)
    
    #files_1_3 = natsorted(files_1_3)
    #files_2_3 = natsorted(files_2_3)
    files_5_3 = natsorted(files_5_3)
    #files_10_3 = natsorted(files_10_3)
    
    #files_1_4 = natsorted(files_1_4)
    #files_2_4 = natsorted(files_2_4)
    files_5_4 = natsorted(files_5_4)
    #files_10_4 = natsorted(files_10_4)

    for i in range(len(files_5)):
        json_file_path = files_5[i]
        json_data = read_json_file(json_file_path)

        x_values.append(json_data["budget"])

        generic_costs_2.append(json_data["budget"]-json_data["mean_budget_generic"])
        gpr_costs_2.append(json_data["budget"]-json_data["mean_budget_gpr"])
        hybrid_costs_2.append(json_data["budget"]-json_data["mean_budget_hybrid"])
        base_point_costs_2.append(json_data["base_point_cost"])
        
    
    for i in range(len(files_5_3)):
        json_file_path = files_5_3[i]
        json_data = read_json_file(json_file_path)

        generic_costs_3.append(json_data["budget"]-json_data["mean_budget_generic"])
        gpr_costs_3.append(json_data["budget"]-json_data["mean_budget_gpr"])
        hybrid_costs_3.append(json_data["budget"]-json_data["mean_budget_hybrid"])
        base_point_costs_3.append(json_data["base_point_cost"])
    
    for i in range(len(files_5_4)):
        json_file_path = files_5_4[i]
        json_data = read_json_file(json_file_path)

        generic_costs_4.append(json_data["budget"]-json_data["mean_budget_generic"])
        gpr_costs_4.append(json_data["budget"]-json_data["mean_budget_gpr"])
        hybrid_costs_4.append(json_data["budget"]-json_data["mean_budget_hybrid"])
        base_point_costs_4.append(json_data["base_point_cost"])

    y_values_list_costs_2 = [
        generic_costs_2,
        gpr_costs_2,
        hybrid_costs_2,
        #base_point_costs_2
    ]
    
    y_values_list_costs_3 = [
        generic_costs_3,
        gpr_costs_3,
        hybrid_costs_3,
        #base_point_costs_3
    ]
    
    y_values_list_costs_4 = [
        generic_costs_4,
        gpr_costs_4,
        hybrid_costs_4,
        #base_point_costs_4
    ]
    
    labels_points = ['Full matrix', 'CPF strategy', 'GPR strategy', 'Hybrid strategy', 'Minimum points required $\\bar{p}_{min}$']
    labels_cost = ['CPF strategy', 'GPR strategy', 'Hybrid strategy', 'Min. modeling requirement $\\bar{b}_{min}$']
    
    SMALL_SIZE = 8
    MEDIUM_SIZE = 10
    BIGGER_SIZE = 12

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=8)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=8)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "sans-serif",
        #"font.sans-serif": "Helvetica",
        "font.size": 12
    })
    
    # create the figure environment including subplots
    cm = 1/2.54 
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18.5*cm, 4*cm), sharex=True)
    
    ls=['dotted','--',':','dashdot']
    lw = [1.5,1.5,4,1.5]
    colors = ["blue", "red", "orange", "dimgray"]
    zorders=[7,6,5,4]
    style_counter = 0
    for y_values, label in zip(y_values_list_costs_2, labels_cost):
        ax1.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, zorder=zorders[style_counter], color=colors[style_counter])
        style_counter += 1
    ax1.grid(alpha=0.3, which='major')
    ax1.grid(alpha=0.3, which='minor')
    ax1.set_xticks([1,10,20,30,40,50,60,70,80,90,100])
    ax1.set_yticks([0, 5, 10, 15, 20, 25, 30])
    ax1.set_xlim(0,100)
    ax1.set_ylabel('Mean unused modeling\n budget $\\bar{B}_{nu}$ [\%]')
    ax1.set_xlabel('$m=2$')
    
    ls=['dotted','--',':','dashdot']
    lw = [1.5,1.5,4,1.5]
    colors = ["blue", "red", "orange", "dimgray"]
    zorders=[7,6,5,4]
    style_counter = 0
    for y_values, label in zip(y_values_list_costs_3, labels_cost):
        ax2.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, zorder=zorders[style_counter], color=colors[style_counter])
        style_counter += 1
    ax2.grid(alpha=0.3, which='major')
    ax2.grid(alpha=0.3, which='minor')
    ax2.set_xticks([1,10,20,30,40,50,60,70,80,90,100])
    ax2.set_xlim(0,100)
    ax2.set_xlabel('$m=3$')
    
    ls=['dotted','--',':','dashdot']
    lw = [1.5,1.5,4,1.5]
    colors = ["blue", "red", "orange", "dimgray"]
    zorders=[7,6,5,4]
    style_counter = 0
    ax3.set_xscale("symlog")
    #ax3.set_yscale("symlog")
    for y_values, label in zip(y_values_list_costs_4, labels_cost):
        ax3.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, zorder=zorders[style_counter], color=colors[style_counter])
        style_counter += 1
    ax3.grid(alpha=0.3, which='major')
    ax3.grid(alpha=0.3, which='minor')
    #ax3.set_xticks([1,10,20,30,40,50,60,70,80,90,100])
    ax3.set_xlim(0,110)
    ax3.set_xlabel('$m=4$')
    ax3.set_xticks([0.1, 1, 10, 100])
    locmin = matplotlib.ticker.LogLocator(base=10.0, subs=(0.1,0.2,0.3,0.4,0.5,0.6, 0.7, 0.8, 0.9 )) 
    ax3.xaxis.set_minor_locator(locmin)
    ax3.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax3.grid(alpha=0.3, which='major')
    ax3.grid(alpha=0.3, which='minor')
    ax32 = ax3.twinx() 
    ax32.set_ylabel("$n=\pm5\%$")
    ax32.tick_params(right = False)
    ax32.set_yticks([])
    
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=5, bbox_to_anchor=(0.5, 1.17), frameon=False, fontsize=8, columnspacing=0.8)
    
    fig.text(0.5, -0.1, 'Allowed modeling budget $B$ [\%]', ha='center', fontsize=8)
    
    fig.tight_layout(pad=0.2)
    plt.savefig(plot_name, bbox_inches="tight")
    plt.show()
    plt.close()

if __name__ == '__main__':
    main()