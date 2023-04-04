import os
import sys
from pathlib import Path
import subprocess
from processing_stills import colors
import time

"""
Geometry refinement based on dials.refine
"""
class geometry_refinement():
    def __init__(self, data_dir:list, output_dir:str, phil_file:str):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.phil_file = phil_file

    def combine(self):
        #os.chdir(self.output_dir)
        #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
        print(colors.RED + colors.BOLD + "Geometry refinement starts. Please do not touch the GUI until the job is finished" + colors.ENDC)
        command_combine = "dials.combine_experiments " + self.data_dir + "/*refined.expt " + self.data_dir + "/*indexed.refl " + "reference_from_experiment.detector=0 " + "n_subset=2000"
        print("Combine command: " + command_combine)
        subprocess.call(command_combine, cwd=self.output_dir, shell=True)
        print(colors.BLUE + colors.BOLD + "DIALS combine work finished" + colors.ENDC)
        print(colors.RED + colors.BOLD + "Geometry refinement is still running. Please do not touch the GUI until the job is finished" + colors.ENDC)

    def refine(self):
        phil = self.output_dir + "/refine.phil" 
        print(colors.BLUE + colors.BOLD + "Praparing the refinement job" + colors.ENDC)
        #os.chdir(self.output_dir)
        #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
        with open(phil, "a+") as p:
            p.write(self.phil_file)
        command_filter = "cctbx.xfel.filter_experiments_by_rmsd " + "combined.*"
        print(colors.BLUE + colors.BOLD + "Start filtering the combine result" + colors.ENDC)
        print("Filter command: " + command_filter)
        subprocess.call(command_filter, cwd=self.output_dir, shell=True)
        print(colors.BLUE + colors.BOLD + "Filter job finished" + colors.ENDC)
        print(colors.RED + colors.BOLD + "Geometry refinement is still running. Please do not touch the GUI until the job is finished" + colors.ENDC)
        time.sleep(1)
        print(colors.BLUE + colors.BOLD + "Start refining the geometry" + colors.ENDC)
        command_refine = "dials.refine " + "filtered.* " + "refine.phil"
        print("Refine command: " + command_refine)
        subprocess.call(command_refine, cwd=self.output_dir, shell=True)
        time.sleep(1)
        print(colors.BLUE + colors.BOLD + "Spliting the job" + colors.ENDC)
        print(colors.RED + colors.BOLD + "Geometry refinement is still running. Please do not touch the GUI until the job is finished" + colors.ENDC)
        command_split = "mkdir split; cd split \n" + "dials.split_experiments ../refined.expt"
        print("split command: " + command_split)
        subprocess.call(command_split, cwd=self.output_dir, shell=True)
        time.sleep(1)
        print(colors.BLUE + colors.BOLD + "Job splited, copy and rename the new geometry file" + colors.ENDC)
        if os.path.isfile(self.output_dir + "/split/split_0000.expt"):
            command_copy = "cp " + self.output_dir + "/split/split_0000.expt " + self.output_dir + "/refined_0000.expt"
            subprocess.call(command_copy, cwd=self.output_dir, shell=True)
            time.sleep(1)
            print(colors.GREEN + colors.BOLD + "Geometry refinement done, new geometry file: " + self.output_dir + "/refined_0000.expt" + colors.ENDC)
        elif os.path.isfile(self.output_dir + "/split/split_000.expt"):
            command_copy = "cp " + self.output_dir + "/split/split_000.expt " + self.output_dir + "/refined_0000.expt"
            subprocess.call(command_copy, cwd=self.output_dir, shell=True)
            time.sleep(1)
            print(colors.GREEN + colors.BOLD + "Geometry refinement done, new geometry file: " + self.output_dir + "/refined_0000.expt" + colors.ENDC)
        else:
            print(colors.RED + colors.BOLD + "Not enough files for geometry refinement (<100), please collect and process more data" + colors.ENDC)
    
    def compare(self):
        #shall=True can be dangerous, make sure no bad command in it. "module" can not be called with out shell=True
        print("Ploting geomerty comparison: " + self.output_dir)
        command_compare = "dxtbx.plot_detector_models " + self.output_dir + "/combined.expt " + self.output_dir + "/refined.expt"
        subprocess.call(command_compare, shell=True)

    def run_job(self):
        try:
            subprocess.call(["dials.version"])
        except:
            print ("dials not found, please check")
        else:
            if os.path.isfile(self.output_dir + "/refine.phil"):
                print(colors.RED + colors.BOLD + "Refinement job has done, please check: " + self.output_dir + colors.ENDC)
                print(colors.RED + colors.BOLD + "Or you can remove the files in: " + self.output_dir + " and re-submit the job" + colors.ENDC)
            else:
                if not self.data_dir == "" and not self.output_dir == "":
                    self.combine()
                    time.sleep(2)
                    self.refine()
                else:
                    print("data dir or processing dir is not given, please check")
    
    def run_compare(self):
        try:
            subprocess.call(["dials.version"])
        except:
            print ("dials not found, please check")
        else:
            if not self.output_dir == "":
                self.compare()
            else:
                print("processing dir is not given, please check")





