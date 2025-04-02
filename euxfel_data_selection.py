import os
from pathlib import Path
from processing_stills import colors
import argparse
import glob
from pandas import *
import subprocess
import csv


"""
Select the dials processed data based on a csv file with image numbers that generated from euxfel_generate_pulse_id_list

The csv file can be generated using another script: euxfel_generate_id_list.py

make sure the name of the csv is correct, with the format of run_number_selected.csv (e.g. r0062_split_3_selected.csv)

Make sure give folders, not files

how to use:
dials.python euxfel_pulse_id_selection.py -i /processing/FOLDER_1 /processing/FOLDER_2 -c cxi/or/csv/folder -o out/put/dir


"""

# input file path and parameters
def process_args():
    input_args = argparse.ArgumentParser()

    #input folder(s) as list
    input_args.add_argument("-i","--input_processing_folder",
        nargs="+",
        help="give the input folder that contains the processed files as list, make sure you have output.composite_output=False for data processing"
        )
    
    #cxi/csv file(s) for extrace image number and pulse ID
    input_args.add_argument("-csv","--csv_folder",
        type=str,
        help="give the selected csv file folder for extract pulse ID and image number"
        )
    

    #output directory
    input_args.add_argument("-o", "--output_dir",
        type = str,
        help = "output directory, default is pwd. The script will create subfolders in the output directory",
        )

    #do not create symlinks, default is no
    input_args.add_argument("-sym", "--symlink",
        action='store_true', 
        help = "Whether to create symlinks, always have this arguments unless you want to test the code",
        )
    
    #verbose
    input_args.add_argument("-v", "--verbose",
        action='store_true', 
        help = "choose whether to pring all image number selected in the terminal, default is false",
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

#get the image number for integrated files
def get_image_number(data:str):
    if os.path.isfile(data):
        file_name = Path(data).stem
        image_number = int(file_name.split("_")[-2])
    else:
        print(f"Integrated file {data} does not exist")

    return image_number


#read and create a list from csv with image number
#it will also return a sanity check dict with {image_num: [pulse_ID, train_ID]} to make sure we select the correct image
def read_csv_image_num(input_csv_file:str):
    image_num_list = []
    sanity_check = {}
    with open(input_csv_file, "r") as f:
        reader = csv.reader(f)
        for line in reader:
            image_num_list.append(int(line[0]))
            sanity_check[int(line[0])] = [int(line[1]), int(line[2])]
    
    return image_num_list, sanity_check

#function to create symlink based on the pulse ID
def create_symlink(args):
    #Check the output folder
    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)
    else:
        pass

    #Create symlink folder in the output folder and create symlink, only selected image link will be created
    for data_path in args.input_processing_folder:
        if glob.glob(data_path): #check whether input folder exist
            for data_dir in glob.glob(data_path):
                #check the csv file
                input_dir_abs = os.path.abspath(data_dir) #get absolute path for symlink
                data_name = input_dir_abs.strip("\n").split("/")
                    
                if not data_name[-1]:
                    print(colors.RED + colors.BOLD + 'make sure there is no "/" at the end of the file path: ' + data_dir + colors.ENDC)
                    break
                else:
                    symlink_sample_name = data_name[-1]
                    symlink_folder = f"{args.output_dir}/{symlink_sample_name}"

                    #check whether output folder exists
                    if not os.path.isdir(symlink_folder):
                        print(f"{colors.BLUE}creating out put folders {symlink_folder} for select image{colors.ENDC}")
                        os.makedirs(symlink_folder)
                    else: 
                        print(f"Folder {colors.BLUE}{symlink_folder}{colors.ENDC} exists, prepare create symbolic links")
                        
                    #Check whether the folder is empty
                    empty_or_not= check_empty_folder(symlink_folder) 
                    if empty_or_not== False:
                        print(colors.BLUE + colors.BOLD + "symlink for " + symlink_folder + " has been made, please check" + colors.ENDC)       
                    else:
                        #check the csv file
                        selected_csv = f"{args.csv_folder}/{symlink_sample_name}_selected.csv"
                        if os.path.isfile(selected_csv):
                            select_image_list, sanity_check_dict = read_csv_image_num(selected_csv)   #get the selected image number as a list
                            select_image_set = list(select_image_list) #convert the list to set for faster searching speed

                            #check input file exist
                            input_file = f"{input_dir_abs}/*_integrated.*" 
                            if glob.glob(input_file):
                                for integrate_file in glob.glob(input_file):
                                    #Get image number
                                    image_number = get_image_number(integrate_file)

                                    #check whether image in the selectd set and create symlink if yes
                                    if image_number in select_image_set:
                                        if args.verbose == True:
                                            print(f"image number: {colors.GREEN}{image_number}{colors.ENDC} with the " 
                                            f"pulse ID {colors.GREEN}{sanity_check_dict[image_number][0]}{colors.ENDC} and " 
                                            f"train ID {colors.GREEN}{sanity_check_dict[image_number][-1]}{colors.ENDC} is the hit")
                                            print(f"Data name is {symlink_sample_name} and the selection csv is {selected_csv}")
                                        else:
                                            pass

                                        #create symlink
                                        if args.symlink == True:
                                            if args.verbose == True:
                                                print(f"create symlink for {symlink_sample_name} image {image_number} in folder {symlink_folder}")
                                            symlink_command_hit = "ln -s " + integrate_file + " " + symlink_folder
                                            subprocess.call(symlink_command_hit, shell=True)    
                                        else:
                                            print(f"Not creating symlink, please add {colors.BLUE}-sym for creating links{colors.ENDC}")  
                                    else:
                                        pass   
                            else:
                                print(f"{colors.RED}No integration file in folder: {input_dir_abs}, please check{colors.ENDC}")
                        else:
                            print(f"{colors.RED} csv file {selected_csv} does not exist, please check{colors.ENDC}")
        else:
            print(colors.BLUE + colors.BOLD + "Some data folder in : " + colors.BLUE + colors.BOLD + data_path + colors.BLUE + colors.BOLD + " doesn't exist, please check" + colors.ENDC)


#run the script
def main():
    args = process_args()
    print(f"prepare symlinks for {args.input_processing_folder} with the csv files in {args.csv_folder}")
    create_symlink(args)

if __name__ ==  "__main__" :
    main()




