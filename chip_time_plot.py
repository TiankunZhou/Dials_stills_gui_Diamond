import dxtbx
from dxtbx.format.FormatCBF import FormatCBF
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
import statistics


"""
Plot the collection time of each image for drop-on-chip system.
assessing the time point

how to use:
dials.python /home/tbf48622/programming/scripts/stills_process_gui/chip_time_plot.py -i ../../../ctxm15/aston/aston00002_00[0-4]* -df cbf --zero -rn 2
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
        help = "out put file prefixed name, no extensions needed, default is same as the input file stem + time_plot"
        )
    
    #Row number
    input_args.add_argument("-rn", "--row_number",
        type=int,
        help="specify the raw number for shutter time, can use 2, 4 and 10; default is 2",
        default=2
        )

    #specify whether image starts from 0
    input_args.add_argument("--zero",
        action='store_true',  
        help="specify whether image starts from 0, default is false"
        )

    #specify whether image starts from 0
    input_args.add_argument("--jos",
        action='store_true',  
        help="specify the drop adding time, devide the shutter time by (row_number * 20), minus 1 if false, default is false",
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
            args.output_prefix = file_name.split("_")[0] + "_time_plot"
            print(f"No output prefix set using the input file name: {args.output_prefix}")
    else:
        print(f"Not saving output, add -s if you want to save the csv")

    return args


"""
Read the image headers 
"""
def read_image_header(data:str, args=process_args()):
    if glob.glob(data):
        for path in glob.glob(data):
            #get image number ONLY works for DLS-i24 cbf for now
            file_name = Path(path).stem
            image_number = int(file_name.split("_")[-1])

            #get image header
            image_header = FormatCBF.get_cbf_header(path) #get image header as a str
            header_cleanup1 = image_header.replace("\r\n\r\n", "\r\n") #change the \r\n\r\n to \r\n
            header_cleanup2 = header_cleanup1.replace("#", "") #remove # in the str
            header_list = header_cleanup2.split("\r\n") # creast a list of header lines, in which the image time should be at position 6 - [6]

            #get image collection data and time
            date_and_time_list = header_list[6].split("T") #get the date and time, in dateTtime format: 2024-05-03T11:14:47.132, also convert to a list [date, time]
            date_raw = date_and_time_list[0]
            date_list_raw = date_raw.split("-") # create a list of data collection data [Year, month, day]
            image_time_raw = date_and_time_list[-1] 
            time_list_raw = image_time_raw.split(":") # create a list of data collection time [hour, min, sec.millisec]

            #get the image collection time as millisecond
            time_millisec = int(time_list_raw[0]) * 3600000 + int(time_list_raw[1]) * 60000 + int(float(time_list_raw[-1]) * 1000)

            #get the date (day) of data collection
            date_day = int(date_list_raw[-1])
            
            

            #check whether starts from image 0
            if args.zero == True:
                print(f"image number: {image_number}; date_day: {date_day}; time_in_ms: {time_millisec}")
            elif args.zero == False:
                if image_number <= 0:
                    print(f"cbf image number: {image_number} is probabily a trigger image, real data starts from image number: 1")
                else:
                    print(f"image number: {image_number}; date_day: {date_day}; time_in_ms: {time_millisec}")
    
    #return the values
    return image_number, date_day, time_millisec


"""
Get the image time if the date is different, find out the sutter time and actual mixing time
also reset the time of the first image to zero
return a 2-D list [[image_number, day_pass_time, zeroed_time, actual_mixing_time],[day_pass_time, zeroed_time, actual_mixing_time]...]
"""
def actual_mixing_time(args, dataset:dict):
    actual_mixing = []
    shutter_time_list = []
    zero_list = []
    #print(dataset)
    image_time_list = list(map(list, dataset.items())) # convert the dict to 2-D list, in this case it is the ordered image time dict
    image_time_list_ordered = sorted(image_time_list) #re-order the list, just in case: [[image_number, [date_day, image_time_ms]], [] ...]
    image_date = [i[-1][0] for i in image_time_list_ordered] #get a list of date,, ordered the image number
    image_time_ms = [i[-1][-1] for i in image_time_list_ordered] #get the image time ms, ordered by the image number

    first_image_time = image_time_ms[0]

    for i in image_time_ms:
        zero_list.append(i - first_image_time)


    #get the list of actual collection time:
    #get the basic trun_point, remember to add 1 for the list position, as it starts with 0
    turn_point = args.row_number * 20
    
    #get average shutter time, remember, the list starts with 0
    for i in range(len(image_time_ms)):
        if i == 0:
            pass
        elif i + 1 == len(image_time_ms):
            pass
        else:
            if (i + 1) % turn_point == 0:
                shutter_time = image_time_ms[i+1] - image_time_ms[i]
                shutter_time_list.append(shutter_time)
    
    #get the average drop loading time per well
    avg_shutter_total = int(sum(shutter_time_list)/len(shutter_time_list))
    if args.jos == False:
        avg_shutter_wells = int(avg_shutter_total/((args.row_number * 20) - 1))
    else:
        avg_shutter_wells = int(avg_shutter_total/(args.row_number * 20))


    #calculate the day_pass time, zeroed time and actual time of mixing, stroed in a 2-D list
    for i in range(len(image_time_list_ordered)):
        temp_list = []
        temp_list.append(i)
        #day pass time:
        if i == 0:
            temp_list.append(image_time_ms[i])
        else:
            if image_date[i-1] == image_date[i]:
                temp_list.append(image_time_ms[i])
            else:
                temp_list.append(image_time_ms[i] + 86400000)
        
        #add zeroed time
        temp_list.append(zero_list[i])

        #actual_mixing_time
        #calculate actual mixing time
        """
        total_collection_time = list[a * turn_point + b -1] - list[a * turn_point] (middle of the roll)
        total_collection_time =  list[(a * turn_point) - 1] - list[(a - 1) * turn_point] (last well of the roll)
        actual_mixing_time = total_collection_time - avg_shutter_wells * (b - 1) (middle of the roll)
        actual_mixing_time = total_collection_time - avg_shutter_wells * (39) (if b = 0)
        
        """
        a, b = divmod(i + 1, turn_point)
        #print(f"first index is: {(a * turn_point) + b - 1} and second index is: {(a * turn_point)} and the collection time shift is: {avg_shutter_wells * (b - 1)}")
        #print(f"time1 is: {image_time_ms[(a * turn_point) + b - 1]} and time2 is: {image_time_ms[a * turn_point]}")
        if a == 0:
            if b == 1:
                collection_time = avg_shutter_total
            else:
                total_collection_time = image_time_ms[(a * turn_point) + b - 1] - image_time_ms[a * turn_point]
                collection_time = avg_shutter_total + total_collection_time - (avg_shutter_wells * (b - 1))   
        else:
            if b == 1:
                collection_time = avg_shutter_total
            elif b == 0:
                total_collection_time =  image_time_ms[(a * turn_point) - 1] - image_time_ms[(a - 1) * turn_point]
                collection_time = avg_shutter_total + total_collection_time - (avg_shutter_wells * (turn_point - 1)) 
            else:
                total_collection_time = image_time_ms[(a * turn_point) + b - 1] - image_time_ms[a * turn_point]
                collection_time = avg_shutter_total + total_collection_time - (avg_shutter_wells * (b - 1))
        
        temp_list.append(collection_time)

        print(f"actual mixing for image {i}: {temp_list}")
        actual_mixing.append(temp_list)

    print(f'list of all shutter times: {shutter_time_list}')
    print(f'Average shutter time for all is: {avg_shutter_total}')
    print(f'Average shutter per well time is: {avg_shutter_wells}')
    print(f'Stander deviation of the total shutter time is: {statistics.stdev(shutter_time_list)}')
    #return the value
    return actual_mixing



"""
Create a dictionary with  the structure of:
{image_number:[date_day, image_time_ms, image_number, day_pass_time, zeroed_time, actual_mixing_time]}

"""
def get_image_time(args:argparse.ArgumentParser):
    image_time_unordered = {} #dictionary stors image number and times
    data = args.input_file
    #cbf files ONLY works af DLS-i24
    if args.data_format == "cbf":
        with multiprocessing.Pool(args.cpu_use) as pool:
            results = pool.imap_unordered(read_image_header, data)
            pool.close()
            pool.join()
            #add to dict
            for image_number, date_day, image_time_ms in results:
                if args.zero == True:
                    image_time_unordered[image_number] = [date_day, image_time_ms]
                elif args.zero == False:
                    if image_number > 0:
                        image_time_unordered[image_number] = [date_day, image_time_ms]

            image_time_ordered = dict(sorted(image_time_unordered.items()))
                                   
            #add the actual_mixing time
            actual_mixing = actual_mixing_time(args, image_time_ordered)
            for i, j in zip(image_time_ordered.keys(), range(len(actual_mixing))):
                for h in range(len(actual_mixing[j])):
                    image_time_ordered[i].append(actual_mixing[j][h])
        #print(image_time_ordered)
   
    #h5 files
    elif args.data_format == "h5":
        print(f"h5 files ploting under construction")
        exit()

    #csv plot
    elif args.data_format == "csv":
        image_time_ordered = {}
        if Path(args.input_file[0]).suffix == ".csv":
            if len(args.input_file) == 1:
                pass
            else:
                print(f"Please give ONE .csv file, current has {len(args.input_file)} files")
                exit()
        else:
            print(f"Please give csv file, current is {args.input_file[0]}")
            exit()
    
    #return the ordered image time as a dictionary {image_number: [day, time_in_ms]}
    return image_time_ordered


"""
Save the time as .csv:
with column: Image_Number, Date_day, Image_time_ms, Day_pass_time, Zeroed_time, Actual_mixing_time
dictionary structural: {image_number:[date_day, image_time_ms, image_number, day_pass_time, zeroed_time, actual_mixing_time]}
converted list structural: [image_number, [date_day, image_time_ms, image_number, day_pass_time, zeroed_time, actual_mixing_time]]
"""


def save_output(args, image_time_ordered:dict):
    #get values
    output_file = os.path.join(args.output_dir, args.output_prefix + ".csv")
    image_time_list = list(map(list, image_time_ordered.items()))
    image_time_ordered_list = sorted(image_time_list)
    image_number = [i[0] for i in image_time_ordered_list]
    date_day = [i[1][0] for i in image_time_ordered_list]
    image_time_ms = [i[1][1] for i in image_time_ordered_list]
    day_pass_time = [i[1][3] for i in image_time_ordered_list]
    zeroed_time = [i[1][4] for i in image_time_ordered_list]
    actual_mixing_time = [i[1][5] for i in image_time_ordered_list]

    #save csv
    with open(output_file,"w", newline='') as output_csv:
        write_csv = csv.writer(output_csv, dialect="excel-tab")
        write_csv.writerow(["Image_Number", "Date_day", "Image_time_ms", "Day_pass_time", "Zeroed_time", "Actual_mixing_time"])
        for i in range(len(image_number)):
            write_csv.writerow([image_number[i], date_day[i], image_time_ms[i], day_pass_time[i], zeroed_time[i], actual_mixing_time[i]])
    output_csv.close()

    print(f"Spectra written to {output_file}")



"""
plot the image collection time
"""
def plot_image_time(args, image_time:dict):
    if args.data_format == "csv":
        data = read_csv(args.input_file[0], sep = "\t")
        image_number = data["Image_Number"].tolist()
        image_time_ms = data["Image_time_ms"].tolist()
        day_pass_time = data["Day_pass_time"].tolist()
        zeroed_time = data["Zeroed_time"].tolist()
        actual_mixing_time = data["Actual_mixing_time"].tolist()

    else:
        image_time_list = list(map(list, image_time.items()))
        image_time_ordered_list = sorted(image_time_list)
        #for i in image_time_ordered_list:
            #print(i)
        image_number = [i[0] for i in image_time_ordered_list]
        #date_day = [i[1][0] for i in image_time_ordered_list]
        #image_time_ms = [i[1][1] for i in image_time_ordered_list]
        day_pass_time = [i[1][3] for i in image_time_ordered_list]
        zeroed_time = [i[1][4] for i in image_time_ordered_list]
        actual_mixing_time = [i[1][5] for i in image_time_ordered_list]

    font = 12
    #plot all intensities
    plt.figure(f"Image collection and mixing time: {args.input_file[0]}", figsize = (18, 10))
    plt.subplot(311)
    plt.plot(image_number, day_pass_time, marker="o")
    plt.ylabel("Image time (ms)",fontsize=font,fontweight="bold")
    plt.xlabel("Image number",fontsize=font)
    plt.title(f"Overall collection time per image as ms",fontsize=16)
      
    #plot intensity with moving average (intensity/max_intensity)
    plt.subplot(312)
    plt.plot(image_number, zeroed_time, marker="o")
    #plt.plot(image_number, image_moving_average, marker="o", label="Moving average")
    plt.ylabel("Zeroed image time (ms)",fontsize=font,fontweight="bold")
    plt.xlabel("Image number",fontsize=font)
    #plt.legend()
    plt.title(f"Zeroed collection time per image as ms",fontsize=16)

    plt.subplot(313)
    plt.plot(image_number, actual_mixing_time, marker="o")
    #plt.plot(image_number, filtered_intensity, marker="o",label="filtered intensity")
    #plt.plot(image_number, diff_intensity, marker="o",label="intensity difference")
    plt.ylabel("Actual mixing time (ms)",fontsize=font,fontweight="bold")
    plt.xlabel("Image number",fontsize=font)
    #plt.legend()
    plt.title(f"Actual mixing time per image",fontsize=16)

    plt.subplots_adjust(left=0.075, bottom=0.05, right=0.95, top=0.95, hspace=0.5)
    plt.show()

    
"""
run the script
"""
def main():
    args = process_args()
    print(f"plot the sum of background intensities per image for Diamond cbf and other h5 files")

    #get the image:intensity dictionary
    starttime = time.time()
    image_time = get_image_time(args)

    #print(image_time)

    print('That took {} seconds'.format(time.time() - starttime))

    #save the file
    if args.save_output == True:
        save_output(args, image_time)

    #plot data
    plot_image_time(args, image_time)

if __name__ ==  "__main__" :
    main()




