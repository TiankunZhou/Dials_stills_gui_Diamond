from __future__ import absolute_import, division, print_function
from processing_stills import colors
import os
import shutil
import stat
import string
import subprocess
import sys
import numpy as np 
import glob


"""
Sacling and merging settings
"""

class scaling_job:
    def __init__(self, data_dir:list, processing_dir:str, queue_option:str, phil_file:str):
        self.data_dir = data_dir
        self.processing_dir = processing_dir
        self.queue_option = queue_option
        self.phil_file = phil_file
    
    def create_job(self, data_folder:str, process_name:str):
        processing_folder = self.processing_dir + "/" + process_name
        submit_script = processing_folder + "/" + str("run_scaling_" + process_name + ".sh")
        phil = processing_folder + "/" + "scaling.phil"
        print(colors.GREEN + colors.BOLD + "Submit scaling jobs for: " + process_name + colors.ENDC)
        if os.path.isdir(processing_folder) and os.path.isfile(submit_script):
            print(colors.BLUE + colors.BOLD + "scaling job of " + process_name + " has been submitted, please check the foled: " + processing_folder + colors.ENDC)
        else:
            if not os.path.isdir(processing_folder):
                os.makedirs(processing_folder)
            if os.path.exists(phil):
                os.remove(phil)
            with open(phil, "a+") as p:
                p.write("input.path=" + data_folder + "\n")
                p.write(self.phil_file)
            with open(submit_script, "a") as f:
                f.write("source /dls/science/users/tbf48622/dials_own/dials\n")
                f.write("mpirun -n ${NSLOTS} cctbx.xfel.merge "+ phil + " mp.method=mpi\n")
            print(phil)

            os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            command = [
                    "module load global/cluster && qsub -j y -wd " + processing_folder + " -pe smp 20 -l redhat_release=rhel7 -l m_mem_free=3G -q "
                    + self.queue_option
                    + ".q "
                    + submit_script
                ]
            print("Running:", " ".join(command))
            subprocess.call(command, shell=True)
    
    def submit_job(self):
        for line in self.data_dir:
            if glob.glob(line):
                for path in glob.glob(line):
                    data_name = path.strip("\n").split("/")
                    if not data_name[-1]:
                        print('make sure there is no "/" at the end of the file path')
                        break
                    else:
                        data_tag = data_name[-1]
                        data_folder = str(path)
                        self.create_job(data_folder, data_tag)
            else:
                print("Data processing folder not exist:" + line + " please check")

class merging_job:
    def __init__(self, data_dir:list, processing_dir:str, queue_option:str, phil_file:str):
        self.data_dir = data_dir
        self.processing_dir = processing_dir
        self.queue_option = queue_option
        self.phil_file = phil_file
    
    def create_job(self, data_folder:str, process_name:str):
        processing_folder = self.processing_dir + "/" + process_name
        submit_script = processing_folder + "/" + str("run_merging_" + process_name + ".sh")
        phil = processing_folder + "/" + "merging.phil"
        print(colors.GREEN + colors.BOLD + "Submit merging jobs for: " + process_name + colors.ENDC)
        if os.path.isdir(processing_folder) and os.path.isfile(submit_script):
            print(colors.BLUE + colors.BOLD + "Merging job of " + process_name + " has been submitted, please check the foled: " + processing_folder + colors.ENDC)
        else:
            if not os.path.isdir(processing_folder):
                os.makedirs(processing_folder)
            if os.path.exists(phil):
                os.remove(phil)
            with open(phil, "a") as p:
                p.write("input.path=" + data_folder + "\n")
                p.write(self.phil_file)
            with open(submit_script, "a") as f:
                f.write("source /dls/science/users/tbf48622/dials_own/dials\n")
                f.write("mpirun -n ${NSLOTS} cctbx.xfel.merge "+ phil + " mp.method=mpi\n")
            print(phil)

            os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            command = [
                    "module load global/cluster && qsub -j y -wd " + processing_folder + " -pe smp 20 -l redhat_release=rhel7 -l m_mem_free=3G -q "
                    + self.queue_option
                    + ".q "
                    + submit_script
                ]
            print("Running:", " ".join(command))
            subprocess.call(command, shell=True)
    
    def submit_job(self):
        for line in self.data_dir:
            if glob.glob(line):
                data_name = line.strip("\n").split("/")
                if not data_name[-1]:
                    print('make sure there is no "/" at the end of the file path')
                    break
                else:
                    data_tag = data_name[-2]
                    data_folder = str(line)
                    self.create_job(data_folder, data_tag)
            else:
                print("Data processing folder not exist:" + line + " please check")



