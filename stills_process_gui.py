import tkinter as tk
from tkinter import ttk
from processing_stills import colors, generate_and_process
from plotting_status import count, dot, bar, pie, plot
from scaling_merging import scaling_job, merging_job
"""
This is a gui for submit dials stills processing
and merging jobs at DLS 
may need python 3.8 or later
"""

#set up the gui
class MainGUI(tk.Tk):
  def __init__(self):
    tk.Tk.__init__(self) #this is important, call super class ' __init__'
    self.title("Processing and plotting gui")
    tabs = ttk.Notebook(self)
    tab_still = ttk.Frame(tabs)
    tab_plot = ttk.Frame(tabs)
    tab_scaling = ttk.Frame(tabs)
    tab_merging = ttk.Frame(tabs)
    tabs.add(tab_still, text="Stills processing")
    tabs.add(tab_plot, text="Plot processing stat")
    tabs.add(tab_scaling, text="Scaling")
    tabs.add(tab_merging, text="Merging")
    tabs.pack()

    """stills processing tab"""
    tk.Label(tab_still, text="Phil file stills", font=("Arial", 15)).grid(row=0, column=0)
    phil_file_stills = tk.Text(tab_still, width=75, height=20)
    #phil_file.insert(tk.END, "test")
    phil_file_stills.grid(row=1, column=0)
    #data dir
    tk.Label(tab_still, text="Data dir stills", font=("Arial", 15)).grid(row=0, column=1)
    data_folder_stills = tk.Text(tab_still, width=50, height=15)
    data_folder_stills.grid(row=1, column=1)
    #process folder
    tk.Label(tab_still, text="Process folder stills", font=("Arial", 15)).grid(row=2, column=1)
    process_folder_stills = tk.Entry(tab_still, width=50)
    process_folder_stills.grid(row=3, column=1)
    #file format
    tk.Label(tab_still, text="File format", font=("Arial", 15)).grid(row=0, column=2)
    file_format_list = ["cbf", "h5", "nxs"]
    file_format = tk.StringVar(tab_still)
    file_format.set("Select file format")
    file_format_choice = tk.OptionMenu(tab_still, file_format, *file_format_list, command = lambda selected: plot.read_file_format(file_format.get())).grid(row=1, column=2)
    #queue option
    tk.Label(tab_still, text="Queue option", font=("Arial", 15)).grid(row=2, column=2)
    queue_option_list = ["low", "medium", "high"]
    queue_option = tk.StringVar(self)
    queue_option.set("medium")
    queue_choice = tk.OptionMenu(tab_still, queue_option, *queue_option_list, command = lambda selected: plot.read_queue_option(queue_option.get())).grid(row=3, column=2)
    #buttons
    tk.Button(tab_still, text="Submit job", width =12, height=4,font=("Arial", 12), command = lambda: generate_and_process(file_format.get(), data_folder_stills.get("1.0","end").splitlines(), process_folder_stills.get(), queue_option.get(), phil_file_stills.get("1.0","end")).submit_job()).grid(row=4, column=0)

    """plot tab"""
    tk.Label(tab_plot, text="Enter the ABSOLUTE path of prcessing folder\n separate with new line\n can use * or []\n Currently only works for finished jobs", font=("Arial", 15)).grid(row=0, column=0)
    
    check_dir = tk.Text(tab_plot, width=75, height=20)
    check_dir.grid(row=0, column = 1)

    option_list = ["single", "stack"]
    plot_name = tk.StringVar(self)
    plot_name.set("Select plot option")
    plot_option = tk.OptionMenu(tab_plot, plot_name, *option_list, command = lambda selected: plot.read_option(plot_name.get()))
    plot_option.grid(row=0, column=2)

    tk.Button(tab_plot, text="Plot dot", width =12, height=4,font=("Arial", 12), command = lambda: plot.dot(plot_name.get(), check_dir.get("1.0","end").splitlines())).grid(row=2, column=0) #convert text to a list
    tk.Button(tab_plot, text="Plot bar", width =12, height=4,font=("Arial", 12), command = lambda: plot.bar(plot_name.get(), check_dir.get("1.0","end").splitlines())).grid(row=2, column=1)
    tk.Button(tab_plot, text="Plot pie", width =12, height=4,font=("Arial", 12), command = lambda: plot.pie(plot_name.get(), check_dir.get("1.0","end").splitlines())).grid(row=2, column=2)
    #tk.Button(tab_plot, text="Plot bar realtime", width =12, height =4, font=("Arial", 12), command = lambda: plot.real_time_bar(plot_name.get(), check_dir.get("1.0","end").splitlines())).grid(row=2, column=3)

    """scaling tab"""
    tk.Label(tab_scaling, text="Phil file scaling. DO NOT forger to add the ref pdb", font=("Arial", 15)).grid(row=0, column=0)
    phil_file_scaling = tk.Text(tab_scaling, width=75, height=20)
    phil_file_scaling.insert(tk.END, """input.experiments_suffix=_integrated.expt
input.reflections_suffix=_integrated.refl
output.prefix=ampc_apo_1_1.7A
dispatch.step_list=input balance model_scaling modify filter errors_premerge scale postrefine statistics_unitcell statistics_beam model_statistics statistics_resolution
input.parallel_file_load.method=uniform
filter.outlier.min_corr=0.1
filter.algorithm=unit_cell
filter.unit_cell.value.relative_length_tolerance=0.03
select.algorithm=significance_filter
select.significance_filter.sigma=0.1
scaling.model=
scaling.resolution_scalar=0.95
scaling.mtz.mtz_column_F=I-obs
merging.d_min=1.7
merging.merge_anomalous=True
postrefinement.enable=True
output.do_timing=True
output.save_experiments_and_reflections=True""")
    phil_file_scaling.grid(row=1, column=0)
    #data dir
    tk.Label(tab_scaling, text="Data dir scaling", font=("Arial", 15)).grid(row=0, column=1)
    data_folder_scaling = tk.Text(tab_scaling, width=50, height=15)
    data_folder_scaling.grid(row=1, column=1)
    #process folder
    tk.Label(tab_scaling, text="Process folder scaling", font=("Arial", 15)).grid(row=2, column=1)
    process_folder_scaling = tk.Entry(tab_scaling, width=50)
    process_folder_scaling.grid(row=3, column=1)
    #reference pdb
    """
    tk.Label(tab_scaling, text="reference pdb scaling", font=("Arial", 15)).grid(row=4, column=1)
    ref_pdb_scaling = tk.Entry(tab_scaling, width=50)
    ref_pdb_scaling.grid(row=5, column=1)
    """
    #buttons
    tk.Button(tab_scaling, text="Submit scaling job", width =12, height=4,font=("Arial", 12), command = lambda: scaling_job(data_folder_scaling.get("1.0","end").splitlines(), process_folder_scaling.get(), queue_option.get(), phil_file_scaling.get("1.0","end")).submit_job()).grid(row=6, column=0)

    """merging tab"""
    tk.Label(tab_merging, text="Phil file merging. DO NOT forger to add the ref pdb", font=("Arial", 15)).grid(row=0, column=0)
    phil_file_merging = tk.Text(tab_merging, width=75, height=20)
    phil_file_merging.insert(tk.END, """input.experiments_suffix=.expt
input.reflections_suffix=.refl
output.prefix=ampc_apo_2_2.4A
dispatch.step_list=input model_scaling statistics_unitcell statistics_beam model_statistics statistics_resolution group errors_merge statistics_intensity merge statistics_intensity_cxi
input.parallel_file_load.method=uniform
scaling.model=
scaling.resolution_scalar=0.95
scaling.mtz.mtz_column_F=I-obs
statistics.n_bins=20
merging.d_min=2.4
merging.merge_anomalous=True
merging.error.model=ev11
output.do_timing=True
""")
    phil_file_merging.grid(row=1, column=0)
    #data dir
    tk.Label(tab_merging, text="Data dir", font=("Arial", 15)).grid(row=0, column=1)
    data_folder_merging = tk.Text(tab_merging, width=50, height=15)
    data_folder_merging.grid(row=1, column=1)
    #process folder
    tk.Label(tab_merging, text="Process folder", font=("Arial", 15)).grid(row=2, column=1)
    process_folder_merging = tk.Entry(tab_merging, width=50)
    process_folder_merging.grid(row=3, column=1)
    #reference pdb
    """
    tk.Label(tab_merging, text="reference pdb merging", font=("Arial", 15)).grid(row=4, column=1)
    ref_pdb_merging = tk.Entry(tab_merging, width=50)
    ref_pdb_merging.grid(row=5, column=1)
    """
    #buttons
    tk.Button(tab_merging, text="Submit scaling job", width =12, height=4,font=("Arial", 12), command = lambda: merging_job(data_folder_merging.get("1.0","end").splitlines(), process_folder_merging.get(), queue_option.get(), phil_file_merging.get("1.0","end")).submit_job()).grid(row=6, column=0)

#run the gui
if __name__ == "__main__":
  app = MainGUI()
  app.mainloop()







