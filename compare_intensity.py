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
        nargs="+",
        help="give the input files as list, give only csv files"
        )

    #cpu used
    input_args.add_argument("-cpu","--cpu_use",
        type=int,
        help="set number of cpu used, default is 8",
        default=8
        )

    #save args
    args = input_args.parse_args()

    return args


def save_output(args, image_intensity:dict):
    #get values
    output_file = os.path.join(args.output_dir, args.output_prefix + ".csv")
    image_intensity_list = list(map(list, image_intensity.items()))
    image_intensity_list = sorted(image_intensity_list)
    image_number = [i[0] for i in image_intensity_list]
    all_intensity = [i[1][0] for i in image_intensity_list]
    filtered_intensity = [i[1][1] for i in image_intensity_list]
    diff_intensity = [i[1][2] for i in image_intensity_list]
    sum_intensity_filtered_chip_remove = [i[1][3] for i in image_intensity_list]
    image_moving_average = [i[1][4] for i in image_intensity_list]

    #save csv
    with open(output_file,"w", newline='') as output_csv:
        write_csv = csv.writer(output_csv, dialect="excel-tab")
        write_csv.writerow(["Image_Number", "Total_Intensity", "Filtered_intensity", "Intensity_Difference", "Filtered_Intensity_Chip_scattering_removed", "moving_average"])
        for i in range(len(image_number)):
            write_csv.writerow([image_number[i], all_intensity[i], filtered_intensity[i], diff_intensity[i], sum_intensity_filtered_chip_remove[i], image_moving_average[i]])
    output_csv.close()

    print(f"Spectra written to {output_file}")

def plot_intensity(args, image_intensity:dict):
    if args.data_format == "csv":
        data = read_csv(args.input_file[0], sep = "\t")
        image_number = data["Image_Number"].tolist()
        sum_intensity_filtered_chip_remove = data["Filtered_Intensity_Chip_scattering_removed"].tolist()
        diff_intensity = data["Intensity_Difference"].tolist()
        all_intensity = data["Total_Intensity"].tolist()
        filtered_intensity = data["Filtered_intensity"].tolist()
        moving_averages = data["moving_average"].tolist()
        #print(image_number, sum_intensity_filtered_chip_remove)
        #exit()
    else:
        #print(image_intensity)
        image_intensity_list = list(map(list, image_intensity.items()))
        image_intensity_list = sorted(image_intensity_list)
        for i in image_intensity_list:
            print(i)
        image_number = [i[0] for i in image_intensity_list]
        all_intensity = [i[1][0] for i in image_intensity_list]
        filtered_intensity = [i[1][1] for i in image_intensity_list]
        diff_intensity = [i[1][2] for i in image_intensity_list]
        sum_intensity_filtered_chip_remove = [i[1][3] for i in image_intensity_list]
        image_moving_average = [i[1][4] for i in image_intensity_list]

    """if max(sum_intensity_filtered_chip_remove) == 0:
        norm_intensity = sum_intensity_filtered_chip_remove
    else:
        norm_intensity = [i/max(sum_intensity_filtered_chip_remove) for i in sum_intensity_filtered_chip_remove]"""

    #print(image_number, sum_intensity_filtered_chip_remove, norm_intensity)

    font = 12
    #plot all intensities
    plt.figure("sum of intensities per image", figsize = (18, 10))
    plt.subplot(211)
    plt.plot(image_number, sum_intensity_filtered_chip_remove, marker="o")
    plt.ylabel("All intensities",fontsize=font,fontweight="bold")
    plt.xlabel("image number",fontsize=font)
    plt.title(f"All intensities",fontsize=16)
      
    #plot intensity with moving average (intensity/max_intensity)
    plt.subplot(212)
    plt.plot(image_number, sum_intensity_filtered_chip_remove, marker="o", label="All intensity")
    plt.plot(image_number, image_moving_average, marker="o", label="Moving average")
    plt.ylabel("All intensities and moving average",fontsize=font,fontweight="bold")
    plt.xlabel("image number",fontsize=font)
    plt.title(f"All intensities with moving average",fontsize=16)

    plt.subplots_adjust(left=0.075, bottom=0.05, right=0.95, top=0.95, hspace=0.5)
    plt.show()
    

def main():
    args = process_args()
    print(f"plot the sum of background intensities per image for Diamond cbf and other h5 files")

    #get the image:intensity dictionary
    starttime = time.time()
    image_intens = read_and_sum_intensities(args)
    #print(image_intens)
    print('That took {} seconds'.format(time.time() - starttime))

    #save the file
    if args.save_output == True:
        save_output(args, image_intens)

    #plot data
    plot_intensity(args, image_intens)

if __name__ ==  "__main__" :
    main()










