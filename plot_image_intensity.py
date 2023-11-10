import dxtbx
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
import time


# input file path and parameters
def process_args():
    input_args = argparse.ArgumentParser()

    #input file(s) as list
    input_args.add_argument("-i","--input_file",
        nargs="+",
        help="give the input files as list, usually give multiple files for .cbf and one file for .h5, DO NOT mix formats"
        )

    #file format
    input_args.add_argument("-df","--data_format",
        type=str,
        choices = ["cbf","h5", "csv"],
        help="set format of the files, cbf or h5(nxs), or read exported json file, default is .cbf; The cbf format ONLY works for DLS-i24 pilatus detector",
        default = "cbf"
        )
    
    #set low threshold
    input_args.add_argument("-lt","--low_threshold",
        type=int,
        help="set low thresold value filter for the SUM intensity, use this to remove the chip background, default is 0",
        default=0
        )

    #set high threshold
    input_args.add_argument("-ht","--high_threshold",
        type=int,
        help="set high thresold value filter PER PIXEL, default is 15",
        default=15
        )
    
    #save output
    input_args.add_argument("-s","--save_output",
        action='store_true',  
        help="Save image_intensity dictionary as csv file, default is true"
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
    
    #cpu used
    input_args.add_argument("-cpu","--cpu_use",
        type=int,
        help="set number of cpu used, default is 8",
        default=8
        )

    #save args
    args = input_args.parse_args()


    #setup saving default
    if args.save_output == True:
        if not args.output_dir:
            args.output_dir= os.getcwd()
            print(f"No output dir set using current working folder: {args.output_dir}")

        if not args.output_prefix:
            file_name = str(args.input_file[0].split("/")[-1])
            args.output_prefix = file_name.split("_")[0]
            print(f"No output prefix set using the input file name: {args.output_prefix}")
    else:
        print(f"Not saving output, add -s if you want to save the csv")

    return args


    #Check the xrd inputs are allowed
def check_inputs(args:argparse.ArgumentParser):
    if not args.input_file:
        print(f"please give input files")
        exit()

    if args.data_formatnot in ["cbf","h5", "csv"]:
        print(f"input format not recognised {args.data_format}, please give cbf, h5 or csv, exiting")
        exit()


def read_cbf(data:str, args=process_args()):
    if glob.glob(data):
        for path in glob.glob(data):
            #get image number ONLY works for DLS-i24
            file_name = Path(path).stem
            image_number = int(file_name.split("_")[-1])

            #get intensity
            image = dxtbx.load(path)
            i = image.get_raw_data()
            i_array = i.as_numpy_array()
            i_filter = np.where(i_array>args.high_threshold, 0, i_array)
            i_sum = i_array.sum()
            i_sum_filter = i_filter.sum()
            i_diff = i_sum - i_sum_filter
            if i_sum_filter < 0 :
                i_sum_filter = 0
            i_sum_filter_remove_chip = i_sum_filter - args.low_threshold
            print(f"image number: {image_number}; none_filterred intensity: {i_sum}; filtered intensity: {i_sum_filter}; intensity difference: {i_diff}")
    return image_number, i_sum, i_sum_filter, i_diff, i_sum_filter_remove_chip


def read_and_sum_intensities(args:argparse.ArgumentParser):
    image_intensity = {} #dictionary stors image number and intensity
    data = args.input_file
    #cbf files ONLY works af DLS-i24
    if args.data_format == "cbf":
        with multiprocessing.Pool(args.cpu_use) as pool:
            results = pool.imap_unordered(read_cbf, data)
            #print(results)
            pool.close()
            pool.join()
            #add to dict
            for image_number, i_sum, i_sum_filter, i_diff, i_sum_filter_remove_chip in results:
                image_intensity[image_number] = [i_sum, i_sum_filter, i_diff, i_sum_filter_remove_chip]
    
    #h5 files
    elif args.data_format == "h5":
        print(f"h5 files ploting under construction")
        exit()

    #csv plot
    elif args.data_format == "csv":
        if Path(args.input_file[0]).suffix == ".csv":
            if len(args.input_file) == 1:
                pass
            else:
                print(f"Please give ONE .csv file, current has {len(args.input_file)} files")
                exit()
        else:
            print(f"Please give csv file, current is {args.input_file[0]}")
            exit()
    
    print(image_intensity)
    return image_intensity

def save_output(args, image_intensity:dict):
    #get values
    output_file = os.path.join(args.output_dir, args.output_prefix + ".csv")
    image_intensity_list = list(map(list, image_intensity.items()))
    image_intensity_list = sorted(image_intensity_list)
    image_number = [i[0] for i in image_intensity_list]
    sum_intensity_filtered_chip_remove = [i[1][-1] for i in image_intensity_list]
    diff_intensity = [i[1][-2] for i in image_intensity_list]
    all_intensity = [i[1][0] for i in image_intensity_list]
    filtered_intensity = [i[1][1] for i in image_intensity_list]

    #save csv
    with open(output_file,"w", newline='') as output_csv:
        write_csv = csv.writer(output_csv, dialect="excel-tab")
        write_csv.writerow(["Image_Number", "Total_Intensity", "Filtered_intensity", "Intensity_Difference", "Filtered_Intensity_Chip_scattering_removed"])
        for i in range(len(image_number)):
            write_csv.writerow([image_number[i], all_intensity[i], filtered_intensity[i], diff_intensity[i], sum_intensity_filtered_chip_remove[i]])
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
        #print(image_number, sum_intensity_filtered_chip_remove)
        #exit()
    else:
        #print(image_intensity)
        image_intensity_list = list(map(list, image_intensity.items()))
        image_intensity_list = sorted(image_intensity_list)
        for i in image_intensity_list:
            print(i)
        image_number = [i[0] for i in image_intensity_list]
        sum_intensity_filtered_chip_remove = [i[1][-1] for i in image_intensity_list]
        diff_intensity = [i[1][-2] for i in image_intensity_list]
        all_intensity = [i[1][0] for i in image_intensity_list]
        filtered_intensity = [i[1][1] for i in image_intensity_list]

    if max(sum_intensity_filtered_chip_remove) == 0:
        norm_intensity = sum_intensity_filtered_chip_remove
    else:
        norm_intensity = [i/max(sum_intensity_filtered_chip_remove) for i in sum_intensity_filtered_chip_remove]

    #print(image_number, sum_intensity_filtered_chip_remove, norm_intensity)

    font = 12
    #plot all intensities
    plt.figure("sum of intensities per image", figsize = (18, 10))
    plt.subplot(311)
    plt.scatter(image_number, sum_intensity_filtered_chip_remove, marker="o")
    plt.ylabel("All intensities",fontsize=font,fontweight="bold")
    plt.xlabel("image number",fontsize=font)
    plt.title(f"All intensities",fontsize=16)
      
    #plot normalized intensities (intensity/max_intensity)
    plt.subplot(312)
    plt.scatter(image_number, norm_intensity, marker="o")
    plt.ylabel("All intensities",fontsize=font,fontweight="bold")
    plt.xlabel("image number",fontsize=font)
    plt.title(f"Normalized intensities (intensity/max_intensity)",fontsize=16)

    plt.subplot(313)
    plt.plot(image_number, all_intensity, marker="o",label="All intensity")
    plt.plot(image_number, filtered_intensity, marker="o",label="filtered intensity")
    plt.plot(image_number, diff_intensity, marker="o",label="intensity difference")
    plt.ylabel("Intensities",fontsize=font,fontweight="bold")
    plt.xlabel("image number",fontsize=font)
    plt.legend()
    plt.title(f"Filtered/non-filtered intensity difference with the high threshold: {args.high_threshold}",fontsize=16)

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




