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

"""
compare two intensities and save the difference
How to use:
dias.python compare_intensity -i xxx1.csv xxx2.csv

"""

# input file path and parameters
def process_args():
    input_args = argparse.ArgumentParser()

    #input file(s) as list
    input_args.add_argument("-i","--input_file",
        nargs="+",
        help="give the input files as list, give only csv files"
        )
        
    #save output
    input_args.add_argument("-s","--save_output",
        action='store_true',  
        help="Save image_intensity dictionary as csv file, default is false"
        )

    #output directory
    input_args.add_argument("-o", "--output_dir",
        type = str,
        help = "out put directory, default is pwd",
        )

    #output file name prefix
    input_args.add_argument("-p", "--output_prefix",
        type = str,
        help = "out put file prefixed name, no extensions needed, default is same as the input file stem"
        )

    #save args
    args = input_args.parse_args()

    if len(args.input_file) == 2:
        pass
    else:
        print(f"Please give TWO csv files")
        exit()

    return args


def plot_intensity(args):
    file_name_0 = Path(args.input_file[0]).stem
    data = read_csv(args.input_file[0], sep = "\t")
    image_number_0= data["Image_Number"].tolist()
    sum_intensity_0 = data["Filtered_Intensity_Chip_scattering_removed"].tolist()

    file_name_1 = Path(args.input_file[1]).stem
    data = read_csv(args.input_file[1], sep = "\t")
    image_number_1= data["Image_Number"].tolist()
    sum_intensity_1 = data["Filtered_Intensity_Chip_scattering_removed"].tolist()

    difference = [i - j for i,j in zip(sum_intensity_0, sum_intensity_1)]
    difference_x = [i +1 for i in range(len(difference))]

    font = 12
    #plot all intensities
    plt.figure(f"compare intensities: {file_name_0} and {file_name_1}", figsize = (18, 10))
    plt.subplot(211)
    plt.plot(image_number_0, sum_intensity_0, marker="o", label=f"{file_name_0}")
    plt.plot(image_number_1, sum_intensity_1, marker="o", label=f"{file_name_1}")
    plt.ylabel("All intensities",fontsize=font,fontweight="bold")
    plt.xlabel("image number",fontsize=font)
    plt.legend()
    plt.title(f"All intensities",fontsize=16)

    #plot intensity difference
    plt.subplot(212)
    plt.plot(difference_x, difference, marker="o", label=f"{file_name_0} - {file_name_1}")
    plt.ylabel("All intensities",fontsize=font,fontweight="bold")
    plt.xlabel("image number",fontsize=font)
    plt.legend()
    plt.title(f"Intensity difference",fontsize=16)
    plt.show()
    

def main():
    args = process_args()
    print(f"compareing intensities between:  {args.input_file[0]} and {args.input_file[1]}")

    #plot data
    plot_intensity(args)

if __name__ ==  "__main__" :
    main()










