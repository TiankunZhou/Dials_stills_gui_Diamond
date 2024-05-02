import numpy as np
import os
import sys
from pathlib import Path
from processing_stills import colors
import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib
import argparse
import glob
import csv
from pandas import *
import multiprocessing
"""
How to use:

dials.python plot_chip_heatmap -i xxx.csv

"""

# input file path and parameters
def process_args():
    input_args = argparse.ArgumentParser()

    #input file(s) as list
    input_args.add_argument("-i","--input_file",
        type=str,
        help="give the input files as str, give only ONE csv files"
        )

    input_args.add_argument("-t","--test_chip",
        action='store_true',
        help="Use the test dataset to test the chip assignment",
        )

    #save args
    args = input_args.parse_args()
    return args

#convert the 1d list to 2d (n x n), choose how to do the reverse (the line): odd, even, eight, none
def convert_1dto2d(data:list, row_number:int, reverse_option:str):
    new_list = []
    i = 0
    data_length = len(data)
    #print(f"Input 1d list length is {data_length}") #check the length of the data list (image numbers)
    #create a new list with given list sliced into sublists inside it. The lenth of sub lists is the row number.
    while i + row_number < data_length:
        #print(i)
        list_section = [i for i in data[i:i+row_number]]
        new_list.append(list_section)
        i += row_number
    else:
        #print(f"last block: {i}")
        list_section =[i for i in data[i:]]
        new_list.append(list_section)

    #reverse the line, based on the line number starts with 1
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
    #reverse the city block list after every 8 blocks, e.g. [[2800...3199], [3599...3200], [3999...3600]...]
    block_list = convert_1dto2d(data, 400, "eight")

    #convert each 1d citi block to 20 x 20 1d lists, each 1d list has 20 values: [[0...19], [20...39], [40...59]...]
    #then reverse the even row (n+1, as starts with 0): [[0...19], [39...20], [40...59]...]
    for i, j in zip(block_list, range(len(block_list))):
        print(f"length of the sublist {j} is : {len(i)}")
        well_list = convert_1dto2d(i, 20, "even")
        converted_chip_data.append(well_list)
    
    #print(converted_chip_data[0], converted_chip_data[-1])
    #print(len(converted_chip_data[0][0]), len(converted_chip_data[-1][-1]))
    return converted_chip_data


def check_yes_no(data:list):
    yes_or_no = []
    even_list = []
    odd_list = []
    
    """
    create even/ood list, image starts with 1, and the first position is 1 (notated as 0)
        as i starts with 0, need i+1    
    """
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
                    if yes_or_no[-1] > yes_or_no[-2] or yes_or_no[-1] < yes_or_no[-2]:
                        yes_or_no.append(0.5)
                    else:
                        yes_or_no.append(0)
        else:
            yes_or_no.append(0) 
    
    """compare even and odd"""
    even_compare = [1 if i - j == 0 else 0.5 if -0.9 < i - j < 0.9 else 0 for i, j in zip(even_list, yes_or_no)]
    odd_compare = [1 if i - j == 0 else 0.5 if -0.9 < i - j < 0.9 else 0 for i, j in zip(odd_list, yes_or_no)]

    even_test = [i - j for i, j in zip(even_list, yes_or_no)]
    odd_test = [i - j for i, j in zip(odd_list, yes_or_no)]

    #print(even_list)
    #print(odd_list) 
    #print(yes_or_no)
    return yes_or_no, even_compare, odd_compare


def plot_heatmaps(args):
    """get the list of intensities as 1d list"""
    file_name = Path(args.input_file).stem
    data = read_csv(args.input_file, sep = "\t")
    sum_intensity = data["Filtered_Intensity_Chip_scattering_removed"].tolist()

    """check the length of the Intensity list, needs to be 25600, will add 0 intensity if it is shorter"""
    if len(sum_intensity) < 25600:
        number_fill = 25600 - len(sum_intensity)
        fill = 0
        for i in range(number_fill):
            sum_intensity.append(fill)
    
    """test chip layout"""
    test_1d = []
    for i in range(25600):
        test_1d.append(i+1)

    """convert the 1d list intensities to the chip layout"""
    print(colors.BLUE + colors.BOLD + "Sum intensity length" + colors.ENDC)
    data = convert_to_chip(sum_intensity)

    yes_no, even_comp, odd_comp = check_yes_no(sum_intensity)
    print(colors.BLUE + colors.BOLD + "Yes no length" + colors.ENDC)
    
    #Prepare yeas_no list and even/odd compare
    yes_no_chip = convert_to_chip(yes_no)
    print(colors.BLUE + colors.BOLD + "Even chip length" + colors.ENDC)
    even_chip = convert_to_chip(even_comp)
    print(colors.BLUE + colors.BOLD + "Odd chip length" + colors.ENDC)
    odd_chip = convert_to_chip(odd_comp)
    print(colors.BLUE + colors.BOLD + "test data length" + colors.ENDC)
    test = convert_to_chip(test_1d)
    #print(yes_no)

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
        #print(yes_no_chip[test_block[0]])

    """function for multi processing, not working yet"""
    def assign_chip(block_corr:list, datalist:list, plot_type:str):
        fig, axes = plt.subplots(nrows=8, ncols=8, sharex=True, sharey=True, figsize = (18, 10))
        cbar_position = fig.add_axes([.85, .3, .05, .4])
        #costumized color
        colors_all = ["#56B4E9", "#EFEFF8", "#F0E442"]
        colors_yes_no = ["#56B4E9", "#000000", "#F0E442"]
        colors_match = ["#FFD700", "#000000", "#2D68C4"]
        color_bar_all = matplotlib.colors.LinearSegmentedColormap.from_list("", colors_all)

        #vmin and vmax define the global min/max value.
        if plot_type == "all":
            for ax, block in zip(axes.flat, block_assign):
                print(f"preparing: block {block[0]}, row {block[1]}, column {block[2]}")
                sns.heatmap(datalist[block[0]], cmap=color_bar_all, annot=False, cbar=False, linewidths=0.01, linecolor='gray', ax=axes[block[1],block[2]])
            cbar_ax = fig.add_axes(cbar_position)
            cbar = fig.colorbar(axes[0, 0].collections[0], cax=cbar_ax, orientation='vertical')
        elif plot_type == "yes_no":
            for ax, block in zip(axes.flat, block_assign):
                print(f"preparing: block {block[0]}, row {block[1]}, column {block[2]}")
                sns.heatmap(datalist[block[0]], cmap=colors_yes_no, annot=False, cbar=False, vmin=0, vmax=1, linewidths=0.01, linecolor='gray', ax=axes[block[1],block[2]])
            cbar_ax = fig.add_axes(cbar_position)
            cbar = fig.colorbar(axes[0, 0].collections[0], cax=cbar_ax, orientation='vertical')
            cbar.set_ticks([0.15, 0.5, 0.85])
            cbar.set_ticklabels(["No Drop", "Not Sure", "Drop"])
        elif plot_type == "odd_or_even":
            for ax, block in zip(axes.flat, block_assign):
                print(f"preparing: block {block[0]}, row {block[1]}, column {block[2]}")
                sns.heatmap(datalist[block[0]], cmap=colors_match, annot=False, cbar=False, linewidths=0.01, vmin=0, vmax=1, linecolor='gray', ax=axes[block[1],block[2]])
            cbar_ax = fig.add_axes(cbar_position)
            cbar = fig.colorbar(axes[0, 0].collections[0], cax=cbar_ax, orientation='vertical')
            cbar.set_ticks([0.15, 0.5, 0.85])
            cbar.set_ticklabels(["Not Match", "Not Sure", "Match"])
        else:
            print(f"Wrong plot type: {plot_type}, please check the code.")
        fig.subplots_adjust(bottom=0.1, top=0.9, left=0.1, right=0.8, wspace=0.02, hspace=0.02)

    """ploting"""
    """Plot chip layout test"""
    if args.test_chip == True:
        print(f"Preparing test")
        assign_chip(block_assign, test, "all")
        plt.suptitle(f"Chip layout test")

    else:
        """plot overall intensity heatmap """
        print(f"Preparing all intensity")
        assign_chip(block_assign, data, "all")
        plt.suptitle(f"Intensity heatplot for chip: {file_name}")

        """plot drop hit heatmap """
        print(f"Preparing hit map")
        assign_chip(block_assign, yes_no_chip, "yes_no")
        plt.suptitle(f"Hits heatplot for chip: {file_name}")

        """plot the odd match"""
        print(f"Preparing odd match")
        assign_chip(block_assign, odd_chip, "odd_or_even")
        plt.suptitle(f"Odd match for chip: {file_name}")

        """plot the even match"""
        print(f"Preparing even match; Last one")
        assign_chip(block_assign, even_chip, "odd_or_even")
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
