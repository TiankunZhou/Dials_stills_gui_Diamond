from __future__ import absolute_import, division, print_function
from textwrap import dedent
import os
import stat
import subprocess
import sys
import numpy as np 
import glob
from processing_stills import colors
"""
create and submit the xia2.ssx jobs
"""

class run_xia2:
    def __init__(self, file_format:str, data_dir:list, processing_dir:str, cluster_option:str, submit_file:str, dials_path:str):
        self.file_format = file_format
        self.data_dir = data_dir
        self.processing_dir = processing_dir
        self.cluster_option = cluster_option
        self.submit_file = submit_file
        self.dials_path = dials_path
    
    def generate_xia2(self, data_files:str, process_name:str):
        processing_folder = self.processing_dir + "/" + process_name
        submit_script = processing_folder + "/" + str("run_xia2_process_" + process_name + ".sh")
        print(colors.GREEN + colors.BOLD + "Submit jobs for: " + process_name + colors.ENDC)
        if os.path.isdir(processing_folder) and os.path.isfile(submit_script):
            print(colors.BLUE + colors.BOLD + "xia2.ssx job for dataset " + process_name + " is processing or has been processed, please check the foled: " + processing_folder + colors.ENDC)        
        else:
            if not os.path.isdir(processing_folder):
                os.makedirs(processing_folder)
            if self.cluster_option == "sge":
                with open(submit_script, "a") as f:
                    f.write("module load dials/latest\n")
                    if self.file_format == "cbf":
                        f.write("xia2.ssx template=" + data_files + " \\\n")
                    else:
                        f.write("xia2.ssx image=" + data_files + " \\\n")
                    f.write(self.submit_file)
                print(data_files)

                os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                command = [
                        "module load global/cluster && qsub -j y -wd " + processing_folder + " -pe smp 20 -l redhat_release=rhel7 -l m_mem_free=3G -q "
                        + "medium.q "
                        + submit_script
                    ]
                print("Running:", " ".join(command))
                #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                subprocess.call(command, shell=True)
            elif self.cluster_option == "slurm EuXFEL":
                with open(submit_script, "a") as f:
                    f.write(dedent("""\
                                    #!/bin/bash
                                    #SBATCH --partition=upex
                                    #SBATCH --time=01:00:00                           # Maximum time requested
                                    #SBATCH --nodes=2                               # Number of nodes
                                    #SBATCH --output    dsp-%N-%j.out            # File to which STDOUT will be written
                                    #SBATCH --error     dsp-%N-%j.err            # File to which STDERR will be written \n"""))
                    f.write("#SBATCH --chdir " + processing_folder + "\n")
                    f.write("#SBATCH --job-name " + process_name + "\n" + "\n" + "\n")                                                              
                    f.write("source /usr/share/Modules/init/bash \n")
                    f.write("source " + self.dials_path + "\n")
                    f.write(self.submit_file)
                print(data_files)

                os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                command = "sbatch " + submit_script
                print("Running: ", command)
                #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                subprocess.call(command, cwd=processing_folder, shell=True)

    def submit_xia2(self):
        for line in self.data_dir:
            if glob.glob(line):
                for path in glob.glob(line):
                    data_name = path.strip("\n").split("/")
                    if not data_name[-1]:
                        print('make sure there is no "/" at the end of the file path')
                        break
                    else:
                        if self.file_format == "cbf":
                            chip_name = glob.glob(path + "/*00001.cbf")[0].split("/")[-1].split("_")[0]
                            for i in range(10):
                                stills_arg = path + "/" + chip_name + "_####" + str(i) + ".cbf"
                                data_tag = data_name[-1] + str(i)
                                self.generate_xia2(stills_arg, data_tag)
                        elif self.file_format == "Select file format":
                            print("Please select data format")
                        elif self.file_format == "h5 palxfel":
                            stills_arg = path + "/*." + "h5"
                            data_tag = data_name[-1]
                            self.generate_xia2(stills_arg, data_tag)
                        elif self.file_format == "h5 master":
                            stills_arg = path + "/*master." + "h5"
                            data_tag = data_name[-1]
                            self.generate_xia2(stills_arg, data_tag)
                        elif self.file_format == "nxs":
                            stills_arg = path + "/*." + self.file_format
                            data_tag = data_name[-1]
                            self.generate_xia2(stills_arg, data_tag)
                        else:
                            print("Unknown format, please check")
            
            else:
                print("Some data folder not exist in:" + line + " please check")






