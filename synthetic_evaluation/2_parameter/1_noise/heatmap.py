import matplotlib as mpl
import matplotlib.pyplot as plt
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

def plot_heatmap(x1, x2, data, strategy):

    strat = strategy

    #generic_point_map = np.array(data)
    generic_point_map = np.array([[9, 0, 0, 0, 0],
                        [8, 0, 0, 0, 0],
                        [7, 0, 0, 0, 0],
                        [6, 10, 0, 0, 0],
                        [1, 2, 3, 4, 5],])

    fig, ax = plt.subplots()
    im = ax.imshow(generic_point_map)

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(x1)), labels=x1)
    ax.set_yticks(np.arange(len(x2)), labels=x2)

    # Loop over data dimensions and create text annotations.
    for i in range(len(x2)):
        for j in range(len(x1)):
            text = ax.text(j, i, generic_point_map[i, j],
                        ha="center", va="center", color="w")

    ax.set_title("Point Selection Heatmap "+str(strat)+" Strategy")
    fig.tight_layout()
    plt.savefig('heatmap.png')
    plt.show()
    plt.close()


def main():

    x2 = [50,40,30,20,10]
    x1 = [4,8,16,32,64]
    
    """folder_path = "analysis_results/"
    files = find_files(folder_path)
    #print("DEBUG:",len(files))

    files = natsorted(files)
    #print("DEBUG:",len(files))

    temp = {}
    temp2 = []
    temp3 = []
    for y in x2:
        x_line = []
        x_line2 = []
        for x in x1:
            temp[(x, y)] = 0
            x_line.append((x, y))
            x_line2.append(0)
        temp2.append(x_line)
        temp3.append(x_line2)

    print("temp:",temp)
    print("temp2:",temp2)
    print("temp3:",temp3)

    for i in range(len(files)):
        json_file_path = files[i]
        json_data = read_json_file(json_file_path)

        temp = json_data["point_map_generic"]

        for key, value in temp.items():
            temp[key] += value
        
    for key, value in temp.items():
        value = value / len(files)
        temp[key] = value

    for key, value in temp.items():
        for i in range(len(temp2)):
            if temp2[i] == key:
                temp3[i] = value

    print("temp3:",temp3)"""


    plot_heatmap(x1, x2, [], "GPR")


if __name__ == '__main__':
    main()
