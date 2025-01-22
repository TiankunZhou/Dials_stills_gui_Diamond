import os
from pathlib import Path
from processing_stills import colors
from matplotlib import pyplot as plt
import argparse
import glob
from pandas import *
import subprocess


"""
Create TEN symbolic link for checkerboard and dose serials data scaling and merging
If you want to use this script, make sure have "output.composite_output=False"
for data processing.

how to use:
dials.python checkerboard_create_symlink.py -i /processing/FOLDER_1 /processing/FOLDER_2

or

dials.python checkerboard_create_symlink.py -i /processing/FOLDER_* -o out/put/FOLDER

"""

# input file path and parameters
def process_args():
    input_args = argparse.ArgumentParser()

    #input folder(s) as list
    input_args.add_argument("-i","--input_folder",
        nargs="+",
        help="give the input folder that contains the processed files as list, make sure you have output.composite_output=False for data processing"
        )
        
    #output directory
    input_args.add_argument("-o", "--output_dir",
        type = str,
        help = "output directory, default is pwd. The script will create subfolders in the output directory",
        )
    
    #save args
    args = input_args.parse_args()
    return args

#funstion to check whether the folder is empty:
def check_empty_folder(dir:str):
    folder = os.listdir(dir)
    if len(folder) == 0:
        return True
    else:
        return False

#create output folders and symbolic link
def create_symlink(args):
    #Check the output folder
    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)
    else:
        pass
    #Create symlink folder in the output folder and create symlink
    for data_path in args.input_folder:
        if glob.glob(data_path): #check whether all input path exist
            for data_dir in glob.glob(data_path):
                data_name = data_dir.strip("\n").split("/")
                if os.path.isdir(data_dir):     #check whether data folder exist
                    if not data_name[-1]:
                        print(colors.RED + colors.BOLD + 'make sure there is no "/" at the end of the file path: ' + data_dir + colors.ENDC)
                        break
                    else:
                        # make symlink folder in the output dir
                        #for odd_even
                        symlink_dir_main = data_name[-1]
                        for i in range(10):
                            i = str(i)
                            folder_name = f"{symlink_dir_main}_{i}"
                            folder_path = f"{args.output_dir}/{folder_name}"
                            if not os.path.isdir(folder_path):
                                print(f"Creating symlink folder: {folder_path}")
                                os.makedirs(folder_path)
                                print(f"Making symlink for {folder_name}")
                                input_dir_abs = os.path.abspath(data_dir)
                                symlink_command = "ln -s " + input_dir_abs + "/*" + i + "_integrated.* " + folder_path
                                print(colors.BLUE + colors.BOLD + "Running: ", symlink_command + colors.ENDC)
                                #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                                subprocess.call(symlink_command, shell=True)              
                            elif os.path.isdir(folder_path):
                                empty_or_not = check_empty_folder(folder_path)
                                if empty_or_not == False:
                                    print(colors.BLUE + colors.BOLD + "symlink for " + folder_name + " has been made, please check the folder: " + folder_path + colors.ENDC)
                                elif empty_or_not == True:
                                    print(f"empty folder {folder_path} exist, prepare create symbolic links")
                                    print(f"Making symlink for {folder_name}")
                                    input_dir_abs = os.path.abspath(data_dir)
                                    symlink_command = "ln -s " + input_dir_abs + "/*" + i + "_integrated.* " + folder_path
                                    print(colors.BLUE + colors.BOLD + "Running: ", symlink_command + colors.ENDC)
                                    #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                                    subprocess.call(symlink_command, shell=True)   


                else:
                    print(colors.BLUE + colors.BOLD + "Data processing folder: " + colors.BLUE + colors.BOLD + folder + colors.BLUE + colors.BOLD + " doesn't exist, please check" + colors.ENDC)
        else:
            print(colors.BLUE + colors.BOLD + "Some data folder in : " + colors.BLUE + colors.BOLD + data_path + colors.BLUE + colors.BOLD + " doesn't exist, please check" + colors.ENDC)


#run the script
def main():
    args = process_args()
    print(f"prepare symlinks for checkerboard and/or dose serials, split processed data to ten subsets based on the image name")

    #Check the data folder
    create_symlink(args)

if __name__ ==  "__main__" :
    main()




