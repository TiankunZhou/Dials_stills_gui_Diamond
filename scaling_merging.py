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
from change_line import change_phil
from textwrap import dedent

"""
Sacling and merging settings
"""

class scaling_job:
    def __init__(self, **kwargs):
        self.data_dir = kwargs["data_dir"]
        self.processing_dir = kwargs["output_dir"]
        self.cluster_option = kwargs["cluster_option"]
        self.phil_file = kwargs["phil_file_scaling"]
        self.tag = kwargs["sample_tag_scaling"]
        self.resolution = str(kwargs["resolution_scaling"])
        self.ref_pdb = kwargs["ref_pdb_scaling"]
        self.dials_path = kwargs["dials_path"]
        self.cpu_diamond_scaling = kwargs["cpu_diamond_scaling"]
    
    def create_job(self, data_folder:str, process_name:str, run_name:str):
        processing_folder = self.processing_dir + "/scaling/" + process_name + "/" + run_name
        submit_script = processing_folder + "/" + str("run_scaling_" + process_name + ".sh")
        condor_script = processing_folder + "/" + str("condor_" + process_name + ".sh") #this is only for condor at PAL-XFEL
        phil = processing_folder + "/" + "scaling.phil"
        prefix = str(self.tag + "_scaling_" + self.resolution + "A")
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
            change_phil(phil, self.resolution, prefix, self.ref_pdb)
            if self.cluster_option == "slurm Diamond":
                with open(submit_script, "a") as f:
                    f.write(dedent("""\
                                    #!/bin/bash
                                    #SBATCH --time=40:00:00
                                    #SBATCH --partition=cs04r  \n"""))
                    f.write("#SBATCH --ntasks=" + self.cpu_diamond_scaling + "\n")
                    f.write("#SBATCH --chdir " + processing_folder + "\n")
                    f.write("#SBATCH --job-name " + process_name + "\n" + "\n" + "\n")
                    f.write("source " + self.dials_path + "\n")
                    f.write("mpirun -n 10 cctbx.xfel.merge "+ phil + " mp.method=mpi\n")
                print(phil)

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
                                    #SBATCH --nodes=1                               # Number of nodes
                                    #SBATCH --output    dsp-%N-%j.out            # File to which STDOUT will be written
                                    #SBATCH --error     dsp-%N-%j.err            # File to which STDERR will be written \n"""))
                    f.write("#SBATCH --chdir " + processing_folder + "\n")
                    f.write("#SBATCH --job-name " + process_name + "\n" + "\n" + "\n")                                                                
                    f.write("source /usr/share/Modules/init/bash \n")
                    f.write("source " + self.dials_path + "\n")
                    f.write("mpirun cctbx.xfel.merge " + phil + " mp.method=mpi \n")
                print(phil)

                os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                command = "sbatch " + submit_script
                print("Running:", command)
                #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                subprocess.call(command, cwd=processing_folder, shell=True)

            elif self.cluster_option == "slurm SwissFEL":
                with open(submit_script, "a") as f:
                    f.write(dedent("""\
                                    #!/bin/bash
                                    #SBATCH --ntasks=1
                                    #SBATCH --cpus-per-task=20
                                    #SBATCH -p day \n"""))
                    f.write("#SBATCH --chdir " + processing_folder + "\n")
                    f.write("#SBATCH --job-name " + process_name + "\n" + "\n" + "\n")
                    f.write("source " + self.dials_path + "\n")
                    f.write("mpirun -n 20 cctbx.xfel.merge " + phil + " mp.method=mpi \n")
                print(phil)

                os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                command = "sbatch " + submit_script
                print("Running:", command)
                #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                subprocess.call(command, cwd=processing_folder, shell=True) 

            elif self.cluster_option == "condor":
                with open(submit_script, "a") as f1:
                    f1.write("#!/bin/bash" + "\n")
                    f1.write("source " + self.dials_path + "\n")
                    f1.write("mpirun -n ${1} cctbx.xfel.merge " + phil + " mp.method=mpi \n")
                with open(condor_script, "a") as f2:
                    f2.write("request_cpus = 10 " + "\n")
                    f2.write("request_memory = 10000M " + "\n")
                    f2.write("executable = " + submit_script + "\n")
                    f2.write("arguments = 10" + "\n")
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
            if line == "":
                pass
            elif glob.glob(line):
                for path in glob.glob(line):
                    data_name = path.strip("\n").split("/")
                    if not data_name[-1]:
                        print('make sure there is no "/" at the end of the file path')
                        break
                    else:
                        run_folder = data_name[-1]
                        data_tag = self.tag
                        data_folder = str(path)
                        self.create_job(data_folder, data_tag, run_folder)
            else:
                print("Data processing folder not exist:" + line + " please check")

class merging_job:
    def __init__(self, **kwargs):
        self.data_dir = kwargs["data_dir"]
        self.processing_dir = kwargs["output_dir"]
        self.cluster_option = kwargs["cluster_option"]
        self.phil_file = kwargs["phil_file_merging"]
        self.tag = kwargs["sample_tag_merging"]
        self.resolution = str(kwargs["resolution_merging"])
        self.ref_pdb = kwargs["ref_pdb_merging"]
        self.dials_path = kwargs["dials_path"]
        self.cpu_diamond_merging = kwargs["cpu_diamond_merging"]
    
    def create_job(self, data_folder:str, process_name:str, run_name:str):
        processing_folder = self.processing_dir + "/merging/" + process_name + "/" + run_name
        submit_script = processing_folder + "/" + str("run_merging_" + process_name + ".sh")
        condor_script = processing_folder + "/" + str("condor_" + process_name + ".sh") #this is only for condor at PAL-XFEL
        phil = processing_folder + "/" + "merging.phil"
        prefix = self.tag + "_merging_" + self.resolution + "A"
        print(colors.GREEN + colors.BOLD + "Submit merging jobs for: " + process_name + colors.ENDC)
        if os.path.isdir(processing_folder) and os.path.isfile(submit_script):
            print(colors.BLUE + colors.BOLD + "Merging job of " + process_name + " has been submitted, please check the foled: " + processing_folder + colors.ENDC)
        
        else:
            if not os.path.isdir(processing_folder):
                os.makedirs(processing_folder)
            if os.path.exists(phil):
                os.remove(phil)
            with open(phil, "a") as p:
                for line in data_folder:
                    if line == "":
                        pass
                    elif glob.glob(line):
                        for path in glob.glob(line):
                            data_name = path.strip("\n").split("/")
                            if not data_name[-1]:
                                print('make sure there is no "/" at the end of the file path')
                                break
                            else:
                                p.write("input.path=" + str(path) + "\n")
                    else:
                        print("Data scaling folder not exist:" + line + " please check")
                p.write(self.phil_file)
            change_phil(phil, self.resolution, prefix, self.ref_pdb)
            if self.cluster_option == "slurm Diamond":
                with open(submit_script, "a") as f:
                    f.write(dedent("""\
                                    #!/bin/bash
                                    #SBATCH --time=40:00:00
                                    #SBATCH --partition=cs04r  \n"""))
                    f.write("#SBATCH --ntasks=" + self.cpu_diamond_merging + "\n")
                    f.write("#SBATCH --chdir " + processing_folder + "\n")
                    f.write("#SBATCH --job-name " + process_name + "\n" + "\n" + "\n")
                    f.write("source " + self.dials_path + "\n")
                    f.write("mpirun -n 10 cctbx.xfel.merge "+ phil + " mp.method=mpi\n")
                print(phil)

                os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                command = "sbatch " + submit_script
                print("Running: ", command)
                #command_merginglist = "ls -d " + data_folder + " > " + processing_folder + "/" + process_name + "_" + run_name +"_file_list.log"
                #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                #subprocess.call(command_merginglist, shell=True)
                subprocess.call(command, shell=True)

            elif self.cluster_option == "slurm EuXFEL":
                with open(submit_script, "a") as f:
                    f.write(dedent("""\
                                    #!/bin/bash
                                    #SBATCH --partition=upex
                                    #SBATCH --time=01:00:00                           # Maximum time requested
                                    #SBATCH --nodes=1                               # Number of nodes
                                    #SBATCH --output    dsp-%N-%j.out            # File to which STDOUT will be written
                                    #SBATCH --error     dsp-%N-%j.err            # File to which STDERR will be written \n"""))
                    f.write("#SBATCH --chdir " + processing_folder + "\n")
                    f.write("#SBATCH --job-name " + process_name + "\n" + "\n" + "\n")                                                                  
                    f.write("source /usr/share/Modules/init/bash \n")
                    f.write("source " + self.dials_path + "\n")
                    f.write("mpirun cctbx.xfel.merge " + phil + " mp.method=mpi \n")
                print(phil)

                os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                command = "sbatch " + submit_script
                print("Running:", command)
                #command_merginglist = "ls -d " + data_folder + " > " + processing_folder + "/" + process_name + "_" + run_name +"_file_list.log"
                #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                #subprocess.call(command_merginglist, shell=True)

                subprocess.call(command, shell=True)
            elif self.cluster_option == "slurm SwissFEL":
                with open(submit_script, "a") as f:
                    f.write(dedent("""\
                                    #!/bin/bash
                                    #SBATCH --ntasks=1
                                    #SBATCH --cpus-per-task=20
                                    #SBATCH -p day \n"""))
                    f.write("#SBATCH --chdir " + processing_folder + "\n")
                    f.write("#SBATCH --job-name " + process_name + "\n" + "\n" + "\n")  
                    f.write("source " + self.dials_path + "\n")
                    f.write("mpirun -n 20 cctbx.xfel.merge " + phil + " mp.method=mpi \n")
                print(phil)

                os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                command = "sbatch " + submit_script
                print("Running:", command)
                #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                subprocess.call(command, cwd=processing_folder, shell=True) 

            elif self.cluster_option == "condor":
                with open(submit_script, "a") as f1:
                    f1.write("#!/bin/bash" + "\n")
                    f1.write("source " + self.dials_path + "\n")
                    f1.write("mpirun -n ${1} cctbx.xfel.merge " + phil + " mp.method=mpi \n")
                with open(condor_script, "a") as f2:
                    f2.write("request_cpus = 10 " + "\n")
                    f2.write("request_memory = 10000M " + "\n")
                    f2.write("executable = " + submit_script + "\n")
                    f2.write("arguments = 10" + "\n")
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
        data_tag = self.tag
        if not os.path.isdir(self.processing_dir + "/merging/" + data_tag + "/"):
            version = 0 
        else:
            folder_list = [f.name for f in os.scandir(self.processing_dir + "/merging/" + data_tag + "/") if f.is_dir()]
            lastchara_list = [n[1:] for n in folder_list]
            version_list = [b for b in lastchara_list if b.isdigit()]
            if not version_list:
                version = 0
            else:
                version = int(max(version_list)) + 1
        run_name = "v" + str('{0:03}'.format(version))
        print(colors.BLUE + colors.BOLD + "merging version: " + run_name + colors.ENDC)
        self.create_job(self.data_dir, data_tag, run_name)





