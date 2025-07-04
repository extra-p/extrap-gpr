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
        plot_name = "paper_plot_extended.pdf"
    
    path_1 = "2_parameter/1_noise/rebuttal"
    path_2 = "2_parameter/2_noise/rebuttal"
    path_5 = "2_parameter/5_noise/rebuttal"
    path_10 = "2_parameter/10_noise/rebuttal"
    
    path_1_3 = "3_parameter/1_noise/rebuttal"
    path_2_3 = "3_parameter/2_noise/rebuttal"
    path_5_3 = "3_parameter/5_noise/rebuttal"
    path_10_3 = "3_parameter/10_noise/rebuttal"
    
    path_1_4 = "4_parameter/1_noise/rebuttal"
    path_2_4 = "4_parameter/2_noise/rebuttal"
    path_5_4 = "4_parameter/5_noise/rebuttal"
    path_10_4 = "4_parameter/10_noise/rebuttal"
    
    files_1 = find_files(path_1)
    files_2 = find_files(path_2)
    files_5 = find_files(path_5)
    files_10 = find_files(path_10)
    
    files_1_3 = find_files(path_1_3)
    files_2_3 = find_files(path_2_3)
    files_5_3 = find_files(path_5_3)
    files_10_3 = find_files(path_10_3)
    
    files_1_4 = find_files(path_1_4)
    files_2_4 = find_files(path_2_4)
    files_5_4 = find_files(path_5_4)
    files_10_4 = find_files(path_10_4)
    
    x_values = []
    full_values_1 = []
    generic_values_1 = []
    gpr_values_1 = []
    hybrid_values_1 = []
    random_values_1 = []
    grid_values_1 = []
    bayesian_values_1 = []
    
    full_values_2 = []
    generic_values_2 = []
    gpr_values_2 = []
    hybrid_values_2 = []
    random_values_2 = []
    grid_values_2 = []
    bayesian_values_2 = []
    
    full_values_5 = []
    generic_values_5 = []
    gpr_values_5 = []
    hybrid_values_5 = []
    random_values_5 = []
    grid_values_5 = []
    bayesian_values_5 = []
    
    full_values_10 = []
    generic_values_10 = []
    gpr_values_10 = []
    hybrid_values_10 = []
    random_values_10 = []
    grid_values_10 = []
    bayesian_values_10 = []
    
    x_values_3 = []
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
    
    x_values_4 = []
    full_values_1_4 = []
    generic_values_1_4 = []
    gpr_values_1_4 = []
    hybrid_values_1_4 = []
    random_values_1_4 = []
    grid_values_1_4 = []
    bayesian_values_1_4 = []
    
    full_values_2_4 = []
    generic_values_2_4 = []
    gpr_values_2_4 = []
    hybrid_values_2_4 = []
    random_values_2_4 = []
    grid_values_2_4 = []
    bayesian_values_2_4 = []
    
    full_values_5_4 = []
    generic_values_5_4 = []
    gpr_values_5_4 = []
    hybrid_values_5_4 = []
    random_values_5_4 = []
    grid_values_5_4 = []
    bayesian_values_5_4 = []
    
    full_values_10_4 = []
    generic_values_10_4 = []
    gpr_values_10_4 = []
    hybrid_values_10_4 = []
    random_values_10_4 = []
    grid_values_10_4 = []
    bayesian_values_10_4 = []

    generic_costs = []
    gpr_costs = []
    hybrid_costs = []
    random_costs = []
    grid_costs = []
    bayesian_costs = []

    points_generic = []
    points_gpr = []
    points_hybrid = []
    points_random = []
    points_grid = []
    points_bayesian = []

    base_point_costs = []
    base_points = []
    
    all_points = []

    files_1 = natsorted(files_1)
    files_2 = natsorted(files_2)
    files_5 = natsorted(files_5)
    files_10 = natsorted(files_10)
    
    files_1_3 = natsorted(files_1_3)
    files_2_3 = natsorted(files_2_3)
    files_5_3 = natsorted(files_5_3)
    files_10_3 = natsorted(files_10_3)
    
    files_1_4 = natsorted(files_1_4)
    files_2_4 = natsorted(files_2_4)
    files_5_4 = natsorted(files_5_4)
    files_10_4 = natsorted(files_10_4)


    for i in range(len(files_1)):
        json_file_path = files_1[i]
        json_data = read_json_file(json_file_path)

        x_values.append(json_data["budget"])
        full_values_1.append(json_data["percentage_bucket_counter_full"]["5"])
        generic_values_1.append(json_data["percentage_bucket_counter_generic"]["5"])
        gpr_values_1.append(json_data["percentage_bucket_counter_gpr"]["5"])
        hybrid_values_1.append(json_data["percentage_bucket_counter_hybrid"]["5"])
        random_values_1.append(json_data["percentage_bucket_counter_random"]["5"])
        grid_values_1.append(json_data["percentage_bucket_counter_grid"]["5"])
        bayesian_values_1.append(json_data["percentage_bucket_counter_bayesian"]["5"])

        generic_costs.append(json_data["mean_budget_generic"])
        gpr_costs.append(json_data["mean_budget_gpr"])
        hybrid_costs.append(json_data["mean_budget_hybrid"])
        random_costs.append(json_data["mean_budget_random"])
        grid_costs.append(json_data["mean_budget_grid"])
        bayesian_costs.append(json_data["mean_budget_bayesian"])

        points_generic.append(json_data["mean_add_points_generic"])
        points_gpr.append(json_data["mean_add_points_gpr"])
        points_hybrid.append(json_data["mean_add_points_hybrid"])
        points_random.append(json_data["mean_add_points_random"])
        points_grid.append(json_data["mean_add_points_grid"])
        points_bayesian.append(json_data["mean_add_points_bayesian"])
        
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
        random_values_2.append(json_data["percentage_bucket_counter_random"]["5"])
        grid_values_2.append(json_data["percentage_bucket_counter_grid"]["5"])
        bayesian_values_2.append(json_data["percentage_bucket_counter_bayesian"]["5"])

        generic_costs.append(json_data["mean_budget_generic"])
        gpr_costs.append(json_data["mean_budget_gpr"])
        hybrid_costs.append(json_data["mean_budget_hybrid"])
        random_costs.append(json_data["mean_budget_random"])
        grid_costs.append(json_data["mean_budget_grid"])
        bayesian_costs.append(json_data["mean_budget_bayesian"])

        points_generic.append(json_data["mean_add_points_generic"])
        points_gpr.append(json_data["mean_add_points_gpr"])
        points_hybrid.append(json_data["mean_add_points_hybrid"])
        points_random.append(json_data["mean_add_points_random"])
        points_grid.append(json_data["mean_add_points_grid"])
        points_bayesian.append(json_data["mean_add_points_bayesian"])
        
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
        random_values_5.append(json_data["percentage_bucket_counter_random"]["5"])
        grid_values_5.append(json_data["percentage_bucket_counter_grid"]["5"])
        bayesian_values_5.append(json_data["percentage_bucket_counter_bayesian"]["5"])

        generic_costs.append(json_data["mean_budget_generic"])
        gpr_costs.append(json_data["mean_budget_gpr"])
        hybrid_costs.append(json_data["mean_budget_hybrid"])
        random_costs.append(json_data["mean_budget_random"])
        grid_costs.append(json_data["mean_budget_grid"])
        bayesian_costs.append(json_data["mean_budget_bayesian"])

        points_generic.append(json_data["mean_add_points_generic"])
        points_gpr.append(json_data["mean_add_points_gpr"])
        points_hybrid.append(json_data["mean_add_points_hybrid"])
        points_random.append(json_data["mean_add_points_random"])
        points_grid.append(json_data["mean_add_points_grid"])
        points_bayesian.append(json_data["mean_add_points_bayesian"])
        
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
        random_values_10.append(json_data["percentage_bucket_counter_random"]["5"])
        grid_values_10.append(json_data["percentage_bucket_counter_grid"]["5"])
        bayesian_values_10.append(json_data["percentage_bucket_counter_bayesian"]["5"])

        generic_costs.append(json_data["mean_budget_generic"])
        gpr_costs.append(json_data["mean_budget_gpr"])
        hybrid_costs.append(json_data["mean_budget_hybrid"])
        random_costs.append(json_data["mean_budget_random"])
        grid_costs.append(json_data["mean_budget_grid"])
        bayesian_costs.append(json_data["mean_budget_bayesian"])

        points_generic.append(json_data["mean_add_points_generic"])
        points_gpr.append(json_data["mean_add_points_gpr"])
        points_hybrid.append(json_data["mean_add_points_hybrid"])
        points_random.append(json_data["mean_add_points_random"])
        points_grid.append(json_data["mean_add_points_grid"])
        points_bayesian.append(json_data["mean_add_points_bayesian"])
        
        #all_points.append(25*reps)
        #base_point_costs.append(json_data["base_point_cost"])
        #base_points.append(json_data["min_points"])
        
        
    for i in range(len(files_1_3)):
        json_file_path = files_1_3[i]
        json_data = read_json_file(json_file_path)

        #x_values.append(json_data["budget"])
        full_values_1_3.append(json_data["percentage_bucket_counter_full"]["5"])
        generic_values_1_3.append(json_data["percentage_bucket_counter_generic"]["5"])
        gpr_values_1_3.append(json_data["percentage_bucket_counter_gpr"]["5"])
        hybrid_values_1_3.append(json_data["percentage_bucket_counter_hybrid"]["5"])
        random_values_1_3.append(json_data["percentage_bucket_counter_random"]["5"])
        grid_values_1_3.append(json_data["percentage_bucket_counter_grid"]["5"])
        bayesian_values_1_3.append(json_data["percentage_bucket_counter_bayesian"]["5"])
        
    for i in range(len(files_2_3)):
        json_file_path = files_2_3[i]
        json_data = read_json_file(json_file_path)

        #x_values.append(json_data["budget"])
        full_values_2_3.append(json_data["percentage_bucket_counter_full"]["5"])
        generic_values_2_3.append(json_data["percentage_bucket_counter_generic"]["5"])
        gpr_values_2_3.append(json_data["percentage_bucket_counter_gpr"]["5"])
        hybrid_values_2_3.append(json_data["percentage_bucket_counter_hybrid"]["5"])
        random_values_2_3.append(json_data["percentage_bucket_counter_random"]["5"])
        grid_values_2_3.append(json_data["percentage_bucket_counter_grid"]["5"])
        bayesian_values_2_3.append(json_data["percentage_bucket_counter_bayesian"]["5"])
        
    for i in range(len(files_5_3)):
        json_file_path = files_5_3[i]
        json_data = read_json_file(json_file_path)

        #x_values.append(json_data["budget"])
        full_values_5_3.append(json_data["percentage_bucket_counter_full"]["5"])
        generic_values_5_3.append(json_data["percentage_bucket_counter_generic"]["5"])
        gpr_values_5_3.append(json_data["percentage_bucket_counter_gpr"]["5"])
        hybrid_values_5_3.append(json_data["percentage_bucket_counter_hybrid"]["5"])
        random_values_5_3.append(json_data["percentage_bucket_counter_random"]["5"])
        grid_values_5_3.append(json_data["percentage_bucket_counter_grid"]["5"])
        bayesian_values_5_3.append(json_data["percentage_bucket_counter_bayesian"]["5"])
        
    for i in range(len(files_10_3)):
        json_file_path = files_10_3[i]
        json_data = read_json_file(json_file_path)

        #x_values.append(json_data["budget"])
        full_values_10_3.append(json_data["percentage_bucket_counter_full"]["5"])
        generic_values_10_3.append(json_data["percentage_bucket_counter_generic"]["5"])
        gpr_values_10_3.append(json_data["percentage_bucket_counter_gpr"]["5"])
        hybrid_values_10_3.append(json_data["percentage_bucket_counter_hybrid"]["5"])
        random_values_10_3.append(json_data["percentage_bucket_counter_random"]["5"])
        grid_values_10_3.append(json_data["percentage_bucket_counter_grid"]["5"])
        bayesian_values_10_3.append(json_data["percentage_bucket_counter_bayesian"]["5"])
        
    
    for i in range(len(files_1_4)):
        json_file_path = files_1_4[i]
        json_data = read_json_file(json_file_path)

        #x_values.append(json_data["budget"])
        full_values_1_4.append(json_data["percentage_bucket_counter_full"]["5"])
        generic_values_1_4.append(json_data["percentage_bucket_counter_generic"]["5"])
        gpr_values_1_4.append(json_data["percentage_bucket_counter_gpr"]["5"])
        hybrid_values_1_4.append(json_data["percentage_bucket_counter_hybrid"]["5"])
        random_values_1_4.append(json_data["percentage_bucket_counter_random"]["5"])
        grid_values_1_4.append(json_data["percentage_bucket_counter_grid"]["5"])
        bayesian_values_1_4.append(json_data["percentage_bucket_counter_bayesian"]["5"])
        
    for i in range(len(files_2_4)):
        json_file_path = files_2_4[i]
        json_data = read_json_file(json_file_path)

        #x_values.append(json_data["budget"])
        full_values_2_4.append(json_data["percentage_bucket_counter_full"]["5"])
        generic_values_2_4.append(json_data["percentage_bucket_counter_generic"]["5"])
        gpr_values_2_4.append(json_data["percentage_bucket_counter_gpr"]["5"])
        hybrid_values_2_4.append(json_data["percentage_bucket_counter_hybrid"]["5"])
        random_values_2_4.append(json_data["percentage_bucket_counter_random"]["5"])
        grid_values_2_4.append(json_data["percentage_bucket_counter_grid"]["5"])
        bayesian_values_2_4.append(json_data["percentage_bucket_counter_bayesian"]["5"])
        
    for i in range(len(files_5_4)):
        json_file_path = files_5_4[i]
        json_data = read_json_file(json_file_path)

        #x_values.append(json_data["budget"])
        full_values_5_4.append(json_data["percentage_bucket_counter_full"]["5"])
        generic_values_5_4.append(json_data["percentage_bucket_counter_generic"]["5"])
        gpr_values_5_4.append(json_data["percentage_bucket_counter_gpr"]["5"])
        hybrid_values_5_4.append(json_data["percentage_bucket_counter_hybrid"]["5"])
        random_values_5_4.append(json_data["percentage_bucket_counter_random"]["5"])
        grid_values_5_4.append(json_data["percentage_bucket_counter_grid"]["5"])
        bayesian_values_5_4.append(json_data["percentage_bucket_counter_bayesian"]["5"])
        
    for i in range(len(files_10_4)):
        json_file_path = files_10_4[i]
        json_data = read_json_file(json_file_path)

        #x_values.append(json_data["budget"])
        full_values_10_4.append(json_data["percentage_bucket_counter_full"]["5"])
        generic_values_10_4.append(json_data["percentage_bucket_counter_generic"]["5"])
        gpr_values_10_4.append(json_data["percentage_bucket_counter_gpr"]["5"])
        hybrid_values_10_4.append(json_data["percentage_bucket_counter_hybrid"]["5"])
        random_values_10_4.append(json_data["percentage_bucket_counter_random"]["5"])
        grid_values_10_4.append(json_data["percentage_bucket_counter_grid"]["5"])
        bayesian_values_10_4.append(json_data["percentage_bucket_counter_bayesian"]["5"])
    
    y_values_list_acc_1 = [
        full_values_1 ,
        generic_values_1 ,
        gpr_values_1 ,
        hybrid_values_1,
        random_values_1 ,
        grid_values_1,
        bayesian_values_1
    ]
    y_values_list_acc_2 = [
        full_values_2,
        generic_values_2,
        gpr_values_2,
         hybrid_values_2,
        random_values_2,
        grid_values_2,
        bayesian_values_2
    ]
    y_values_list_acc_5 = [
        full_values_5,
        generic_values_5,
        gpr_values_5,
        hybrid_values_5,
        random_values_5,
        grid_values_5,
        bayesian_values_5
    ]
    y_values_list_acc_10 = [
        full_values_10,
        generic_values_10,
        gpr_values_10,
        hybrid_values_10,
        random_values_10,
        grid_values_10,
        bayesian_values_10
    ]
    
    print("m=2, n=+-1%")
    
    full_B_max_2_1 = 0
    maxv = 0
    for i in range(len(full_values_1)):
        if full_values_1[i] >= maxv:
            maxv = full_values_1[i]
            full_B_max_2_1 = x_values[i]
    full_max_2_1 = max(full_values_1)
    print("Max. accuracy Full:",full_max_2_1,"% at B=",full_B_max_2_1,"%.")
    
    cpf_B_max_2_1 = 0
    maxv = 0
    for i in range(len(generic_values_1)):
        if generic_values_1[i] >= maxv:
            maxv = generic_values_1[i]
            cpf_B_max_2_1 = x_values[i]
    cpf_max_2_1 = max(generic_values_1)
    print("Max. accuracy CPF:",cpf_max_2_1,"% at B=",cpf_B_max_2_1,"%.")
    
    gpr_B_max_2_1 = 0
    maxv = 0
    for i in range(len(gpr_values_1)):
        if gpr_values_1[i] >= maxv:
            maxv = gpr_values_1[i]
            gpr_B_max_2_1 = x_values[i]
    gpr_max_2_1 = max(gpr_values_1)
    print("Max. accuracy GPR:",gpr_max_2_1,"% at B=",gpr_B_max_2_1,"%.")

    random_B_max_2_1 = 0
    maxv = 0
    for i in range(len(random_values_1)):
        if random_values_1[i] >= maxv:
            maxv = random_values_1[i]
            random_B_max_2_1 = x_values[i]
    random_max_2_1 = max(random_values_1)
    print("Max. accuracy random:",random_max_2_1,"% at B=",random_B_max_2_1,"%.")

    grid_B_max_2_1 = 0
    maxv = 0
    for i in range(len(grid_values_1)):
        if grid_values_1[i] >= maxv:
            maxv = grid_values_1[i]
            grid_B_max_2_1 = x_values[i]
    grid_max_2_1 = max(grid_values_1)
    print("Max. accuracy grid:",grid_max_2_1,"% at B=",grid_B_max_2_1,"%.")

    bayesian_B_max_2_1 = 0
    maxv = 0
    for i in range(len(bayesian_values_1)):
        if bayesian_values_1[i] >= maxv:
            maxv = bayesian_values_1[i]
            bayesian_B_max_2_1 = x_values[i]
    bayesian_max_2_1 = max(bayesian_values_1)
    print("Max. accuracy bayesian:",bayesian_max_2_1,"% at B=",bayesian_B_max_2_1,"%.")

    hybrid_B_max_2_1 = 0
    maxv = 0
    for i in range(len(hybrid_values_1)):
        if hybrid_values_1[i] >= maxv:
            maxv = hybrid_values_1[i]
            hybrid_B_max_2_1 = x_values[i]
    hybrid_max_2_1 = max(hybrid_values_1)
    print("Max. accuracy hybrid:",hybrid_max_2_1,"% at B=",hybrid_B_max_2_1,"%.")
    
    maxv_2_1 = 0
    Bv_2_1 = 0
    cpfv_2_1 = 0
    gprv_2_1 = 0
    for i in range(len(gpr_values_1)):
        diff = gpr_values_1[i] - generic_values_1[i]
        if diff >= maxv_2_1:
            maxv_2_1 = diff
            Bv_2_1 = x_values[i]
            cpfv_2_1 = generic_values_1[i]
            gprv_2_1 = gpr_values_1[i]
    print("max. difference GPR/CPF:",maxv_2_1,"at B=",Bv_2_1,"%.")
    print("")

    ##################################################################################################
    
    print("m=2, n=+-2%")
    
    full_B_max_2_2 = 0
    maxv = 0
    for i in range(len(full_values_2)):
        if full_values_2[i] >= maxv:
            maxv = full_values_2[i]
            full_B_max_2_2 = x_values[i]
    full_max_2_2 = max(full_values_2)
    print("Max. accuracy Full:",full_max_2_2,"% at B=",full_B_max_2_2,"%.")
    
    cpf_B_max_2_2 = 0
    maxv = 0
    for i in range(len(generic_values_2)):
        if generic_values_2[i] >= maxv:
            maxv = generic_values_2[i]
            cpf_B_max_2_2 = x_values[i]
    cpf_max_2_2 = max(generic_values_2)
    print("Max. accuracy Full:",cpf_max_2_2,"% at B=",cpf_B_max_2_2,"%.")
    
    gpr_B_max_2_2 = 0
    maxv = 0
    for i in range(len(gpr_values_2)):
        if gpr_values_2[i] >= maxv:
            maxv = gpr_values_2[i]
            gpr_B_max_2_2 = x_values[i]
    gpr_max_2_2 = max(gpr_values_2)
    print("Max. accuracy Full:",gpr_max_2_2,"% at B=",gpr_B_max_2_2,"%.")

    random_B_max_2_2 = 0
    maxv = 0
    for i in range(len(random_values_1)):
        if random_values_1[i] >= maxv:
            maxv = random_values_1[i]
            random_B_max_2_2 = x_values[i]
    random_max_2_2 = max(random_values_1)
    print("Max. accuracy random:",random_max_2_2,"% at B=",random_B_max_2_2,"%.")

    grid_B_max_2_2 = 0
    maxv = 0
    for i in range(len(grid_values_1)):
        if grid_values_1[i] >= maxv:
            maxv = grid_values_1[i]
            grid_B_max_2_2 = x_values[i]
    grid_max_2_2 = max(grid_values_1)
    print("Max. accuracy grid:",grid_max_2_2,"% at B=",grid_B_max_2_2,"%.")

    bayesian_B_max_2_2 = 0
    maxv = 0
    for i in range(len(bayesian_values_1)):
        if bayesian_values_1[i] >= maxv:
            maxv = bayesian_values_1[i]
            bayesian_B_max_2_2 = x_values[i]
    bayesian_max_2_2 = max(bayesian_values_1)
    print("Max. accuracy bayesian:",bayesian_max_2_2,"% at B=",bayesian_B_max_2_2,"%.")

    hybrid_B_max_2_2 = 0
    maxv = 0
    for i in range(len(hybrid_values_1)):
        if hybrid_values_1[i] >= maxv:
            maxv = hybrid_values_1[i]
            hybrid_B_max_2_2 = x_values[i]
    hybrid_max_2_2 = max(hybrid_values_1)
    print("Max. accuracy hybrid:",hybrid_max_2_2,"% at B=",hybrid_B_max_2_2,"%.")
    
    maxv_2_2 = 0
    Bv_2_2 = 0
    cpfv_2_2 = 0
    gprv_2_2 = 0
    for i in range(len(gpr_values_2)):
        diff = gpr_values_2[i] - generic_values_2[i]
        if diff >= maxv_2_2:
            maxv_2_2 = diff
            Bv_2_2 = x_values[i]
            cpfv_2_2 = generic_values_2[i]
            gprv_2_2 = gpr_values_2[i]
    print("max. difference GPR/CPF:",maxv_2_2,"at B=",Bv_2_2,"%.")
    
    print("")
    
    ################################################################################################################
    
    print("m=2, n=+-5%")
    
    full_B_max_2_5 = 0
    maxv = 0
    for i in range(len(full_values_5)):
        if full_values_5[i] >= maxv:
            maxv = full_values_5[i]
            full_B_max_2_5 = x_values[i]
    full_max_2_5 = max(full_values_5)
    print("Max. accuracy Full:",full_max_2_5,"% at B=",full_B_max_2_5,"%.")
    
    cpf_B_max_2_5 = 0
    maxv = 0
    for i in range(len(generic_values_5)):
        if generic_values_5[i] >= maxv:
            maxv = generic_values_5[i]
            cpf_B_max_2_5 = x_values[i]
    cpf_max_2_5 = max(generic_values_5)
    print("Max. accuracy Full:",cpf_max_2_5,"% at B=",cpf_B_max_2_5,"%.")
    
    gpr_B_max_2_5 = 0
    maxv = 0
    for i in range(len(gpr_values_5)):
        if gpr_values_5[i] >= maxv:
            maxv = gpr_values_5[i]
            gpr_B_max_2_5 = x_values[i]
    gpr_max_2_5 = max(gpr_values_5)
    print("Max. accuracy Full:",gpr_max_2_5,"% at B=",gpr_B_max_2_5,"%.")

    random_B_max_2_5 = 0
    maxv = 0
    for i in range(len(random_values_1)):
        if random_values_1[i] >= maxv:
            maxv = random_values_1[i]
            random_B_max_2_5 = x_values[i]
    random_max_2_5 = max(random_values_1)
    print("Max. accuracy random:",random_max_2_5,"% at B=",random_B_max_2_5,"%.")

    grid_B_max_2_5 = 0
    maxv = 0
    for i in range(len(grid_values_1)):
        if grid_values_1[i] >= maxv:
            maxv = grid_values_1[i]
            grid_B_max_2_5 = x_values[i]
    grid_max_2_5 = max(grid_values_1)
    print("Max. accuracy grid:",grid_max_2_5,"% at B=",grid_B_max_2_5,"%.")

    bayesian_B_max_2_5 = 0
    maxv = 0
    for i in range(len(bayesian_values_1)):
        if bayesian_values_1[i] >= maxv:
            maxv = bayesian_values_1[i]
            bayesian_B_max_2_5 = x_values[i]
    bayesian_max_2_5 = max(bayesian_values_1)
    print("Max. accuracy bayesian:",bayesian_max_2_5,"% at B=",bayesian_B_max_2_5,"%.")

    hybrid_B_max_2_5 = 0
    maxv = 0
    for i in range(len(hybrid_values_1)):
        if hybrid_values_1[i] >= maxv:
            maxv = hybrid_values_1[i]
            hybrid_B_max_2_5 = x_values[i]
    hybrid_max_2_5 = max(hybrid_values_1)
    print("Max. accuracy hybrid:",hybrid_max_2_5,"% at B=",hybrid_B_max_2_5,"%.")
    
    maxv_2_5 = 0
    Bv_2_5 = 0
    cpfv_2_5 = 0
    gprv_2_5 = 0
    for i in range(len(gpr_values_5)):
        diff = gpr_values_5[i] - generic_values_5[i]
        if diff >= maxv_2_5:
            maxv_2_5 = diff
            Bv_2_5 = x_values[i]
            cpfv_2_5 = generic_values_5[i]
            gprv_2_5 = gpr_values_5[i]
    print("max. difference GPR/CPF:",maxv_2_5,"at B=",Bv_2_5,"%.")
    
    print("")
    
    ##############################################################################################################
    
    print("m=2, n=+-10%")
    
    full_B_max_2_10 = 0
    maxv = 0
    for i in range(len(full_values_10)):
        if full_values_10[i] >= maxv:
            maxv = full_values_10[i]
            full_B_max_2_10 = x_values[i]
    full_max_2_10 = max(full_values_10)
    print("Max. accuracy Full:",full_max_2_10,"% at B=",full_B_max_2_10,"%.")
    
    cpf_B_max_2_10 = 0
    maxv = 0
    for i in range(len(generic_values_10)):
        if generic_values_10[i] >= maxv:
            maxv = generic_values_10[i]
            cpf_B_max_2_10 = x_values[i]
    cpf_max_2_10 = max(generic_values_10)
    print("Max. accuracy Full:",cpf_max_2_10,"% at B=",cpf_B_max_2_10,"%.")
    
    gpr_B_max_2_10 = 0
    maxv = 0
    for i in range(len(gpr_values_10)):
        if gpr_values_10[i] >= maxv:
            maxv = gpr_values_10[i]
            gpr_B_max_2_10 = x_values[i]
    gpr_max_2_10 = max(gpr_values_10)
    print("Max. accuracy Full:",gpr_max_2_10,"% at B=",gpr_B_max_2_10,"%.")

    random_B_max_2_10 = 0
    maxv = 0
    for i in range(len(random_values_1)):
        if random_values_1[i] >= maxv:
            maxv = random_values_1[i]
            random_B_max_2_10 = x_values[i]
    random_max_2_10 = max(random_values_1)
    print("Max. accuracy random:",random_max_2_10,"% at B=",random_B_max_2_10,"%.")

    grid_B_max_2_10 = 0
    maxv = 0
    for i in range(len(grid_values_1)):
        if grid_values_1[i] >= maxv:
            maxv = grid_values_1[i]
            grid_B_max_2_10 = x_values[i]
    grid_max_2_10 = max(grid_values_1)
    print("Max. accuracy grid:",grid_max_2_10,"% at B=",grid_B_max_2_10,"%.")

    bayesian_B_max_2_10 = 0
    maxv = 0
    for i in range(len(bayesian_values_1)):
        if bayesian_values_1[i] >= maxv:
            maxv = bayesian_values_1[i]
            bayesian_B_max_2_10 = x_values[i]
    bayesian_max_2_10 = max(bayesian_values_1)
    print("Max. accuracy bayesian:",bayesian_max_2_10,"% at B=",bayesian_B_max_2_10,"%.")

    hybrid_B_max_2_10 = 0
    maxv = 0
    for i in range(len(hybrid_values_1)):
        if hybrid_values_1[i] >= maxv:
            maxv = hybrid_values_1[i]
            hybrid_B_max_2_10 = x_values[i]
    hybrid_max_2_10 = max(hybrid_values_1)
    print("Max. accuracy hybrid:",hybrid_max_2_10,"% at B=",hybrid_B_max_2_10,"%.")
    
    maxv_2_10 = 0
    Bv_2_10 = 0
    cpfv_2_10 = 0
    gprv_2_10 = 0
    for i in range(len(gpr_values_10)):
        diff = gpr_values_10[i] - generic_values_10[i]
        if diff >= maxv_2_10:
            maxv_2_10 = diff
            Bv_2_10 = x_values[i]
            cpfv_2_10 = generic_values_10[i]
            gprv_2_10 = gpr_values_10[i]
    print("max. difference GPR/CPF:",maxv_2_10,"at B=",Bv_2_10,"%.")
    print("")
    
    #########################################################################################################################
    #########################################################################################################################
    
    y_values_list_acc_1_3 = [
        full_values_1_3 ,
        generic_values_1_3 ,
        gpr_values_1_3 ,
        hybrid_values_1_3,
        random_values_1_3,
        grid_values_1_3,
        bayesian_values_1_3
    ]
    y_values_list_acc_2_3 = [
        full_values_2_3,
        generic_values_2_3,
        gpr_values_2_3,
        hybrid_values_2_3,
        random_values_2_3,
        grid_values_2_3,
        bayesian_values_2_3
    ]
    y_values_list_acc_5_3 = [
        full_values_5_3,
        generic_values_5_3,
        gpr_values_5_3,
        hybrid_values_5_3,
        random_values_5_3,
        grid_values_5_3,
        bayesian_values_5_3
    ]
    y_values_list_acc_10_3 = [
        full_values_10_3,
        generic_values_10_3,
        gpr_values_10_3,
        hybrid_values_10_3,
        random_values_10_3,
        grid_values_10_3,
        bayesian_values_10_3
    ]
    
    ############################################################################################################

    print("m=3, n=+-1%")

    full_B_max_3_1 = 0
    maxv = 0
    for i in range(len(full_values_1_3)):
        if full_values_1_3[i] >= maxv:
            maxv = full_values_1_3[i]
            full_B_max_3_1 = x_values[i]
    full_max_3_1 = max(full_values_1_3)
    print("Max. accuracy Full:",full_max_3_1,"% at B=",full_B_max_3_1,"%.")

    cpf_B_max_3_1 = 0
    maxv = 0
    for i in range(len(generic_values_1_3)):
        if generic_values_1_3[i] >= maxv:
            maxv = generic_values_1_3[i]
            cpf_B_max_3_1 = x_values[i]
    cpf_max_3_1 = max(generic_values_1_3)
    print("Max. accuracy Full:",cpf_max_3_1,"% at B=",cpf_B_max_3_1,"%.")

    gpr_B_max_3_1 = 0
    maxv = 0
    for i in range(len(gpr_values_1_3)):
        if gpr_values_1_3[i] >= maxv:
            maxv = gpr_values_1_3[i]
            gpr_B_max_3_1 = x_values[i]
    gpr_max_3_1 = max(gpr_values_1_3)
    print("Max. accuracy Full:",gpr_max_3_1,"% at B=",gpr_B_max_3_1,"%.")

    random_B_max_3_1 = 0
    maxv = 0
    for i in range(len(random_values_1)):
        if random_values_1[i] >= maxv:
            maxv = random_values_1[i]
            random_B_max_3_1 = x_values[i]
    random_max_3_1 = max(random_values_1)
    print("Max. accuracy random:",random_max_3_1,"% at B=",random_B_max_3_1,"%.")

    grid_B_max_3_1 = 0
    maxv = 0
    for i in range(len(grid_values_1)):
        if grid_values_1[i] >= maxv:
            maxv = grid_values_1[i]
            grid_B_max_3_1 = x_values[i]
    grid_max_3_1 = max(grid_values_1)
    print("Max. accuracy grid:",grid_max_3_1,"% at B=",grid_B_max_3_1,"%.")

    bayesian_B_max_3_1 = 0
    maxv = 0
    for i in range(len(bayesian_values_1)):
        if bayesian_values_1[i] >= maxv:
            maxv = bayesian_values_1[i]
            bayesian_B_max_3_1 = x_values[i]
    bayesian_max_3_1 = max(bayesian_values_1)
    print("Max. accuracy bayesian:",bayesian_max_3_1,"% at B=",bayesian_B_max_3_1,"%.")

    hybrid_B_max_3_1 = 0
    maxv = 0
    for i in range(len(hybrid_values_1)):
        if hybrid_values_1[i] >= maxv:
            maxv = hybrid_values_1[i]
            hybrid_B_max_3_1 = x_values[i]
    hybrid_max_3_1 = max(hybrid_values_1)
    print("Max. accuracy hybrid:",hybrid_max_3_1,"% at B=",hybrid_B_max_3_1,"%.")

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

    ##################################################################################################

    print("m=3, n=+-2%")

    full_B_max_3_2 = 0
    maxv = 0
    for i in range(len(full_values_2_3)):
        if full_values_2_3[i] >= maxv:
            maxv = full_values_2_3[i]
            full_B_max_3_2 = x_values[i]
    full_max_3_2 = max(full_values_2_3)
    print("Max. accuracy Full:",full_max_3_2,"% at B=",full_B_max_3_2,"%.")

    cpf_B_max_3_2 = 0
    maxv = 0
    for i in range(len(generic_values_2_3)):
        if generic_values_2_3[i] >= maxv:
            maxv = generic_values_2_3[i]
            cpf_B_max_3_2 = x_values[i]
    cpf_max_3_2 = max(generic_values_2_3)
    print("Max. accuracy Full:",cpf_max_3_2,"% at B=",cpf_B_max_3_2,"%.")

    gpr_B_max_3_2 = 0
    maxv = 0
    for i in range(len(gpr_values_2_3)):
        if gpr_values_2_3[i] >= maxv:
            maxv = gpr_values_2_3[i]
            gpr_B_max_3_2 = x_values[i]
    gpr_max_3_2 = max(gpr_values_2_3)
    print("Max. accuracy Full:",gpr_max_3_2,"% at B=",gpr_B_max_3_2,"%.")

    random_B_max_3_2 = 0
    maxv = 0
    for i in range(len(random_values_1)):
        if random_values_1[i] >= maxv:
            maxv = random_values_1[i]
            random_B_max_3_2 = x_values[i]
    random_max_3_2 = max(random_values_1)
    print("Max. accuracy random:",random_max_3_2,"% at B=",random_B_max_3_2,"%.")

    grid_B_max_3_2 = 0
    maxv = 0
    for i in range(len(grid_values_1)):
        if grid_values_1[i] >= maxv:
            maxv = grid_values_1[i]
            grid_B_max_3_2 = x_values[i]
    grid_max_3_2 = max(grid_values_1)
    print("Max. accuracy grid:",grid_max_3_2,"% at B=",grid_B_max_3_2,"%.")

    bayesian_B_max_3_2 = 0
    maxv = 0
    for i in range(len(bayesian_values_1)):
        if bayesian_values_1[i] >= maxv:
            maxv = bayesian_values_1[i]
            bayesian_B_max_3_2 = x_values[i]
    bayesian_max_3_2 = max(bayesian_values_1)
    print("Max. accuracy bayesian:",bayesian_max_3_2,"% at B=",bayesian_B_max_3_2,"%.")

    hybrid_B_max_3_2 = 0
    maxv = 0
    for i in range(len(hybrid_values_1)):
        if hybrid_values_1[i] >= maxv:
            maxv = hybrid_values_1[i]
            hybrid_B_max_3_2 = x_values[i]
    hybrid_max_3_2 = max(hybrid_values_1)
    print("Max. accuracy hybrid:",hybrid_max_3_2,"% at B=",hybrid_B_max_3_2,"%.")

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

    ################################################################################################################

    print("m=3, n=+-5%")

    full_B_max_3_5 = 0
    maxv = 0
    for i in range(len(full_values_5_3)):
        if full_values_5_3[i] >= maxv:
            maxv = full_values_5_3[i]
            full_B_max_3_5 = x_values[i]
    full_max_3_5 = max(full_values_5_3)
    print("Max. accuracy Full:",full_max_3_5,"% at B=",full_B_max_3_5,"%.")

    cpf_B_max_3_5 = 0
    maxv = 0
    for i in range(len(generic_values_5_3)):
        if generic_values_5_3[i] >= maxv:
            maxv = generic_values_5_3[i]
            cpf_B_max_3_5 = x_values[i]
    cpf_max_3_5 = max(generic_values_5_3)
    print("Max. accuracy Full:",cpf_max_3_5,"% at B=",cpf_B_max_3_5,"%.")

    gpr_B_max_3_5 = 0
    maxv = 0
    for i in range(len(gpr_values_5_3)):
        if gpr_values_5_3[i] >= maxv:
            maxv = gpr_values_5_3[i]
            gpr_B_max_3_5 = x_values[i]
    gpr_max_3_5 = max(gpr_values_5_3)
    print("Max. accuracy Full:",gpr_max_3_5,"% at B=",gpr_B_max_3_5,"%.")

    random_B_max_3_5 = 0
    maxv = 0
    for i in range(len(random_values_1)):
        if random_values_1[i] >= maxv:
            maxv = random_values_1[i]
            random_B_max_3_5 = x_values[i]
    random_max_3_5 = max(random_values_1)
    print("Max. accuracy random:",random_max_3_5,"% at B=",random_B_max_3_5,"%.")

    grid_B_max_3_5 = 0
    maxv = 0
    for i in range(len(grid_values_1)):
        if grid_values_1[i] >= maxv:
            maxv = grid_values_1[i]
            grid_B_max_3_5 = x_values[i]
    grid_max_3_5 = max(grid_values_1)
    print("Max. accuracy grid:",grid_max_3_5,"% at B=",grid_B_max_3_5,"%.")

    bayesian_B_max_3_5 = 0
    maxv = 0
    for i in range(len(bayesian_values_1)):
        if bayesian_values_1[i] >= maxv:
            maxv = bayesian_values_1[i]
            bayesian_B_max_3_5 = x_values[i]
    bayesian_max_3_5 = max(bayesian_values_1)
    print("Max. accuracy bayesian:",bayesian_max_3_5,"% at B=",bayesian_B_max_3_5,"%.")

    hybrid_B_max_3_5 = 0
    maxv = 0
    for i in range(len(hybrid_values_1)):
        if hybrid_values_1[i] >= maxv:
            maxv = hybrid_values_1[i]
            hybrid_B_max_3_5 = x_values[i]
    hybrid_max_3_5 = max(hybrid_values_1)
    print("Max. accuracy hybrid:",hybrid_max_3_5,"% at B=",hybrid_B_max_3_5,"%.")

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

    ##############################################################################################################

    print("m=3, n=+-10%")

    full_B_max_3_10 = 0
    maxv = 0
    for i in range(len(full_values_10_3)):
        if full_values_10_3[i] >= maxv:
            maxv = full_values_10_3[i]
            full_B_max_3_10 = x_values[i]
    full_max_3_10 = max(full_values_10_3)
    print("Max. accuracy Full:",full_max_3_10,"% at B=",full_B_max_3_10,"%.")

    cpf_B_max_3_10 = 0
    maxv = 0
    for i in range(len(generic_values_10_3)):
        if generic_values_10_3[i] >= maxv:
            maxv = generic_values_10_3[i]
            cpf_B_max_3_10 = x_values[i]
    cpf_max_3_10 = max(generic_values_10_3)
    print("Max. accuracy Full:",cpf_max_3_10,"% at B=",cpf_B_max_3_10,"%.")

    gpr_B_max_3_10 = 0
    maxv = 0
    for i in range(len(gpr_values_10_3)):
        if gpr_values_10_3[i] >= maxv:
            maxv = gpr_values_10_3[i]
            gpr_B_max_3_10 = x_values[i]
    gpr_max_3_10 = max(gpr_values_10_3)
    print("Max. accuracy Full:",gpr_max_3_10,"% at B=",gpr_B_max_3_10,"%.")

    random_B_max_3_10 = 0
    maxv = 0
    for i in range(len(random_values_1)):
        if random_values_1[i] >= maxv:
            maxv = random_values_1[i]
            random_B_max_3_10 = x_values[i]
    random_max_3_10 = max(random_values_1)
    print("Max. accuracy random:",random_max_3_10,"% at B=",random_B_max_3_10,"%.")

    grid_B_max_3_10 = 0
    maxv = 0
    for i in range(len(grid_values_1)):
        if grid_values_1[i] >= maxv:
            maxv = grid_values_1[i]
            grid_B_max_3_10 = x_values[i]
    grid_max_3_10 = max(grid_values_1)
    print("Max. accuracy grid:",grid_max_3_10,"% at B=",grid_B_max_3_10,"%.")

    bayesian_B_max_3_10 = 0
    maxv = 0
    for i in range(len(bayesian_values_1)):
        if bayesian_values_1[i] >= maxv:
            maxv = bayesian_values_1[i]
            bayesian_B_max_3_10 = x_values[i]
    bayesian_max_3_10 = max(bayesian_values_1)
    print("Max. accuracy bayesian:",bayesian_max_3_10,"% at B=",bayesian_B_max_3_10,"%.")

    hybrid_B_max_3_10 = 0
    maxv = 0
    for i in range(len(hybrid_values_1)):
        if hybrid_values_1[i] >= maxv:
            maxv = hybrid_values_1[i]
            hybrid_B_max_3_10 = x_values[i]
    hybrid_max_3_10 = max(hybrid_values_1)
    print("Max. accuracy hybrid:",hybrid_max_3_10,"% at B=",hybrid_B_max_3_10,"%.")

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

    #########################################################################################################################
    #########################################################################################################################
    
    y_values_list_acc_1_4 = [
        full_values_1_4 ,
        generic_values_1_4 ,
        gpr_values_1_4 ,
        hybrid_values_1_4,
        random_values_1_4,
        grid_values_1_4,
        bayesian_values_1_4
    ]
    y_values_list_acc_2_4 = [
        full_values_2_4,
        generic_values_2_4,
        gpr_values_2_4,
        hybrid_values_2_4,
        random_values_2_4,
        grid_values_2_4,
        bayesian_values_2_4
    ]
    y_values_list_acc_5_4 = [
        full_values_5_4,
        generic_values_5_4,
        gpr_values_5_4,
        hybrid_values_5_4,
        random_values_5_4,
        grid_values_5_4,
        bayesian_values_5_4
    ]
    y_values_list_acc_10_4 = [
        full_values_10_4,
        generic_values_10_4,
        gpr_values_10_4,
        hybrid_values_10_4,
        random_values_10_4,
        grid_values_10_4,
        bayesian_values_10_4
    ]

    ############################################################################################################
    
    print("m=4, n=+-1%")

    full_B_max_4_1 = 0
    maxv = 0
    for i in range(len(full_values_1_4)):
        if full_values_1_4[i] >= maxv:
            maxv = full_values_1_4[i]
            full_B_max_4_1 = x_values[i]
    full_max_4_1 = max(full_values_1_4)
    print("Max. accuracy Full:",full_max_4_1,"% at B=",full_B_max_4_1,"%.")

    cpf_B_max_4_1 = 0
    maxv = 0
    for i in range(len(generic_values_1_4)):
        if generic_values_1_4[i] >= maxv:
            maxv = generic_values_1_4[i]
            cpf_B_max_4_1 = x_values[i]
    cpf_max_4_1 = max(generic_values_1_4)
    print("Max. accuracy Full:",cpf_max_4_1,"% at B=",cpf_B_max_4_1,"%.")

    gpr_B_max_4_1 = 0
    maxv = 0
    for i in range(len(gpr_values_1_4)):
        if gpr_values_1_4[i] >= maxv:
            maxv = gpr_values_1_4[i]
            gpr_B_max_4_1 = x_values[i]
    gpr_max_4_1 = max(gpr_values_1_4)
    print("Max. accuracy Full:",gpr_max_4_1,"% at B=",gpr_B_max_4_1,"%.")

    random_B_max_4_1 = 0
    maxv = 0
    for i in range(len(random_values_1)):
        if random_values_1[i] >= maxv:
            maxv = random_values_1[i]
            random_B_max_4_1 = x_values[i]
    random_max_4_1 = max(random_values_1)
    print("Max. accuracy random:",random_max_4_1,"% at B=",random_B_max_4_1,"%.")

    grid_B_max_4_1 = 0
    maxv = 0
    for i in range(len(grid_values_1)):
        if grid_values_1[i] >= maxv:
            maxv = grid_values_1[i]
            grid_B_max_4_1 = x_values[i]
    grid_max_4_1 = max(grid_values_1)
    print("Max. accuracy grid:",grid_max_4_1,"% at B=",grid_B_max_4_1,"%.")

    bayesian_B_max_4_1 = 0
    maxv = 0
    for i in range(len(bayesian_values_1)):
        if bayesian_values_1[i] >= maxv:
            maxv = bayesian_values_1[i]
            bayesian_B_max_4_1 = x_values[i]
    bayesian_max_4_1 = max(bayesian_values_1)
    print("Max. accuracy bayesian:",bayesian_max_4_1,"% at B=",bayesian_B_max_4_1,"%.")

    hybrid_B_max_4_1 = 0
    maxv = 0
    for i in range(len(hybrid_values_1)):
        if hybrid_values_1[i] >= maxv:
            maxv = hybrid_values_1[i]
            hybrid_B_max_4_1 = x_values[i]
    hybrid_max_4_1 = max(hybrid_values_1)
    print("Max. accuracy hybrid:",hybrid_max_4_1,"% at B=",hybrid_B_max_4_1,"%.")

    maxv_4_1 = 0
    Bv_4_1 = 0
    cpfv_4_1 = 0
    gprv_4_1 = 0
    for i in range(len(gpr_values_1_4)):
        diff = gpr_values_1_4[i] - generic_values_1_4[i]
        if diff >= maxv_4_1:
            maxv_4_1 = diff
            Bv_4_1 = x_values[i]
            cpfv_4_1 = generic_values_1_4[i]
            gprv_4_1 = gpr_values_1_4[i]
    print("max. difference GPR/CPF:",maxv_4_1,"at B=",Bv_4_1,"%.")
    print("")

    ##################################################################################################

    print("m=4, n=+-2%")

    full_B_max_4_2 = 0
    maxv = 0
    for i in range(len(full_values_2_4)):
        if full_values_2_4[i] >= maxv:
            maxv = full_values_2_4[i]
            full_B_max_4_2 = x_values[i]
    full_max_4_2 = max(full_values_2_4)
    print("Max. accuracy Full:",full_max_4_2,"% at B=",full_B_max_4_2,"%.")

    cpf_B_max_4_2 = 0
    maxv = 0
    for i in range(len(generic_values_2_4)):
        if generic_values_2_4[i] >= maxv:
            maxv = generic_values_2_4[i]
            cpf_B_max_4_2 = x_values[i]
    cpf_max_4_2 = max(generic_values_2_4)
    print("Max. accuracy Full:",cpf_max_4_2,"% at B=",cpf_B_max_4_2,"%.")

    gpr_B_max_4_2 = 0
    maxv = 0
    for i in range(len(gpr_values_2_4)):
        if gpr_values_2_4[i] >= maxv:
            maxv = gpr_values_2_4[i]
            gpr_B_max_4_2 = x_values[i]
    gpr_max_4_2 = max(gpr_values_2_4)
    print("Max. accuracy Full:",gpr_max_4_2,"% at B=",gpr_B_max_4_2,"%.")

    random_B_max_4_2 = 0
    maxv = 0
    for i in range(len(random_values_1)):
        if random_values_1[i] >= maxv:
            maxv = random_values_1[i]
            random_B_max_4_2 = x_values[i]
    random_max_4_2 = max(random_values_1)
    print("Max. accuracy random:",random_max_4_2,"% at B=",random_B_max_4_2,"%.")

    grid_B_max_4_2 = 0
    maxv = 0
    for i in range(len(grid_values_1)):
        if grid_values_1[i] >= maxv:
            maxv = grid_values_1[i]
            grid_B_max_4_2 = x_values[i]
    grid_max_4_2 = max(grid_values_1)
    print("Max. accuracy grid:",grid_max_4_2,"% at B=",grid_B_max_4_2,"%.")

    bayesian_B_max_4_2 = 0
    maxv = 0
    for i in range(len(bayesian_values_1)):
        if bayesian_values_1[i] >= maxv:
            maxv = bayesian_values_1[i]
            bayesian_B_max_4_2 = x_values[i]
    bayesian_max_4_2 = max(bayesian_values_1)
    print("Max. accuracy bayesian:",bayesian_max_4_2,"% at B=",bayesian_B_max_4_2,"%.")

    hybrid_B_max_4_2 = 0
    maxv = 0
    for i in range(len(hybrid_values_1)):
        if hybrid_values_1[i] >= maxv:
            maxv = hybrid_values_1[i]
            hybrid_B_max_4_2 = x_values[i]
    hybrid_max_4_2 = max(hybrid_values_1)
    print("Max. accuracy hybrid:",hybrid_max_4_2,"% at B=",hybrid_B_max_4_2,"%.")

    maxv_4_2 = 0
    Bv_4_2 = 0
    cpfv_4_2 = 0
    gprv_4_2 = 0
    for i in range(len(gpr_values_2_4)):
        diff = gpr_values_2_4[i] - generic_values_2_4[i]
        if diff >= maxv_4_2:
            maxv_4_2 = diff
            Bv_4_2 = x_values[i]
            cpfv_4_2 = generic_values_2_4[i]
            gprv_4_2 = gpr_values_2_4[i]
    print("max. difference GPR/CPF:",maxv_4_2,"at B=",Bv_4_2,"%.")

    print("")

    ################################################################################################################

    print("m=4, n=+-5%")

    full_B_max_4_5 = 0
    maxv = 0
    for i in range(len(full_values_5_4)):
        if full_values_5_4[i] >= maxv:
            maxv = full_values_5_4[i]
            full_B_max_4_5 = x_values[i]
    full_max_4_5 = max(full_values_5_4)
    print("Max. accuracy Full:",full_max_4_5,"% at B=",full_B_max_4_5,"%.")

    cpf_B_max_4_5 = 0
    maxv = 0
    for i in range(len(generic_values_5_4)):
        if generic_values_5_4[i] >= maxv:
            maxv = generic_values_5_4[i]
            cpf_B_max_4_5 = x_values[i]
    cpf_max_4_5 = max(generic_values_5_4)
    print("Max. accuracy Full:",cpf_max_4_5,"% at B=",cpf_B_max_4_5,"%.")

    gpr_B_max_4_5 = 0
    maxv = 0
    for i in range(len(gpr_values_5_4)):
        if gpr_values_5_4[i] >= maxv:
            maxv = gpr_values_5_4[i]
            gpr_B_max_4_5 = x_values[i]
    gpr_max_4_5 = max(gpr_values_5_4)
    print("Max. accuracy Full:",gpr_max_4_5,"% at B=",gpr_B_max_4_5,"%.")

    random_B_max_4_5 = 0
    maxv = 0
    for i in range(len(random_values_1)):
        if random_values_1[i] >= maxv:
            maxv = random_values_1[i]
            random_B_max_4_5 = x_values[i]
    random_max_4_5 = max(random_values_1)
    print("Max. accuracy random:",random_max_4_5,"% at B=",random_B_max_4_5,"%.")

    grid_B_max_4_5 = 0
    maxv = 0
    for i in range(len(grid_values_1)):
        if grid_values_1[i] >= maxv:
            maxv = grid_values_1[i]
            grid_B_max_4_5 = x_values[i]
    grid_max_4_5 = max(grid_values_1)
    print("Max. accuracy grid:",grid_max_4_5,"% at B=",grid_B_max_4_5,"%.")

    bayesian_B_max_4_5 = 0
    maxv = 0
    for i in range(len(bayesian_values_1)):
        if bayesian_values_1[i] >= maxv:
            maxv = bayesian_values_1[i]
            bayesian_B_max_4_5 = x_values[i]
    bayesian_max_4_5 = max(bayesian_values_1)
    print("Max. accuracy bayesian:",bayesian_max_4_5,"% at B=",bayesian_B_max_4_5,"%.")

    hybrid_B_max_4_5 = 0
    maxv = 0
    for i in range(len(hybrid_values_1)):
        if hybrid_values_1[i] >= maxv:
            maxv = hybrid_values_1[i]
            hybrid_B_max_4_5 = x_values[i]
    hybrid_max_4_5 = max(hybrid_values_1)
    print("Max. accuracy hybrid:",hybrid_max_4_5,"% at B=",hybrid_B_max_4_5,"%.")

    maxv_4_5 = 0
    Bv_4_5 = 0
    cpfv_4_5 = 0
    gprv_4_5 = 0
    for i in range(len(gpr_values_5_4)):
        diff = gpr_values_5_4[i] - generic_values_5_4[i]
        if diff >= maxv_4_5:
            maxv_4_5 = diff
            Bv_4_5 = x_values[i]
            cpfv_4_5 = generic_values_5_4[i]
            gprv_4_5 = gpr_values_5_4[i]
    print("max. difference GPR/CPF:",maxv_4_5,"at B=",Bv_4_5,"%.")

    print("")

    ##############################################################################################################

    print("m=4, n=+-10%")

    full_B_max_4_10 = 0
    maxv = 0
    for i in range(len(full_values_10_4)):
        if full_values_10_4[i] >= maxv:
            maxv = full_values_10_4[i]
            full_B_max_4_10 = x_values[i]
    full_max_4_10 = max(full_values_10_4)
    print("Max. accuracy Full:",full_max_4_10,"% at B=",full_B_max_4_10,"%.")

    cpf_B_max_4_10 = 0
    maxv = 0
    for i in range(len(generic_values_10_4)):
        if generic_values_10_4[i] >= maxv:
            maxv = generic_values_10_4[i]
            cpf_B_max_4_10 = x_values[i]
    cpf_max_4_10 = max(generic_values_10_4)
    print("Max. accuracy Full:",cpf_max_4_10,"% at B=",cpf_B_max_4_10,"%.")

    gpr_B_max_4_10 = 0
    maxv = 0
    for i in range(len(gpr_values_10_4)):
        if gpr_values_10_4[i] >= maxv:
            maxv = gpr_values_10_4[i]
            gpr_B_max_4_10 = x_values[i]
    gpr_max_4_10 = max(gpr_values_10_4)
    print("Max. accuracy Full:",gpr_max_4_10,"% at B=",gpr_B_max_4_10,"%.")

    random_B_max_4_10 = 0
    maxv = 0
    for i in range(len(random_values_1)):
        if random_values_1[i] >= maxv:
            maxv = random_values_1[i]
            random_B_max_4_10 = x_values[i]
    random_max_4_10 = max(random_values_1)
    print("Max. accuracy random:",random_max_4_10,"% at B=",random_B_max_4_10,"%.")

    grid_B_max_4_10 = 0
    maxv = 0
    for i in range(len(grid_values_1)):
        if grid_values_1[i] >= maxv:
            maxv = grid_values_1[i]
            grid_B_max_4_10 = x_values[i]
    grid_max_4_10 = max(grid_values_1)
    print("Max. accuracy grid:",grid_max_4_10,"% at B=",grid_B_max_4_10,"%.")

    bayesian_B_max_4_10 = 0
    maxv = 0
    for i in range(len(bayesian_values_1)):
        if bayesian_values_1[i] >= maxv:
            maxv = bayesian_values_1[i]
            bayesian_B_max_4_10 = x_values[i]
    bayesian_max_4_10 = max(bayesian_values_1)
    print("Max. accuracy bayesian:",bayesian_max_4_10,"% at B=",bayesian_B_max_4_10,"%.")

    hybrid_B_max_4_10 = 0
    maxv = 0
    for i in range(len(hybrid_values_1)):
        if hybrid_values_1[i] >= maxv:
            maxv = hybrid_values_1[i]
            hybrid_B_max_4_10 = x_values[i]
    hybrid_max_4_10 = max(hybrid_values_1)
    print("Max. accuracy hybrid:",hybrid_max_4_10,"% at B=",hybrid_B_max_4_10,"%.")

    maxv_4_10 = 0
    Bv_4_10 = 0
    cpfv_4_10 = 0
    gprv_4_10 = 0
    for i in range(len(gpr_values_10_4)):
        diff = gpr_values_10_4[i] - generic_values_10_4[i]
        if diff >= maxv_4_10:
            maxv_4_10 = diff
            Bv_4_10 = x_values[i]
            cpfv_4_10 = generic_values_10_4[i]
            gprv_4_10 = gpr_values_10_4[i]
    print("max. difference GPR/CPF:",maxv_4_10,"at B=",Bv_4_10,"%.")
    print("")

    #########################################################################################################################
    #########################################################################################################################

    y_values_list_cost = [
        generic_costs,
        gpr_costs,
        hybrid_costs,
        random_costs,
        grid_costs,
        bayesian_costs,
        base_point_costs
    ]
    y_values_list_points = [
        all_points,
        points_generic,
        points_gpr,
        points_hybrid,
        points_random,
        points_grid,
        points_bayesian,
        base_points
    ]
    
    labels_acc = ['Full matrix', 'CPF', 'GPR', 'Hybrid', "Random", "Grid", "Bayesian"]
    labels_cost = ['CPF strategy', 'GPR strategy', 'Hybrid strategy', "Random strategy", "Grid strategy", "Bayesian strategy", 'Min. modeling requirement $\\bar{b}_{min}$']
    labels_points = ['All available points', 'CPF strategy', 'GPR strategy', 'Hybrid strategy', "Random strategy", "Grid strategy", "Bayesian strategy", 'Min. points required $\\bar{p}_{min}$']

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
    fig, ((ax1, ax2, ax3, ax4), (ax5, ax6, ax7, ax8), (ax9, ax10, ax11, ax12)) = plt.subplots(3, 4, figsize=(18.5*cm, 11*cm), sharex=True, sharey=True)
    
    # plot the accuracy of bucket 5 and n=1%
    ls=["-",(0,(1,1)),'-',':',(0, (3,1,1,1,1,1)), "-.", "--"]
    lw = [1,1.5,1.5,3,1.5, 1.5, 1.5]
    ax1.set_xscale("symlog")
    ax1.set_xlim(0.1, 120)
    style_counter = 0
    zorders=[7,6,5,4,3,2,1]
    colors=["gray", "blue", "red", "orange", "purple", "green", "dimgray"]
    
    for y_values, label, color in zip(y_values_list_acc_1, labels_acc, colors):
        if style_counter == 0:
            ax1.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax1.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    
    # annotations
    ax1.plot([Bv_2_1,Bv_2_1], [cpfv_2_1,gprv_2_1], color = "black", linewidth=1, marker="_")
    ytemp = gprv_2_1 - (maxv_2_1/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_2_1))+"\% for \nB="+str('{0:.0f}'.format(Bv_2_1))+"\%"
    ax1.annotate(strtemp, xy=(Bv_2_1, ytemp), xycoords='data', xytext=(-60, 0), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    #strtemp = str('{0:.2f}'.format(cpf_max_2_1))+"\% for \nB="+str('{0:.2f}'.format(cpf_B_max_2_1))+"\%"
    #ax1.annotate(strtemp, xy=(cpf_B_max_2_1, cpf_max_2_1), xycoords='data', xytext=(-50, 0), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7, color="blue")
    #strtemp = str('{0:.2f}'.format(gpr_max_2_1))+"\% for \nB="+str('{0:.2f}'.format(gpr_B_max_2_1))+"\%"
    #ax1.annotate(strtemp, xy=(gpr_B_max_2_1, gpr_max_2_1), xycoords='data', xytext=(0, 0), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7, color="red")
    #strtemp = str('{0:.2f}'.format(full_max_2_1))+"\% for \nB="+str('{0:.2f}'.format(full_B_max_2_1))+"\%"
    #ax1.annotate(strtemp, xy=(full_B_max_2_1, full_max_2_1), xycoords='data', xytext=(50, 0), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7, color="dimgray")

    ax1.grid(alpha=0.3, which='major')
    ax1.grid(alpha=0.3, which='minor')
    ax1.set_yticks(np.arange(0, 100, 10))
    ax1.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    #ax1.set_xlabel('$n=1\%$')
    ax1.set_ylabel('Models within\n $\pm5\%$ at $P_{+}$ [\%]')
    
    # plot the accuracy of bucket 5 and n=2%
    ax2.set_xscale("symlog")
    ax2.set_xlim(0.1, 120)
    style_counter = 0
    for y_values, label, color in zip(y_values_list_acc_2, labels_acc, colors):
        if style_counter == 0:
            ax2.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            #print(x_values, y_values)
            #print(len(x_values), len(y_values))
            ax2.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1

    # annotations
    ax2.plot([Bv_2_2,Bv_2_2], [cpfv_2_2,gprv_2_2], color = "black", linewidth=1, marker="_")
    ytemp = gprv_2_2 - (maxv_2_2/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_2_2))+"\% for \nB="+str('{0:.0f}'.format(Bv_2_2))+"\%"
    ax2.annotate(strtemp, xy=(Bv_2_2, ytemp), xycoords='data', xytext=(-60, 0), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    #strtemp = str('{0:.2f}'.format(cpf_max_2_2))+"\% for \nB="+str('{0:.2f}'.format(cpf_B_max_2_2))+"\%"
    #ax2.annotate(strtemp, xy=(cpf_B_max_2_2, cpf_max_2_2), xycoords='data', xytext=(-50, 0), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7, color="blue")
    #strtemp = str('{0:.2f}'.format(gpr_max_2_2))+"\% for \nB="+str('{0:.2f}'.format(gpr_B_max_2_2))+"\%"
    #ax2.annotate(strtemp, xy=(gpr_B_max_2_2, gpr_max_2_2), xycoords='data', xytext=(-50, -25), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7, color="red")
    #strtemp = str('{0:.2f}'.format(full_max_2_2))+"\% for \nB="+str('{0:.2f}'.format(full_B_max_2_2))+"\%"
    #ax2.annotate(strtemp, xy=(full_B_max_2_2, full_max_2_2), xycoords='data', xytext=(-50, -50), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7, color="dimgray")

    ax2.grid(alpha=0.3, which='major')
    ax2.grid(alpha=0.3, which='minor')
    ax2.set_yticks(np.arange(0, 100, 10))
    ax2.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    #ax2.set_xlabel('$n=2\%$')
    
    # plot the accuracy of bucket 5 and n=5%
    ax3.set_xscale("symlog")
    ax3.set_xlim(0.1, 120)
    style_counter = 0
    for y_values, label, color in zip(y_values_list_acc_5, labels_acc, colors):
        if style_counter == 0:
            ax3.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax3.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    #ax3.fill_between(x_values, y_values_list_acc_5[1], y_values_list_acc_5[2], color="green", where=np.array(y_values_list_acc_5[2]) > np.array(y_values_list_acc_5[1]), alpha=0.4, label='GPR better than CPF', hatch="x", interpolate=True)
    #ax3.fill_between(x_values, y_values_list_acc_5[2], y_values_list_acc_5[1], color="red", where=np.array(y_values_list_acc_5[2]) < np.array(y_values_list_acc_5[1]), alpha=0.4, label='GPR worse than CPF', hatch="+", zorder=5, interpolate=True)
    
    # annotations
    ax3.plot([Bv_2_5,Bv_2_5], [cpfv_2_5,gprv_2_5], color = "black", linewidth=1, marker="_")
    ytemp = gprv_2_5 - (maxv_2_5/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_2_5))+"\% for \nB="+str('{0:.0f}'.format(Bv_2_5))+"\%"
    ax3.annotate(strtemp, xy=(Bv_2_5, ytemp), xycoords='data', xytext=(-60, -25), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    strtemp = str('{0:.2f}'.format(cpf_max_2_5))+"\% \nB="+str('{0:.0f}'.format(cpf_B_max_2_5))+"\%"
    ax3.annotate(strtemp, xy=(cpf_B_max_2_5, cpf_max_2_5), xycoords='data', xytext=(-20, -50), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(gpr_max_2_5))+"\% \nB="+str('{0:.0f}'.format(gpr_B_max_2_5))+"\%"
    ax3.annotate(strtemp, xy=(gpr_B_max_2_5, gpr_max_2_5), xycoords='data', xytext=(-70, -10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    strtemp = str('{0:.2f}'.format(full_max_2_5))+"\% \nB="+str('{0:.0f}'.format(full_B_max_2_5))+"\%"
    ax3.annotate(strtemp, xy=(full_B_max_2_5, full_max_2_5), xycoords='data', xytext=(-25, -55), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color='dimgray'), fontsize=7, color="dimgray")
    
    ax3.grid(alpha=0.3, which='major')
    ax3.grid(alpha=0.3, which='minor')
    ax3.set_yticks(np.arange(0, 100, 10))
    ax3.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    #ax3.set_xlabel('$n=5\%$')
    #ax3.set_ylabel('Models within $\pm15\%$ at $P_{+}$ [%]')
    #ax3.legend(loc="lower right", prop={'size': 8})
    
    # plot the accuracy of bucket 5 and n=10%
    ax4.set_xscale("symlog")
    ax4.set_xlim(0.1, 120)
    style_counter = 0
    for y_values, label, color in zip(y_values_list_acc_10, labels_acc, colors):
        if style_counter == 0:
            ax4.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax4.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    #ax4.fill_between(x_values, y_values_list_acc_10[1], y_values_list_acc_10[2], color="green", where=np.array(y_values_list_acc_10[2]) > np.array(y_values_list_acc_10[1]), alpha=0.4, label='GPR better than CPF', hatch="x", interpolate=True)
    #ax4.fill_between(x_values, y_values_list_acc_10[2], y_values_list_acc_10[1], color="red", where=np.array(y_values_list_acc_10[2]) < np.array(y_values_list_acc_10[1]), alpha=0.4, label='GPR worse than CPF', hatch="+", zorder=5, interpolate=True)
    
    # annotations
    ax4.plot([Bv_2_10,Bv_2_10], [cpfv_2_10,gprv_2_10], color = "black", linewidth=1, marker="_")
    ytemp = gprv_2_10 - (maxv_2_10/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_2_10))+"\% for \nB="+str('{0:.0f}'.format(Bv_2_10))+"\%"
    ax4.annotate(strtemp, xy=(Bv_2_10, ytemp), xycoords='data', xytext=(-60, -15), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    strtemp = str('{0:.2f}'.format(cpf_max_2_10))+"\% \nB="+str('{0:.0f}'.format(cpf_B_max_2_10))+"\%"
    ax4.annotate(strtemp, xy=(cpf_B_max_2_10, cpf_max_2_10), xycoords='data', xytext=(-90, 0), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(gpr_max_2_10))+"\% \nB="+str('{0:.0f}'.format(gpr_B_max_2_10))+"\%"
    ax4.annotate(strtemp, xy=(gpr_B_max_2_10, gpr_max_2_10), xycoords='data', xytext=(-60, -20), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    strtemp = str('{0:.2f}'.format(full_max_2_10))+"\% \nB="+str('{0:.0f}'.format(full_B_max_2_10))+"\%"
    ax4.annotate(strtemp, xy=(full_B_max_2_10, full_max_2_10), xycoords='data', xytext=(-30, -22), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="dimgray"), fontsize=7, color="dimgray")
    
    ax4.grid(alpha=0.3, which='major')
    ax4.grid(alpha=0.3, which='minor')
    ax4.set_yticks(np.arange(0, 100, 10))
    ax4.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    #ax4.set_xlabel('$n=10\%$')
    #ax4.set_ylabel('Models within $\pm20\%$ at $P_{+}$ [%]')
    #ax4.legend(loc="lower right", prop={'size': 8})
    ax42 = ax4.twinx() 
    ax42.set_ylabel("$m=2$")
    ax42.tick_params(right = False)
    ax42.set_yticks([])

    #### 3 parameters #####
    
    # plot the accuracy of bucket 5 and n=1%
    ax5.set_xscale("symlog")
    ax5.set_xlim(0.1, 120)
    style_counter = 0
    for y_values, label, color in zip(y_values_list_acc_1_3, labels_acc, colors):
        if style_counter == 0:
            ax5.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax5.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1

    # annotations
    ax5.plot([Bv_3_1,Bv_3_1], [cpfv_3_1,gprv_3_1], color = "black", linewidth=1, marker="_")
    ytemp = gprv_3_1 - (maxv_3_1/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_3_1))+"\% for \nB="+str('{0:.0f}'.format(Bv_3_1))+"\%"
    ax5.annotate(strtemp, xy=(Bv_3_1, ytemp), xycoords='data', xytext=(10, -40), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    #strtemp = str('{0:.2f}'.format(cpf_max_3_1))+"\% for \nB="+str('{0:.2f}'.format(cpf_B_max_3_1))+"\%"
    #ax5.annotate(strtemp, xy=(cpf_B_max_3_1, cpf_max_3_1), xycoords='data', xytext=(-50, 0), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    #strtemp = str('{0:.2f}'.format(gpr_max_3_1))+"\% for \nB="+str('{0:.2f}'.format(gpr_B_max_3_1))+"\%"
    #ax5.annotate(strtemp, xy=(gpr_B_max_3_1, gpr_max_3_1), xycoords='data', xytext=(-50, -25), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    #strtemp = str('{0:.2f}'.format(full_max_3_1))+"\% for \nB="+str('{0:.2f}'.format(full_B_max_3_1))+"\%"
    #ax5.annotate(strtemp, xy=(full_B_max_3_1, full_max_3_1), xycoords='data', xytext=(-50, -50), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="dimgray"), fontsize=7, color="dimgray")

    ax5.grid(alpha=0.3, which='major')
    ax5.grid(alpha=0.3, which='minor')
    ax5.set_yticks(np.arange(0, 100, 10))
    ax5.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    #ax5.set_xlabel('$n=1\%$')
    ax5.set_ylabel('Models within\n $\pm5\%$ at $P_{+}$ [\%]')
    
    ax6.set_xscale("symlog")
    ax6.set_xlim(0.1, 120)
    style_counter = 0
    for y_values, label, color in zip(y_values_list_acc_2_3, labels_acc, colors):
        if style_counter == 0:
            ax6.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax6.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1

    # annotations
    ax6.plot([Bv_3_2,Bv_3_2], [cpfv_3_2,gprv_3_2], color = "black", linewidth=1, marker="_")
    ytemp = gprv_3_2 - (maxv_3_2/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_3_2))+"\% for \nB="+str('{0:.0f}'.format(Bv_3_2))+"\%"
    ax6.annotate(strtemp, xy=(Bv_3_2, ytemp), xycoords='data', xytext=(10, -40), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    #strtemp = str('{0:.2f}'.format(cpf_max_3_2))+"\% for \nB="+str('{0:.2f}'.format(cpf_B_max_3_2))+"\%"
    #ax6.annotate(strtemp, xy=(cpf_B_max_3_2, cpf_max_3_2), xycoords='data', xytext=(-50, 0), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7, color="blue")
    #strtemp = str('{0:.2f}'.format(gpr_max_3_2))+"\% for \nB="+str('{0:.2f}'.format(gpr_B_max_3_2))+"\%"
    #ax6.annotate(strtemp, xy=(gpr_B_max_3_2, gpr_max_3_2), xycoords='data', xytext=(-50, -25), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7, color="red")
    #strtemp = str('{0:.2f}'.format(full_max_3_2))+"\% for \nB="+str('{0:.2f}'.format(full_B_max_3_2))+"\%"
    #ax6.annotate(strtemp, xy=(full_B_max_3_2, full_max_3_2), xycoords='data', xytext=(-50, -50), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7, color="dimgray")

    ax6.grid(alpha=0.3, which='major')
    ax6.grid(alpha=0.3, which='minor')
    ax6.set_yticks(np.arange(0, 100, 10))
    ax6.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    #ax6.set_xlabel('$n=2\%$')
    
    ax7.set_xscale("symlog")
    ax7.set_xlim(0.1, 120)
    style_counter = 0
    for y_values, label, color in zip(y_values_list_acc_5_3, labels_acc, colors):
        if style_counter == 0:
            ax7.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax7.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1

    # annotations
    ax7.plot([Bv_3_5,Bv_3_5], [cpfv_3_5,gprv_3_5], color = "black", linewidth=1, marker="_")
    ytemp = gprv_3_5 - (maxv_3_5/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_3_5))+"\% for \nB="+str('{0:.0f}'.format(Bv_3_5))+"\%"
    ax7.annotate(strtemp, xy=(Bv_3_5, ytemp), xycoords='data', xytext=(15, -45), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    strtemp = str('{0:.2f}'.format(cpf_max_3_5))+"\% for \nB="+str('{0:.0f}'.format(cpf_B_max_3_5))+"\%"
    ax7.annotate(strtemp, xy=(cpf_B_max_3_5, cpf_max_3_5), xycoords='data', xytext=(-97, -10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(gpr_max_3_5))+"\% \nB="+str('{0:.0f}'.format(gpr_B_max_3_5))+"\%"
    ax7.annotate(strtemp, xy=(gpr_B_max_3_5, gpr_max_3_5), xycoords='data', xytext=(-25, -40), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    #strtemp = str('{0:.2f}'.format(full_max_3_5))+"\% for \nB="+str('{0:.2f}'.format(full_B_max_3_5))+"\%"
    #ax7.annotate(strtemp, xy=(full_B_max_3_5, full_max_3_5), xycoords='data', xytext=(-50, -70), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7, color="dimgray")

    ax7.grid(alpha=0.3, which='major')
    ax7.grid(alpha=0.3, which='minor')
    ax7.set_yticks(np.arange(0, 100, 10))
    ax7.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    #ax7.set_xlabel('$n=5\%$')
    
    ax8.set_xscale("symlog")
    ax8.set_xlim(0.1, 120)
    style_counter = 0
    for y_values, label, color in zip(y_values_list_acc_10_3, labels_acc, colors):
        if style_counter == 0:
            ax8.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax8.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1

    # annotations
    ax8.plot([Bv_3_10,Bv_3_10], [cpfv_3_10,gprv_3_10], color = "black", linewidth=1, marker="_")
    ytemp = gprv_3_10 - (maxv_3_10/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_3_10))+"\% for \nB="+str('{0:.0f}'.format(Bv_3_10))+"\%"
    ax8.annotate(strtemp, xy=(Bv_3_10, ytemp), xycoords='data', xytext=(15, -35), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    #strtemp = str('{0:.2f}'.format(cpf_max_3_10))+"\% for \nB="+str('{0:.2f}'.format(cpf_B_max_3_10))+"\%"
    #ax8.annotate(strtemp, xy=(cpf_B_max_3_10, cpf_max_3_10), xycoords='data', xytext=(-50, 0), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7, color="blue")
    #strtemp = str('{0:.2f}'.format(gpr_max_3_10))+"\% for \nB="+str('{0:.2f}'.format(gpr_B_max_3_10))+"\%"
    #ax8.annotate(strtemp, xy=(gpr_B_max_3_10, gpr_max_3_10), xycoords='data', xytext=(-50, -25), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7, color="red")
    #strtemp = str('{0:.2f}'.format(full_max_3_10))+"\% for \nB="+str('{0:.2f}'.format(full_B_max_3_10))+"\%"
    #ax8.annotate(strtemp, xy=(full_B_max_3_10, full_max_3_10), xycoords='data', xytext=(-50, -50), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7, color="dimgray")

    ax8.grid(alpha=0.3, which='major')
    ax8.grid(alpha=0.3, which='minor')
    ax8.set_yticks(np.arange(0, 100, 10))
    ax8.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    #ax8.set_xlabel('$n=10\%$')
    ax82 = ax8.twinx() 
    ax82.set_ylabel("$m=3$")
    ax82.tick_params(right = False)
    ax82.set_yticks([])
    
    #### 4 parameters ######

    # plot the accuracy of bucket 5 and n=1%
    ax9.set_xscale("symlog")
    ax9.set_xlim(0.1, 120)
    style_counter = 0
    for y_values, label, color in zip(y_values_list_acc_1_4, labels_acc, colors):
        if style_counter == 0:
            ax9.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax9.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1

    # annotations
    ax9.plot([Bv_4_1,Bv_4_1], [cpfv_4_1,gprv_4_1], color = "black", linewidth=1, marker="_")
    ytemp = gprv_4_1 - (maxv_4_1/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_4_1))+"\% for \nB="+str('{0:.1f}'.format(Bv_4_1))+"\%"
    ax9.annotate(strtemp, xy=(Bv_4_1, ytemp), xycoords='data', xytext=(15, -10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    strtemp = str('{0:.2f}'.format(cpf_max_4_1))+"\% \nB="+str('{0:.0f}'.format(cpf_B_max_4_1))+"\%"
    ax9.annotate(strtemp, xy=(cpf_B_max_4_1, cpf_max_4_1), xycoords='data', xytext=(-40, -40), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(gpr_max_4_1))+"\% \nB="+str('{0:.0f}'.format(gpr_B_max_4_1))+"\%"
    ax9.annotate(strtemp, xy=(gpr_B_max_4_1, gpr_max_4_1), xycoords='data', xytext=(-25, -70), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    #strtemp = str('{0:.2f}'.format(full_max_4_1))+"\% for \nB="+str('{0:.0f}'.format(full_B_max_4_1))+"\%"
    #ax9.annotate(strtemp, xy=(full_B_max_4_1, full_max_4_1), xycoords='data', xytext=(-50, -50), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7, color="dimgray")

    ax9.grid(alpha=0.3, which='major')
    ax9.grid(alpha=0.3, which='minor')
    ax9.set_yticks(np.arange(0, 100, 10))
    ax9.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    ax9.set_xlabel('$n=\pm1\%$')
    ax9.set_ylabel('Models within\n $\pm5\%$ at $P_{+}$ [\%]')
    
    ax10.set_xscale("symlog")
    ax10.set_xlim(0.1, 120)
    style_counter = 0
    for y_values, label, color in zip(y_values_list_acc_2_4, labels_acc, colors):
        if style_counter == 0:
            ax10.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax10.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1

    # annotations
    ax10.plot([Bv_4_2,Bv_4_2], [cpfv_4_2,gprv_4_2], color = "black", linewidth=1, marker="_")
    ytemp = gprv_4_2 - (maxv_4_2/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_4_2))+"\% for \nB="+str('{0:.1f}'.format(Bv_4_2))+"\%"
    ax10.annotate(strtemp, xy=(Bv_4_2, ytemp), xycoords='data', xytext=(15, -10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    strtemp = str('{0:.2f}'.format(cpf_max_4_2))+"\% \nB="+str('{0:.0f}'.format(cpf_B_max_4_2))+"\%"
    ax10.annotate(strtemp, xy=(cpf_B_max_4_2, cpf_max_4_2), xycoords='data', xytext=(-35, -40), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(gpr_max_4_2))+"\% \nB="+str('{0:.0f}'.format(gpr_B_max_4_2))+"\%"
    ax10.annotate(strtemp, xy=(gpr_B_max_4_2, gpr_max_4_2), xycoords='data', xytext=(-25, -70), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    #strtemp = str('{0:.2f}'.format(full_max_4_2))+"\% for \nB="+str('{0:.0f}'.format(full_B_max_4_2))+"\%"
    #ax10.annotate(strtemp, xy=(full_B_max_4_2, full_max_4_2), xycoords='data', xytext=(-50, -50), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7, color="dimgray")

    ax10.grid(alpha=0.3, which='major')
    ax10.grid(alpha=0.3, which='minor')
    ax10.set_yticks(np.arange(0, 100, 10))
    ax10.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    ax10.set_xlabel('$n=\pm2\%$')
    
    ax11.set_xscale("symlog")
    ax11.set_xlim(0.1, 120)
    style_counter = 0
    for y_values, label, color in zip(y_values_list_acc_5_4, labels_acc, colors):
        if style_counter == 0:
            ax11.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax11.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1

    # annotations
    ax11.plot([Bv_4_5,Bv_4_5], [cpfv_4_5,gprv_4_5], color = "black", linewidth=1, marker="_")
    ytemp = gprv_4_5 - (maxv_4_5/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_4_5))+"\% for \nB="+str('{0:.1f}'.format(Bv_4_5))+"\%"
    ax11.annotate(strtemp, xy=(Bv_4_5, ytemp), xycoords='data', xytext=(15, -10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    strtemp = str('{0:.2f}'.format(cpf_max_4_5))+"\% for \nB="+str('{0:.0f}'.format(cpf_B_max_4_5))+"\%"
    ax11.annotate(strtemp, xy=(cpf_B_max_4_5, cpf_max_4_5), xycoords='data', xytext=(-70, -5), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(gpr_max_4_5))+"\% \nB="+str('{0:.0f}'.format(gpr_B_max_4_5))+"\%"
    ax11.annotate(strtemp, xy=(gpr_B_max_4_5, gpr_max_4_5), xycoords='data', xytext=(-20, -60), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    #strtemp = str('{0:.2f}'.format(full_max_4_5))+"\% \nB="+str('{0:.0f}'.format(full_B_max_4_5))+"\%"
    #ax11.annotate(strtemp, xy=(full_B_max_4_5, full_max_4_5), xycoords='data', xytext=(-30, -70), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="dimgray"), fontsize=7, color="dimgray")

    ax11.grid(alpha=0.3, which='major')
    ax11.grid(alpha=0.3, which='minor')
    ax11.set_yticks(np.arange(0, 100, 10))
    ax11.set_xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,8,9,10,20,30,40,50,60,70,80,90,100])
    ax11.set_xlabel('$n=\pm5\%$')
    
    ax12.set_xscale("symlog")
    ax12.set_xlim(0.1, 120)
    style_counter = 0
    for y_values, label, color in zip(y_values_list_acc_10_4, labels_acc, colors):
        if style_counter == 0:
            ax12.scatter(100, y_values[len(y_values)-1], s=15, label=label, marker="D", linestyle = 'None', zorder=10, edgecolor="black", facecolor=colors[style_counter])
        else:
            ax12.plot(x_values, y_values, label=label, linestyle=ls[style_counter], linewidth=lw[style_counter], alpha=0.7, color=colors[style_counter], zorder=zorders[style_counter])
        style_counter += 1
    
    # annotations
    ax12.plot([Bv_4_10,Bv_4_10], [cpfv_4_10,gprv_4_10], color = "black", linewidth=1, marker="_")
    ytemp = gprv_4_10 - (maxv_4_10/2)
    strtemp = "+"+str('{0:.2f}'.format(maxv_4_10))+"\% for \nB="+str('{0:.1f}'.format(Bv_4_10))+"\%"
    ax12.annotate(strtemp, xy=(Bv_4_10, ytemp), xycoords='data', xytext=(15, -10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5,), fontsize=7)
    strtemp = str('{0:.2f}'.format(cpf_max_4_10))+"\% for \nB="+str('{0:.0f}'.format(cpf_B_max_4_10))+"\%"
    ax12.annotate(strtemp, xy=(cpf_B_max_4_10, cpf_max_4_10), xycoords='data', xytext=(-70, -10), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="blue"), fontsize=7, color="blue")
    strtemp = str('{0:.2f}'.format(gpr_max_4_10))+"\% \nB="+str('{0:.0f}'.format(gpr_B_max_4_10))+"\%"
    ax12.annotate(strtemp, xy=(gpr_B_max_4_10, gpr_max_4_10), xycoords='data', xytext=(-20, -60), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="red"), fontsize=7, color="red")
    #strtemp = str('{0:.2f}'.format(full_max_4_10))+"\% \nB="+str('{0:.0f}'.format(full_B_max_4_10))+"\%"
    #ax12.annotate(strtemp, xy=(full_B_max_4_10, full_max_4_10), xycoords='data', xytext=(-25, -60), textcoords='offset points', arrowprops=dict(arrowstyle="->", lw=0.5, color="dimgray"), fontsize=7, color="dimgray")

    ax12.set_yticks(np.arange(0, 100, 10))
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
    ax122.set_yticks([])
    
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=7, bbox_to_anchor=(0.5, 1.065), frameon=False, fontsize=8, columnspacing=0.8)
    
    fig.text(0.5, -0.05, 'Allowed modeling budget $B$ [\%]', ha='center', fontsize=8)
    
    fig.tight_layout(pad=0.2)
    plt.savefig(plot_name, bbox_inches="tight")
    plt.show()
    plt.close()

if __name__ == '__main__':
    main()