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
        plot_name = "paper_plot_points.pdf"
    
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

    points_generic_2 = []
    points_gpr_2 = []
    points_hybrid_2 = []
    
    points_generic_3 = []
    points_gpr_3 = []
    points_hybrid_3 = []
    
    points_generic_4 = []
    points_gpr_4 = []
    points_hybrid_4 = []

    base_points_2 = []
    all_points_2 = []
    
    base_points_3 = []
    all_points_3 = []
    
    base_points_4 = []
    all_points_4 = []

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

        points_generic_2.append(json_data["mean_add_points_generic"])
        points_gpr_2.append(json_data["mean_add_points_gpr"])
        points_hybrid_2.append(json_data["mean_add_points_hybrid"])
        
        all_points_2.append(25*reps)
        base_points_2.append(json_data["min_points"])
    
    for i in range(len(files_5_3)):
        json_file_path = files_5_3[i]
        json_data = read_json_file(json_file_path)

        points_generic_3.append(json_data["mean_add_points_generic"])
        points_gpr_3.append(json_data["mean_add_points_gpr"])
        points_hybrid_3.append(json_data["mean_add_points_hybrid"])
        
        all_points_3.append(125*reps)
        base_points_3.append(json_data["min_points"])
    
    for i in range(len(files_5_4)):
        json_file_path = files_5_4[i]
        json_data = read_json_file(json_file_path)

        points_generic_4.append(json_data["mean_add_points_generic"])
        points_gpr_4.append(json_data["mean_add_points_gpr"])
        points_hybrid_4.append(json_data["mean_add_points_hybrid"])
        
        all_points_4.append(625*reps)
        base_points_4.append(json_data["min_points"])

    y_values_list_points_2 = [
        all_points_2,
        points_generic_2,
        points_gpr_2,
        points_hybrid_2,
        base_points_2
    ]
    
    y_values_list_points_3 = [
        all_points_3,
        points_generic_3,
        points_gpr_3,
        points_hybrid_3,
        base_points_3
    ]
    
    y_values_list_points_4 = [
        all_points_4,
        points_generic_4,
        points_gpr_4,
        points_hybrid_4,
        base_points_4
    ]
    
    labels_points = ['Full matrix', 'CPF strategy', 'GPR strategy', 'Hybrid strategy', 'Minimum points required $\\bar{p}_{min}$']

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
        #"text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": "Helvetica",
        "font.size": 12
    })
    
    # create the figure environment including subplots
    cm = 1/2.54 
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18.5*cm, 4*cm), sharex=True)
    
    ls=["-",'dotted','--',':','dashdot']
    lw = [1,1.5,1.5,4,1.5]
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "dimgray"]
    ax1.set_xscale("symlog")
    for y_values, label in zip(y_values_list_points_2, labels_points):
        if style_counter == 0:
            ax1.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax1.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax1.set_ylabel('Mean number of points\n used for modelnig $\\bar{p}$')
    ax1.grid(alpha=0.3)
    ax1.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    ax1.set_yticks(np.arange(0, 25*reps+10, 10))
    ax1.set_xlim(0,120)
    ax1.set_xlabel('$m=2$')
    
    ls=["-",'dotted','--',':','dashdot']
    lw = [1,1.5,1.5,4,1.5]
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "dimgray"]
    ax2.set_xscale("symlog")
    for y_values, label in zip(y_values_list_points_3, labels_points):
        if style_counter == 0:
            ax2.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax2.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    #ax2.set_ylabel('Mean number of points\n used for modelnig $\\bar{p}$')
    ax2.grid(alpha=0.3)
    ax2.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    ax2.set_yticks(np.arange(0, 125*reps+10, 50))
    ax2.set_xlim(0,120)
    ax2.set_xlabel('$m=3$')
    
    ls=["-",'dotted','--',':','dashdot']
    lw = [1,1.5,1.5,4,1.5]
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "dimgray"]
    ax3.set_xscale("symlog")
    for y_values, label in zip(y_values_list_points_4, labels_points):
        if style_counter == 0:
            ax3.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax3.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    #ax3.set_ylabel('Mean number of points\n used for modelnig $\\bar{p}$')
    ax3.grid(alpha=0.3)
    ax3.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    ax3.set_yticks(np.arange(0, 625*reps+10, 250))
    ax3.set_xlim(0,120)
    ax3.set_xlabel('$m=4$')
    ax32 = ax3.twinx() 
    ax32.set_ylabel("$n=\pm5\%$")
    ax32.tick_params(right = False)
    ax32.set_yticks([])
    
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=5, bbox_to_anchor=(0.5, 1.2), frameon=False, fontsize=8, columnspacing=0.8)
    
    fig.text(0.5, -0.08, 'Allowed modeling budget $b$ [%]', ha='center', fontsize=8)
    
    fig.tight_layout(pad=0.2)
    plt.savefig(plot_name, bbox_inches="tight")
    plt.show()
    plt.close()

if __name__ == '__main__':
    main()