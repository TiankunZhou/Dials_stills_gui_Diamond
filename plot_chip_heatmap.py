import numpy as np
import os
import sys
from pathlib import Path
from processing_stills import colors
import seaborn as sns
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

#convert the 1d list to 2d (n x n), choose how to do the reverse: odd, even, eight, none
def convert_1dto2d(data:list, row_number:int, reverse_option:str):
    new_list = []
    i = 0
    data_length = len(data)
    #print(f"Input 1d list length is {data_length}")
    while i + row_number < data_length:
        #print(i)
        list_section = [i for i in data[i:i+row_number]]
        new_list.append(list_section)
        i += row_number
    else:
        #print(f"last block: {i}")
        list_section =[i for i in data[i:]]
        new_list.append(list_section)

    #define reverse 
    if reverse_option == "odd":
        for i in range(len(new_list)):
            if (i+1)%2 != 0:
                new_list[i].reverse()
    elif reverse_option == "even":
        for i in range(len(new_list)):
            if (i+1)%2 == 0:
                new_list[i].reverse()
    elif reverse_option == "eight":
        for i in range(len(new_list)):
            j = int((i/8) % 8)
            if (j+1)%2 == 0:
                new_list[i].reverse()
    elif reverse_option == "none":
        pass
    
    return new_list

#convert the 1-D intensity data to the chip layout
def convert_to_chip(data:list):
    city_block_notconv = []
    converted_chip_data = []
    #create list with separate block intensities as 1d list: [[0...399], [400...799], [800...1199]...]
    block_list = convert_1dto2d(data, 400, "eight")

    #convert each 1d siti block to 20 x 20 1d lists, each 1d list has 20 values: [[0...19], [20...39], [40...59]...]
    #then reverse the odd row (n+1, as starts with 0): [[19...0], [20...39], [59...40]...]
    for i, j in zip(block_list, range(len(block_list))):
        print(f"length of the sublist {j} is : {len(i)}")
        well_list = convert_1dto2d(i, 20, "odd")
        converted_chip_data.append(well_list)
        #converted_chip_data.append(well_list)
    
    #print(converted_chip_data[0], converted_chip_data[-1])
    #print(len(converted_chip_data[0][0]), len(converted_chip_data[-1][-1]))
    return converted_chip_data


def check_yes_no(data:list):
    yes_or_no = []
    even_list = []
    odd_list = []
    
    """create even list"""
    for i in range(len(data)):
        if (i+1)%2 == 0:
            even_list.append(1)
        else:
            even_list.append(0)
    
        """create odd list"""
        if (i+1)%2 != 0:
            odd_list.append(1)
        else:
            odd_list.append(0)

        """create yes_or_no list"""    
        if i+1 < len(data) - 1 and i != 0:
            if data[i] > data[i+1] and data[i] > data [i-1]:
                yes_or_no.append(1)
            elif data[i] < data[i+1] and data[i] < data [i-1]:
                yes_or_no.append(0)
            else:
                if len(yes_or_no) == 1:
                    yes_or_no.append(0)
                else:
                    if yes_or_no[-1] > yes_or_no[-2]:
                        yes_or_no.append(0.49)
                    elif yes_or_no[-1] < yes_or_no[-2]:
                        yes_or_no.append(0.51)
                    else:
                        yes_or_no.append(0)
        else:
            yes_or_no.append(0) 
    
    """compare even and odd"""
    even_compare = [1 if i - j == 0 else 0.5 if -0.9 < i - j < 0.9 else 0 for i, j in zip(even_list, yes_or_no)]
    odd_compare = [1 if i - j == 0 else 0.5 if -0.9 < i - j < 0.9 else 0 for i, j in zip(odd_list, yes_or_no)]

    #print(even_list)
    #print(odd_list) 
    return yes_or_no, even_compare, odd_compare


def plot_heatmaps(args):
    """get the list of intensities as 1d list"""
    file_name = Path(args.input_file).stem
    data = read_csv(args.input_file, sep = "\t")
    sum_intensity = data["Filtered_Intensity_Chip_scattering_removed"].tolist()
    
    """test chip layout"""
    test_1d = []
    for i in range(25600):
        test_1d.append(i+1)

    """convert the 1d list intensities to the chip layout"""
    data = convert_to_chip(sum_intensity)
    yes_no, even, odd = check_yes_no(sum_intensity)
    yes_no_chip = convert_to_chip(yes_no)
    even_chip = convert_to_chip(even)
    odd_chip = convert_to_chip(odd)
    test = convert_to_chip(test_1d)
    #print(yes_no)
    #plot all intensities
    #plt.figure(f"Heatplot for chip: {file_name}", figsize = (18, 10))

    """asign blocksfor ploting"""
    block_assign = []
    for section in range(len(data)):
        i = (section) % 8
        j = int((section/8) % 8)

        """reverse the city block in the even column (j+1 as column starts with 0)"""
        if (j+1)%2 == 0 :
            i = 7 - i
        else:
            i = i
        block_assign.append([section, i, j])
    
    for test_block in block_assign:
        print(f"block number: {test_block[0]},row: {test_block[1]}, column: {test_block[2]}")
        print(yes_no_chip[test_block[0]])

    """function for multi processing"""
    def assign_chip(block_corr:list, datalist:list):
        fig, axes = plt.subplots(nrows=8, ncols=8, sharex=True, sharey=True, figsize = (18, 10))
        cbar_position = fig.add_axes([.85, .3, .05, .4])
        for block in block_assign:
            print(f"preparing: block {block[0]}, row {block[1]}, column {block[2]}")
            if block[0] == 0:
                sns.heatmap(datalist[block[0]], cmap="RdYlGn", annot=False, cbar=True, cbar_ax=cbar_position, linewidths=0.01, linecolor='gray', ax=axes[block[1],block[2]])
            else:
                sns.heatmap(datalist[block[0]], cmap="RdYlGn", annot=False, cbar=False, linewidths=0.01, linecolor='gray', ax=axes[block[1],block[2]])
        fig.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.8, wspace=0.02, hspace=0.02)

    """ploting"""
    """Plot chip layout test"""
    print(f"Preparing test")
    #assign_chip(block_assign, test)
    #plt.suptitle(f"Chip layout test for: {file_name}")

    """plot overall intensity heatmap """
    print(f"Preparing all intensity")
    assign_chip(block_assign, data)
    plt.suptitle(f"Intensity heatplot for chip: {file_name}")

    """plot drop hit heatmap """
    print(f"Preparing hit map")
    assign_chip(block_assign, yes_no_chip)
    plt.suptitle(f"Hits heatplot for chip: {file_name}")

    """plot the odd match"""
    print(f"Preparing odd match")
    assign_chip(block_assign, odd_chip)
    plt.suptitle(f"Odd match for chip: {file_name}")

    """plot the even match"""
    print(f"Preparing even match; Last one")
    assign_chip(block_assign, even_chip)
    plt.suptitle(f"Even match for chip: {file_name}")

    #plt.show()
    

def main():
    args = process_args()
    print(f"ploting chip heat map for : {args.input_file}")

    #plot data
    plot_heatmaps(args)
    plt.show()

if __name__ ==  "__main__" :
    main()
