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
        plot_name = "paper_plot_case_studies_gpr_only.pdf"
    
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
        #hybrid_values_fastest
    ]
    y_values_list_points_fastest = [
        all_points_fastest,
        points_generic_fastest,
        points_gpr_fastest,
        #points_hybrid_fastest,
    ]
    y_values_list_costs_fastest = [
        generic_costs_fastest,
        gpr_costs_fastest,
        #hybrid_costs_fastest,
    ]

    print("")
    print("### FASTEST ###")
    B_NU_FASTEST_GENERIC = np.nanmax(generic_costs_fastest)
    B_NU_FASTEST_GPR = np.nanmax(gpr_costs_fastest)
    #print(B_NU_FASTEST_GENERIC,B_NU_FASTEST_GPR)
    print("unused budget factor CPF/GPR:",B_NU_FASTEST_GENERIC/B_NU_FASTEST_GPR)
    
    B_CPF_FASTEST = 0
    maxv = 0
    for i in range(len(generic_costs_fastest)):
        if generic_costs_fastest[i] >= maxv:
            maxv = generic_costs_fastest[i]
            B_CPF_FASTEST = x_values_fastest[i]
            
    B_GPR_FASTEST = 0
    maxv = 0
    for i in range(len(gpr_costs_fastest)):
        if gpr_costs_fastest[i] >= maxv:
            maxv = gpr_costs_fastest[i]
            B_GPR_FASTEST = x_values_fastest[i]

    full_B_max_FASTEST = 0
    maxv = 0
    for i in range(len(full_values_fastest)):
        if full_values_fastest[i] >= maxv:
            maxv = full_values_fastest[i]
            full_B_max_FASTEST = x_values_fastest[i]
    full_max_FASTEST = max(full_values_fastest)
    print("Max. accuracy Full:",full_max_FASTEST,"% at B=",full_B_max_FASTEST,"%.")
    
    cpf_B_max_FASTEST = 0
    maxv = 0
    for i in range(len(generic_values_fastest)):
        if generic_values_fastest[i] >= maxv:
            maxv = generic_values_fastest[i]
            cpf_B_max_FASTEST = x_values_fastest[i]
    cpf_max_FASTEST = max(generic_values_fastest)
    print("Max. accuracy CPF:",cpf_max_FASTEST,"% at B=",cpf_B_max_FASTEST,"%.")
    
    gpr_B_max_FASTEST = 0
    maxv = 0
    for i in range(len(gpr_values_fastest)):
        if gpr_values_fastest[i] >= maxv:
            maxv = gpr_values_fastest[i]
            gpr_B_max_FASTEST = x_values_fastest[i]
    gpr_max_FASTEST = max(gpr_values_fastest)
    print("Max. accuracy GPR:",gpr_max_FASTEST,"% at B=",gpr_B_max_FASTEST,"%.")
    
    maxv_FASTEST = 0
    Bv_FASTEST = 0
    cpfv_FASTEST = 0
    gprv_FASTEST = 0
    for i in range(len(gpr_values_fastest)):
        diff = gpr_values_fastest[i] - generic_values_fastest[i]
        if diff >= maxv_FASTEST:
            maxv_FASTEST = diff
            Bv_FASTEST = x_values_fastest[i]
            cpfv_FASTEST = generic_values_fastest[i]
            gprv_FASTEST = gpr_values_fastest[i]
    print("max. difference GPR/CPF:",maxv_FASTEST,"at B=",Bv_FASTEST,"%.")
    
    max_points_FASTEST = 0
    B_points_FASTEST = 0
    cpf_points_FASTEST = 0
    gpr_points_FASTEST = 0
    for i in range(len(points_gpr_fastest)):
        diff = points_gpr_fastest[i] - points_generic_fastest[i]
        if diff >= max_points_FASTEST:
            max_points_FASTEST = diff
            B_points_FASTEST = x_values_fastest[i]
            cpf_points_FASTEST = points_generic_fastest[i]
            gpr_points_FASTEST = points_gpr_fastest[i]
    print("max. difference points GPR/CPF:",max_points_FASTEST,"at B=",B_points_FASTEST,"%.")
    
    max_points_FASTEST_2 = 0
    B_points_FASTEST_2 = 0
    cpf_points_FASTEST_2 = 0
    gpr_points_FASTEST_2 = 0
    for i in range(len(points_gpr_fastest)):
        diff = points_generic_fastest[i] - points_gpr_fastest[i]
        if diff >= max_points_FASTEST_2:
            max_points_FASTEST_2 = diff
            B_points_FASTEST_2 = x_values_fastest[i]
            cpf_points_FASTEST_2 = points_generic_fastest[i]
            gpr_points_FASTEST_2 = points_gpr_fastest[i]
    print("max. difference points GPR/CPF:",max_points_FASTEST_2,"at B=",B_points_FASTEST_2,"%.")

    print("############")   
    print("")
    
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
        #hybrid_values_kripke
    ]
    y_values_list_points_kripke = [
        all_points_kripke,
        points_generic_kripke,
        points_gpr_kripke,
        #points_hybrid_kripke,
    ]
    y_values_list_costs_kripke = [
        generic_costs_kripke,
        gpr_costs_kripke,
        #hybrid_costs_kripke,
    ]

    print("")
    print("### Kripke ###")
    B_NU_KRIPKE_GENERIC = np.nanmax(generic_costs_kripke)
    B_NU_KRIPKE_GPR = np.nanmax(gpr_costs_kripke)
    #print(B_NU_KRIPKE_GENERIC,B_NU_KRIPKE_GPR)
    print("unused budget factor CPF/GPR:",B_NU_KRIPKE_GENERIC/B_NU_KRIPKE_GPR)
    
    B_CPF_KRIPKE = 0
    maxv = 0
    for i in range(len(generic_costs_kripke)):
        if generic_costs_kripke[i] >= maxv:
            maxv = generic_costs_kripke[i]
            B_CPF_KRIPKE = x_values_kripke[i]
            
    B_GPR_KRIPKE = 0
    maxv = 0
    for i in range(len(gpr_costs_kripke)):
        if gpr_costs_kripke[i] >= maxv:
            maxv = gpr_costs_kripke[i]
            B_GPR_KRIPKE = x_values_kripke[i]

    full_B_max_KRIPKE = 0
    maxv = 0
    for i in range(len(full_values_kripke)):
        if full_values_kripke[i] >= maxv:
            maxv = full_values_kripke[i]
            full_B_max_KRIPKE = x_values_kripke[i]
    full_max_KRIPKE = max(full_values_kripke)
    print("Max. accuracy Full:",full_max_KRIPKE,"% at B=",full_B_max_KRIPKE,"%.")
    
    cpf_B_max_KRIPKE = 0
    maxv = 0
    for i in range(len(generic_values_kripke)):
        if generic_values_kripke[i] >= maxv:
            maxv = generic_values_kripke[i]
            cpf_B_max_KRIPKE = x_values_kripke[i]
    cpf_max_KRIPKE = max(generic_values_kripke)
    print("Max. accuracy CPF:",cpf_max_KRIPKE,"% at B=",cpf_B_max_KRIPKE,"%.")
    
    gpr_B_max_KRIPKE = 0
    maxv = 0
    for i in range(len(gpr_values_kripke)):
        if gpr_values_kripke[i] >= maxv:
            maxv = gpr_values_kripke[i]
            gpr_B_max_KRIPKE = x_values_kripke[i]
    gpr_max_KRIPKE = max(gpr_values_kripke)
    print("Max. accuracy GPR:",gpr_max_KRIPKE,"% at B=",gpr_B_max_KRIPKE,"%.")
    
    maxv_KRIPKE = 0
    Bv_KRIPKE = 0
    cpfv_KRIPKE = 0
    gprv_KRIPKE = 0
    for i in range(len(gpr_values_kripke)):
        diff = gpr_values_kripke[i] - generic_values_kripke[i]
        if diff >= maxv_KRIPKE:
            maxv_KRIPKE = diff
            Bv_KRIPKE = x_values_kripke[i]
            cpfv_KRIPKE = generic_values_kripke[i]
            gprv_KRIPKE = gpr_values_kripke[i]
    print("max. difference GPR/CPF:",maxv_KRIPKE,"at B=",Bv_KRIPKE,"%.")
    
    max_points_KRIPKE = 0
    B_points_KRIPKE = 0
    cpf_points_KRIPKE = 0
    gpr_points_KRIPKE = 0
    for i in range(len(points_generic_kripke)):
        diff = points_generic_kripke[i] - points_gpr_kripke[i]
        if diff >= max_points_KRIPKE:
            max_points_KRIPKE = diff
            B_points_KRIPKE = x_values_kripke[i]
            cpf_points_KRIPKE = points_generic_kripke[i]
            gpr_points_KRIPKE = points_gpr_kripke[i]
    print("max. difference points GPR/CPF:",max_points_KRIPKE,"at B=",B_points_KRIPKE,"%.")

    print("############")
    print("")
    
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
        #hybrid_values_lulesh
    ]
    y_values_list_points_lulesh = [
        all_points_lulesh,
        points_generic_lulesh,
        points_gpr_lulesh,
        #points_hybrid_lulesh,
    ]
    y_values_list_costs_lulesh = [
        generic_costs_lulesh,
        gpr_costs_lulesh,
        #hybrid_costs_lulesh,
    ]

    print("")
    print("### LULESH ###")
    B_NU_LULESH_GENERIC = np.nanmax(generic_costs_lulesh)
    B_NU_LULESH_GPR = np.nanmax(gpr_costs_lulesh)
    #print(B_NU_LULESH_GENERIC,B_NU_LULESH_GPR)
    print("unused budget factor CPF/GPR:",B_NU_LULESH_GENERIC/B_NU_LULESH_GPR)
    
    B_CPF_LULESH = 0
    maxv = 0
    for i in range(len(generic_costs_lulesh)):
        if generic_costs_lulesh[i] >= maxv:
            maxv = generic_costs_lulesh[i]
            B_CPF_LULESH = x_values_lulesh[i]
            
    B_GPR_LULESH = 0
    maxv = 0
    for i in range(len(gpr_costs_lulesh)):
        if gpr_costs_lulesh[i] >= maxv:
            maxv = gpr_costs_lulesh[i]
            B_GPR_LULESH = x_values_lulesh[i]

    full_B_max_LULESH = 0
    maxv = 0
    for i in range(len(full_values_lulesh)):
        if full_values_lulesh[i] >= maxv:
            maxv = full_values_lulesh[i]
            full_B_max_LULESH = x_values_lulesh[i]
    full_max_LULESH = max(full_values_lulesh)
    print("Max. accuracy Full:",full_max_LULESH,"% at B=",full_B_max_LULESH,"%.")
    
    cpf_B_max_LULESH = 0
    maxv = 0
    for i in range(len(generic_values_lulesh)):
        if generic_values_lulesh[i] >= maxv:
            maxv = generic_values_lulesh[i]
            cpf_B_max_LULESH = x_values_lulesh[i]
    cpf_max_LULESH = max(generic_values_lulesh)
    print("Max. accuracy CPF:",cpf_max_LULESH,"% at B=",cpf_B_max_LULESH,"%.")
    
    gpr_B_max_LULESH = 0
    maxv = 0
    for i in range(len(gpr_values_lulesh)):
        if gpr_values_lulesh[i] >= maxv:
            maxv = gpr_values_lulesh[i]
            gpr_B_max_LULESH = x_values_lulesh[i]
    gpr_max_LULESH = max(gpr_values_lulesh)
    print("Max. accuracy GPR:",gpr_max_LULESH,"% at B=",gpr_B_max_LULESH,"%.")
    
    maxv_LULESH = 0
    Bv_LULESH = 0
    cpfv_LULESH = 0
    gprv_LULESH = 0
    for i in range(len(gpr_values_lulesh)):
        diff = gpr_values_lulesh[i] - generic_values_lulesh[i]
        if diff >= maxv_LULESH:
            maxv_LULESH = diff
            Bv_LULESH = x_values_lulesh[i]
            cpfv_LULESH = generic_values_lulesh[i]
            gprv_LULESH = gpr_values_lulesh[i]
    print("max. difference GPR/CPF:",maxv_LULESH,"at B=",Bv_LULESH,"%.")
    
    max_points_LULESH = 0
    B_points_LULESH = 0
    cpf_points_LULESH = 0
    gpr_points_LULESH = 0
    for i in range(len(points_generic_lulesh)):
        diff = points_generic_lulesh[i] - points_gpr_lulesh[i]
        if diff >= max_points_LULESH:
            max_points_LULESH = diff
            B_points_LULESH = x_values_lulesh[i]
            cpf_points_LULESH = points_generic_lulesh[i]
            gpr_points_LULESH = points_gpr_lulesh[i]
    print("max. difference points GPR/CPF:",max_points_LULESH,"at B=",B_points_LULESH,"%.")

    print("############")
    print("")
    
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
        #hybrid_values_minife
    ]
    y_values_list_points_minife = [
        all_points_minife,
        points_generic_minife,
        points_gpr_minife,
        #points_hybrid_minife,
    ]
    y_values_list_costs_minife = [
        generic_costs_minife,
        gpr_costs_minife,
        #hybrid_costs_minife,
    ]

    print("")
    print("### MiniFE ###")
    B_NU_MINIFE_GENERIC = np.nanmax(generic_costs_minife)
    B_NU_MINIFE_GPR = np.nanmax(gpr_costs_minife)
    #print(B_NU_MINIFE_GENERIC,B_NU_MINIFE_GPR)
    print("unused budget factor CPF/GPR:",B_NU_MINIFE_GENERIC/B_NU_MINIFE_GPR)
    
    B_CPF_MINIFE = 0
    maxv = 0
    for i in range(len(generic_costs_minife)):
        if generic_costs_minife[i] >= maxv:
            maxv = generic_costs_minife[i]
            B_CPF_MINIFE = x_values_minife[i]
            
    B_GPR_MINIFE = 0
    maxv = 0
    for i in range(len(gpr_costs_minife)):
        if gpr_costs_minife[i] >= maxv:
            maxv = gpr_costs_minife[i]
            B_GPR_MINIFE = x_values_minife[i]

    full_B_max_MINIFE = 0
    maxv = 0
    for i in range(len(full_values_minife)):
        if full_values_minife[i] >= maxv:
            maxv = full_values_minife[i]
            full_B_max_MINIFE = x_values_minife[i]
    full_max_MINIFE = max(full_values_minife)
    print("Max. accuracy Full:",full_max_MINIFE,"% at B=",full_B_max_MINIFE,"%.")
    
    cpf_B_max_MINIFE = 0
    maxv = 0
    for i in range(len(generic_values_minife)):
        if generic_values_minife[i] >= maxv:
            maxv = generic_values_minife[i]
            cpf_B_max_MINIFE = x_values_minife[i]
    cpf_max_MINIFE = max(generic_values_minife)
    print("Max. accuracy CPF:",cpf_max_MINIFE,"% at B=",cpf_B_max_MINIFE,"%.")
    
    gpr_B_max_MINIFE = 0
    maxv = 0
    for i in range(len(gpr_values_minife)):
        if gpr_values_minife[i] >= maxv:
            maxv = gpr_values_minife[i]
            gpr_B_max_MINIFE = x_values_minife[i]
    gpr_max_MINIFE = max(gpr_values_minife)
    print("Max. accuracy GPR:",gpr_max_MINIFE,"% at B=",gpr_B_max_MINIFE,"%.")
    
    maxv_MINIFE = 0
    Bv_MINIFE = 0
    cpfv_MINIFE = 0
    gprv_MINIFE = 0
    for i in range(len(gpr_values_minife)):
        diff = gpr_values_minife[i] - generic_values_minife[i]
        if diff >= maxv_MINIFE:
            maxv_MINIFE = diff
            Bv_MINIFE = x_values_minife[i]
            cpfv_MINIFE = generic_values_minife[i]
            gprv_MINIFE = gpr_values_minife[i]
    print("max. difference GPR/CPF:",maxv_MINIFE,"at B=",Bv_MINIFE,"%.")

    max_points_MINIFE = 0
    B_points_MINIFE = 0
    cpf_points_MINIFE = 0
    gpr_points_MINIFE = 0
    for i in range(len(points_generic_minife)):
        diff = points_generic_minife[i] - points_gpr_minife[i]
        if diff >= max_points_MINIFE:
            max_points_MINIFE = diff
            B_points_MINIFE = x_values_minife[i]
            cpf_points_MINIFE = points_generic_minife[i]
            gpr_points_MINIFE = points_gpr_minife[i]
    print("max. difference points GPR/CPF:",max_points_MINIFE,"at B=",B_points_MINIFE,"%.")
    
    print("############")
    print("")
    
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
        #hybrid_values_quicksilver
    ]
    y_values_list_points_quicksilver = [
        all_points_quicksilver,
        points_generic_quicksilver,
        points_gpr_quicksilver,
        #points_hybrid_quicksilver,
    ]
    y_values_list_costs_quicksilver = [
        generic_costs_quicksilver,
        gpr_costs_quicksilver,
        #hybrid_costs_quicksilver,
    ]

    print("")
    print("### Quicksilver ###")
    B_NU_QUICKSILVER_GENERIC = np.nanmax(generic_costs_quicksilver)
    B_NU_QUICKSILVER_GPR = np.nanmax(gpr_costs_quicksilver)
    #print(B_NU_QUICKSILVER_GENERIC,B_NU_QUICKSILVER_GPR)
    print("unused budget factor CPF/GPR:",B_NU_QUICKSILVER_GENERIC/B_NU_QUICKSILVER_GPR)
    
    B_CPF_QUICKSILVER = 0
    maxv = 0
    for i in range(len(generic_costs_quicksilver)):
        if generic_costs_quicksilver[i] >= maxv:
            maxv = generic_costs_quicksilver[i]
            B_CPF_QUICKSILVER = x_values_quicksilver[i]
            
    B_GPR_QUICKSILVER = 0
    maxv = 0
    for i in range(len(gpr_costs_quicksilver)):
        if gpr_costs_quicksilver[i] >= maxv:
            maxv = gpr_costs_quicksilver[i]
            B_GPR_QUICKSILVER = x_values_quicksilver[i]

    full_B_max_QUICKSILVER = 0
    maxv = 0
    for i in range(len(full_values_quicksilver)):
        if full_values_quicksilver[i] >= maxv:
            maxv = full_values_quicksilver[i]
            full_B_max_QUICKSILVER = x_values_quicksilver[i]
    full_max_QUICKSILVER = max(full_values_quicksilver)
    print("Max. accuracy Full:",full_max_QUICKSILVER,"% at B=",full_B_max_QUICKSILVER,"%.")
    
    cpf_B_max_QUICKSILVER = 0
    maxv = 0
    for i in range(len(generic_values_quicksilver)):
        if generic_values_quicksilver[i] >= maxv:
            maxv = generic_values_quicksilver[i]
            cpf_B_max_QUICKSILVER = x_values_quicksilver[i]
    cpf_max_QUICKSILVER = max(generic_values_quicksilver)
    print("Max. accuracy CPF:",cpf_max_QUICKSILVER,"% at B=",cpf_B_max_QUICKSILVER,"%.")
    
    gpr_B_max_QUICKSILVER = 0
    maxv = 0
    for i in range(len(gpr_values_quicksilver)):
        if gpr_values_quicksilver[i] >= maxv:
            maxv = gpr_values_quicksilver[i]
            gpr_B_max_QUICKSILVER = x_values_quicksilver[i]
    gpr_max_QUICKSILVER = max(gpr_values_quicksilver)
    print("Max. accuracy GPR:",gpr_max_QUICKSILVER,"% at B=",gpr_B_max_QUICKSILVER,"%.")
    
    maxv_QUICKSILVER = 0
    Bv_QUICKSILVER = 0
    cpfv_QUICKSILVER = 0
    gprv_QUICKSILVER = 0
    for i in range(len(gpr_values_quicksilver)):
        diff = gpr_values_quicksilver[i] - generic_values_quicksilver[i]
        if diff >= maxv_QUICKSILVER:
            maxv_QUICKSILVER = diff
            Bv_QUICKSILVER = x_values_quicksilver[i]
            cpfv_QUICKSILVER = generic_values_quicksilver[i]
            gprv_QUICKSILVER = gpr_values_quicksilver[i]
    print("max. difference GPR/CPF:",maxv_QUICKSILVER,"at B=",Bv_QUICKSILVER,"%.")

    max_points_QUICKSILVER = 0
    B_points_QUICKSILVER = 0
    cpf_points_QUICKSILVER = 0
    gpr_points_QUICKSILVER = 0
    for i in range(len(points_generic_quicksilver)):
        diff = points_generic_quicksilver[i] - points_gpr_quicksilver[i]
        if diff >= max_points_QUICKSILVER:
            max_points_QUICKSILVER = diff
            B_points_QUICKSILVER = x_values_quicksilver[i]
            cpf_points_QUICKSILVER = points_generic_quicksilver[i]
            gpr_points_QUICKSILVER = points_gpr_quicksilver[i]
    print("max. difference points GPR/CPF:",max_points_QUICKSILVER,"at B=",B_points_QUICKSILVER,"%.")
    
    print("############")
    print("")

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
        #hybrid_values_relearn
    ]
    y_values_list_points_relearn = [
        all_points_relearn,
        points_generic_relearn,
        points_gpr_relearn,
        #points_hybrid_relearn,
    ]
    y_values_list_costs_relearn = [
        generic_costs_relearn,
        gpr_costs_relearn,
        #hybrid_costs_relearn,
    ]

    print("")
    print("### RELEARN ###")
    B_NU_RELEARN_GENERIC = np.nanmax(generic_costs_relearn)
    B_NU_RELEARN_GPR = np.nanmax(gpr_costs_relearn)
    #print(B_NU_RELEARN_GENERIC,B_NU_RELEARN_GPR)
    print("unused budget factor CPF/GPR:",B_NU_RELEARN_GENERIC/B_NU_RELEARN_GPR)
    
    B_CPF_RELEARN = 0
    maxv = 0
    for i in range(len(generic_costs_relearn)):
        if generic_costs_relearn[i] >= maxv:
            maxv = generic_costs_relearn[i]
            B_CPF_RELEARN = x_values_relearn[i]
            
    B_GPR_RELEARN = 0
    maxv = 0
    for i in range(len(gpr_costs_relearn)):
        if gpr_costs_relearn[i] >= maxv:
            maxv = gpr_costs_relearn[i]
            B_GPR_RELEARN = x_values_relearn[i]

    full_B_max_RELEARN = 0
    maxv = 0
    for i in range(len(full_values_relearn)):
        if full_values_relearn[i] >= maxv:
            maxv = full_values_relearn[i]
            full_B_max_RELEARN = x_values_relearn[i]
    full_max_RELEARN = max(full_values_relearn)
    print("Max. accuracy Full:",full_max_RELEARN,"% at B=",full_B_max_RELEARN,"%.")
    
    cpf_B_max_RELEARN = 0
    maxv = 0
    for i in range(len(generic_values_relearn)):
        if generic_values_relearn[i] >= maxv:
            maxv = generic_values_relearn[i]
            cpf_B_max_RELEARN = x_values_relearn[i]
    cpf_max_RELEARN = max(generic_values_relearn)
    print("Max. accuracy CPF:",cpf_max_RELEARN,"% at B=",cpf_B_max_RELEARN,"%.")
    
    gpr_B_max_RELEARN = 0
    maxv = 0
    for i in range(len(gpr_values_relearn)):
        if gpr_values_relearn[i] >= maxv:
            maxv = gpr_values_relearn[i]
            gpr_B_max_RELEARN = x_values_relearn[i]
    gpr_max_RELEARN = max(gpr_values_relearn)
    print("Max. accuracy GPR:",gpr_max_RELEARN,"% at B=",gpr_B_max_RELEARN,"%.")
    
    maxv_RELEARN = 0
    Bv_RELEARN = 0
    cpfv_RELEARN = 0
    gprv_RELEARN = 0
    for i in range(len(gpr_values_relearn)):
        diff = gpr_values_relearn[i] - generic_values_relearn[i]
        if diff >= maxv_RELEARN:
            maxv_RELEARN = diff
            Bv_RELEARN = x_values_relearn[i]
            cpfv_RELEARN = generic_values_relearn[i]
            gprv_RELEARN = gpr_values_relearn[i]
    print("max. difference GPR/CPF:",maxv_RELEARN,"at B=",Bv_RELEARN,"%.")

    max_points_RELEARN = 0
    B_points_RELEARN = 0
    cpf_points_RELEARN = 0
    gpr_points_RELEARN = 0
    for i in range(len(points_gpr_relearn)):
        diff = points_gpr_relearn[i] - points_generic_relearn[i]
        if diff >= max_points_RELEARN:
            max_points_RELEARN = diff
            B_points_RELEARN = x_values_relearn[i]
            cpf_points_RELEARN = points_generic_relearn[i]
            gpr_points_RELEARN = points_gpr_relearn[i]
    print("max. difference points GPR/CPF:",max_points_RELEARN,"at B=",B_points_RELEARN,"%.")
    
    max_points_RELEARN_2 = 0
    B_points_RELEARN_2 = 0
    cpf_points_RELEARN_2 = 0
    gpr_points_RELEARN_2 = 0
    for i in range(len(points_gpr_relearn)):
        diff = points_generic_relearn[i] - points_gpr_relearn[i]
        if diff >= max_points_RELEARN_2:
            max_points_RELEARN_2 = diff
            B_points_RELEARN_2 = x_values_relearn[i]
            cpf_points_RELEARN_2 = points_generic_relearn[i]
            gpr_points_RELEARN_2 = points_gpr_relearn[i]
    print("max. difference points GPR/CPF:",max_points_RELEARN_2,"at B=",B_points_RELEARN_2,"%.")
    
    print("############")
    print("")
    
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
        
    ax1.plot([Bv_FASTEST,Bv_FASTEST], [cpfv_FASTEST,gprv_FASTEST], color = "black", linewidth=1, marker="_")
    ytemp = gprv_FASTEST - (maxv_FASTEST/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_FASTEST))+"\% for \nB="+str('{0:.0f}'.format(Bv_FASTEST))+"\%"
    ax1.annotate(strtemp, xy=(Bv_FASTEST, ytemp), xycoords='data', xytext=(-50, 10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    strtemp = str('{0:.2f}'.format(cpf_max_FASTEST))+"\% \nB="+str('{0:.0f}'.format(cpf_B_max_FASTEST))+"\%"
    ax1.annotate(strtemp, xy=(cpf_B_max_FASTEST, cpf_max_FASTEST), xycoords='data', xytext=(-10, -40), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(gpr_max_FASTEST))+"\% \nB="+str('{0:.0f}'.format(gpr_B_max_FASTEST))+"\%"
    ax1.annotate(strtemp, xy=(gpr_B_max_FASTEST, gpr_max_FASTEST), xycoords='data', xytext=(0, -55), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    strtemp = str('{0:.2f}'.format(full_max_FASTEST))+"\% \nB="+str('{0:.0f}'.format(full_B_max_FASTEST))+"\%"
    ax1.annotate(strtemp, xy=(full_B_max_FASTEST, full_max_FASTEST), xycoords='data', xytext=(-25, -60), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="dimgray"), fontsize=7, color="dimgray")

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
    
    # annotations
    strtemp = str('{0:.2f}'.format(B_NU_FASTEST_GENERIC))+"\% for \nB="+str('{0:.0f}'.format(B_CPF_FASTEST))+"\%"
    ax2.annotate(strtemp, xy=(B_CPF_FASTEST, B_NU_FASTEST_GENERIC), xycoords='data', xytext=(-60, -20), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(B_NU_FASTEST_GPR))+"\% for \nB="+str('{0:.0f}'.format(B_GPR_FASTEST))+"\%"
    ax2.annotate(strtemp, xy=(B_GPR_FASTEST, B_NU_FASTEST_GPR), xycoords='data', xytext=(-80, 10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    
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
    
    ax3.plot([B_points_FASTEST,B_points_FASTEST], [cpf_points_FASTEST,gpr_points_FASTEST], color = "black", linewidth=1, marker="_")
    ytemp = gpr_points_FASTEST - (max_points_FASTEST/2)
    strtemp = "+"+str('{0:.2f}'.format(max_points_FASTEST))+"\ for \nB="+str('{0:.0f}'.format(B_points_FASTEST))+"\%"
    ax3.annotate(strtemp, xy=(B_points_FASTEST, ytemp), xycoords='data', xytext=(25, -10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    ax3.plot([B_points_FASTEST_2,B_points_FASTEST_2], [cpf_points_FASTEST_2,gpr_points_FASTEST_2], color = "black", linewidth=1, marker="_")
    ytemp = cpf_points_FASTEST_2 - (max_points_FASTEST_2/2)
    strtemp = "-"+str('{0:.2f}'.format(max_points_FASTEST_2))+"\ for \nB="+str('{0:.0f}'.format(B_points_FASTEST_2))+"\%"
    ax3.annotate(strtemp, xy=(B_points_FASTEST_2, ytemp), xycoords='data', xytext=(25, -10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    ax3.grid(alpha=0.3, which='major')
    ax3.grid(alpha=0.3, which='minor')
    ax3.set_xlim(x_values_fastest[0]-2,103)
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
        
    ax4.plot([Bv_KRIPKE,Bv_KRIPKE], [cpfv_KRIPKE,gprv_KRIPKE], color = "black", linewidth=1, marker="_")
    ytemp = gprv_KRIPKE - (maxv_KRIPKE/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_KRIPKE))+"\% for \nB="+str('{0:.0f}'.format(Bv_KRIPKE))+"\%"
    ax4.annotate(strtemp, xy=(Bv_KRIPKE, ytemp), xycoords='data', xytext=(-60, -30), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    #strtemp = str('{0:.2f}'.format(cpf_max_KRIPKE))+"\% \nB="+str('{0:.0f}'.format(cpf_B_max_KRIPKE))+"\%"
    #ax4.annotate(strtemp, xy=(cpf_B_max_KRIPKE, cpf_max_KRIPKE), xycoords='data', xytext=(-50, -20), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    #strtemp = str('{0:.2f}'.format(gpr_max_KRIPKE))+"\% \nB="+str('{0:.0f}'.format(gpr_B_max_KRIPKE))+"\%"
    #ax4.annotate(strtemp, xy=(gpr_B_max_KRIPKE, gpr_max_KRIPKE), xycoords='data', xytext=(-20, -20), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    #strtemp = str('{0:.2f}'.format(full_max_KRIPKE))+"\% \nB="+str('{0:.0f}'.format(full_B_max_KRIPKE))+"\%"
    #ax4.annotate(strtemp, xy=(full_B_max_KRIPKE, full_max_KRIPKE), xycoords='data', xytext=(-25, -65), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="dimgray"), fontsize=7, color="dimgray")

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
        
    # annotations
    strtemp = str('{0:.2f}'.format(B_NU_KRIPKE_GENERIC))+" for \nB="+str('{0:.0f}'.format(B_CPF_KRIPKE))+"\%"
    ax5.annotate(strtemp, xy=(B_CPF_KRIPKE, B_NU_KRIPKE_GENERIC), xycoords='data', xytext=(-50, 0), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(B_NU_KRIPKE_GPR))+" for \nB="+str('{0:.0f}'.format(B_GPR_KRIPKE))+"\%"
    ax5.annotate(strtemp, xy=(B_GPR_KRIPKE, B_NU_KRIPKE_GPR), xycoords='data', xytext=(-70, 30), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    
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
        
    ax6.plot([B_points_KRIPKE,B_points_KRIPKE], [cpf_points_KRIPKE,gpr_points_KRIPKE], color = "black", linewidth=1, marker="_")
    ytemp = cpf_points_KRIPKE - (max_points_KRIPKE/2)
    strtemp = "-"+str('{0:.2f}'.format(max_points_KRIPKE))+" for \nB="+str('{0:.0f}'.format(B_points_KRIPKE))+"\%"
    ax6.annotate(strtemp, xy=(B_points_KRIPKE, ytemp), xycoords='data', xytext=(25, -10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
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
        
    ax7.plot([Bv_LULESH,Bv_LULESH], [cpfv_LULESH,gprv_LULESH], color = "black", linewidth=1, marker="_")
    ytemp = gprv_LULESH - (maxv_LULESH/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_LULESH))+"\% for \nB="+str('{0:.0f}'.format(Bv_LULESH))+"\%"
    ax7.annotate(strtemp, xy=(Bv_LULESH, ytemp), xycoords='data', xytext=(20, -20), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    strtemp = str('{0:.2f}'.format(cpf_max_LULESH))+"\% \nB="+str('{0:.0f}'.format(cpf_B_max_LULESH))+"\%"
    ax7.annotate(strtemp, xy=(cpf_B_max_LULESH, cpf_max_LULESH), xycoords='data', xytext=(-35, -35), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(gpr_max_LULESH))+"\% \nB="+str('{0:.0f}'.format(gpr_B_max_LULESH))+"\%"
    ax7.annotate(strtemp, xy=(gpr_B_max_LULESH, gpr_max_LULESH), xycoords='data', xytext=(-65, -40), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    strtemp = str('{0:.2f}'.format(full_max_LULESH))+"\% \nB="+str('{0:.0f}'.format(full_B_max_LULESH))+"\%"
    ax7.annotate(strtemp, xy=(full_B_max_LULESH, full_max_LULESH), xycoords='data', xytext=(-25, -55), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="dimgray"), fontsize=7, color="dimgray")

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
        
    # annotations
    strtemp = str('{0:.2f}'.format(B_NU_LULESH_GENERIC))+"\% for \nB="+str('{0:.0f}'.format(B_CPF_LULESH))+"\%"
    ax8.annotate(strtemp, xy=(B_CPF_LULESH, B_NU_LULESH_GENERIC), xycoords='data', xytext=(-50, -5), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(B_NU_LULESH_GPR))+"\% for \nB="+str('{0:.0f}'.format(B_GPR_LULESH))+"\%"
    ax8.annotate(strtemp, xy=(B_GPR_LULESH, B_NU_LULESH_GPR), xycoords='data', xytext=(-60, 20), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    
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
        
    ax9.plot([B_points_LULESH,B_points_LULESH], [cpf_points_LULESH,gpr_points_LULESH], color = "black", linewidth=1, marker="_")
    ytemp = cpf_points_LULESH - (max_points_LULESH/2)
    strtemp = "-"+str('{0:.2f}'.format(max_points_LULESH))+" for \nB="+str('{0:.0f}'.format(B_points_LULESH))+"\%"
    ax9.annotate(strtemp, xy=(B_points_LULESH, ytemp), xycoords='data', xytext=(25, 0), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    ax9.grid(alpha=0.3, which='major')
    ax9.grid(alpha=0.3, which='minor')
    ax9.set_xlim(x_values_lulesh[0]-2,103)
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
    
    ax10.plot([Bv_MINIFE,Bv_MINIFE], [cpfv_MINIFE,gprv_MINIFE], color = "black", linewidth=1, marker="_")
    ytemp = gprv_MINIFE - (maxv_MINIFE/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_MINIFE))+"\% for \nB="+str('{0:.0f}'.format(Bv_MINIFE))+"\%"
    ax10.annotate(strtemp, xy=(Bv_MINIFE, ytemp), xycoords='data', xytext=(20, -20), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    strtemp = str('{0:.2f}'.format(cpf_max_MINIFE))+"\% \nB="+str('{0:.0f}'.format(cpf_B_max_MINIFE))+"\%"
    ax10.annotate(strtemp, xy=(cpf_B_max_MINIFE, cpf_max_MINIFE), xycoords='data', xytext=(-25, -40), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(gpr_max_MINIFE))+"\% \nB="+str('{0:.0f}'.format(gpr_B_max_MINIFE))+"\%"
    ax10.annotate(strtemp, xy=(gpr_B_max_MINIFE, gpr_max_MINIFE), xycoords='data', xytext=(10, -35), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    strtemp = str('{0:.2f}'.format(full_max_MINIFE))+"\% \nB="+str('{0:.0f}'.format(full_B_max_MINIFE))+"\%"
    ax10.annotate(strtemp, xy=(full_B_max_MINIFE, full_max_MINIFE), xycoords='data', xytext=(-25, -55), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="dimgray"), fontsize=7, color="dimgray")

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
        
    # annotations
    strtemp = str('{0:.2f}'.format(B_NU_MINIFE_GENERIC))+"\% for \nB="+str('{0:.0f}'.format(B_CPF_MINIFE))+"\%"
    ax11.annotate(strtemp, xy=(B_CPF_MINIFE, B_NU_MINIFE_GENERIC), xycoords='data', xytext=(-50, 0), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(B_NU_MINIFE_GPR))+"\% for \nB="+str('{0:.0f}'.format(B_GPR_MINIFE))+"\%"
    ax11.annotate(strtemp, xy=(B_GPR_MINIFE, B_NU_MINIFE_GPR), xycoords='data', xytext=(-70, 20), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    
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
        
    ax12.plot([B_points_MINIFE,B_points_MINIFE], [cpf_points_MINIFE,gpr_points_MINIFE], color = "black", linewidth=1, marker="_")
    ytemp = cpf_points_MINIFE - (max_points_MINIFE/2)
    strtemp = "-"+str('{0:.2f}'.format(max_points_MINIFE))+" for \nB="+str('{0:.0f}'.format(B_points_MINIFE))+"\%"
    ax12.annotate(strtemp, xy=(B_points_MINIFE, ytemp), xycoords='data', xytext=(25, 0), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    ax12.grid(alpha=0.3, which='major')
    ax12.grid(alpha=0.3, which='minor')
    ax12.set_xlim(x_values_minife[0]-2,103)
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
        
    ax13.plot([Bv_QUICKSILVER,Bv_QUICKSILVER], [cpfv_QUICKSILVER,gprv_QUICKSILVER], color = "black", linewidth=1, marker="_")
    ytemp = gprv_QUICKSILVER - (maxv_QUICKSILVER/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_QUICKSILVER))+"\% for \nB="+str('{0:.1f}'.format(Bv_QUICKSILVER))+"\%"
    ax13.annotate(strtemp, xy=(Bv_QUICKSILVER, ytemp), xycoords='data', xytext=(20, -20), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    #strtemp = str('{0:.2f}'.format(cpf_max_QUICKSILVER))+"\% \nB="+str('{0:.0f}'.format(cpf_B_max_QUICKSILVER))+"\%"
    #ax13.annotate(strtemp, xy=(cpf_B_max_QUICKSILVER, cpf_max_QUICKSILVER), xycoords='data', xytext=(-50, -20), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    #strtemp = str('{0:.2f}'.format(gpr_max_QUICKSILVER))+"\% \nB="+str('{0:.0f}'.format(gpr_B_max_QUICKSILVER))+"\%"
    #ax13.annotate(strtemp, xy=(gpr_B_max_QUICKSILVER, gpr_max_QUICKSILVER), xycoords='data', xytext=(-20, -20), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    #strtemp = str('{0:.2f}'.format(full_max_QUICKSILVER))+"\% \nB="+str('{0:.0f}'.format(full_B_max_QUICKSILVER))+"\%"
    #ax13.annotate(strtemp, xy=(full_B_max_QUICKSILVER, full_max_QUICKSILVER), xycoords='data', xytext=(-25, -60), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="dimgray"), fontsize=7, color="dimgray")
    
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
        
    # annotations
    strtemp = str('{0:.2f}'.format(B_NU_QUICKSILVER_GENERIC))+"\% for \nB="+str('{0:.0f}'.format(B_CPF_QUICKSILVER))+"\%"
    ax14.annotate(strtemp, xy=(B_CPF_QUICKSILVER, B_NU_QUICKSILVER_GENERIC), xycoords='data', xytext=(-50, -15), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(B_NU_QUICKSILVER_GPR))+"\% for \nB="+str('{0:.0f}'.format(B_GPR_QUICKSILVER))+"\%"
    ax14.annotate(strtemp, xy=(B_GPR_QUICKSILVER, B_NU_QUICKSILVER_GPR), xycoords='data', xytext=(-60, 10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    
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
    
    ax15.plot([B_points_QUICKSILVER,B_points_QUICKSILVER], [cpf_points_QUICKSILVER,gpr_points_QUICKSILVER], color = "black", linewidth=1, marker="_")
    ytemp = cpf_points_QUICKSILVER - (max_points_QUICKSILVER/2)
    strtemp = "-"+str('{0:.2f}'.format(max_points_QUICKSILVER))+" for \nB="+str('{0:.0f}'.format(B_points_QUICKSILVER))+"\%"
    ax15.annotate(strtemp, xy=(B_points_QUICKSILVER, ytemp), xycoords='data', xytext=(25, -10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
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
    
    ax16.plot([Bv_RELEARN,Bv_RELEARN], [cpfv_RELEARN,gprv_RELEARN], color = "black", linewidth=1, marker="_")
    ytemp = gprv_RELEARN - (maxv_RELEARN/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_RELEARN))+"\% for \nB="+str('{0:.0f}'.format(Bv_RELEARN))+"\%"
    ax16.annotate(strtemp, xy=(Bv_RELEARN, ytemp), xycoords='data', xytext=(20, -20), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    strtemp = str('{0:.2f}'.format(cpf_max_RELEARN))+"\% \nB="+str('{0:.0f}'.format(cpf_B_max_RELEARN))+"\%"
    ax16.annotate(strtemp, xy=(cpf_B_max_RELEARN, cpf_max_RELEARN), xycoords='data', xytext=(-10, -40), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(gpr_max_RELEARN))+"\% \nB="+str('{0:.0f}'.format(gpr_B_max_RELEARN))+"\%"
    ax16.annotate(strtemp, xy=(gpr_B_max_RELEARN, gpr_max_RELEARN), xycoords='data', xytext=(-20, -35), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    strtemp = str('{0:.2f}'.format(full_max_RELEARN))+"\% \nB="+str('{0:.0f}'.format(full_B_max_RELEARN))+"\%"
    ax16.annotate(strtemp, xy=(full_B_max_RELEARN, full_max_RELEARN), xycoords='data', xytext=(-25, -55), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="dimgray"), fontsize=7, color="dimgray")

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
    
    # annotations
    strtemp = str('{0:.2f}'.format(B_NU_RELEARN_GENERIC))+"\% for \nB="+str('{0:.0f}'.format(B_CPF_RELEARN))+"\%"
    ax17.annotate(strtemp, xy=(B_CPF_RELEARN, B_NU_RELEARN_GENERIC), xycoords='data', xytext=(-60, -5), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(B_NU_RELEARN_GPR))+"\% for \nB="+str('{0:.0f}'.format(B_GPR_RELEARN))+"\%"
    ax17.annotate(strtemp, xy=(B_GPR_RELEARN, B_NU_RELEARN_GPR), xycoords='data', xytext=(-35, -45), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    
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
        
    ax18.plot([B_points_RELEARN,B_points_RELEARN], [cpf_points_RELEARN,gpr_points_RELEARN], color = "black", linewidth=1, marker="_")
    ytemp = gpr_points_RELEARN - (max_points_RELEARN/2)
    strtemp = "+"+str('{0:.2f}'.format(max_points_RELEARN))+" for \nB="+str('{0:.0f}'.format(B_points_RELEARN))+"\%"
    ax18.annotate(strtemp, xy=(B_points_RELEARN, ytemp), xycoords='data', xytext=(30, 0), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    ax18.plot([B_points_RELEARN_2,B_points_RELEARN_2], [cpf_points_RELEARN_2,gpr_points_RELEARN_2], color = "black", linewidth=1, marker="_")
    ytemp = cpf_points_RELEARN_2 - (max_points_RELEARN_2/2)
    strtemp = "-"+str('{0:.2f}'.format(max_points_RELEARN_2))+" for \nB="+str('{0:.0f}'.format(B_points_RELEARN_2))+"\%"
    ax18.annotate(strtemp, xy=(B_points_RELEARN_2, ytemp), xycoords='data', xytext=(30, -25), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    
    ax18.grid(alpha=0.3, which='major')
    ax18.grid(alpha=0.3, which='minor')
    ax18.set_xlim(x_values_relearn[0]-2,103)
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