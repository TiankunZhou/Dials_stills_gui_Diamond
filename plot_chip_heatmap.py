import numpy as np
import os
import sys
from pathlib import Path
from processing_stills import colors
from matplotlib import pyplot as plt
import argparse
import glob
import csv
from pandas import *
import multiprocessing


# input file path and parameters
def process_args():
    input_args = argparse.ArgumentParser()

    #input file(s) as list
    input_args.add_argument("-i","--input_file",
        type=str,
        help="give the input files as str, give only ONE csv files"
        )


    #save args
    args = input_args.parse_args()
    return args

#convert the 1d list to 2d (n x n):
def convert_1dto2d(data:list, row_number:int):
    new_list = []
    i = 0
    data_length = len(data)
    print(f"Input 1d list length is {data_length}")
    while i + row_number < data_length:
        print(i)
        list_section = [i for i in data[i:i+row_number]]
        new_list.append(list_section)
        i += row_number
    else:
        print(f"last block: {i}")
        list_section =[i for i in data[i:]]
        new_list.append(list_section)
    
    return new_list


#convert the 1-D intensity data to the chip layout
def convert_to_chip(data:list):
    converted_chip_data = []
    block_list = convert_1dto2d(data, 400)
    #print(block_list)

    for i, j in zip(block_list, range(len(block_list))):
        print(f"length of the sublist {j} is : {len(i)}")
        well_list = convert_1dto2d(i, 20)
        converted_chip_data.append(well_list)
    
    #print(converted_chip_data[0], converted_chip_data[-1])
    #print(len(converted_chip_data[0][0]), len(converted_chip_data[-1][-1]))
    return converted_chip_data


def plot_heatmap(args):
    file_name = Path(args.input_file).stem
    data = read_csv(args.input_file, sep = "\t")
    sum_intensity = data["Filtered_Intensity_Chip_scattering_removed"].tolist()

    data = convert_to_chip(sum_intensity)
    test = data[0]
    test2 = data[1]

    font = 12
    #plot all intensities
    plt.figure(f"Heatplot for chip: {file_name}", figsize = (18, 10))
    
    plt.subplot(211)
    plt.imshow(test, cmap='hot', interpolation='nearest')

    plt.subplot(212)
    plt.imshow(test2, cmap='hot', interpolation='nearest')

    plt.show()
    

def main():
    args = process_args()
    print(f"ploting chip heat map for : {args.input_file}")

    #plot data
    plot_heatmap(args)

if __name__ ==  "__main__" :
    main()
