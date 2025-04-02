import os
from pathlib import Path
from processing_stills import colors
import argparse
import glob
from pandas import *
import csv
import h5py

"""
This script will generate two csv files from .cxi file in different fold

for cxi format, each folder can only have ONE cxi file
For csv input, you can have multiple csv file in the same folder.

One csv file is the image_number, puls_ID and train_ID, this csv file can also be sued to generate
the second csv file

Another csv file is the image number that selected based on the pulse id, and will be used for the data 
selection with this script: euxfel_data_selection



"""

# input file path and parameters
def process_args():
    input_args = argparse.ArgumentParser()

    #input folder(s) as list
    input_args.add_argument("-i","--input_folder",
        nargs="+",
        help="give the input folder that contains the processed files as list takes the cxi and the csv file (csv file needs to have the pulse ID in the second column)"
        )
    
    #format of the files that use for create the ID list
    input_args.add_argument("-ff", "--file_format",
        type = str,
        choices = ["cxi", "csv"],
        help = "output directory, default is pwd. The script will create subfolders in the output directory",
        default = "cxi"
        )

    #whether save file as .csv default is no
    input_args.add_argument("-s", "--save_csv_file",
        action='store_true', 
        help = "choose whether you want the save the IDs as .csv, default is false",
        )

    #output directory
    input_args.add_argument("-o", "--output_dir",
        type = str,
        help = "output directory, default is pwd. The script will create subfolders in the output directory",
        )

    #pulse IDs required
    input_args.add_argument("-fpid", "--first_pulse_id",
        type = int,
        help = "give the first pulse ID needed, such as 8 (default)",
        default = 8
        )
    
    #give the number of skipped images, such as 3 for on, off, off, off
    input_args.add_argument("-off", "--off_image_number",
        type = int,
        help = "give number of off state images between on state, such as 3 (default) for on, off, off, off, on",
        default = 3
        )
    #save args
    args = input_args.parse_args()
    return args


#extract the pulse ID, train ID and the image number as dict; image_number:[pulse_ID, train_ID] and a list [image_number, pulse_ID, train_ID]
def extract_IDs(cxi_file:str):
    IDs = {}
    file = h5py.File(cxi_file, "r")
    Pulse_ID = file["entry_1/pulseId"]
    Train_ID = file["entry_1/trainId"]
    Pulse_ID_list = list(Pulse_ID)
    Train_ID_list = list(Train_ID)
    IDs_list = []

    #create dict 
    for i in range(len(Pulse_ID_list)):
        IDs[f"image_{i}"] = [int(Pulse_ID_list[i]), int(Train_ID_list[i])]

    #convert dict to list
    for i, j in zip(IDs.keys(), IDs.values()):
        image_num = i.split("_")[-1]
        print(f"image {colors.GREEN}{image_num}{colors.ENDC} has the pulse ID of {colors.GREEN}{j[0]}{colors.ENDC} and the train ID of {colors.GREEN}{j[1]}{colors.ENDC}")
        IDs_list.append([int(image_num), int(j[0]), int(j[1])])
    
    return IDs, IDs_list


#get the desired image number, based on the pulse ID
#output lists with image number as int
def select_image_number(IDs:list, first_puls_id:int, off_gap:int):
    image_num_desired = []

    for i in IDs:
        selected_number = int(i[1])/first_puls_id
        if selected_number == 1:
            print(f"image number {colors.GREEN}{i[0]}{colors.ENDC} is selected with the pulse id of {colors.GREEN}{i[1]}{colors.ENDC} and train id of {colors.GREEN}{i[2]}{colors.ENDC}")
            image_num_desired.append(i)
        elif (selected_number - 1)%(off_gap + 1) == 0:
            print(f"image number {colors.GREEN}{i[0]}{colors.ENDC} is selected with the pulse id of {colors.GREEN}{i[1]}{colors.ENDC} and train id of {colors.GREEN}{i[2]}{colors.ENDC}")
            image_num_desired.append(i)
        else:
            pass
    
    return image_num_desired


#save the image number and the IDs as csv, can also use for saving the selected image numbers
def save_IDs(IDs_list:list, file_path:str, file_name:str):
    #save csv   
    output_file = f"{file_path}/{file_name}"
    with open(output_file , "w") as IDs_csv:
        write_IDs = csv.writer(IDs_csv)
        for i in range(len(IDs_list)):
            write_IDs.writerow(IDs_list[i])


#read csv file and convert it as a list [[column1_1, column2_1, ...], [column1_2, column2_2,...]]
def read_csv_file(input_csv_file:str):
    all_IDs_list = []
    with open(input_csv_file, "r") as f:
        reader = csv.reader(f)
        for line in reader:
            all_IDs_list.append([int(x) for x in line])
    
    return all_IDs_list


# get file name from cxi/csv file to name the csv file
def get_file_name(file_path:str, prefix:str):
    #get file name by remove the prefix at the end
    file_name = Path(file_path).stem.replace(prefix, "")
      
    return file_name


def generate_csv(args):
    #create folder for the csv
    output_dir = args.output_dir
    all_ids_dir = f"{output_dir}/all_IDs"
    selected_image_num_dir = f"{output_dir}/selected_image_num"

    if not os.path.isdir(all_ids_dir):
        print(f"creating out put folders for all IDs")
        os.makedirs(all_ids_dir)
    else:
        print(f"all IDs folder exists, go to next step")
        pass

    if not os.path.isdir(selected_image_num_dir):
        print(f"creating out put folders for select image")
        os.makedirs(selected_image_num_dir)
    else:
        print(f"select image folder exists, go to next step")
        pass
    
    #create lists
    for line in args.input_folder:
        if glob.glob(line):
            if not os.path.isdir(line):
                print(f"Please give a folder, current path {colors.RED}{line}{colors.ENDC} is not a folder")
                break
            else:
                pass
            for path in glob.glob(line):
                if args.file_format == "cxi":
                    input_file = glob.glob(f"{path}/*.cxi")
                    #check cxi file exist and generate the list
                    if len(input_file) == 0:
                        print(f"{colors.RED}input {args.file_format} file doest not exist in: {line}, plese check{colors.ENDC}")
                    elif len(input_file) == 1:
                        file_path = input_file[0]
                        print(f"prepare IDs for {file_path}")
                        _, all_ID_list = extract_IDs(file_path)
                        if args.save_csv_file == True:
                            all_IDs_name_prefix = get_file_name(file_path, "_vds")
                            all_IDs_file_name = f"{all_IDs_name_prefix}_all_IDs.csv"
                            if not os.path.isfile(f"{all_ids_dir}/{all_IDs_file_name}"):
                                #get all IDs
                                print(f"saving all IDs of {colors.BLUE}{file_path}{colors.ENDC} to csv")
                                save_IDs(all_ID_list, all_ids_dir, all_IDs_file_name)
                            else:
                                print(f"{colors.RED}csv file {all_ids_dir}/{all_IDs_file_name} exists, please check{colors.ENDC}")

                            #select IDs
                            print(f"select IDs based on first pulse ID {colors.BLUE}{args.first_pulse_id}{colors.ENDC} and off image number of {colors.BLUE}{args.off_image_number}{colors.ENDC}")
                            selected_IDs = select_image_number(all_ID_list, args.first_pulse_id, args.off_image_number)
                            selected_IDs_file_name = f"{all_IDs_name_prefix}_selected.csv"
                            if not os.path.isfile(f"{selected_image_num_dir}/{selected_IDs_file_name}"):
                                print(f"saving selected IDs of {colors.BLUE}{file_path}{colors.ENDC} to csv")
                                save_IDs(selected_IDs, selected_image_num_dir, selected_IDs_file_name)
                            else:
                                print(f"{colors.RED}csv file {selected_image_num_dir}/{selected_IDs_file_name} exists, please check{colors.ENDC}")
                        else:
                            print(f"{colors.BLUE}not saveing csv file, just checking the script{colors.ENDC}")
                    else:
                        print(f"{colors.RED}multiple cxi files detected in the same folder: {line}, please check{colors.ENDC}")

                elif args.file_format == "csv":
                    input_files = glob.glob(f"{line}/*.csv")
                    #check cxi file exist and generate the list
                    for file_path in input_files:
                        print(f"prepare IDs for {file_path}")
                        all_ID_list = read_csv_file(file_path)
                        if args.save_csv_file == True:
                            selected_IDs = select_image_number(all_ID_list, args.first_pulse_id, args.off_image_number)
                            all_IDs_name_prefix = get_file_name(file_path, "_all_IDs")
                            selected_IDs_file_name = f"{all_IDs_name_prefix}_selected.csv"
                            if not os.path.isfile(f"{selected_image_num_dir}/{selected_IDs_file_name}"):
                                #get all IDs
                                print(f"saving selected IDs of {colors.BLUE}{file_path}{colors.ENDC} to csv")
                                save_IDs(selected_IDs, selected_image_num_dir, selected_IDs_file_name)
                            else:
                                print(f"csv file {colors.RED}{selected_image_num_dir}/{selected_IDs_file_name}{colors.ENDC} exists, please check")
                        else:
                            print(f"{colors.BLUE}not saveing csv file, just checking the script{colors.ENDC}")
                else:
                    print(f"{colors.RED}Please give the correct file format, it needs to be either .cxi or .csv{colors.ENDC}")
        else:
            print(f"folder {colors.RED}{line}{colors.ENDC} does not exist, please check")




def main():
    args = process_args()
    print(f"Getting the pulse ID and related image number")
    generate_csv(args)



if __name__ ==  "__main__" :
    main()
