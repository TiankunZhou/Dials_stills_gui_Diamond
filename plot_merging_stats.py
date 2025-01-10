import glob
from matplotlib import pyplot as plt
from processing_stills import colors
import os
import sys
import re
from pathlib import Path
"""
Plot cctbx.xfel.merge statistics. Data acquired from main log file
Based on the current log file structure, changes may needed if the log file changed.

"""

class plot_mergingstat:
    def __init__(self, data_dir:list):
        self.data_dir = data_dir
        
    def is_float(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    #extract the intensity statistics stored in a dict
    def extract_intensity(self, merging_log:str):       
        log_intensity = open(merging_log).readlines()
        log_intensity_strip = [a.strip() for a in log_intensity] #remove the space at the beginning of the line for searching keywords
        log_intensity_tidy = [' '.join(re.sub(r"(\[)|(\])", " ", x.replace(" - ", " ")).split()) for x in log_intensity_strip] #convert multiple space and ' - ' to one space and remove the [ (sometimes cause error), using the strip result
        select_intensity_all = [] #pick up every line between key lines in this list
        select_intensity_table = [] #pick up the table starts with "Bin"
        #use this variable (select_line) to pick up specific content between key lines
        select_line = False
        for line in log_intensity_tidy: #select all intensity content (text and table)
            if line.startswith("Intensity Statistics (all accepted experiments)"):
                select_line = True
            elif line.startswith("CC 1/2"):
                select_line = False
            if select_line:
                select_intensity_all.append(line)
        select_line_2 = False
        for line in select_intensity_all: # select all intensity table
            if line.startswith("Bin"):
                select_line_2 = True
            elif line.startswith("CC 1/2"):
                select_line_2 = False
            if select_line_2:
                select_intensity_table.append(line)
        select_intensity_content = [x for x in select_intensity_table if x.split(" ")[0].isdigit()]  #pick the first item with bin numbers (if the str is an int) as a list, values are stored as str
        select_intensity_overall = [x for x in select_intensity_table if x.startswith("All")] #find overall line
        stats_intensity = {} #diactionaly storing bin number: resolution and statistics, order: low resolution, high resolution, compleleness, multiplicity
        overall_intensity_stats = {}
        for line in select_intensity_content:
            line_list = line.split(" ") #change the str to list
            if float(line_list[1]) <= 0:
                line_list[1] = str(float(line_list[2]) + 5)   #change the lowest res from -1 to d_min + 5
            indice = [1, 2, 4, 6, 10] # select lowres, highres, completeness, multiplicity and I/sigma
            stats_intensity[line_list[0]] = [line_list[x] for x in indice] #values list: 0.lowres, 1.highres, 2.completeness, 3.multiplicity, 4.I/sigma
        for line in select_intensity_overall:
            line_list = line.split(" ") #change the str to list
            indice = [2, 4, 8] # select completeness, multiplicity and I/sigma overall
            overall_intensity_stats[line_list[0]] = [line_list[x] for x in indice] #values list: 0.completeness, 1.multiplicity, 2.I/sigma
        return select_intensity_all, stats_intensity, overall_intensity_stats

    #extract the CC1/2 statistics
    def extract_scaling(self, merging_log:str):
        log_scaling = open(merging_log).readlines()
        log_scaling_strip = [a.strip() for a in log_scaling] #remove the space at the beginning of the line for searching keywords
        log_scaling_tidy = [' '.join(re.sub(r"(\[)|(\])", " ", x.replace(" - ", " ")).split()) for x in log_scaling_strip] #convert multiple space and ' - ' to one space and remove the [ (sometimes cause error), using the strip result
        select_scaling_all = [] #pick up every line between key lines in this list 
        select_scaling_table = [] #pick up the table starts with "Bin"
        #use this variable (select_line) to pick up specific content between key lines
        select_line = False
        for line in log_scaling_tidy:
            if line.startswith("Table of Scaling Results:"):
                select_line = True
            elif line.startswith("CCint is the CC-1/2"):
                select_line = False
            if select_line:
                select_scaling_all.append(line)
        select_line_2 = False
        for line in select_scaling_all:
            if line.startswith("Bin"):
                select_line_2 = True
            elif line.startswith("CCint is the CC-1/2"):
                select_line_2 = False
            if select_line_2:
                select_scaling_table.append(line)
        select_scaling_content = [x for x in select_scaling_table if x.split(" ")[0].isdigit()]  #pick the first item with bin numbers (if the str is an int) as a list, values are stored as str
        select_overall_scaling = [x for x in select_scaling_table if x.startswith("All")] #find overall line
        stats_intensity = {} #diactionaly storing bin number: resolution and statistics, order: low resolution, high resolution, compleleness, multiplicity
        overall_scaling_stats = {}
        for line in select_scaling_content:
            line_list = line.split(" ") #change the str to list
            if float(line_list[1]) <= 0:
                line_list[1] = str(float(line_list[2]) + 5)   #change the lowest res from -1 to d_min + 5
            indice = [1, 2, 4, 9] # select lowres, highres, CC1/2 and Rsplit
            for i in indice:
                if "%" in line_list[i]:
                    line_list[i] = float(line_list[i].replace("%", ""))/100
            stats_intensity[line_list[0]] = ["{:.3f}".format(float(line_list[x])) if self.is_float(line_list[x]) else "0.000" for x in indice ] #values list: 0.lowres, 1.highres, 2.CC1/2, 3.Rsplit
        for line in select_overall_scaling:
            line_list = line.split(" ") #change the str to list
            indice = [2, 7] # select CC1/2 and Rsplit overall
            for i in indice:
                if "%" in line_list[i]:
                    line_list[i] = float(line_list[i].replace("%", ""))/100
            overall_scaling_stats[line_list[0]] = ["{:.3f}".format(float(line_list[x])) if self.is_float(line_list[x]) else "0.000" for x in indice ] #values list: 0.CC1/2, 1.Rsplit
        return select_scaling_all, stats_intensity, overall_scaling_stats

    #extact the value for plotting
    def extract_stats(self, merging_log:str, stats1:str, stats2:str):
        if os.path.isfile(merging_log):
            table_intensity, value_intensity, value_intensity_overall = self.extract_intensity(merging_log)
            table_scaling, value_scaling, value_scaling_overall = self.extract_scaling(merging_log) 
            highres = []
            lowres = []
            stats_1 = []
            stats_2 = []
            stats_overall_1 = []
            stats_overall_2 = []
            for i in list(value_intensity.values()):
                highres.append(float(i[0]))
                lowres.append(float(i[1]))
            resolution = ["{:.3f}".format((x+y)/2) for x,y in zip(lowres, highres)] #define the resolution (x-axis)
            if stats1 == "CC1/2" or stats1 == "Rsplit":
                for i in list(value_scaling.values()):
                    if stats1 == "CC1/2":
                        stats_1.append(i[2])
                    elif stats1 == "Rsplit":
                        stats_1.append(i[3])
                for j in list(value_scaling_overall.values()):
                    if stats1 == "CC1/2":
                        stats_overall_1.append(j[0])
                    elif stats1 == "Rsplit":
                        stats_overall_1.append(j[1])
            elif stats1 == "I/sigma" or stats1 == "Multiplicity" or stats1 == "Completeness":
                for i in list(value_intensity.values()):
                    if stats1 == "I/sigma":
                        stats_1.append(i[4])
                    elif stats1 == "Multiplicity":
                        stats_1.append(i[3])
                    elif stats1 == "Completeness":
                        stats_1.append(i[2])
                for j in list(value_intensity_overall.values()):
                    if stats1 == "I/sigma":
                        stats_overall_1.append(j[2])
                    elif stats1 == "Multiplicity":
                        stats_overall_1.append(j[1])
                    elif stats1 == "Completeness":
                        stats_overall_1.append(j[0])
            if  stats2 == "CC1/2" or stats2 == "Rsplit":
                for i in list(value_scaling.values()):
                    if stats2 == "CC1/2":
                        stats_2.append(i[2])
                    elif stats2 == "Rsplit":
                        stats_2.append(i[3])
                for j in list(value_scaling_overall.values()):
                    if stats2 == "CC1/2":
                        stats_overall_2.append(j[0])
                    elif stats2 == "Rsplit":
                        stats_overall_2.append(j[1])
            elif stats2 == "I/sigma" or stats2 == "Multiplicity" or stats2 == "Completeness":
                for i in list(value_intensity.values()):
                    if stats2 == "I/sigma":
                        stats_2.append(i[4])
                    elif stats2 == "Multiplicity":
                        stats_2.append(i[3])
                    elif stats2 == "Completeness":
                        stats_2.append(i[2]) 
                for j in list(value_intensity_overall.values()):
                    if stats2 == "I/sigma":
                        stats_overall_2.append(j[2])
                    elif stats2 == "Multiplicity":
                        stats_overall_2.append(j[1])
                    elif stats2 == "Completeness":
                        stats_overall_2.append(j[0])
            return resolution, stats_1, stats_2, stats_overall_1, stats_overall_2   
        else:
            print("Main log files dose not exist, please check")
    
    #plot the stats
    def plot_stats(self, value1:str, value2:str):
        for line in self.data_dir:
            if glob.glob(os.path.join(line, "*main*")):
                for file_name in glob.glob(os.path.join(line, "*main*")):
                    table_intensity, value_intensity, _ = self.extract_intensity(file_name)
                    table_scaling, value_scaling, _ = self.extract_scaling(file_name) # _ is the blank identifier
                    resolution, stats_1, stats_2, stats_overall_1, stats_overall_2 = self.extract_stats(file_name, value1, value2)
                    print("Intensity statistic table for " + colors.BLUE + colors.BOLD + str(file_name) + ": " + colors.ENDC)
                    print("\n".join(table_intensity))
                    print("Scaling statistics table for " + colors.BLUE + colors.BOLD + str(file_name) + ": " + colors.ENDC)
                    print("\n".join(table_scaling))

                    #plot stats
                    resolution_float = [float(x) for x in resolution]
                    stats_float_1 = [float(x) for x in stats_1]
                    stats_float_2 = [float(x) for x in stats_2] #use these three to change the items in the list from str to float for plotting

                    fig, ax1 = plt.subplots(figsize=(22, 12)) #set up dual y-axis
                    ax1.plot(resolution_float, stats_float_1, marker = "o", linestyle = "--", color="blue")
                    ax1.set_ylim(ymin=0)
                    ax1.invert_xaxis() #invert x-axis, make the bottom right the lowest value
                    ax1.set_xlabel("Resolution", fontsize=14)
                    ax1.set_ylabel(str(value1), fontsize=14, color='blue')

                    ax2 = ax1.twinx() #set up dual y-axis
                    ax2.plot(resolution_float, stats_float_2 , marker = "o", linestyle = "--", color="red")
                    ax2.set_ylim(ymin=0)
                    ax2.set_ylabel(str(value2), fontsize=14, color='red')

                    text_str = "\n".join(
                        ("Overall " + str(value1) + ": " + str(stats_overall_1[0]),
                        "Overall " + str(value2) + ": " + str(stats_overall_2[0]),
                        "Highest res " + str(value1) + ": " + str(stats_float_1[-1]),
                        "Highest res " + str(value2) + ": " + str(stats_float_2[-1])))
                    plt.text(0.99, 0.99, text_str, fontsize=14, va="top", ha="right", transform=plt.gca().transAxes)
                    plt.title("Plot merging statistics for \n" + str(file_name), fontsize=14)
            else:
                print(colors.RED + colors.BOLD + "merging log file not exist: " + str(line) + " Pleace check" + colors.ENDC)
        plt.show()

    
    def compare_merging_stat(self, value1:str, value2:str):
        #create lists for the plot
        value_1_list = []
        value_2_list = []
        resolution_list = []
        data_name_list = []

        #fill the list
        for line in self.data_dir:
            if line == "":
                pass
            elif glob.glob(os.path.join(line, "*main*")):
                for file_name in glob.glob(os.path.join(line, "*main*")):
                    #create a list of data name
                    data_name_split = file_name.strip("\n").split("/")
                    data_name = f"{data_name_split[-3]} - {data_name_split[-2]}"
                    data_name_list.append(data_name)

                    #generate lists of values and resolution
                    table_intensity, value_intensity, _ = self.extract_intensity(file_name)
                    table_scaling, value_scaling, _ = self.extract_scaling(file_name) # _ is the blank identifier
                    resolution, stats_1, stats_2, stats_overall_1, stats_overall_2 = self.extract_stats(file_name, value1, value2)
                    print("Intensity statistic table for " + colors.BLUE + colors.BOLD + str(file_name) + ": " + colors.ENDC)
                    print("\n".join(table_intensity))
                    print("Scaling statistics table for " + colors.BLUE + colors.BOLD + str(file_name) + ": " + colors.ENDC)
                    print("\n".join(table_scaling))

                    resolution_float = [float(x) for x in resolution]
                    resolution_list.append(resolution_float)
                    stats_float_1 = [float(x) for x in stats_1]
                    value_1_list.append(stats_float_1 )
                    stats_float_2 = [float(x) for x in stats_2] #use these three to change the items in the list from str to float for plotting
                    value_2_list.append(stats_float_2)
            else:
                print(colors.RED + colors.BOLD + "merging log file not exist: " + str(line) + " Pleace check" + colors.ENDC)
                

        #check length of lists
        list_length = len(data_name_list)
        #print(list_length)
        if len(resolution_list) == list_length and len(value_1_list) == list_length and len(value_2_list) == list_length:
            pass
        else:
            print("lists length are not the same")

        #plot 
        image, (plot1, plot2) = plt.subplots(2, 1, figsize = (22, 12))
        #plt.figure(f"compare merging stats", figsize = (22, 12))
        plot1.set_title(f"Compare merging stats: {str(value1)}",fontsize=16)
        for i in range(list_length):
            plot1.plot(resolution_list[i], value_1_list[i], marker="o", label=f"{data_name_list[i]}")
        plot1.set_ylabel(str(value1),fontsize=14,fontweight="bold")
        plot1.set_xlabel("resolution",fontsize=14)
        plot1.invert_xaxis()
        plot1.legend()
        #plt.title(f"Compare merging stats: {str(value1)}",fontsize=16)
  
        #plot value 2
        #plt.subplot(212)
        plot2.set_title(f"Compare merging stats: {str(value2)}",fontsize=16)
        for i in range(list_length):
            plot2.plot(resolution_list[i], value_2_list[i], marker="o", label=f"{data_name_list[i]}")
        plot2.set_ylabel(str(value2),fontsize=14,fontweight="bold")
        plot2.set_xlabel("resolution",fontsize=14)
        plot2.invert_xaxis()
        plot2.legend()
        #plt.title(f"Compare merging stats: {str(value2)}",fontsize=16)
        plt.show()

   
       
























