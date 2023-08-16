import tkinter as tk
from tkinter import ttk
from textwrap import dedent
from processing_stills import colors, generate_and_process
from plotting_status import count, dot, bar, pie, plot, uc_plot
from scaling_merging import scaling_job, merging_job
from geo_refine import geometry_refinement
from plot_merging_stats import plot_mergingstat
from processing_xia2 import run_xia2
from scaling_merging_xia2 import merging_xia2
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
    self.config = config(self.notebook, )
    self.stills_process = stills_process(self.notebook, self.config.cluster_option, self.config.file_format_option, self.config.dials_path)
    self.plot_stills = plot_stills(self.notebook)
    self.geo = geo(self.notebook)
    self.scaling = scaling(self.notebook, self.config.cluster_option, self.config.dials_path)
    self.merging = merging(self.notebook, self.config.cluster_option, self.config.dials_path)
    self.plot_merging = plot_merging(self.notebook)
    self.xia2_processing = xia2_processing(self.notebook, self.config.cluster_option, self.config.file_format_option, self.config.dials_path)
    self.xia2_plot_process = xia2_plot_process(self.notebook)
    self.xia2_merging = xia2_merging(self.notebook, self.config.cluster_option, self.config.dials_path)
    self.xia2_merging_plot = xia2_merging_plot(self.notebook)

    #add tabs to the gui
    self.notebook.add(self.config, text="Settings") 
    self.notebook.add(self.stills_process, text="Stills processing")
    self.notebook.add(self.plot_stills, text="Plot processing stat")
    self.notebook.add(self.geo, text="Geometry refinement")
    self.notebook.add(self.scaling, text="Scaling")
    self.notebook.add(self.merging, text="Merging")
    self.notebook.add(self.plot_merging, text="Merging statistics")
    self.notebook.add(self.xia2_processing, text="Xia2 processing")
    self.notebook.add(self.xia2_plot_process, text="Plot xia2 processing")
    self.notebook.add(self.xia2_merging, text="Xia2 merging")
    self.notebook.add(self.xia2_merging_plot, text="Xia2 merging statistics")

    self.notebook.pack()    

#config/setting page
class config(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)

    #file format
    tk.Label(self, text="File format", font=("Arial", 15)).grid(row=0, column=0)
    file_format_list = ["cbf", "h5 master", "h5 palxfel", "nxs"]
    file_format = tk.StringVar(self)
    file_format.set("Select file format")
    file_format_choice = tk.OptionMenu(self, file_format, *file_format_list, command = lambda selected: plot.read_file_format(file_format.get())).grid(row=1, column=0, pady=(0, 10))

    #cluster option
    tk.Label(self, text="Cluster option", font=("Arial", 15)).grid(row=2, column=0)
    cluster_option_list = ["sge", "slurm EuXFEL", "slurm SwissFEL"]
    cluster_option = tk.StringVar(self)
    cluster_option.set("sge")
    cluster_choice = tk.OptionMenu(self, cluster_option, *cluster_option_list, command = lambda selected: plot.read_cluster_option(cluster_option.get())).grid(row=3, column=0, pady=(0, 10))

    #dials source file location
    tk.Label(self, text="Dials source path (only for self-installed dials)", font=("Arial", 15)).grid(row=4, column=0)
    dials_source_path = tk.Entry(self, width=60, font=("Aria", 15))
    dials_source_path.insert(0, "/gpfs/exfel/exp/SPB/202201/p002826/usr/Software/Tiankun/dials_test_conda3/dials")
    dials_source_path.grid(row=5, column=0, pady=(0, 10))
    #make the options available to other classes
    self.cluster_option = cluster_option
    self.file_format_option = file_format
    self.dials_path = dials_source_path

#stills processing tab
class stills_process(tk.Frame):
  def __init__(self, master, cluster_option, file_format, dials_path):
    tk.Frame.__init__(self, master)
    ## Getting phil file
    tk.Label(self, text="Phil file stills", font=("Arial", 15)).grid(row=0, column=0)
    phil_file_stills = tk.Text(self, width=75, height=25, font=("Aria", 15))
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
    phil_file_stills.grid(row=1, column=0, rowspan=5)
    #scroll bar 
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=phil_file_stills.yview)
    scroll.grid(row=1, column=1, rowspan=5, sticky="ns")
    phil_file_stills['yscrollcommand'] = scroll.set
    #data dir
    tk.Label(self, text="Data dir stills", font=("Arial", 15)).grid(row=0, column=2, padx=(20, 0))
    data_folder_stills = tk.Text(self, width=60, height=20, font=("Aria", 15))
    data_folder_stills.grid(row=1, column=2, padx=(20, 0))
    #scroll bar data dir
    scroll= tk.Scrollbar(self, orient="vertical", width=20, elementborderwidth=3, command=data_folder_stills.yview)
    scroll.grid(row=1, column=3, padx=(0, 20), sticky="ns")
    data_folder_stills['yscrollcommand'] = scroll.set
    #process folder
    tk.Label(self, text="Process folder stills", font=("Arial", 15)).grid(row=2, column=2, padx=(20, 0))
    process_folder_stills = tk.Entry(self, width=60, font=("Aria", 15))
    process_folder_stills.grid(row=3, column=2, padx=(20, 0))
    #buttons
    tk.Button(self, text="Submit job", width =12, height=4,font=("Arial", 12), command = lambda: generate_and_process(file_format.get(), data_folder_stills.get("1.0","end").splitlines(), \
    process_folder_stills.get(), cluster_option.get(), phil_file_stills.get("1.0","end"), dials_path.get()).submit_job()).grid(row=6, column=0, pady=20)

#plot tab
class plot_stills(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    tk.Label(self, text="Enter the ABSOLUTE path of prcessing folder\n separate with new line\n can use * or []\n Currently only works for finished jobs", font=("Arial", 15)).grid(row=0, column=0)
    
    check_dir = tk.Text(self, width=90, height=25, font=("Aria", 15))
    check_dir.grid(row=0, column = 1, rowspan=4, columnspan=4)

    #scroll bar 
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=check_dir.yview)
    scroll.grid(row=0, column=5, rowspan=4, sticky="ns")
    check_dir['yscrollcommand'] = scroll.set

    tk.Label(self, text="Plot option \nRecommend stack", font=("Arial", 15)).grid(row=1, column=0)
    option_list = ["single", "stack"]
    plot_name = tk.StringVar(self)
    plot_name.set("stack")
    plot_option = tk.OptionMenu(self, plot_name, *option_list, command = lambda selected: plot.read_option(plot_name.get()))
    plot_option.grid(row=2, column=0)

    tk.Button(self, text="Plot dot", width =12, height=4,font=("Arial", 12), command = lambda: plot.dot(plot_name.get(), check_dir.get("1.0","end").splitlines())).grid(row=6, column=1, pady=20) #convert text to a list
    tk.Button(self, text="Plot bar", width =12, height=4,font=("Arial", 12), command = lambda: plot.bar(plot_name.get(), check_dir.get("1.0","end").splitlines())).grid(row=6, column=2, pady=20)
    tk.Button(self, text="Plot pie", width =12, height=4,font=("Arial", 12), command = lambda: plot.pie(plot_name.get(), check_dir.get("1.0","end").splitlines())).grid(row=6, column=3, pady=20)
    tk.Button(self, text="uc plot", width =12, height =4,font=("Arial", 12), command = lambda: uc_plot(check_dir.get("1.0","end").splitlines(), plot_name.get()).plot_uc()).grid(row=6, column=4, pady=20)

#geo tab
class geo(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    tk.Label(self, text="Phil file geometry refinement", font=("Arial", 15)).grid(row=0, column=0)
    #set default phil file
    phil_file_georefine = tk.Text(self, width=75, height=25, font=("Aria", 15))
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
    phil_file_georefine.grid(row=1, column=0, rowspan=4, columnspan=2)
    #scroll bar 
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=phil_file_georefine.yview)
    scroll.grid(row=1, column=2, rowspan=4, sticky="ns")
    phil_file_georefine['yscrollcommand'] = scroll.set
    #data dir
    tk.Label(self, text="Data dir geo refinement", font=("Arial", 15)).grid(row=1, column=3, padx=20)
    data_folder_georefine = tk.Entry(self, width=60, font=("Aria", 15))
    data_folder_georefine.grid(row=2, column=3, padx=20)
    #processing dir
    tk.Label(self, text="Process folder geo refinement", font=("Arial", 15)).grid(row=3, column=3, padx=20)
    process_folder_georefine = tk.Entry(self, width=60, font=("Aria", 15))
    process_folder_georefine.grid(row=4, column=3, padx=20)
    #buttons
    tk.Button(self, text="Submit georefine job", width =15, height=4,font=("Arial", 12), command = lambda: geometry_refinement(data_folder_georefine.get(), process_folder_georefine.get(),\
    phil_file_georefine.get("1.0","end")).run_job()).grid(row=6, column=0, pady=20)
    tk.Button(self, text="Compare geometry", width =15, height=4,font=("Arial", 12), command = lambda: geometry_refinement(data_folder_georefine.get(), process_folder_georefine.get(),\
    phil_file_georefine.get("1.0","end")).run_compare()).grid(row=6, column=1, pady=20)
     
#scaling tab
class scaling(tk.Frame):
  def __init__(self, master, cluster_option, dials_path):
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
    #scroll bar phil file
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=phil_file_scaling.yview)
    scroll.grid(row=1, column=1, sticky="ns")
    phil_file_scaling['yscrollcommand'] = scroll.set
    #data dir
    tk.Label(self, text="Data dir (stills processing ouputs)", font=("Arial", 15)).grid(row=0, column=2, padx=(20, 0))
    data_folder_scaling = tk.Text(self, width=60, height=20, font=("Aria", 15))
    data_folder_scaling.grid(row=1, column=2, padx=(20, 0))
    #scroll bar data folder
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=data_folder_scaling.yview)
    scroll.grid(row=1, column=3, sticky="ns")
    data_folder_scaling['yscrollcommand'] = scroll.set
    #process folder
    tk.Label(self, text="Process folder scaling", font=("Arial", 15)).grid(row=2, column=2, padx=20)
    process_folder_scaling = tk.Entry(self, width=50, font=("Aria", 15))
    process_folder_scaling.grid(row=3, column=2, padx=20)
    #reference pdb
    tk.Label(self, text="Reference pdb scaling", font=("Arial", 15)).grid(row=2, column=0)
    ref_pdb_scaling = tk.Entry(self, width=50, font=("Aria", 15))
    ref_pdb_scaling.grid(row=3, column=0)
    #tag
    tk.Label(self, text="Sample tag scaling", font=("Arial", 15)).grid(row=4, column=2, padx=20)
    sample_tag_scaling = tk.Entry(self, width=50, font=("Aria", 15))
    sample_tag_scaling.grid(row=5, column=2, padx=20)
    #resolution
    tk.Label(self, text="Resolution scaling", font=("Arial", 15)).grid(row=4, column=0)
    resolution_scaling = tk.Entry(self, width=50, font=("Aria", 15))
    resolution_scaling.grid(row=5, column=0)
    #buttons
    tk.Button(self, text="Submit scaling job", width =12, height=4,font=("Arial", 12), command = lambda: scaling_job(data_folder_scaling.get("1.0","end").splitlines(), \
    process_folder_scaling.get(), cluster_option.get(), phil_file_scaling.get("1.0","end"), sample_tag_scaling.get(), resolution_scaling.get(), ref_pdb_scaling.get(), \
    dials_path.get()).submit_job()).grid(row=6, column=0, pady=20)

#merging tab
class merging(tk.Frame):
  def __init__(self, master, cluster_option, dials_path):
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
    #scroll bar phil file
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=phil_file_merging.yview)
    scroll.grid(row=1, column=1, sticky="ns")
    phil_file_merging['yscrollcommand'] = scroll.set
    #data dir
    tk.Label(self, text="Data dir (scaling ouputs)", font=("Arial", 15)).grid(row=0, column=2, padx=(20, 0))
    data_folder_merging = tk.Text(self, width=60, height=20, font=("Aria", 15))
    data_folder_merging.grid(row=1, column=2, padx=(20, 0))
    #process folder
    tk.Label(self, text="Process folder merging", font=("Arial", 15)).grid(row=2, column=2, padx=20)
    process_folder_merging = tk.Entry(self, width=50, font=("Aria", 15))
    process_folder_merging.grid(row=3, column=2, padx=20)
    #scroll bar data folder
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=data_folder_merging.yview)
    scroll.grid(row=1, column=3, sticky="ns")
    data_folder_merging['yscrollcommand'] = scroll.set
    #reference pdb
    tk.Label(self, text="Reference pdb merging", font=("Arial", 15)).grid(row=2, column=0)
    ref_pdb_merging = tk.Entry(self, width=50, font=("Aria", 15))
    ref_pdb_merging.grid(row=3, column=0)
    #tag
    tk.Label(self, text="Sample tag merging", font=("Arial", 15)).grid(row=4, column=2, padx=20)
    sample_tag_merging = tk.Entry(self, width=50, font=("Aria", 15))
    sample_tag_merging.grid(row=5, column=2, padx=20)
    #resolution
    tk.Label(self, text="Resolution merging", font=("Arial", 15)).grid(row=4, column=0)
    resolution_merging = tk.Entry(self, width=50, font=("Aria", 15))
    resolution_merging.grid(row=5, column=0)
    #buttons
    tk.Button(self, text="Submit merging job", width =14, height=4,font=("Arial", 12), command = lambda: merging_job(data_folder_merging.get("1.0","end").splitlines(), \
    process_folder_merging.get(), cluster_option.get(), phil_file_merging.get("1.0","end"), sample_tag_merging.get(), resolution_merging.get(), ref_pdb_merging.get(), \
    dials_path.get()).submit_job()).grid(row=6, column=0, pady=20)

#merging plot
class plot_merging(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    
    #merging dir
    tk.Label(self, text="merging dir (absolute path)", font=("Arial", 15)).grid(row=0, column=0)
    merging_dir = tk.Text(self, width=100, height=25, font=("Aria", 15))
    merging_dir.grid(row=1, column=0, rowspan=5)
    #scroll bar phil file
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=merging_dir.yview)
    scroll.grid(row=1, column=1, rowspan=5, sticky="ns")
    merging_dir['yscrollcommand'] = scroll.set

    #plot_1 option
    tk.Label(self, text="Plot stats 1", font=("Arial", 15)).grid(row=1, column=2, padx=20)
    stats_1_list = ["CC1/2", "Rsplit", "I/sigma", "Multiplicity", "Completeness"]
    stats_1 = tk.StringVar(self)
    stats_1.set("CC1/2")
    stats_1_choice = tk.OptionMenu(self, stats_1, *stats_1_list, command = lambda selected: plot.read_merging_stats(stats_1.get())).grid(row=2, column=2, padx=20)

    #plot_2 option
    tk.Label(self, text="Plot stats 2", font=("Arial", 15)).grid(row=3, column=2, padx=20)
    stats_2_list = ["CC1/2", "Rsplit", "I/sigma", "Multiplicity", "Completeness"]
    stats_2 = tk.StringVar(self)
    stats_2.set("Multiplicity")
    stats_2_choice = tk.OptionMenu(self, stats_2, *stats_2_list, command = lambda selected: plot.read_merging_stats(stats_2.get())).grid(row=4, column=2, padx=20)

    #button
    tk.Button(self, text="Plot merging stats", width =15, height=4,font=("Arial", 12), command = lambda: \
    plot_mergingstat(merging_dir.get("1.0","end").splitlines()).plot_stats(stats_1.get(), stats_2.get())).grid(row=6, column=0, pady=20)

class xia2_processing(tk.Frame):
  def __init__(self, master, cluster_option, file_format, dials_path):
    tk.Frame.__init__(self, master)
    tk.Label(self, text="Enter the ABSOLUTE path of the data dir", font=("Arial", 15)).grid(row=0, column=0)
    submit_file_xia2 = tk.Text(self, width=75, height=25, font=("Aria", 15))
    default_submit_file_xia2 = dedent("""\
                                      reference_geometry=None \\
                                      mask=None \\
                                      unit_cell=96.4,96.4,96.4,90,90,90 \\
                                      space_group=P213 \\
                                      max_lattices=10 \\
                                      reference=None \\
                                      min_spot_size=2 \\
                                      absolute_length_tolerance=3.0 \\
                                      absolute_angle_tolerance=5.0 \\
                                      steps=find_spots+index+integrate""")
    submit_file_xia2.insert(tk.END, default_submit_file_xia2)
    submit_file_xia2.grid(row=1, column=0, rowspan=5)
    #scroll bar 
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=submit_file_xia2.yview)
    scroll.grid(row=1, column=1, rowspan=5, sticky="ns")
    submit_file_xia2['yscrollcommand'] = scroll.set
    #data dir
    tk.Label(self, text="Data dir xia2", font=("Arial", 15)).grid(row=0, column=2, padx=(20, 0))
    data_folder_xia2 = tk.Text(self, width=60, height=20, font=("Aria", 15))
    data_folder_xia2.grid(row=1, column=2, padx=(20, 0))
    #scroll bar data dir
    scroll= tk.Scrollbar(self, orient="vertical", width=20, elementborderwidth=3, command=data_folder_xia2.yview)
    scroll.grid(row=1, column=3, padx=(0, 20), sticky="ns")
    data_folder_xia2['yscrollcommand'] = scroll.set
    #process folder
    tk.Label(self, text="Process folder xia2", font=("Arial", 15)).grid(row=2, column=2, padx=(20, 0))
    process_folder_xia2 = tk.Entry(self, width=60, font=("Aria", 15))
    process_folder_xia2.grid(row=3, column=2, padx=(20, 0))
    #buttons
    tk.Button(self, text="Submit job", width =12, height=4,font=("Arial", 12), command = lambda: run_xia2(file_format.get(), data_folder_xia2.get("1.0","end").splitlines(), \
    process_folder_xia2.get(), cluster_option.get(), submit_file_xia2.get("1.0","end"), dials_path.get()).submit_xia2()).grid(row=6, column=0, pady=20)

class xia2_plot_process(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    tk.Label(self, text="Under constrction", font=("Arial", 15)).grid(row=0, column=0)

class xia2_merging(tk.Frame):
  def __init__(self, master, cluster_option, dials_path):
    tk.Frame.__init__(self, master)
    tk.Label(self, text="scaling/merging submit file (normally empty)", font=("Arial", 15)).grid(row=0, column=0)
    sbumit_file_merging = tk.Text(self, width=75, height=22, font=("Aria", 15))
    default_sbumit_file_merging = dedent("""\
                                        reference=None \\ 
                                        d_min=None \\""")
    sbumit_file_merging.insert(tk.END, default_sbumit_file_merging)
    sbumit_file_merging.grid(row=1, column=0)
    #scroll bar phil file
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=sbumit_file_merging.yview)
    scroll.grid(row=1, column=1, sticky="ns")
    sbumit_file_merging['yscrollcommand'] = scroll.set
    #data dir
    tk.Label(self, text="Data dir", font=("Arial", 15)).grid(row=0, column=2, padx= (20, 0))
    data_folder_merging = tk.Text(self, width=60, height=22, font=("Aria", 15))
    data_folder_merging.grid(row=1, column=2, padx=(20, 0))
    #scroll bar data folder
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=data_folder_merging.yview)
    scroll.grid(row=1, column=3, sticky="ns")
    data_folder_merging['yscrollcommand'] = scroll.set
    #process folder
    tk.Label(self, text="Process folder", font=("Arial", 15)).grid(row=2, column=0)
    process_folder_merging = tk.Entry(self, width=50, font=("Aria", 15))
    process_folder_merging.grid(row=3, column=0)
    #tag
    tk.Label(self, text="Sample tag merging", font=("Arial", 15)).grid(row=2, column=2, padx=(20, 0))
    sample_tag_merging = tk.Entry(self, width=50, font=("Aria", 15))
    sample_tag_merging.grid(row=3, column=2, padx=(20, 0))
    #buttons
    tk.Button(self, text="Submit xia2 merging job", width =16, height=4,font=("Arial", 12), command = lambda: merging_xia2(data_folder_merging.get("1.0","end").splitlines(), \
    process_folder_merging.get(), cluster_option.get(), sample_tag_merging.get(), sbumit_file_merging.get("1.0","end"), dials_path.get()).submit_xia2_merging()).grid(row=6, column=0, pady=20)

class xia2_merging_plot(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    tk.Label(self, text="Under constrction", font=("Arial", 15)).grid(row=0, column=0) 

#run the gui
if __name__ == "__main__":
  app = MainGUI()
  app.mainloop()







