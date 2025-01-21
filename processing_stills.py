
from __future__ import absolute_import, division, print_function
from textwrap import dedent
import os
import shutil
import stat
import string
import subprocess
import sys
import numpy as np 
import glob
"""
create and submit the dails.stills_processing
"""

#color setting
class colors:
    BOLD = '\033[1m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    RED = '\033[31m'
    ENDC = '\033[m'

class generate_and_process:
    """generate the procrssing files and submit the job"""
    #def __init__(self, file_format:str, data_dir:list, processing_dir:str, cluster_option:str, phil_file:str, dials_path:str, cpu_diamond_processing:str):
    def __init__(self, **kwargs):
        #print(kwargs)
        self.file_format = kwargs["file_format"]
        self.data_dir = kwargs["data_dir"]
        self.processing_dir = kwargs["processing_dir"]
        self.sample_tag = kwargs["sample_tag"]
        self.cluster_option = kwargs["cluster_option"]
        self.geom = kwargs["geom"]
        self.mask = kwargs["mask"]
        self.min_spot_size = kwargs["min_spot_size"]
        self.max_spot_size = kwargs["max_spot_size"]
        self.resolution = kwargs["resolution"]
        self.space_group = kwargs["space_group"]
        self.unit_cell = kwargs["unit_cell"]
        self.phil_file_extra = kwargs["phil_file_extra"]
        self.composite = kwargs["composite"]
        self.ouput_all = kwargs["output_all"]
        self.dials_path = kwargs["dials_path"]
        self.cpu_diamond_processing = kwargs["cpu_diamond_processing"]

    def create_job(self, data_files:str, process_name:str):
        processing_folder = self.processing_dir + "/stills_processing/" + self.sample_tag + "/" + process_name
        submit_script = processing_folder + "/" + str("run_" + process_name + ".sh")
        condor_script = processing_folder + "/" + str("condor_" + process_name + ".sh") #this is only for condor at PAL-XFEL
        phil = processing_folder + "/" + "input.phil"
        phil_condor = processing_folder + "/" + "${1}" #only for condor jobs
        stdout_dir = processing_folder + "/stdout"
        print(colors.GREEN + colors.BOLD + "Submit jobs for: " + process_name + colors.ENDC)
        print(colors.GREEN + colors.BOLD + "Generate phil file: " + process_name + colors.ENDC)
        if os.path.isdir(processing_folder) and os.path.isfile(submit_script):
            print(colors.BLUE + colors.BOLD + "dataset " + process_name + " is processing or has been processed, please check the foled: " + processing_folder + colors.ENDC)
        elif self.processing_dir == "Please select output folder":
            print(colors.BLUE + colors.BOLD + "Please specify a processing folder" + colors.ENDC)
        else:
            #create phil file based on gui settings:
            if not os.path.isdir(processing_folder):
                os.makedirs(processing_folder)
            if os.path.exists(phil):
                os.remove(phil)
            with open(phil, "a") as p:
                if self.geom.endswith(".expt"):
                    p.write(f"input.reference_geometry={self.geom} \n")
                if self.mask.endswith(".mask"):
                    p.write(f"spotfinder.lookup.mask={self.mask} \n")
                    p.write(f"integration.lookup.mask={self.mask} \n\n\n")
                p.write(f"spotfinder.filter.min_spot_size={self.min_spot_size} \nspotfinder.filter.max_spot_size={self.max_spot_size} \n")
                p.write(f"spotfinder.filter.d_min={self.resolution} \n\n\n")
                #if self.cluster_option == "slurm Diamond":
                #    p.write(f"mp.nproc={self.cpu_diamond_processing} \nmp.method=multiprocessing \n\n\n")
                p.write(f"indexing.known_symmetry.space_group={self.space_group} \nindexing.known_symmetry.unit_cell={self.unit_cell} \n\n\n")
                p.write(self.phil_file_extra)
                if self.composite == "no":
                    p.write(f"output.composite_output=False \n")
                if self.ouput_all == "yes":
                    p.write(f"output.experiments_filename=%s_imported.expt \noutput.strong_filename=%s_strong.refl \n\n\n")
                #add output logging file dir except for condor (PAL-XFEL)
                if self.cluster_option == "condor":
                    pass
                else:
                    p.write(f"\n\n\noutput.logging_dir=stdout")
            #make stdout dir
            if not os.path.isdir(stdout_dir):
                os.makedirs(stdout_dir)
            #set up cluster files
            if self.cluster_option == "slurm Diamond":
                with open(submit_script, "a") as f:
                    f.write(dedent("""\
                                    #!/bin/bash
                                    #SBATCH --time=40:00:00
                                    #SBATCH --partition=cs04r  \n"""))
                    f.write("#SBATCH --ntasks=" + self.cpu_diamond_processing + "\n")
                    f.write("#SBATCH --chdir " + processing_folder + "\n")
                    f.write("#SBATCH --job-name " + process_name + "\n" + "\n" + "\n")
                    f.write("source " + self.dials_path + "\n")
                    if self.file_format == "cbf":
                        f.write("mpirun dials.stills_process input.glob=" + data_files + " " + phil + " mp.method=mpi \n")
                    else:
                        f.write("mpirun dials.stills_process " + data_files + " " + phil + " mp.method=mpi \n")
                print(data_files)

                os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                command = "sbatch " + submit_script
                print("Running: ", command)
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
                    f.write("mpirun dials.stills_process " + data_files + " " + phil + " mp.method=mpi \n")
                print(data_files)

                os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                command = "sbatch " + submit_script
                print("Running: ", command)
                #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                subprocess.call(command, cwd=processing_folder, shell=True)
            elif self.cluster_option == "slurm SwissFEL":
                with open(submit_script, "a") as f:
                    f.write(dedent("""\
                                    #!/bin/bash
                                    #SBATCH --ntasks=1
                                    #SBATCH --cpus-per-task=32                          
                                    #SBATCH -p day \n"""))
                    f.write("#SBATCH --chdir " + processing_folder + "\n")
                    f.write("#SBATCH --job-name " + process_name + "\n" + "\n" + "\n")  
                    f.write("source " + self.dials_path + "\n")
                    f.write("dials.stills_process " + data_files + " " + phil + "\n")
                print(data_files)

                os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                command = "sbatch " + submit_script
                print("Running: ", command)
                #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                subprocess.call(command, cwd=processing_folder, shell=True)

            elif self.cluster_option == "condor":
                with open(submit_script, "a") as f1:
                    f1.write("#!/bin/bash" + "\n")
                    f1.write("source " + self.dials_path + "\n")
                    f1.write("dials.stills_process " + data_files + " " + phil_condor + " mp.nproc=20 " + "\n")
                with open(condor_script, "a") as f2:
                    f2.write("request_cpus = 20 " + "\n")
                    f2.write("request_memory = 20000M " + "\n")
                    f2.write("executable = " + submit_script + "\n")
                    f2.write("arguments = input.phil" + "\n")
                    f2.write("Requirements = (Machine != \"pal-wn1004.sdfarm.kr\") " + "\n")
                    f2.write("log = " + process_name + ".log" + "\n")
                    f2.write("error = " + process_name + ".err" + "\n")
                    f2.write("output = " + process_name + ".out" + "\n")
                    f2.write("queue" + "\n")
                
                os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                command = "condor_submit " + "-batch-name " + process_name + " " + condor_script
                print("Running: ", command)
                #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                subprocess.call(command, cwd=processing_folder, shell=True)

    def submit_job(self):
        for line in self.data_dir:
            if glob.glob(line):
                for path in glob.glob(line):
                    data_name = path.strip("\n").split("/")
                    if os.path.isdir(path):
                        if not data_name[-1]:
                            print('make sure there is no "/" at the end of the file path')
                            break
                        else:
                            if self.file_format == "cbf":
                                stills_arg = path + "/*" + ".cbf"
                                data_tag = data_name[-1]
                                self.create_job(stills_arg, data_tag)
                            elif self.file_format == "Select file format":
                                print("Please select data format")
                            elif self.file_format == "h5 palxfel":
                                stills_arg = path + "/*." + "h5"
                                data_tag = data_name[-1]
                                self.create_job(stills_arg, data_tag)
                            elif self.file_format == "h5 master":
                                stills_arg = path + "/*master." + "h5"
                                data_tag = data_name[-1]
                                self.create_job(stills_arg, data_tag)
                            elif self.file_format == "nxs":
                                stills_arg = path + "/*." + self.file_format
                                data_tag = data_name[-1]
                                self.create_job(stills_arg, data_tag)
                            else:
                                print("Unknown format, please check")
                    else:
                        print(f"Data folder {path} not exists, please check")
            elif line == "":
                pass
            else:
                print("Some data folder not exist in:" + line + " please check")

    def test(self):
        print("test")
        print(str(self.processing_dir))

