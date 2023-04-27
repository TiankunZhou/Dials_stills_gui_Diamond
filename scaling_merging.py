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
    def __init__(self, data_dir:list, processing_dir:str, cluster_option:str, phil_file:str, tag:str, resolution:float, ref_pdb:str):
        self.data_dir = data_dir
        self.processing_dir = processing_dir
        self.cluster_option = cluster_option
        self.phil_file = phil_file
        self.tag = tag
        self.resolution = str(resolution)
        self.ref_pdb = ref_pdb
    
    def create_job(self, data_folder:str, process_name:str, run_name:str):
        processing_folder = self.processing_dir + "/" + process_name + "/" + run_name
        submit_script = processing_folder + "/" + str("run_scaling_" + process_name + ".sh")
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
            if self.cluster_option == "sge":
                with open(submit_script, "a") as f:
                    f.write("source /dls/science/users/tbf48622/dials_own/dials\n")
                    f.write("mpirun -n ${NSLOTS} cctbx.xfel.merge "+ phil + " mp.method=mpi\n")
                print(phil)

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
                print("Slurm under construction")
                with open(submit_script, "a") as f:
                    f.write(dedent("""\
                                    #!/bin/bash
                                    #SBATCH --partition=upex
                                    #SBATCH --time=01:00:00                           # Maximum time requested
                                    #SBATCH --nodes=1                               # Number of nodes
                                    #SBATCH --output    dsp-%N-%j.out            # File to which STDOUT will be written
                                    #SBATCH --error     dsp-%N-%j.err            # File to which STDERR will be written \n"""))
                    f.write("#SBATCH --job-name " + run_name + "\n")                                                                 
                    f.write("source /usr/share/Modules/init/bash \n")
                    f.write("source /gpfs/exfel/exp/SPB/202201/p002826/usr/Software/Tiankun/dials_test_conda3/dials \n")
                    f.write("mpirun cctbx.xfel.merge " + phil + " mp.method=mpi \n")
                print(phil)

                os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                command = "sbatch " + submit_script
                print("Running:", command)
                #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                #subprocess.call(command, cwd=processing_folder, shell=True)
    
    def submit_job(self):
        for line in self.data_dir:
            if glob.glob(line):
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
    def __init__(self, data_dir:list, processing_dir:str, cluster_option:str, phil_file:str, tag:str, resolution:float, ref_pdb:str):
        self.data_dir = data_dir
        self.processing_dir = processing_dir
        self.cluster_option = cluster_option
        self.phil_file = phil_file
        self.tag = tag
        self.resolution = str(resolution)
        self.ref_pdb = ref_pdb
    
    def create_job(self, data_folder:str, process_name:str, run_name:str):
        processing_folder = self.processing_dir + "/" + process_name + "/" + run_name
        submit_script = processing_folder + "/" + str("run_merging_" + process_name + ".sh")
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
                p.write("input.path=" + data_folder + "\n")
                p.write(self.phil_file)
            change_phil(phil, self.resolution, prefix, self.ref_pdb)
            if self.cluster_option == "sge":
                with open(submit_script, "a") as f:
                    f.write("source /dls/science/users/tbf48622/dials_own/dials\n")
                    f.write("mpirun -n ${NSLOTS} cctbx.xfel.merge "+ phil + " mp.method=mpi\n")
                print(phil)

                os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                command = [
                        "module load global/cluster && qsub -j y -wd " + processing_folder + " -pe smp 20 -l redhat_release=rhel7 -l m_mem_free=3G -q "
                        + "medium.q "
                        + submit_script
                    ]
                print("Running:", " ".join(command))
                command_merginglist = "ls -d " + data_folder + " > " + processing_folder + "/" + process_name + "_" + run_name +"_file_list.log"
                #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                subprocess.call(command_merginglist, shell=True)
                subprocess.call(command, shell=True)
            elif self.cluster_option == "slurm EuXFEL":
                print("Slurm under construction")
                with open(submit_script, "a") as f:
                    f.write(dedent("""\
                                    #!/bin/bash
                                    #SBATCH --partition=upex
                                    #SBATCH --time=01:00:00                           # Maximum time requested
                                    #SBATCH --nodes=1                               # Number of nodes
                                    #SBATCH --output    dsp-%N-%j.out            # File to which STDOUT will be written
                                    #SBATCH --error     dsp-%N-%j.err            # File to which STDERR will be written \n"""))
                    f.write("#SBATCH --job-name " + process_name + "\n")                                                                 
                    f.write("source /usr/share/Modules/init/bash \n")
                    f.write("source /gpfs/exfel/exp/SPB/202201/p002826/usr/Software/Tiankun/dials_test_conda3/dials \n")
                    f.write("mpirun cctbx.xfel.merge " + phil + " mp.method=mpi \n")
                print(phil)

                os.chmod(submit_script, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                command = "sbatch " + submit_script
                print("Running:", command)
                command_merginglist = "ls -d " + data_folder + " > " + processing_folder + "/" + process_name + "_" + run_name +"_file_list.log"
                #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
                subprocess.call(command_merginglist, shell=True)
                #subprocess.call(command, shell=True)

    
    def submit_job(self):
        for line in self.data_dir:
            if glob.glob(line):
                data_name = line.strip("\n").split("/")
                if not data_name[-1]:
                    print('make sure there is no "/" at the end of the file path')
                    break
                else:
                    data_tag = self.tag
                    data_folder = str(line)
                    if not os.path.isdir(self.processing_dir + "/" + data_tag + "/"):
                        version = 0 
                    else:
                        folder_list = [f.name for f in os.scandir(self.processing_dir + "/" + data_tag + "/") if f.is_dir()]
                        lastchara_list = [n[1:] for n in folder_list]
                        version_list = [b for b in lastchara_list if b.isdigit()]
                        if not version_list:
                            version = 0
                        else:
                            version = int(max(version_list)) + 1
                    run_name = "v" + str('{0:03}'.format(version))
                    print(colors.BLUE + colors.BOLD + "merging version: " + run_name + colors.ENDC)
                    self.create_job(data_folder, data_tag, run_name)
            else:
                print("Data scaling folder not exist:" + line + " please check")




