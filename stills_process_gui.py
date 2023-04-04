import tkinter as tk
from tkinter import ttk
from textwrap import dedent
from processing_stills import colors, generate_and_process
from plotting_status import count, dot, bar, pie, plot
from scaling_merging import scaling_job, merging_job
from geo_refine import geometry_refinement
#from geo_refine import geometry_refinement
"""
This is a gui for submit dials stills processing
and merging jobs at DLS 
may need python 3.8 or later
"""

#set up the gui
class MainGUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self) #this is important, call super class ' __init__'
        self.frame = None
        tabs(self).pack() #pack tabs from class tab
        self.title("Processing and plotting gui")

#set up tabs
class tabs(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    self.notebook = ttk.Notebook(self)
    
    #set up tabs using classes below; orders is very important, or it will not work
    self.stills_process = stills_process(self.notebook)
    self.plot_stills = plot_stills(self.notebook)
    self.geo = geo(self.notebook)
    self.scaling = scaling(self.notebook, self.stills_process.queue_option_stills)
    self.merging = merging(self.notebook, self.stills_process.queue_option_stills)
    self.plot_merging = plot_merging(self.notebook)

    #add tabs to the gui
    self.notebook.add(self.stills_process, text="Stills processing")
    self.notebook.add(self.plot_stills, text="Plot processing stat")
    self.notebook.add(self.geo, text="Geometry refinement")
    self.notebook.add(self.scaling, text="Scaling")
    self.notebook.add(self.merging, text="Merging")
    self.notebook.add(self.plot_merging, text="Merging statistics")

    self.notebook.pack()    

#stills processing tab
class stills_process(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    ## Getting phil file
    tk.Label(self, text="Phil file stills", font=("Arial", 15)).grid(row=0, column=0)
    phil_file_stills = tk.Text(self, width=75, height=20, font=("Aria", 15))
    default_phil_processing = dedent("""\
                                  input.reference_geometry=/dls/i24/data/2023/mx25260-43/processing/Tiankun/JR/refined_000.expt
                                  #spotfinder.lookup.mask=/dls/i24/data/2022/mx25260-26/processing/Tiankun_beamtime_processing/dials/Mpro_H41A/test/pixels.mask
                                  #integration.lookup.mask=/dls/i24/data/2022/mx25260-26/processing/Tiankun_beamtime_processing/dials/Mpro_H41A/test/pixels.mask
                                  spotfinder.filter.min_spot_size=2
                                  spotfinder.filter.d_min=1.5
                                  spotfinder.filter.max_spot_size=10

                                  mp.nproc = 20
                                  mp.method=multiprocessing

                                  indexing {
                                    known_symmetry {
                                      space_group = P212121
                                  
                                      unit_cell = 45.2, 45.7, 118.3, 90, 90, 90
                                  
                                    }

                                    stills.indexer=stills
                                    stills.method_list=fft1d real_space_grid_search
                                    multiple_lattice_search.max_lattices=10
                                  }""")
    phil_file_stills.insert(tk.END, default_phil_processing)
    phil_file_stills.grid(row=1, column=0)
    #data dir
    tk.Label(self, text="Data dir stills", font=("Arial", 15)).grid(row=0, column=1)
    data_folder_stills = tk.Text(self, width=50, height=15, font=("Aria", 15))
    data_folder_stills.grid(row=1, column=1)
    #process folder
    tk.Label(self, text="Process folder stills", font=("Arial", 15)).grid(row=2, column=1)
    process_folder_stills = tk.Entry(self, width=50, font=("Aria", 15))
    process_folder_stills.grid(row=3, column=1)
    #file format
    tk.Label(self, text="File format", font=("Arial", 15)).grid(row=0, column=2)
    file_format_list = ["cbf", "h5", "nxs"]
    file_format = tk.StringVar(self)
    file_format.set("Select file format")
    file_format_choice = tk.OptionMenu(self, file_format, *file_format_list, command = lambda selected: plot.read_file_format(file_format.get())).grid(row=1, column=2)
    #queue option
    tk.Label(self, text="Queue option", font=("Arial", 15)).grid(row=2, column=2)
    queue_option_list = ["low", "medium", "high"]
    queue_option = tk.StringVar(self)
    queue_option.set("medium")
    queue_choice = tk.OptionMenu(self, queue_option, *queue_option_list, command = lambda selected: plot.read_queue_option(queue_option.get())).grid(row=3, column=2)
    #make the queue option available to other classes
    self.queue_option_stills = queue_option
    #buttons
    tk.Button(self, text="Submit job", width =12, height=4,font=("Arial", 12), command = lambda: generate_and_process(file_format.get(), data_folder_stills.get("1.0","end").splitlines(), \
    process_folder_stills.get(), queue_option.get(), phil_file_stills.get("1.0","end")).submit_job()).grid(row=4, column=0)

#plot tab
class plot_stills(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    tk.Label(self, text="Enter the ABSOLUTE path of prcessing folder\n separate with new line\n can use * or []\n Currently only works for finished jobs", font=("Arial", 15)).grid(row=0, column=0)
    
    check_dir = tk.Text(self, width=75, height=20, font=("Aria", 15))
    check_dir.grid(row=0, column = 1)

    option_list = ["single", "stack"]
    plot_name = tk.StringVar(self)
    plot_name.set("Select plot option")
    plot_option = tk.OptionMenu(self, plot_name, *option_list, command = lambda selected: plot.read_option(plot_name.get()))
    plot_option.grid(row=0, column=2)

    tk.Button(self, text="Plot dot", width =12, height=4,font=("Arial", 12), command = lambda: plot.dot(plot_name.get(), check_dir.get("1.0","end").splitlines())).grid(row=2, column=0) #convert text to a list
    tk.Button(self, text="Plot bar", width =12, height=4,font=("Arial", 12), command = lambda: plot.bar(plot_name.get(), check_dir.get("1.0","end").splitlines())).grid(row=2, column=1)
    tk.Button(self, text="Plot pie", width =12, height=4,font=("Arial", 12), command = lambda: plot.pie(plot_name.get(), check_dir.get("1.0","end").splitlines())).grid(row=2, column=2)
    #tk.Button(tab_plot, text="Plot bar realtime", width =12, height =4, font=("Arial", 12), command = lambda: plot.real_time_bar(plot_name.get(), check_dir.get("1.0","end").splitlines())).grid(row=2, column=3)

#geo tab
class geo(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    tk.Label(self, text="Phil file geometry refinement", font=("Arial", 15)).grid(row=0, column=0)
    #set default phil file
    phil_file_georefine = tk.Text(self, width=75, height=20, font=("Aria", 15))
    default_phil_georefine = dedent("""\
                                refinement {
                                  parameterisation {
                                    auto_reduction {
                                      min_nref_per_parameter = 3
                                      action = fail fix *remove
                                    }
                                    beam {
                                      fix = *all in_spindle_plane out_spindle_plane wavelength
                                    }
                                    detector {
                                      fix_list = Tau1
                                    }
                                  }
                                  refinery {
                                    engine = SimpleLBFGS LBFGScurvs GaussNewton LevMar *SparseLevMar
                                  }
                                  reflections {
                                    outlier {
                                      algorithm = null auto mcd tukey *sauter_poon
                                      separate_experiments = False
                                      separate_panels = True
                                    }
                                  }
                                } """)
    phil_file_georefine.insert(tk.END, default_phil_georefine)
    phil_file_georefine.grid(row=1, column=0)
    #data dir
    tk.Label(self, text="Data dir geo refinement", font=("Arial", 15)).grid(row=0, column=1)
    data_folder_georefine = tk.Entry(self, width=60, font=("Aria", 15))
    data_folder_georefine.grid(row=1, column=1)
    #processing dir
    tk.Label(self, text="Process folder geo refinement", font=("Arial", 15)).grid(row=2, column=1)
    process_folder_georefine = tk.Entry(self, width=50, font=("Aria", 15))
    process_folder_georefine.grid(row=3, column=1)
    #buttons
    tk.Button(self, text="Submit georefine job", width =15, height=4,font=("Arial", 12), command = lambda: geometry_refinement(data_folder_georefine.get(), process_folder_georefine.get(),\
    phil_file_georefine.get("1.0","end")).run_job()).grid(row=8, column=0)
    tk.Button(self, text="Compare geometry", width =15, height=4,font=("Arial", 12), command = lambda: geometry_refinement(data_folder_georefine.get(), process_folder_georefine.get(),\
    phil_file_georefine.get("1.0","end")).run_compare()).grid(row=8, column=1)
    

    
#scaling tab
class scaling(tk.Frame):
  def __init__(self, master, queue_option_scaling):
    tk.Frame.__init__(self, master)
    tk.Label(self, text="Phil file scaling", font=("Arial", 15)).grid(row=0, column=0)
    #set default phil file
    phil_file_scaling = tk.Text(self, width=75, height=20, font=("Aria", 15))
    default_phil_scaling = dedent("""\
                              input.experiments_suffix=_integrated.expt
                              input.reflections_suffix=_integrated.refl
                              output.prefix=
                              dispatch.step_list=input balance model_scaling modify filter errors_premerge scale postrefine statistics_unitcell statistics_beam model_statistics statistics_resolution
                              input.parallel_file_load.method=uniform
                              filter.outlier.min_corr=0.1
                              #filter.algorithm=unit_cell
                              #filter.unit_cell.value.relative_length_tolerance=0.03
                              scaling.model=
                              scaling.resolution_scalar=0.95
                              scaling.mtz.mtz_column_F=I-obs
                              merging.d_min=
                              merging.merge_anomalous=True
                              postrefinement.enable=True
                              output.do_timing=True
                              output.save_experiments_and_reflections=True """)
    phil_file_scaling.insert(tk.END, default_phil_scaling)
    phil_file_scaling.grid(row=1, column=0)
    #data dir
    tk.Label(self, text="Data dir scaling", font=("Arial", 15)).grid(row=0, column=1)
    data_folder_scaling = tk.Text(self, width=60, height=20, font=("Aria", 15))
    data_folder_scaling.grid(row=1, column=1)
    #process folder
    tk.Label(self, text="Process folder scaling", font=("Arial", 15)).grid(row=2, column=1)
    process_folder_scaling = tk.Entry(self, width=50, font=("Aria", 15))
    process_folder_scaling.grid(row=3, column=1)
    #reference pdb
    tk.Label(self, text="Reference pdb scaling", font=("Arial", 15)).grid(row=2, column=0)
    ref_pdb_scaling = tk.Entry(self, width=50, font=("Aria", 15))
    ref_pdb_scaling.grid(row=3, column=0)
    #tag
    tk.Label(self, text="Sample tag scaling", font=("Arial", 15)).grid(row=4, column=1)
    sample_tag_scaling = tk.Entry(self, width=50, font=("Aria", 15))
    sample_tag_scaling.grid(row=5, column=1)
    #resolution
    tk.Label(self, text="Resolution scaling", font=("Arial", 15)).grid(row=4, column=0)
    resolution_scaling = tk.Entry(self, width=50, font=("Aria", 15))
    resolution_scaling.grid(row=5, column=0)
    #buttons
    #tk.Button(self, text="Submit scaling job", width =12, height=4,font=("Arial", 12), command = lambda:print(queue_option_scaling.get())).grid(row=8, column=0)
    tk.Button(self, text="Submit scaling job", width =12, height=4,font=("Arial", 12), command = lambda: scaling_job(data_folder_scaling.get("1.0","end").splitlines(), \
    process_folder_scaling.get(), queue_option_scaling.get(), phil_file_scaling.get("1.0","end"), sample_tag_scaling.get(), resolution_scaling.get(), ref_pdb_scaling.get()\
    ).submit_job()).grid(row=8, column=0)

#merging tab
class merging(tk.Frame):
  def __init__(self, master, queue_option_merging):
    tk.Frame.__init__(self, master)
    tk.Label(self, text="Phil file merging", font=("Arial", 15)).grid(row=0, column=0)
    phil_file_merging = tk.Text(self, width=75, height=20, font=("Aria", 15))
    default_phil_merging = dedent("""\
                              input.experiments_suffix=.expt
                              input.reflections_suffix=.refl
                              output.prefix=
                              dispatch.step_list=input model_scaling statistics_unitcell statistics_beam model_statistics statistics_resolution group errors_merge statistics_intensity merge statistics_intensity_cxi
                              input.parallel_file_load.method=uniform
                              scaling.model=
                              scaling.resolution_scalar=0.95
                              scaling.mtz.mtz_column_F=I-obs
                              statistics.n_bins=20
                              merging.d_min=
                              merging.merge_anomalous=True
                              merging.error.model=ev11
                              output.do_timing=True """)
    phil_file_merging.insert(tk.END, default_phil_merging)
    phil_file_merging.grid(row=1, column=0)
    #data dir
    tk.Label(self, text="Data dir", font=("Arial", 15)).grid(row=0, column=1)
    data_folder_merging = tk.Text(self, width=60, height=20, font=("Aria", 15))
    data_folder_merging.grid(row=1, column=1)
    #process folder
    tk.Label(self, text="Process folder", font=("Arial", 15)).grid(row=2, column=1)
    process_folder_merging = tk.Entry(self, width=50, font=("Aria", 15))
    process_folder_merging.grid(row=3, column=1)
    #reference pdb
    tk.Label(self, text="Reference pdb merging", font=("Arial", 15)).grid(row=2, column=0)
    ref_pdb_merging = tk.Entry(self, width=50, font=("Aria", 15))
    ref_pdb_merging.grid(row=3, column=0)
    #tag
    tk.Label(self, text="Sample tag merging", font=("Arial", 15)).grid(row=4, column=1)
    sample_tag_merging = tk.Entry(self, width=50, font=("Aria", 15))
    sample_tag_merging.grid(row=5, column=1)
    #resolution
    tk.Label(self, text="Resolution merging", font=("Arial", 15)).grid(row=4, column=0)
    resolution_merging = tk.Entry(self, width=50, font=("Aria", 15))
    resolution_merging.grid(row=5, column=0)
    #buttons
    #tk.Button(self, text="Submit merging job", width =12, height=4,font=("Arial", 12), command = lambda:print(queue_option_merging.get())).grid(row=6, column=0)
    tk.Button(self, text="Submit merging job", width =12, height=4,font=("Arial", 12), command = lambda: merging_job(data_folder_merging.get("1.0","end").splitlines(), \
    process_folder_merging.get(), queue_option_merging.get(), phil_file_merging.get("1.0","end"), sample_tag_merging.get(), resolution_merging.get(), ref_pdb_merging.get()\
    ).submit_job()).grid(row=6, column=0)

#merging plot
class plot_merging(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    tk.Label(self, text="Under construction", font=("Arial", 15)).grid(row=0, column=0)

#run the gui
if __name__ == "__main__":
  app = MainGUI()
  app.mainloop()







