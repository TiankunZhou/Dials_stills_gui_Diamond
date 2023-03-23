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
        try:
            subprocess.call("dials.version", shell=True)
        else:
            print ("dials not found, please check")
            break
        os.chdir(self.output_dir)
        command_combine = ["dials.combine_experiments " + self.data_dir + "/*refine.expt " + self.data_dir + "/indexed.refl " + "reference_from_experiment.detector=0 n_subset=2000"]
        subprocess.call(command_combine, shell=True)
        print(colors.BLUE + colors.BOLD + "DIALS combine work finished" + colors.ENDC)

    def refine(self):
        phil = self.output_dir + "/refine.phil" 
        print(colors.BLUE + colors.BOLD + "Praparing the refinement work" + colors.ENDC)
        os.chdir(self.output_dir)
        with open(phil, "a+") as p:
            p.write(self.phil_file)
        command_filter = ["cctbx.xfel.filter_experiments_by_rmsd combined.*"]
        print(colors.BLUE + colors.BOLD + "Start filtering the combine result" + colors.ENDC)
        subprocess.call(command_filter, shell=True)
        print(colors.BLUE + colors.BOLD + "Filter job finished" + colors.ENDC)
        time.sleep(1)
        print(colors.BLUE + colors.BOLD + "Start refining the geometry" + colors.ENDC)
        command_refine = ["dials.refine filtered.* refine.phil"]
        subprocess.call(command_refine, shell=True)
        time.sleep(1)
        print(colors.BLUE + colors.BOLD + "Refinement work finished, Please compare the geometry with dials 3.7 or lower" + colors.ENDC)
        print(colors.BLUE + colors.BOLD + "Spliting the job" + colors.ENDC)
        command_split = ["mkdir split; cd split \n" + "dials.split_experiments ../refined.expt"]
        subprocess.call(command_split, shell=True)
        time.sleep(1)
        print(colors.BLUE + colors.BOLD + "Job splited, copy and rename the new geometry file" + colors.ENDC)
        if os.isfile(self.output_dir + "/split/split_0000.expt"):
            command_copy = ["mv split_0000.expt ../refined_0000.expt "]
            subprocess.call(command_copy, shell=True)
            time.slppe(1)
            print(colors.BLUE + colors.BOLD + "New geometry file: " + self.output_dir + "/refined_0000.expt" + colors.ENDC)
        elif os.isfile(self.output_dir + "/split/split_000.expt"):
            command_copy = ["mv split_000.expt ../refined_0000.expt "]
            subprocess.call(command_copy, shell=True)
            time.slppe(1)
            print(colors.BLUE + colors.BOLD + "New geometry file: " + self.output_dir + "/refined_0000.expt" + colors.ENDC)
        else:
            print(colors.RED + colors.BOLD + "Not enough files for geometry refinement (<100), please collect and process more data" + colors.ENDC)
    
    def compare(self):
        print("under construction")


    def run_job(self):
        self.combine()
        time.sleep(2)
        self.refine()

