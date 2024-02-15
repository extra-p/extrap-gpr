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
        plot_name = "paper_plot_case_studies.pdf"
    
    ###########
    # FASTEST #
    ###########
    
    path_1 = "fastest/filtered/analysis_results"
    files_1 = find_files(path_1)
    files_1 = natsorted(files_1)
    
    x_values_fastest = []
    full_values_fastest = []
    generic_values_fastest = []
    gpr_values_fastest = []
    hybrid_values_fastest = []
    generic_costs_fastest = []
    gpr_costs_fastest = []
    hybrid_costs_fastest = []
    base_point_costs_fastest = []
    points_generic_fastest = []
    points_gpr_fastest = []
    points_hybrid_fastest = []
    base_points_fastest = []
    all_points_fastest = []
    
    nr_func_modeled_fastest = 0

    for i in range(len(files_1)):
        json_file_path = files_1[i]
        json_data = read_json_file(json_file_path)
        
        if i == len(files_1)-1:
            nr_func_modeled_fastest = json_data["nr_func_modeled_gpr"]

        x_values_fastest.append(json_data["budget"])
        full_values_fastest.append(json_data["percentage_bucket_counter_full"]["10"])
        generic_values_fastest.append(json_data["percentage_bucket_counter_generic"]["10"])
        gpr_values_fastest.append(json_data["percentage_bucket_counter_gpr"]["10"])
        hybrid_values_fastest.append(json_data["percentage_bucket_counter_hybrid"]["10"])

        generic_costs_fastest.append(json_data["budget"]-json_data["mean_budget_generic"])
        gpr_costs_fastest.append(json_data["budget"]-json_data["mean_budget_gpr"])
        hybrid_costs_fastest.append(json_data["budget"]-json_data["mean_budget_hybrid"])
        base_point_costs_fastest.append(json_data["base_point_cost"])
        
        points_generic_fastest.append(json_data["mean_add_points_generic"])
        points_gpr_fastest.append(json_data["mean_add_points_gpr"])
        points_hybrid_fastest.append(json_data["mean_add_points_hybrid"])
        all_points_fastest.append(25*5)
        base_points_fastest.append(json_data["min_points"])
        
    y_values_list_acc_fastest = [
        full_values_fastest ,
        generic_values_fastest ,
        gpr_values_fastest ,
        hybrid_values_fastest
    ]
    y_values_list_points_fastest = [
        all_points_fastest,
        points_generic_fastest,
        points_gpr_fastest,
        points_hybrid_fastest,
    ]
    y_values_list_costs_fastest = [
        generic_costs_fastest,
        gpr_costs_fastest,
        hybrid_costs_fastest,
    ]

    print("fastest")
    a = max(generic_costs_fastest)
    b = max(gpr_costs_fastest)
    print(a,b)
    print(a/b)
    
    ###########
    # KRIPKE #
    ###########

    path_2 = "kripke/all/analysis_results"
    files_2 = find_files(path_2)
    files_2 = natsorted(files_2)

    x_values_kripke = []
    full_values_kripke = []
    generic_values_kripke = []
    gpr_values_kripke = []
    hybrid_values_kripke = []
    generic_costs_kripke = []
    gpr_costs_kripke = []
    hybrid_costs_kripke = []
    base_point_costs_kripke = []
    points_generic_kripke = []
    points_gpr_kripke = []
    points_hybrid_kripke = []
    base_points_kripke = []
    all_points_kripke = []
    
    nr_func_modeled_kripke = 0

    for i in range(len(files_2)):
        json_file_path = files_2[i]
        json_data = read_json_file(json_file_path)
        
        if i == len(files_1)-1:
            nr_func_modeled_kripke = json_data["nr_func_modeled_gpr"]

        x_values_kripke.append(json_data["budget"])
        full_values_kripke.append(json_data["percentage_bucket_counter_full"]["10"])
        generic_values_kripke.append(json_data["percentage_bucket_counter_generic"]["10"])
        gpr_values_kripke.append(json_data["percentage_bucket_counter_gpr"]["10"])
        hybrid_values_kripke.append(json_data["percentage_bucket_counter_hybrid"]["10"])

        generic_costs_kripke.append(json_data["budget"]-json_data["mean_budget_generic"])
        gpr_costs_kripke.append(json_data["budget"]-json_data["mean_budget_gpr"])
        hybrid_costs_kripke.append(json_data["budget"]-json_data["mean_budget_hybrid"])
        base_point_costs_kripke.append(json_data["base_point_cost"])
        
        points_generic_kripke.append(json_data["mean_add_points_generic"])
        points_gpr_kripke.append(json_data["mean_add_points_gpr"])
        points_hybrid_kripke.append(json_data["mean_add_points_hybrid"])
        all_points_kripke.append((150-1)*5)
        base_points_kripke.append(json_data["min_points"])
        
    y_values_list_acc_kripke = [
        full_values_kripke ,
        generic_values_kripke ,
        gpr_values_kripke ,
        hybrid_values_kripke
    ]
    y_values_list_points_kripke = [
        all_points_kripke,
        points_generic_kripke,
        points_gpr_kripke,
        points_hybrid_kripke,
    ]
    y_values_list_costs_kripke = [
        generic_costs_kripke,
        gpr_costs_kripke,
        hybrid_costs_kripke,
    ]

    print("kripke")
    a = max(generic_costs_kripke)
    b = max(gpr_costs_kripke)
    print(a,b)
    print(a/b)
    
    ###########
    # LULESH  #
    ###########

    path_3 = "lulesh/lichtenberg/all/analysis_results"
    files_3 = find_files(path_3)
    files_3 = natsorted(files_3)

    x_values_lulesh = []
    full_values_lulesh = []
    generic_values_lulesh = []
    gpr_values_lulesh = []
    hybrid_values_lulesh = []
    generic_costs_lulesh = []
    gpr_costs_lulesh = []
    hybrid_costs_lulesh = []
    base_point_costs_lulesh = []
    points_generic_lulesh = []
    points_gpr_lulesh = []
    points_hybrid_lulesh = []
    base_points_lulesh = []
    all_points_lulesh = []
    
    nr_func_modeled_lulesh = 0

    for i in range(len(files_3)):
        json_file_path = files_3[i]
        json_data = read_json_file(json_file_path)
        
        if i == len(files_1)-1:
            nr_func_modeled_lulesh = json_data["nr_func_modeled_gpr"]

        x_values_lulesh.append(json_data["budget"])
        full_values_lulesh.append(json_data["percentage_bucket_counter_full"]["10"])
        generic_values_lulesh.append(json_data["percentage_bucket_counter_generic"]["10"])
        gpr_values_lulesh.append(json_data["percentage_bucket_counter_gpr"]["10"])
        hybrid_values_lulesh.append(json_data["percentage_bucket_counter_hybrid"]["10"])

        generic_costs_lulesh.append(json_data["budget"]-json_data["mean_budget_generic"])
        gpr_costs_lulesh.append(json_data["budget"]-json_data["mean_budget_gpr"])
        hybrid_costs_lulesh.append(json_data["budget"]-json_data["mean_budget_hybrid"])
        base_point_costs_lulesh.append(json_data["base_point_cost"])
        
        points_generic_lulesh.append(json_data["mean_add_points_generic"])
        points_gpr_lulesh.append(json_data["mean_add_points_gpr"])
        points_hybrid_lulesh.append(json_data["mean_add_points_hybrid"])
        all_points_lulesh.append(25*5)
        base_points_lulesh.append(json_data["min_points"])
        
    y_values_list_acc_lulesh = [
        full_values_lulesh ,
        generic_values_lulesh ,
        gpr_values_lulesh ,
        hybrid_values_lulesh
    ]
    y_values_list_points_lulesh = [
        all_points_lulesh,
        points_generic_lulesh,
        points_gpr_lulesh,
        points_hybrid_lulesh,
    ]
    y_values_list_costs_lulesh = [
        generic_costs_lulesh,
        gpr_costs_lulesh,
        hybrid_costs_lulesh,
    ]

    print("lulesh")
    a = max(generic_costs_lulesh)
    b = max(gpr_costs_lulesh)
    print(a,b)
    print(a/b)
    
    ###########
    # MiniFE #
    ###########

    path_4 = "minife/lichtenberg/all/analysis_results"
    files_4 = find_files(path_4)
    files_4 = natsorted(files_4)

    x_values_minife = []
    full_values_minife = []
    generic_values_minife = []
    gpr_values_minife = []
    hybrid_values_minife = []
    generic_costs_minife = []
    gpr_costs_minife = []
    hybrid_costs_minife = []
    base_point_costs_minife = []
    points_generic_minife = []
    points_gpr_minife = []
    points_hybrid_minife = []
    base_points_minife = []
    all_points_minife = []
    
    nr_func_modeled_minife = 0

    for i in range(len(files_4)):
        json_file_path = files_4[i]
        json_data = read_json_file(json_file_path)
        
        if i == len(files_1)-1:
            nr_func_modeled_minife = json_data["nr_func_modeled_gpr"]

        x_values_minife.append(json_data["budget"])
        full_values_minife.append(json_data["percentage_bucket_counter_full"]["10"])
        generic_values_minife.append(json_data["percentage_bucket_counter_generic"]["10"])
        gpr_values_minife.append(json_data["percentage_bucket_counter_gpr"]["10"])
        hybrid_values_minife.append(json_data["percentage_bucket_counter_hybrid"]["10"])

        generic_costs_minife.append(json_data["budget"]-json_data["mean_budget_generic"])
        gpr_costs_minife.append(json_data["budget"]-json_data["mean_budget_gpr"])
        hybrid_costs_minife.append(json_data["budget"]-json_data["mean_budget_hybrid"])
        base_point_costs_minife.append(json_data["base_point_cost"])
        
        points_generic_minife.append(json_data["mean_add_points_generic"])
        points_gpr_minife.append(json_data["mean_add_points_gpr"])
        points_hybrid_minife.append(json_data["mean_add_points_hybrid"])
        all_points_minife.append(25*5)
        base_points_minife.append(json_data["min_points"])
        
    y_values_list_acc_minife = [
        full_values_minife ,
        generic_values_minife ,
        gpr_values_minife ,
        hybrid_values_minife
    ]
    y_values_list_points_minife = [
        all_points_minife,
        points_generic_minife,
        points_gpr_minife,
        points_hybrid_minife,
    ]
    y_values_list_costs_minife = [
        generic_costs_minife,
        gpr_costs_minife,
        hybrid_costs_minife,
    ]

    print("minife")
    a = max(generic_costs_minife)
    b = max(gpr_costs_minife)
    print(a,b)
    print(a/b)
    
    ###########
    # Quicksilver #
    ###########

    path_5 = "quicksilver/lichtenberg/filtered/analysis_results"
    files_5 = find_files(path_5)
    files_5 = natsorted(files_5)

    x_values_quicksilver = []
    full_values_quicksilver = []
    generic_values_quicksilver = []
    gpr_values_quicksilver = []
    hybrid_values_quicksilver = []
    generic_costs_quicksilver = []
    gpr_costs_quicksilver = []
    hybrid_costs_quicksilver = []
    base_point_costs_quicksilver = []
    points_generic_quicksilver = []
    points_gpr_quicksilver = []
    points_hybrid_quicksilver = []
    base_points_quicksilver = []
    all_points_quicksilver = []
    
    nr_func_modeled_quicksilver = 0

    for i in range(len(files_5)):
        json_file_path = files_5[i]
        json_data = read_json_file(json_file_path)
        
        if i == len(files_1)-1:
            nr_func_modeled_quicksilver = json_data["nr_func_modeled_gpr"]

        x_values_quicksilver.append(json_data["budget"])
        full_values_quicksilver.append(json_data["percentage_bucket_counter_full"]["10"])
        generic_values_quicksilver.append(json_data["percentage_bucket_counter_generic"]["10"])
        gpr_values_quicksilver.append(json_data["percentage_bucket_counter_gpr"]["10"])
        hybrid_values_quicksilver.append(json_data["percentage_bucket_counter_hybrid"]["10"])

        generic_costs_quicksilver.append(json_data["budget"]-json_data["mean_budget_generic"])
        gpr_costs_quicksilver.append(json_data["budget"]-json_data["mean_budget_gpr"])
        hybrid_costs_quicksilver.append(json_data["budget"]-json_data["mean_budget_hybrid"])
        base_point_costs_quicksilver.append(json_data["base_point_cost"])
        
        points_generic_quicksilver.append(json_data["mean_add_points_generic"])
        points_gpr_quicksilver.append(json_data["mean_add_points_gpr"])
        points_hybrid_quicksilver.append(json_data["mean_add_points_hybrid"])
        all_points_quicksilver.append(503)
        base_points_quicksilver.append(json_data["min_points"])
        
    y_values_list_acc_quicksilver = [
        full_values_quicksilver ,
        generic_values_quicksilver ,
        gpr_values_quicksilver ,
        hybrid_values_quicksilver
    ]
    y_values_list_points_quicksilver = [
        all_points_quicksilver,
        points_generic_quicksilver,
        points_gpr_quicksilver,
        points_hybrid_quicksilver,
    ]
    y_values_list_costs_quicksilver = [
        generic_costs_quicksilver,
        gpr_costs_quicksilver,
        hybrid_costs_quicksilver,
    ]

    print("quicksilver")
    a = max(generic_costs_quicksilver)
    b = max(gpr_costs_quicksilver)
    print(a,b)
    print(a/b)

    ###########
    # relearn #
    ###########

    path_6 = "relearn/all/analysis_results"
    files_6 = find_files(path_6)
    files_6 = natsorted(files_6)

    x_values_relearn = []
    full_values_relearn = []
    generic_values_relearn = []
    gpr_values_relearn = []
    hybrid_values_relearn = []
    generic_costs_relearn = []
    gpr_costs_relearn = []
    hybrid_costs_relearn = []
    base_point_costs_relearn = []
    points_generic_relearn = []
    points_gpr_relearn = []
    points_hybrid_relearn = []
    base_points_relearn = []
    all_points_relearn = []
    
    nr_func_modeled_relearn = 0

    for i in range(len(files_6)):
        json_file_path = files_6[i]
        json_data = read_json_file(json_file_path)
        
        if i == len(files_6)-1:
            nr_func_modeled_relearn = json_data["nr_func_modeled_gpr"]

        x_values_relearn.append(json_data["budget"])
        full_values_relearn.append(json_data["percentage_bucket_counter_full"]["10"])
        generic_values_relearn.append(json_data["percentage_bucket_counter_generic"]["10"])
        gpr_values_relearn.append(json_data["percentage_bucket_counter_gpr"]["10"])
        hybrid_values_relearn.append(json_data["percentage_bucket_counter_hybrid"]["10"])

        generic_costs_relearn.append(json_data["budget"]-json_data["mean_budget_generic"])
        gpr_costs_relearn.append(json_data["budget"]-json_data["mean_budget_gpr"])
        hybrid_costs_relearn.append(json_data["budget"]-json_data["mean_budget_hybrid"])
        base_point_costs_relearn.append(json_data["base_point_cost"])
        
        points_generic_relearn.append(json_data["mean_add_points_generic"])
        points_gpr_relearn.append(json_data["mean_add_points_gpr"])
        points_hybrid_relearn.append(json_data["mean_add_points_hybrid"])
        all_points_relearn.append((25-1)*2)
        base_points_relearn.append(json_data["min_points"])
        
    y_values_list_acc_relearn = [
        full_values_relearn ,
        generic_values_relearn ,
        gpr_values_relearn ,
        hybrid_values_relearn
    ]
    y_values_list_points_relearn = [
        all_points_relearn,
        points_generic_relearn,
        points_gpr_relearn,
        points_hybrid_relearn,
    ]
    y_values_list_costs_relearn = [
        generic_costs_relearn,
        gpr_costs_relearn,
        hybrid_costs_relearn,
    ]

    print("relearn")
    a = max(generic_costs_relearn)
    b = max(gpr_costs_relearn)
    print(a,b)
    print(a/b)
    
    labels_acc = ['Full matrix', 'CPF strategy', 'GPR strategy', 'Hybrid strategy']
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
    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6), (ax7, ax8, ax9), (ax10, ax11, ax12), (ax13, ax14, ax15), (ax16, ax17, ax18)) = plt.subplots(6, 3, figsize=(20*cm, 20*cm))
    
    ls=["-",'dotted','--',':','-']
    lw = [1,1.5,1.5,4,1.5]
    ax1.set_xlim(x_values_fastest[0], 103)
    ax4.set_ylim(0, np.max(y_values_list_acc_fastest)+5)
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc_fastest, labels_acc, colors):
        if style_counter == 0:
            ax1.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax1.plot(x_values_fastest, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax1.grid(alpha=0.3, which='major')
    ax1.grid(alpha=0.3, which='minor')
    ax1.set_yticks(np.arange(0, np.max(y_values_list_acc_fastest)+5, 10))
    ax1.set_xticks([20,30,40,50,60,70,80,90,100])
    ax1.set_ylabel('Models within\n $\pm10\%$ at $P_{eval}$ [\%]')
    #ax1.tick_params(axis='x', labelsize=7)
    #ax1.tick_params(axis='y', labelsize=7)
    
    ls=['dotted','--',':','dashdot']
    lw = [1.5,1.5,4,1.5]
    colors = ["blue", "red", "orange", "dimgray"]
    zorders=[7,6,5,4]
    style_counter = 0
    for y_values, label in zip(y_values_list_costs_fastest, labels_cost):
        ax2.plot(x_values_fastest, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, zorder=zorders[style_counter], color=colors[style_counter])
        style_counter += 1
    ax2.grid(alpha=0.3, which='major')
    ax2.grid(alpha=0.3, which='minor')
    ax2.set_xticks([20,30,40,50,60,70,80,90,100])
    ax2.set_yticks(np.arange(0, np.max(y_values_list_costs_fastest)+5, 5))
    ax2.set_ylabel('Mean unused\n budget $\\bar{B}_{nu}$ [\%]')
    ax2.set_xlim(x_values_fastest[0],100)
    #ax2.tick_params(axis='x', labelsize=7)
    #ax2.tick_params(axis='y', labelsize=7)
    
    ls=["-",'dotted','--',':','dashdot']
    lw = [1,1.5,1.5,4,1.5]
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "dimgray"]
    for y_values, label in zip(y_values_list_points_fastest, labels_points):
        if style_counter == 0:
            ax3.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax3.plot(x_values_fastest, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax3.grid(alpha=0.3, which='major')
    ax3.grid(alpha=0.3, which='minor')
    ax3.set_xlim(x_values_fastest[0],103)
    ax3.set_ylim(50,135)
    ax3.set_yticks(np.arange(50, 140, 15))
    ax3.set_xticks([20,30,40,50,60,70,80,90,100])
    ax3.set_ylabel('Mean no. points\n used for modelnig $\\bar{k}$')
    locmin = matplotlib.ticker.LogLocator(base=10.0, subs=(0.1,0.2,0.3,0.4,0.5,0.6, 0.7, 0.8, 0.9 )) 
    ax3.xaxis.set_minor_locator(locmin)
    ax3.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax3.grid(alpha=0.3, which='major')
    ax3.grid(alpha=0.3, which='minor')
    ax32 = ax3.twinx() 
    ax32.set_ylabel("\\textbf{FASTEST}\n $\\bar{B}_{min}="+str(x_values_fastest[0])+"\%$\n"+str(nr_func_modeled_fastest)+" kernels\n $\\bar{n}=8.17\%$", fontsize=8)
    ax32.tick_params(right = False)
    ax32.set_yticks([])
    #ax3.tick_params(axis='x', labelsize=7)
    #ax3.tick_params(axis='y', labelsize=7)
    
    ##########
    # Kripke #
    ##########
    
    ls=["-",'dotted','--',':','-']
    lw = [1,1.5,1.5,4,1.5]
    ax4.set_xlim(x_values_kripke[0], 103)
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc_kripke, labels_acc, colors):
        if style_counter == 0:
            ax4.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax4.plot(x_values_kripke, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax4.grid(alpha=0.3, which='major')
    ax4.grid(alpha=0.3, which='minor')
    ax4.set_ylim(0, np.max(y_values_list_acc_kripke)+5)
    ax4.set_yticks(np.arange(0, np.max(y_values_list_acc_kripke)+5, 20))
    ax4.set_xticks([2,10,20,30,40,50,60,70,80,90,100])
    ax4.set_ylabel('Models within\n $\pm10\%$ at $P_{eval}$ [\%]')
    
    ls=['dotted','--',':','dashdot']
    lw = [1.5,1.5,4,1.5]
    colors = ["blue", "red", "orange", "dimgray"]
    zorders=[7,6,5,4]
    style_counter = 0
    for y_values, label in zip(y_values_list_costs_kripke, labels_cost):
        ax5.plot(x_values_kripke, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, zorder=zorders[style_counter], color=colors[style_counter])
        style_counter += 1
    ax5.grid(alpha=0.3, which='major')
    ax5.grid(alpha=0.3, which='minor')
    ax5.set_xticks([2,10,20,30,40,50,60,70,80,90,100])
    ax5.set_yticks(np.arange(0, np.nanmax(y_values_list_costs_kripke)+2.5, 1.5))
    ax5.set_ylabel('Mean unused\n budget $\\bar{B}_{nu}$ [\%]')
    ax5.set_xlim(x_values_kripke[0],100)
    
    ls=["-",'dotted','--',':','dashdot']
    lw = [1,1.5,1.5,4,1.5]
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "dimgray"]
    for y_values, label in zip(y_values_list_points_kripke, labels_points):
        if style_counter == 0:
            ax6.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax6.plot(x_values_kripke, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax6.grid(alpha=0.3, which='major')
    ax6.grid(alpha=0.3, which='minor')
    ax6.set_xlim(x_values_kripke[0],103)
    ax6.set_ylim(400,800)
    ax6.set_yticks(np.arange(400, ((150-1)*5)+75, 75))
    ax6.set_xticks([2,10,20,30,40,50,60,70,80,90,100])
    ax6.set_ylabel('Mean no. points\n used for modelnig $\\bar{k}$')
    ax6.grid(alpha=0.3, which='major')
    ax6.grid(alpha=0.3, which='minor')
    ax62 = ax6.twinx() 
    ax62.set_ylabel("\\textbf{Kripke}\n $\\bar{B}_{min}="+str(int(x_values_kripke[0]))+"\%$\n"+str(nr_func_modeled_kripke)+" kernels\n $\\bar{n}=2.17\%$", fontsize=8)
    ax62.tick_params(right = False)
    ax62.set_yticks([])
    
    ##########
    # LULESH #
    ##########
    
    ls=["-",'dotted','--',':','-']
    lw = [1,1.5,1.5,4,1.5]
    ax7.set_xlim(x_values_lulesh[0], 103)
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc_lulesh, labels_acc, colors):
        if style_counter == 0:
            ax7.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax7.plot(x_values_lulesh, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax7.grid(alpha=0.3, which='major')
    ax7.grid(alpha=0.3, which='minor')
    ax7.set_yticks(np.arange(0, np.max(y_values_list_acc_lulesh)+5, 10))
    ax7.set_xticks([20,30,40,50,60,70,80,90,100])
    ax7.set_ylabel('Models within\n $\pm10\%$ at $P_{eval}$ [\%]')
    #ax7.tick_params(axis='x', labelsize=7)
    #ax7.tick_params(axis='y', labelsize=7)
    
    ls=['dotted','--',':','dashdot']
    lw = [1.5,1.5,4,1.5]
    colors = ["blue", "red", "orange", "dimgray"]
    zorders=[7,6,5,4]
    style_counter = 0
    for y_values, label in zip(y_values_list_costs_lulesh, labels_cost):
        ax8.plot(x_values_lulesh, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, zorder=zorders[style_counter], color=colors[style_counter])
        style_counter += 1
    ax8.grid(alpha=0.3, which='major')
    ax8.grid(alpha=0.3, which='minor')
    ax8.set_xticks([20,30,40,50,60,70,80,90,100])
    ax8.set_yticks(np.arange(0, np.max(y_values_list_costs_lulesh)+5, 5))
    ax8.set_ylabel('Mean unused\n budget $\\bar{B}_{nu}$ [\%]')
    ax8.set_xlim(x_values_lulesh[0],100)
    #ax8.tick_params(axis='x', labelsize=7)
    #ax8.tick_params(axis='y', labelsize=7)
    
    ls=["-",'dotted','--',':','dashdot']
    lw = [1,1.5,1.5,4,1.5]
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "dimgray"]
    for y_values, label in zip(y_values_list_points_lulesh, labels_points):
        if style_counter == 0:
            ax9.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax9.plot(x_values_lulesh, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax9.grid(alpha=0.3, which='major')
    ax9.grid(alpha=0.3, which='minor')
    ax9.set_xlim(x_values_lulesh[0],103)
    ax9.set_ylim(40,130)
    ax9.set_yticks(np.arange(40, 25*5+20, 20))
    ax9.set_xticks([20,30,40,50,60,70,80,90,100])
    ax9.set_ylabel('Mean no. points\n used for modelnig $\\bar{k}$')
    locmin = matplotlib.ticker.LogLocator(base=10.0, subs=(0.1,0.2,0.3,0.4,0.5,0.6, 0.7, 0.8, 0.9 )) 
    ax9.xaxis.set_minor_locator(locmin)
    ax9.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax9.grid(alpha=0.3, which='major')
    ax9.grid(alpha=0.3, which='minor')
    ax92 = ax9.twinx() 
    ax92.set_ylabel("\\textbf{LULESH}\n $\\bar{B}_{min}="+str(int(x_values_lulesh[0]))+"\%$\n 7 kernels\n $\\bar{n}=4.72\%$", fontsize=8)
    ax92.tick_params(right = False)
    ax92.set_yticks([])
    #ax9.tick_params(axis='x', labelsize=7)
    #ax9.tick_params(axis='y', labelsize=7)
    
    ##########
    # MiniFE #
    ##########
    
    ls=["-",'dotted','--',':','-']
    lw = [1,1.5,1.5,4,1.5]
    ax10.set_xlim(x_values_minife[0], 103)
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc_minife, labels_acc, colors):
        if style_counter == 0:
            ax10.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax10.plot(x_values_minife, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax10.grid(alpha=0.3, which='major')
    ax10.grid(alpha=0.3, which='minor')
    ax10.set_yticks(np.arange(0, np.max(y_values_list_acc_minife)+5, 5))
    ax10.set_xticks([20,30,40,50,60,70,80,90,100])
    ax10.set_ylabel('Models within\n $\pm10\%$ at $P_{eval}$ [\%]')
    
    ls=['dotted','--',':','dashdot']
    lw = [1.5,1.5,4,1.5]
    colors = ["blue", "red", "orange", "dimgray"]
    zorders=[7,6,5,4]
    style_counter = 0
    for y_values, label in zip(y_values_list_costs_minife, labels_cost):
        ax11.plot(x_values_minife, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, zorder=zorders[style_counter], color=colors[style_counter])
        style_counter += 1
    ax11.grid(alpha=0.3, which='major')
    ax11.grid(alpha=0.3, which='minor')
    ax11.set_xticks([20,30,40,50,60,70,80,90,100])
    ax11.set_yticks(np.arange(0, np.max(y_values_list_costs_minife)+5, 2.5))
    ax11.set_ylabel('Mean unused\n budget $\\bar{B}_{nu}$ [\%]')
    ax11.set_xlim(x_values_minife[0],100)
    
    ls=["-",'dotted','--',':','dashdot']
    lw = [1,1.5,1.5,4,1.5]
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "dimgray"]
    for y_values, label in zip(y_values_list_points_minife, labels_points):
        if style_counter == 0:
            ax12.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax12.plot(x_values_minife, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax12.grid(alpha=0.3, which='major')
    ax12.grid(alpha=0.3, which='minor')
    ax12.set_xlim(x_values_minife[0],103)
    ax12.set_ylim(35,130)
    ax12.set_yticks(np.arange(35, 25*5+20, 20))
    ax12.set_xticks([20,30,40,50,60,70,80,90,100])
    ax12.set_ylabel('Mean no. points\n used for modelnig $\\bar{k}$')
    locmin = matplotlib.ticker.LogLocator(base=10.0, subs=(0.1,0.2,0.3,0.4,0.5,0.6, 0.7, 0.8, 0.9 )) 
    ax12.xaxis.set_minor_locator(locmin)
    ax12.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax12.grid(alpha=0.3, which='major')
    ax12.grid(alpha=0.3, which='minor')
    ax122 = ax12.twinx() 
    ax122.set_ylabel("\\textbf{MiniFE}\n $\\bar{B}_{min}="+str(x_values_minife[0])+"\%$\n 23 kernels\n $\\bar{n}=10.22\%$", fontsize=8)
    ax122.tick_params(right = False)
    ax122.set_yticks([])
    
    ###############
    # Quicksilver #
    ###############
    
    ls=["-",'dotted','--',':','-']
    lw = [1,1.5,1.5,4,1.5]
    #ax13.set_xscale("symlog")
    ax13.set_xlim(x_values_quicksilver[0], 103)
    ax13.set_ylim(0, 110)
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc_quicksilver, labels_acc, colors):
        if style_counter == 0:
            ax13.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax13.plot(x_values_quicksilver, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax13.set_yticks(np.arange(0, 110, 20))
    ax13.set_xticks([1,10,20,30,40,50,60,70,80,90,100])
    #ax13.set_xticks([0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    ax13.set_ylabel('Models within\n $\pm10\%$ at $P_{eval}$ [\%]')
    #locmin = matplotlib.ticker.LogLocator(base=10.0, subs=(0.1,0.2,0.3,0.4,0.5,0.6, 0.7, 0.8, 0.9 )) 
    #ax13.xaxis.set_minor_locator(locmin)
    #ax13.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax13.grid(alpha=0.3, which='major')
    ax13.grid(alpha=0.3, which='minor')
    #ax13.tick_params(axis='x', labelsize=7)
    
    ls=['dotted','--',':','dashdot']
    lw = [1.5,1.5,4,1.5]
    colors = ["blue", "red", "orange", "dimgray"]
    zorders=[7,6,5,4]
    ax14.set_xlim(x_values_quicksilver[0], 100)
    style_counter = 0
    for y_values, label in zip(y_values_list_costs_quicksilver, labels_cost):
        ax14.plot(x_values_quicksilver, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, zorder=zorders[style_counter], color=colors[style_counter])
        style_counter += 1
    ax14.grid(alpha=0.3, which='major')
    ax14.grid(alpha=0.3, which='minor')
    ax14.set_xticks([1,10,20,30,40,50,60,70,80,90,100])
    ax14.set_yticks(np.arange(0, np.max(y_values_list_costs_quicksilver)+5, 5))
    ax14.set_ylabel('Mean unused\n budget $\\bar{B}_{nu}$ [\%]')
    #ax14.tick_params(axis='x', labelsize=7)
    
    ls=["-",'dotted','--',':','dashdot']
    lw = [1,1.5,1.5,4,1.5]
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "dimgray"]
    for y_values, label in zip(y_values_list_points_quicksilver, labels_points):
        if style_counter == 0:
            ax15.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax15.plot(x_values_quicksilver, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax15.grid(alpha=0.3, which='major')
    ax15.grid(alpha=0.3, which='minor')
    ax15.set_xlim(x_values_quicksilver[0],103)
    ax15.set_ylim(75,525)
    ax15.set_yticks(np.arange(75, 503+55, 75))
    ax15.set_xticks([1,10,20,30,40,50,60,70,80,90,100])
    ax15.set_ylabel('Mean no. points\n used for modelnig $\\bar{k}$')
    #ax15.tick_params(axis='x', labelsize=7)
    ax152 = ax15.twinx() 
    ax152.set_ylabel("\\textbf{Quicksilver}\n $\\bar{B}_{min}="+str(x_values_quicksilver[0])+"\%$\n"+str(nr_func_modeled_quicksilver)+" kernels\n $\\bar{n}=5.66\%$", fontsize=8)
    ax152.tick_params(right = False)
    ax152.set_yticks([])
    
    ###########
    # RELeARN #
    ###########
    
    ls=["-",'dotted','--',':','-']
    lw = [1,1.5,1.5,4,1.5]
    ax16.set_xlim(x_values_relearn[0], 103)
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc_relearn, labels_acc, colors):
        if style_counter == 0:
            ax16.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax16.plot(x_values_relearn, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax16.grid(alpha=0.3, which='major')
    ax16.grid(alpha=0.3, which='minor')
    ax16.set_yticks(np.arange(0, 120, 20))
    ax16.set_xticks([20,30,40,50,60,70,80,90,100])
    ax16.set_ylabel('Models within\n $\pm10\%$ at $P_{eval}$ [\%]')
    #ax16.tick_params(axis='x', labelsize=7)
    
    ls=['dotted','--',':','dashdot']
    lw = [1.5,1.5,4,1.5]
    colors = ["blue", "red", "orange", "dimgray"]
    zorders=[7,6,5,4]
    style_counter = 0
    for y_values, label in zip(y_values_list_costs_relearn, labels_cost):
        ax17.plot(x_values_relearn, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, zorder=zorders[style_counter], color=colors[style_counter])
        style_counter += 1
    ax17.grid(alpha=0.3, which='major')
    ax17.grid(alpha=0.3, which='minor')
    ax17.set_xticks([20,30,40,50,60,70,80,90,100])
    ax17.set_yticks(np.arange(0, np.max(y_values_list_costs_relearn)+5, 5))
    ax17.set_ylabel('Mean unused\n budget $\\bar{B}_{nu}$ [\%]')
    ax17.set_xlim(x_values_relearn[0],100)
    #ax17.tick_params(axis='x', labelsize=7)
    
    ls=["-",'dotted','--',':','dashdot']
    lw = [1,1.5,1.5,4,1.5]
    style_counter = 0
    zorders=[5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "dimgray"]
    for y_values, label in zip(y_values_list_points_relearn, labels_points):
        if style_counter == 0:
            ax18.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax18.plot(x_values_relearn, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    ax18.grid(alpha=0.3, which='major')
    ax18.grid(alpha=0.3, which='minor')
    ax18.set_xlim(x_values_relearn[0],103)
    ax18.set_ylim(15,50)
    ax18.set_yticks(np.arange(15, ((25-1)*2)+5, 5))
    ax18.set_xticks([20,30,40,50,60,70,80,90,100])
    ax18.set_ylabel('Mean no. points\n used for modelnig $\\bar{k}$')
    locmin = matplotlib.ticker.LogLocator(base=10.0, subs=(0.1,0.2,0.3,0.4,0.5,0.6, 0.7, 0.8, 0.9 )) 
    ax18.xaxis.set_minor_locator(locmin)
    ax18.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax18.grid(alpha=0.3, which='major')
    ax18.grid(alpha=0.3, which='minor')
    #ax18.tick_params(axis='x', labelsize=7)
    ax182 = ax18.twinx() 
    ax182.set_ylabel("\\textbf{RELeARN}\n $\\bar{B}_{min}="+str(x_values_relearn[0])+"\%$\n"+str(nr_func_modeled_relearn)+" kernels\n $\\bar{n}=4.5\%$", fontsize=8)
    ax182.tick_params(right = False)
    ax182.set_yticks([])
    
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=5, bbox_to_anchor=(0.5, 1.04), frameon=False, fontsize=9, columnspacing=0.8)
    
    fig.text(0.5, -0.025, 'Allowed modeling budget $B$ [\%]', ha='center', fontsize=9)
    
    fig.tight_layout(pad=0.2)
    plt.savefig(plot_name, bbox_inches="tight")
    plt.show()
    plt.close()

if __name__ == '__main__':
    main()