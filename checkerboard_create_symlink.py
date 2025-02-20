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

for specitic number as hits:

dials.python checkerboard_create_symlink.py -i /processing/FOLDER_* -o out/put/FOLDER -sn -fn 2 -bs 4

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
    
    #option that will only create sym links for specific image numbers, e.g. every fourth image
    input_args.add_argument("-sn", "--specific_number",
        action='store_true', 
        help = "give the number of images that need to be skipped after the desired image",
        )

    #give the first image number
    input_args.add_argument("-fn", "--first_image",
        type=int,
        help = "give the first image number to calculate the number of images that need to be sym-linked",
        default = 2,
        )

    #give the number of blank/contaminated image
    input_args.add_argument("-bs", "--batch_size",
        type=int,
        help = "give the image batch size for calculate the number of images that has the chemistry",
        default = 4,
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


#get the image number for none 1, 2 or 5 symlink
def get_image_number(data:str):
    if os.path.isfile(data):
        #get image number ONLY works for DLS-i24
        file_name = Path(data).stem
        image_number = int(file_name.split("_")[-2])
    else:
        print(f"Integrated file for image {image_number} does not exist")

    return image_number


#create output folders and symbolic link
def create_symlink_all(args):
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


#function to create symlink for specific image number (e.g. 1, 5, 9, 13, 17, 21...)
def create_symlink_specific(args):
    #Check the output folder
    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)
    else:
        pass
    #Create symlink folder in the output folder and create symlink, two folders will be created, hits and non_hits
    for data_path in args.input_folder:
        if glob.glob(data_path): #check whether all input path exist
            for data_dir in glob.glob(data_path):
                input_dir_abs = os.path.abspath(data_dir)
                data_name = data_dir.strip("\n").split("/")
                if os.path.isdir(data_dir):     #check whether data folder exist
                    if not data_name[-1]:
                        print(colors.RED + colors.BOLD + 'make sure there is no "/" at the end of the file path: ' + data_dir + colors.ENDC)
                        break
                    else:
                        #define the symlink folder name and path
                        symlink_dir_main = data_name[-1]
                        hits_dir = symlink_dir_main + "_hits"
                        non_hits_dir = symlink_dir_main + "_non_hits"
                        folder_path_hits_dir = f"{args.output_dir}/{hits_dir}"
                        folder_path_non_hit_dir = f"{args.output_dir}/{non_hits_dir}"
                        
                        #prepare the folder for hits
                        if not os.path.isdir(folder_path_hits_dir):
                                print(f"Creating symlink folder for hits: {folder_path_hits_dir}")
                                os.makedirs(folder_path_hits_dir)
                        else:
                            pass
                        
                        if not os.path.isdir(folder_path_non_hit_dir):
                                print(f"Creating symlink folder: {folder_path_non_hit_dir}")
                                os.makedirs(folder_path_non_hit_dir)
                        else:
                            pass

                        #Check whether the folder is empty
                        empty_or_not_hit = check_empty_folder(folder_path_hits_dir)
                        empty_or_not_nohit = check_empty_folder(folder_path_non_hit_dir)
                        if empty_or_not_hit == False or empty_or_not_nohit == False:
                            print(colors.BLUE + colors.BOLD + "symlink for " + folder_path_hits_dir + " and " + folder_path_non_hit_dir + " has been made, please check" + colors.ENDC)       
                        else:
                            print(f"empty folder {folder_path_hits_dir} and {folder_path_non_hit_dir} exist, prepare create symbolic links")          
                            #get the image number 
                            input_file = f"{input_dir_abs}/*_integrated.*" 
                            #check input file exist
                            if glob.glob(input_file):
                                for integrate_file in glob.glob(input_file):
                                    #Get image number,this will use the *_integrated.expt file.
                                    image_number = get_image_number(integrate_file)
                                    hits_check = (image_number - args.first_image) % args.batch_size
                                    if hits_check == 0:
                                        print(f"image number {image_number} for data {symlink_dir_main} is the hit, symlink to the hits folder")
                                        symlink_command_hit = "ln -s " + integrate_file + " " + folder_path_hits_dir
                                        #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                                        subprocess.call(symlink_command_hit, shell=True) 
                                    else:
                                        symlink_command_nohit = "ln -s " + integrate_file + " " + folder_path_non_hit_dir
                                        #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                                        subprocess.call(symlink_command_nohit, shell=True) 
                            else:
                                print(f"No interation file in folder: {input_dir_abs}, please check")  
                else:
                    print(colors.BLUE + colors.BOLD + "Data processing folder: " + colors.BLUE + colors.BOLD + folder + colors.BLUE + colors.BOLD + " doesn't exist, please check" + colors.ENDC)
        else:
            print(colors.BLUE + colors.BOLD + "Some data folder in : " + colors.BLUE + colors.BOLD + data_path + colors.BLUE + colors.BOLD + " doesn't exist, please check" + colors.ENDC)


#run the script
def main():
    args = process_args()
    if args.specific_number == True:
        print(f"prepare symlinks for , with the first image number: {args.first_image} and the batch size: {args.batch_size}")
        create_symlink_specific(args)
    else:
        print(f"prepare symlinks for checkerboard and/or dose serials, split processed data to ten subsets based on the image name")
        #Check the data folder
        create_symlink_all(args)

if __name__ ==  "__main__" :
    main()




