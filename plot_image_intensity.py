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
import h5py

"""
How to use:

dials.python plot_image_intensity.py -i /dls/i24/data/2024/mx32727-20/emptychip/naomi/* -df cbf -ht 30 -s -c

image number 0 maybe someting as a trigger, real data starts from image number 1
Be careful when interpreted the data, as list position 0 = image 1
solvent scattering to ~4A, leave the resolution to ~2.5A currently
"""

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
    
    #cpu used
    input_args.add_argument("-cpu","--cpu_use",
        type=int,
        help="set number of cpu used, default is 8",
        default=8
        )

    #window size for moving average
    input_args.add_argument("-ws","--window_size",
        type=int,
        help="set number of cpu used, default is 2",
        default=2
        )
    #whether use the central of the detector (as rectangular) for intensity sum
    input_args.add_argument("-c","--centre_region",
        action='store_true',
        help="set whether using centre of the detector (~60%) for intensity calculatio, default is False",
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

#calculate the moving average, with window size of 10
def moving_average(args, dataset:dict):
    moving_average = []
    #print(dataset)
    image_intensity_list = list(map(list, dataset.items()))
    image_intensity_list = sorted(image_intensity_list)
    image_intensity = [i[-1] for i in image_intensity_list]
    window_size = args.window_size
    for i in range(len(image_intensity)):
        if i < len(image_intensity) - window_size + 1:
            window = image_intensity[i:i+window_size]
            #print(window)
            window_average = round(sum(window)/len(window), 4)
        elif i > len(image_intensity) - window_size + 1:
            window = image_intensity[i:-1]
            window_average = round(sum(window)/(len(image_intensity) - i), 5)
        moving_average.append(window_average)
    #print(f"moving average: {moving_average}")
    return moving_average


def read_cbf(data:str, args=process_args()):
    if glob.glob(data):
        for path in glob.glob(data):
            #get image number ONLY works for DLS-i24
            file_name = Path(path).stem
            image_number = int(file_name.split("_")[-1])

            #get intensity
            image = dxtbx.load(path)
            i = image.get_raw_data() #get the intensity per pixel 
            i_array = i.as_numpy_array() #convenrt the intensity per pixel as a 2-D np.array
            i_filter = np.where(i_array>args.high_threshold, 0, i_array) #filter the potential bragg peaks based on the pixel intensity

            #sum the intensity for whole and the centre of detector
            if args.centre_region == True:
                i_centre = i_array[424:2105, 492:1970]  # use the centre of the detector for intensity sum, as a rectangular
                i_centre_filter = i_filter[424:2105, 492:1970]
                i_sum = i_centre.sum()
                i_sum_filter = i_centre_filter.sum()
            else:
                i_sum = i_array.sum()
                i_sum_filter = i_filter.sum()
            
            i_diff = i_sum - i_sum_filter

            if i_sum_filter < 0 :
                i_sum_filter = 0
            i_sum_filter_remove_chip = i_sum_filter - args.low_threshold
            if image_number <= 0:
                print(f"cbf image number: {image_number} is probabily a trigger image, real data starts from image number: 1")
            else:
                print(f"image number: {image_number}; none_filterred intensity: {i_sum}; filtered intensity: {i_sum_filter}; intensity difference: {i_diff}")
    return image_number, i_sum, i_sum_filter, i_diff, i_sum_filter_remove_chip

"""
red h5 files, current olny work for h5 at PAL-XFEL with Rayonix detector
"""
#Get the file number of the first h5 file for combine datasets per chip
def first_image_h5(data_list:list):
    file_number_list = [] #combine intensiies of mutiple h5 files, if the data are split into several files
    for path in data_list:
        file_name = Path(path).stem
        file_number = int(file_name)
        file_number_list.append(file_number)
    
    file_number_sorted = sorted(file_number_list)
    first_file_number = file_number_sorted[0]
    print(file_number_sorted )

    return first_file_number


def read_h5(data:str, args=process_args()):
    image_intensity_h5_unordered = {}
    i_filtered_chip_h5_unordered = {}
    first_file = first_image_h5(args.input_file)
    if glob.glob(data):
        for path in glob.glob(data):
            #get the file stem name and the name of the first key in the h5 file and the data in h5
            file_name = Path(path).stem
            h5_main_key =  'R' + file_name[3:]
            data_in_h5 = h5_main_key + '/scan_dat/raymx_data'
            file_position = int(file_name) - first_file  #give the number of the file, for finding image numbers

            #get image list with intensities pixel as list
            file_h5 = h5py.File(path, "r")
            image_list = list(file_h5[data_in_h5])

            #get overall intensity per image
            for index_number in range(len(image_list)):
                image_number = int(index_number) + 1 + (file_position * 1000)
                i = image_list[index_number] #get intensity per pixel as a 2d list
                i_array = np.array(i)
                i_filter = np.where(i_array>args.high_threshold, 0, i_array) #filter the potential bragg peaks based on the pixel intensity

            #sum the intensity for whole and the centre of detector
                if args.centre_region == True:
                    i_centre = i_array[360:1080, 360:1080]  # use the centre of the detector for intensity sum, as a rectangular
                    i_centre_filter = i_filter[360:1080, 360:1080]
                    i_sum = i_centre.sum()
                    i_sum_filter = i_centre_filter.sum()
                else:
                    i_sum = i_array.sum()
                    i_sum_filter = i_filter.sum()
                
                i_diff = i_sum - i_sum_filter

                if i_sum_filter < 0 :
                    i_sum_filter = 0
                i_sum_filter_remove_chip = i_sum_filter - args.low_threshold
                if image_number <= 0:
                    print(f"h5 image number: {image_number} is probabily a trigger image, real data starts from image number: 1")
                else:
                    print(f"image number: {image_number}; none_filterred intensity: {i_sum}; filtered intensity: {i_sum_filter}; intensity difference: {i_diff}")
                image_intensity_h5_unordered[image_number] = [i_sum, i_sum_filter, i_diff, i_sum_filter_remove_chip]
                i_filtered_chip_h5_unordered[image_number] = (i_sum_filter_remove_chip)
    return image_intensity_h5_unordered, i_filtered_chip_h5_unordered



def read_and_sum_intensities(args:argparse.ArgumentParser):
    image_intensity_unordered = {} #dictionary stors image number and intensity
    i_filtered_chip_unordered = {} #filtered and chip-removed intensity list for moving average
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
                if image_number > 0:
                    image_intensity_unordered[image_number] = [i_sum, i_sum_filter, i_diff, i_sum_filter_remove_chip]
                    i_filtered_chip_unordered[image_number] = (i_sum_filter_remove_chip)
            i_filtered_chip = dict(sorted(i_filtered_chip_unordered.items()))
            image_intensity = dict(sorted(image_intensity_unordered.items()))
            #print(sorted(i_filtered_chip_unordered.items()))
            #print(i_filtered_chip)
            i_moving_average = moving_average(args, i_filtered_chip)
            for i, j in zip(image_intensity.keys(), range(len(i_moving_average))):
                image_intensity[i].append(i_moving_average[j])

    
    #h5 files, currently only works for PAL-XFEL Rayonix data
    elif args.data_format == "h5":
        with multiprocessing.Pool(args.cpu_use) as pool:
            results = pool.imap_unordered(read_h5, data)
            #print(results)
            pool.close()
            pool.join()
            #add to dict
            for image_intensity_h5_unordered, i_filtered_chip_h5_unordered in results:
                    image_intensity_unordered.update(image_intensity_h5_unordered)
                    i_filtered_chip_unordered.update(i_filtered_chip_h5_unordered)
            i_filtered_chip = dict(sorted(i_filtered_chip_unordered.items()))
            image_intensity = dict(sorted(image_intensity_unordered.items()))
            #print(sorted(i_filtered_chip_unordered.items()))
            #print(i_filtered_chip)
            i_moving_average = moving_average(args, i_filtered_chip)
            for i, j in zip(image_intensity.keys(), range(len(i_moving_average))):
                image_intensity[i].append(i_moving_average[j])


    #csv plot
    elif args.data_format == "csv":
        image_intensity = {}
        if Path(args.input_file[0]).suffix == ".csv":
            if len(args.input_file) == 1:
                pass
            else:
                print(f"Please give ONE .csv file, current has {len(args.input_file)} files")
                exit()
        else:
            print(f"Please give csv file, current is {args.input_file[0]}")
            exit()
    
    print(print(image_intensity))
    return image_intensity


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
        image_moving_average = data["moving_average"].tolist()

    else:
        #print(image_intensity)
        image_intensity_list = list(map(list, image_intensity.items()))
        image_intensity_list = sorted(image_intensity_list)
        #for i in image_intensity_list:
            #print(i)
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
    plt.figure(f"sum of intensities per image: {args.input_file[0]}", figsize = (18, 10))
    plt.subplot(311)
    plt.plot(image_number, sum_intensity_filtered_chip_remove, marker="o")
    plt.ylabel("All intensities",fontsize=font,fontweight="bold")
    plt.xlabel("image number",fontsize=font)
    plt.title(f"All intensities",fontsize=16)
      
    #plot intensity with moving average (intensity/max_intensity)
    plt.subplot(312)
    plt.plot(image_number, sum_intensity_filtered_chip_remove, marker="o", label="All intensity")
    plt.plot(image_number, image_moving_average, marker="o", label="Moving average")
    plt.ylabel("All intensities and moving average",fontsize=font,fontweight="bold")
    plt.xlabel("image number",fontsize=font)
    plt.legend()
    plt.title(f"All intensities with moving average",fontsize=16)

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




