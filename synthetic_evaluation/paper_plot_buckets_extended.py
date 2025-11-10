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
        plot_name = "paper_plot_buckets_extended.pdf"
    
    path_10_3 = "3_parameter/10_noise/rebuttal"
  
    files_10_3 = find_files(path_10_3)
    
    x_values = []
    full_values_1_3 = []
    generic_values_1_3 = []
    gpr_values_1_3 = []
    hybrid_values_1_3 = []
    random_values_1_3 = []
    grid_values_1_3 = []
    bayesian_values_1_3 = []
    
    full_values_2_3 = []
    generic_values_2_3 = []
    gpr_values_2_3 = []
    hybrid_values_2_3 = []
    random_values_2_3 = []
    grid_values_2_3 = []
    bayesian_values_2_3 = []
    
    full_values_5_3 = []
    generic_values_5_3 = []
    gpr_values_5_3 = []
    hybrid_values_5_3 = []
    random_values_5_3 = []
    grid_values_5_3 = []
    bayesian_values_5_3 = []
    
    full_values_10_3 = []
    generic_values_10_3 = []
    gpr_values_10_3 = []
    hybrid_values_10_3 = []
    random_values_10_3 = []
    grid_values_10_3 = []
    bayesian_values_10_3 = []

    files_10_3 = natsorted(files_10_3)

    for i in range(len(files_10_3)):
        json_file_path = files_10_3[i]
        json_data = read_json_file(json_file_path)

        x_values.append(json_data["budget"])
        full_values_1_3.append(json_data["percentage_bucket_counter_full"]["5"])
        generic_values_1_3.append(json_data["percentage_bucket_counter_generic"]["5"])
        gpr_values_1_3.append(json_data["percentage_bucket_counter_gpr"]["5"])
        hybrid_values_1_3.append(json_data["percentage_bucket_counter_hybrid"]["5"])
        random_values_1_3.append(json_data["percentage_bucket_counter_random"]["5"])
        grid_values_1_3.append(json_data["percentage_bucket_counter_grid"]["5"])
        bayesian_values_1_3.append(json_data["percentage_bucket_counter_bayesian"]["5"])
        
        full_values_2_3.append(json_data["percentage_bucket_counter_full"]["10"])
        generic_values_2_3.append(json_data["percentage_bucket_counter_generic"]["10"])
        gpr_values_2_3.append(json_data["percentage_bucket_counter_gpr"]["10"])
        hybrid_values_2_3.append(json_data["percentage_bucket_counter_hybrid"]["10"])
        random_values_2_3.append(json_data["percentage_bucket_counter_random"]["10"])
        grid_values_2_3.append(json_data["percentage_bucket_counter_grid"]["10"])
        bayesian_values_2_3.append(json_data["percentage_bucket_counter_bayesian"]["10"])
        
        full_values_5_3.append(json_data["percentage_bucket_counter_full"]["15"])
        generic_values_5_3.append(json_data["percentage_bucket_counter_generic"]["15"])
        gpr_values_5_3.append(json_data["percentage_bucket_counter_gpr"]["15"])
        hybrid_values_5_3.append(json_data["percentage_bucket_counter_hybrid"]["15"])
        random_values_5_3.append(json_data["percentage_bucket_counter_random"]["15"])
        grid_values_5_3.append(json_data["percentage_bucket_counter_grid"]["15"])
        bayesian_values_5_3.append(json_data["percentage_bucket_counter_bayesian"]["15"])
        
        full_values_10_3.append(json_data["percentage_bucket_counter_full"]["20"])
        generic_values_10_3.append(json_data["percentage_bucket_counter_generic"]["20"])
        gpr_values_10_3.append(json_data["percentage_bucket_counter_gpr"]["20"])
        hybrid_values_10_3.append(json_data["percentage_bucket_counter_hybrid"]["20"])
        random_values_10_3.append(json_data["percentage_bucket_counter_random"]["20"])
        grid_values_10_3.append(json_data["percentage_bucket_counter_grid"]["20"])
        bayesian_values_10_3.append(json_data["percentage_bucket_counter_bayesian"]["20"])
   
    y_values_list_acc_1 = [
        full_values_1_3 ,
        generic_values_1_3 ,
        gpr_values_1_3 ,
        hybrid_values_1_3,
        random_values_1_3,
        grid_values_1_3,
        bayesian_values_1_3
    ]
    y_values_list_acc_2 = [
        full_values_2_3,
        generic_values_2_3,
        gpr_values_2_3,
        hybrid_values_2_3,
        random_values_2_3,
        grid_values_2_3,
        bayesian_values_2_3
    ]
    y_values_list_acc_5 = [
        full_values_5_3,
        generic_values_5_3,
        gpr_values_5_3,
        hybrid_values_5_3,
        random_values_5_3,
        grid_values_5_3,
        bayesian_values_5_3
    ]
    y_values_list_acc_10 = [
        full_values_10_3,
        generic_values_10_3,
        gpr_values_10_3,
        hybrid_values_10_3,
        random_values_10_3,
        grid_values_10_3,
        bayesian_values_10_3
    ]
    
    print("m=3, n=+-10%")
    
    maxv_3_1 = 0
    Bv_3_1 = 0
    cpfv_3_1 = 0
    gprv_3_1 = 0
    for i in range(len(gpr_values_1_3)):
        diff = gpr_values_1_3[i] - generic_values_1_3[i]
        if diff >= maxv_3_1:
            maxv_3_1 = diff
            Bv_3_1 = x_values[i]
            cpfv_3_1 = generic_values_1_3[i]
            gprv_3_1 = gpr_values_1_3[i]
    print("max. difference GPR/CPF:",maxv_3_1,"at B=",Bv_3_1,"%.")
    print("")
    
    maxv_3_2 = 0
    Bv_3_2 = 0
    cpfv_3_2 = 0
    gprv_3_2 = 0
    for i in range(len(gpr_values_2_3)):
        diff = gpr_values_2_3[i] - generic_values_2_3[i]
        if diff >= maxv_3_2:
            maxv_3_2 = diff
            Bv_3_2 = x_values[i]
            cpfv_3_2 = generic_values_2_3[i]
            gprv_3_2 = gpr_values_2_3[i]
    print("max. difference GPR/CPF:",maxv_3_2,"at B=",Bv_3_2,"%.")
    print("")
    
    maxv_3_5 = 0
    Bv_3_5 = 0
    cpfv_3_5 = 0
    gprv_3_5 = 0
    for i in range(len(gpr_values_5_3)):
        diff = gpr_values_5_3[i] - generic_values_5_3[i]
        if diff >= maxv_3_5:
            maxv_3_5 = diff
            Bv_3_5 = x_values[i]
            cpfv_3_5 = generic_values_5_3[i]
            gprv_3_5 = gpr_values_5_3[i]
    print("max. difference GPR/CPF:",maxv_3_5,"at B=",Bv_3_5,"%.")
    print("")
    
    maxv_3_10 = 0
    Bv_3_10 = 0
    cpfv_3_10 = 0
    gprv_3_10 = 0
    for i in range(len(gpr_values_10_3)):
        diff = gpr_values_10_3[i] - generic_values_10_3[i]
        if diff >= maxv_3_10:
            maxv_3_10 = diff
            Bv_3_10 = x_values[i]
            cpfv_3_10 = generic_values_10_3[i]
            gprv_3_10 = gpr_values_10_3[i]
    print("max. difference GPR/CPF:",maxv_3_10,"at B=",Bv_3_10,"%.")
    print("")
    
    labels_acc = ['GPR', 'CPF', 'Hybrid', "Random", "Grid", "Bayesian", 'Full matrix']
    
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
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(18.5*cm, 4*cm), sharex=True, sharey=True)

    ls=["-",(0,(1,1)),'-',':',(0, (3,1,1,1,1,1)), "-.", "--"]
    lw = [1,1.5,1.5,3,1.5, 1.5, 1.5]
    ax1.set_xscale("symlog")
    ax1.set_xlim(0.1, 120)
    style_counter = 0
    zorders=[7,6,5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "purple", "green", "dimgray"]
    
    # plot the accuracy of bucket 5 and n=1%
    #ls=["-",'dotted','--',':','-']
    #lw = [1,1.5,1.5,4,1.5]
    ax1.set_xscale("symlog")
    ax1.set_xlim(0.1, 120)
    style_counter = 0
    #zorders=[5,4,3,2,1]
    #colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc_1, labels_acc, colors):
        if style_counter == 0:
            ax1.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax1.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
        
    # annotations
    ax1.plot([Bv_3_1,Bv_3_1], [cpfv_3_1,gprv_3_1], color = "black", linewidth=1, marker="_")
    ytemp = gprv_3_1 - (maxv_3_1/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_3_1))+"\% for \nB="+str('{0:.0f}'.format(Bv_3_1))+"\%"
    ax1.annotate(strtemp, xy=(Bv_3_1, ytemp), xycoords='data', xytext=(-40, 20), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    ax1.grid(alpha=0.3, which='major')
    ax1.grid(alpha=0.3, which='minor')
    ax1.set_yticks(np.arange(0, 100, 10))
    ax1.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    #ax1.set_xlabel('$n=1\%$')
    ax1.set_xlabel('$\pm5\%$ at $P_{+}$')
    ax1.set_ylabel('Models within\n $[a,b]\%$ at $P_{+}$ [\%]')
    
    # plot the accuracy of bucket 5 and n=2%
    #ls=["-",'dotted','--',':','-']
    #lw = [1,1.5,1.5,4,1.5]
    ax2.set_xscale("symlog")
    ax2.set_xlim(0.1, 120)
    style_counter = 0
    #zorders=[5,4,3,2,1]
    #colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc_2, labels_acc, colors):
        if style_counter == 0:
            ax2.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax2.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
        
    # annotations
    ax2.plot([Bv_3_2,Bv_3_2], [cpfv_3_2,gprv_3_2], color = "black", linewidth=1, marker="_")
    ytemp = gprv_3_2 - (maxv_3_2/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_3_2))+"\% for \nB="+str('{0:.0f}'.format(Bv_3_2))+"\%"
    ax2.annotate(strtemp, xy=(Bv_3_2, ytemp), xycoords='data', xytext=(-40, 15), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    ax2.grid(alpha=0.3, which='major')
    ax2.grid(alpha=0.3, which='minor')
    ax2.set_yticks(np.arange(0, 100, 10))
    ax2.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    ax2.set_xlabel('$\pm10\%$ at $P_{+}$')
    
    # plot the accuracy of bucket 5 and n=5%
    #ls=["-",'dotted','--',':','-']
    #lw = [1,1.5,1.5,4,1.5]
    ax3.set_xscale("symlog")
    ax3.set_xlim(0.1, 120)
    style_counter = 0
    #zorders=[5,4,3,2,1]
    #colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc_5, labels_acc, colors):
        if style_counter == 0:
            ax3.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax3.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    #ax3.fill_between(x_values, y_values_list_acc_5[1], y_values_list_acc_5[2], color="green", where=np.array(y_values_list_acc_5[2]) > np.array(y_values_list_acc_5[1]), alpha=0.4, label='GPR better than CPF', hatch="x", interpolate=True)
    #ax3.fill_between(x_values, y_values_list_acc_5[2], y_values_list_acc_5[1], color="red", where=np.array(y_values_list_acc_5[2]) < np.array(y_values_list_acc_5[1]), alpha=0.4, label='GPR worse than CPF', hatch="+", zorder=5, interpolate=True)
    
    # annotations
    ax3.plot([Bv_3_5,Bv_3_5], [cpfv_3_5,gprv_3_5], color = "black", linewidth=1, marker="_")
    ytemp = gprv_3_5 - (maxv_3_5/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_3_5))+"\% for \nB="+str('{0:.0f}'.format(Bv_3_5))+"\%"
    ax3.annotate(strtemp, xy=(Bv_3_5, ytemp), xycoords='data', xytext=(-40, 10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    ax3.grid(alpha=0.3, which='major')
    ax3.grid(alpha=0.3, which='minor')
    ax3.set_yticks(np.arange(0, 100, 10))
    ax3.set_xlabel('$\pm15\%$ at $P_{+}$')
    ax3.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    #ax3.set_xlabel('$n=5\%$')
    #ax3.set_ylabel('Models within $\pm15\%$ at $P_{+}$ [%]')
    #ax3.legend(loc="lower right", prop={'size': 8})
    
    # plot the accuracy of bucket 5 and n=10%
    #ls=["-",'dotted','--',':','-']
    #lw = [1,1.5,1.5,4,1.5]
    ax4.set_xscale("symlog")
    ax4.set_xlim(0.1, 120)
    ax4.set_ylim(0, 105)
    style_counter = 0
    #zorders=[5,4,3,2,1]
    #colors=["gray", "blue", "red", "orange", "yellow"]
    for y_values, label, color in zip(y_values_list_acc_10, labels_acc, colors):
        if style_counter == 0:
            ax4.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax4.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    #ax4.fill_between(x_values, y_values_list_acc_10[1], y_values_list_acc_10[2], color="green", where=np.array(y_values_list_acc_10[2]) > np.array(y_values_list_acc_10[1]), alpha=0.4, label='GPR better than CPF', hatch="x", interpolate=True)
    #ax4.fill_between(x_values, y_values_list_acc_10[2], y_values_list_acc_10[1], color="red", where=np.array(y_values_list_acc_10[2]) < np.array(y_values_list_acc_10[1]), alpha=0.4, label='GPR worse than CPF', hatch="+", zorder=5, interpolate=True)
    
    # annotations
    ax4.plot([Bv_3_10,Bv_3_10], [cpfv_3_10,gprv_3_10], color = "black", linewidth=1, marker="_")
    ytemp = gprv_3_10 - (maxv_3_10/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_3_10))+"\% for \nB="+str('{0:.0f}'.format(Bv_3_10))+"\%"
    ax4.annotate(strtemp, xy=(Bv_3_10, ytemp), xycoords='data', xytext=(-40, 10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    ax4.grid(alpha=0.3, which='major')
    ax4.grid(alpha=0.3, which='minor')
    ax4.set_yticks(np.arange(0, 110, 10))
    ax4.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    #ax4.set_xlabel('$n=10\%$')
    ax4.set_xlabel('$\pm20\%$ at $P_{+}$')
    #ax4.set_ylabel('Models within $\pm20\%$ at $P_{+}$ [%]')
    #ax4.legend(loc="lower right", prop={'size': 8})
    ax42 = ax4.twinx() 
    ax42.set_ylabel("$m=3, n=\pm10\%$")
    ax42.tick_params(right = False)
    ax42.set_yticks([])
    ax4.set_xticks([0, 1, 10, 100])
    locmin = matplotlib.ticker.LogLocator(base=10.0, subs=(0.1,0.2,0.3,0.4,0.5,0.6, 0.7, 0.8, 0.9 )) 
    ax4.xaxis.set_minor_locator(locmin)
    ax4.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    
    """ax12.set_yticks(np.arange(0, 100, 10))
    ax12.set_xticks([0, 1, 10, 100])
    ax12.set_xlabel('$n=\pm10\%$')
    locmin = matplotlib.ticker.LogLocator(base=10.0, subs=(0.1,0.2,0.3,0.4,0.5,0.6, 0.7, 0.8, 0.9 )) 
    ax12.xaxis.set_minor_locator(locmin)
    ax12.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax12.grid(alpha=0.3, which='major')
    ax12.grid(alpha=0.3, which='minor')
    ax122 = ax12.twinx() 
    ax122.set_ylabel("$m=4$")
    ax122.tick_params(right = False)
    ax122.set_yticks([])"""
    
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=7, bbox_to_anchor=(0.5, 1.175), frameon=False, fontsize=8, columnspacing=0.8)
    
    fig.text(0.5, -0.1, 'Allowed modeling budget $B$ [\%]', ha='center', fontsize=8)
    
    fig.tight_layout(pad=0.2)
    plt.savefig(plot_name, bbox_inches="tight")
    plt.show()
    plt.close()

if __name__ == '__main__':
    main()