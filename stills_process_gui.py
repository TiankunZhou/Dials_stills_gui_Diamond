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
from tkinter import filedialog #for folder selection
import os

"""
This is a gui for submit dials stills processing
and merging jobs at DLS 
may need python 3.8 or later
"""

#Functions for select folder
#Selecet dir and put the absolute path to the entry
def select_folder(entry:str):
  folder_path = filedialog.askdirectory()
  if folder_path:
    entry.delete(0, tk.END)  # Clear the Entry
    entry.insert(0, folder_path)
  else:
    print("No folder selected")

#Select/show contented folder in the selected folder
def folder_content_folder(listbox:str):
  folder_path = filedialog.askdirectory()  # Open a folder selection dialog
  if folder_path:
    listbox.delete(1.0, tk.END)  # Clear the Listbox
    for item in os.listdir(folder_path):
      full_path = os.path.join(folder_path, item)
      if os.path.isdir(full_path):
        folders = f"{full_path}\n"
        listbox.insert(tk.END, folders)  # Insert folder contents (folder) into Listbox
  else:
    print("No folder selected")

#add single folder in text box
def add_folder_textbox(listbox:str):
  folder_path = filedialog.askdirectory()
  if folder_path:
    #listbox.delete(1, tk.END)  # Clear the Entry
    listbox.insert(tk.END, f"{folder_path}\n")
  else:
    print("No folder selected")

#Select/show contented file in the selected folder in text box:
def folder_content_file(listbox:str):
  folder_path = filedialog.askdirectory()  # Open a folder selection dialog
  if folder_path:
    listbox.delete(1.0, tk.END)  # Clear the Listbox
    for item in os.listdir(folder_path):
      full_path = os.path.join(folder_path, item)
      if os.path.isfile(full_path):
        files = f"{full_path}\n"
        listbox.insert(tk.END, files)  # Insert folder contents (files) into Listbox
  else:
    print("No folder selected")

#Select/show contented file in the selected folder as drop down menu:
def folder_content_file_drop():
  listfile = []
  folder_path = filedialog.askdirectory()  # Open a folder selection dialog
  if folder_path:
    listbox.delete(1.0, tk.END)  # Clear the Listbox
    for item in os.listdir(folder_path):
      full_path = os.path.join(folder_path, item)
      if os.path.isfile(full_path):
        files = f"{full_path}\n"
        return listfile # return the file list for drop down menu
  else:
    print("No folder selected")

#Select one file:
def select_file(entry:str):
  file_path = filedialog.askopenfilename()
  if file_path:
    entry.delete(0, tk.END)  # Clear the Entry
    entry.insert(0, file_path)
  else:
    print("No files selected.")


#set up the gui
class MainGUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self) #this is important, call super class ' __init__'
        self.frame = None
        tabs(self).pack(fill='both', expand=True) #pack tabs from class tab, with fill='both', expand=True, it will allow changing of the widget
        self.title("Processing and plotting gui")
        self.resizable(True, True)
        #default size if the gui, can be changed if it is too small
        self.geometry("1800x900")

#set up tabs
class tabs(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    self.notebook = ttk.Notebook(self)
    
    #set up tabs using classes below; orders is very important, or it will not work
    self.config = config(self.notebook)
    self.stills_process = stills_process(self.notebook, self.config.cluster_option, self.config.file_format_option, self.config.dials_path, \
                                         self.config.output_dir, self.config.cpu_diamond_processing)
    self.plot_stills = plot_stills(self.notebook)
    self.geo = geo(self.notebook, self.config.output_dir)
    self.scaling = scaling(self.notebook, self.config.cluster_option, self.config.dials_path, self.config.output_dir, self.config.cpu_diamond_scaling)
    self.merging = merging(self.notebook, self.config.cluster_option, self.config.dials_path, self.config.output_dir, self.config.cpu_diamond_scaling)
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

    self.notebook.pack(fill='both', expand=True) #pack tabs, with fill='both', expand=True, it will allow changing of the widget

#config/setting page
class config(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)

    #General gui settings
    tk.Label(self, text="General GUI settings", font=("Arial", 18)).grid(row=0, column=1, padx=(50, 0), pady=(0, 20), sticky="EW")
    
    #file format
    tk.Label(self, text="File format", font=("Arial", 15)).grid(row=1, column=1, sticky="EW")
    file_format_list = ["cbf", "h5 master", "h5 palxfel", "nxs"]
    file_format = tk.StringVar(self)
    file_format.set("Select file format")
    file_format_choice = tk.OptionMenu(self, file_format, *file_format_list, command = lambda selected: plot.read_file_format(file_format.get())).grid(row=2, column=1, pady=(0, 10))

    #cluster option
    tk.Label(self, text="Cluster option", font=("Arial", 15)).grid(row=3, column=1, sticky="EW")
    cluster_option_list = ["slurm Diamond", "slurm EuXFEL", "slurm SwissFEL", "condor"]
    cluster_option = tk.StringVar(self)
    cluster_option.set("slurm Diamond")
    cluster_choice = tk.OptionMenu(self, cluster_option, *cluster_option_list, command = lambda selected: plot.read_cluster_option(cluster_option.get())).grid(row=4, column=1, pady=(0, 10))

    #dials source file location
    tk.Label(self, text="Dials source path (only for self-installed dials)", font=("Arial", 15)).grid(row=5, column=1, sticky="EW")
    dials_source_path = tk.Entry(self, width=60, font=("Aria", 15))
    dials_source_path.insert(0, "/dls/science/users/tbf48622/dials_dev_update_test/dials")
    dials_source_path.grid(row=6, column=1, pady=(0, 10), sticky="EW")

    #select number of cpus required for Diamond slurm - processing
    tk.Label(self, text="Number of cpu required for Diamond Slurm for data processing", font=("Arial", 15)).grid(row=7, column=1, sticky="EW")
    dials_diamond_processing = tk.Entry(self, width=30, font=("Aria", 15), justify="center")
    dials_diamond_processing.insert(0, "70")
    dials_diamond_processing.grid(row=8, column=1, pady=(0, 10), sticky="EW")

    #select number of cpus required for Diamond slurm - scaling and merging
    tk.Label(self, text="Number of cpu required for Diamond Slurm for scaling and merging", font=("Arial", 15)).grid(row=9, column=1, sticky="EW")
    dials_diamond_scaling = tk.Entry(self, width=30, font=("Aria", 15), justify="center")
    dials_diamond_scaling.insert(0, "10")
    dials_diamond_scaling.grid(row=10, column=1, pady=(0, 10), sticky="EW")

    #Overall data processing and scaling/merging settings
    tk.Label(self, text="General processing and scaling/merging settings", font=("Arial", 18)).grid(row=0, column=2, padx=(75, 0), pady=(0, 20), sticky="EW")
    
    #out put directory
    tk.Label(self, text="Output directory", font=("Arial", 15)).grid(row=1, column=2, padx=(75, 0), sticky="EW")
    output_dir = tk.Entry(self, width=60, font=("Aria", 15), justify="center")
    output_dir.insert(0, "Please select output folder")
    output_dir.grid(row=2, column=2, padx=(75, 0), pady=(0, 10), sticky="EW")
    
    # add button for selectiong folder and display it in the Entry
    tk.Button(self, text="select folder", width =12, height=1,font=("Arial", 12), command = lambda:select_folder(output_dir)).grid(row=2, column=3, padx=(10, 0), pady=(0, 10), sticky="W")

    #give weight to extra columns, to make the widgets at the center
    self.grid_columnconfigure([0, 4], weight=1)
    self.grid_columnconfigure([1, 2, 3], weight=4)
 
    #make the options available to other classes
    self.cluster_option = cluster_option
    self.file_format_option = file_format
    self.dials_path = dials_source_path
    self.cpu_diamond_processing = dials_diamond_processing
    self.cpu_diamond_scaling = dials_diamond_scaling
    self.output_dir = output_dir


#stills processing tab
class stills_process(tk.Frame):
  def __init__(self, master, cluster_option, file_format, dials_path, output_dir, cpu_processing):
    tk.Frame.__init__(self, master)
    #Processing settings
    tk.Label(self, text="Stills Processing Settings", font=("Arial", 18)).grid(row=0, column=1, pady=(0, 15), sticky="EW")
    
    #reference geometry:
    tk.Label(self, text="Reference Geomerty path", font=("Arial", 15)).grid(row=1, column=1, sticky="EW")
    reference_geometry = tk.Entry(self, width=60,font=("Aria", 15), justify="center")
    reference_geometry.grid(row=2, column=1, pady=(0, 10), sticky="ew")
    tk.Button(self, text="select geometry", width =12, height=1,font=("Arial", 12), command = lambda:select_file(reference_geometry)).grid(row=2, column=2, padx=(5, 0), pady=(0, 10), sticky="W")
    
    #Mask
    tk.Label(self, text="mask path", font=("Arial", 15)).grid(row=3, column=1, sticky="ew")
    mask = tk.Entry(self, width=60,font=("Aria", 15), justify="center")
    mask.grid(row=4, column=1, pady=(0, 10), sticky="ew")
    tk.Button(self, text="select mask", width =12, height=1,font=("Arial", 12), command = lambda:select_file(mask)).grid(row=4, column=2, padx=(5, 0), pady=(0, 10), sticky="W")
   
    #min spot size
    tk.Label(self, text="Min spot size", font=("Arial", 15)).grid(row=5, column=1, sticky="ew")
    min_spot_size= tk.Entry(self, width=60,font=("Aria", 15), justify="center")
    min_spot_size.insert(0, "2")
    min_spot_size.grid(row=6, column=1, pady=(0, 10), sticky="ew")
    
    #max spot size
    tk.Label(self, text="Max spot size", font=("Arial", 15)).grid(row=7, column=1, sticky="ew")
    max_spot_size= tk.Entry(self, width=60,font=("Aria", 15), justify="center")
    max_spot_size.insert(0, "50")
    max_spot_size.grid(row=8, column=1, pady=(0, 10), sticky="ew")
    
    #resolution
    tk.Label(self, text="Resolution", font=("Arial", 15)).grid(row=9, column=1, sticky="ew")
    resolution = tk.Entry(self, width=60,font=("Aria", 15), justify="center")
    resolution.insert(0, "1.5")
    resolution.grid(row=10, column=1, pady=(0, 10), sticky="ew")
   
    #space group
    tk.Label(self, text="Space group", font=("Arial", 15)).grid(row=11, column=1, sticky="ew")
    space_group = tk.Entry(self, width=60,font=("Aria", 15), justify="center")
    space_group.insert(0, "P212121")
    space_group.grid(row=12, column=1, pady=(0, 10), sticky="ew")
    
    #unit cell parameters
    tk.Label(self, text="Unit cell", font=("Arial", 15)).grid(row=13, column=1, sticky="ew")
    unit_cell = tk.Entry(self, width=60,font=("Aria", 15), justify="center")
    unit_cell.insert(0, "45.2, 45.7, 118.3, 90, 90, 90")
    unit_cell.grid(row=14, column=1, pady=(0, 10), sticky="ew")
    
    #composite output
    tk.Label(self, text="Composite output", font=("Arial", 15)).grid(row=15, column=1, sticky="ew")
    composite_list = ["yes", "no"]
    composite = tk.StringVar(self)
    composite.set("yes")
    compisite_choice = tk.OptionMenu(self, composite, *composite_list, command = lambda selected: plot.read_composite(composite.get())).grid(row=16, column=1, pady=(0, 10))
    
    #output all files
    tk.Label(self, text="Output all files", font=("Arial", 15)).grid(row=17, column=1, sticky="ew")
    output_all_list = ["yes", "no"]
    output_all = tk.StringVar(self)
    output_all.set("no")
    output_all_choice = tk.OptionMenu(self, output_all, *output_all_list, command = lambda selected: plot.read_all_output(output_all.get())).grid(row=18, column=1, pady=(0, 10))
    
    # Extra phil file settings
    tk.Label(self, text="Extra phil file settings", font=("Arial", 15)).grid(row=19, column=1, sticky="ew")
    phil_file_extra = tk.Text(self, width=60, height=5, font=("Aria", 15))
    default_phil_processing = dedent("""\
                                  indexing.stills.indexer=stills
                                  indexing.stills.method_list=fft1d real_space_grid_search
                                  indexing.multiple_lattice_search.max_lattices=10 """)
    phil_file_extra.insert(tk.END, default_phil_processing)
    phil_file_extra.grid(row=20, column=1, rowspan=2, sticky="ew")
    
    #scroll bar 
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=phil_file_extra.yview)
    scroll.grid(row=20, column=2, rowspan=2, sticky="wns")
    phil_file_extra['yscrollcommand'] = scroll.set
    
    #data dir and sample tag
    tk.Label(self, text="Select data dir and sample tag", font=("Arial", 18)).grid(row=0, column=3, columnspan=2, padx=(5, 0), pady=(0, 15), sticky="ew")
    
    #data dir
    tk.Label(self, text="Data dir stills", font=("Arial", 15)).grid(row=1, column=3, columnspan=2, padx=(5, 0), sticky="ew")
    data_folder_stills = tk.Text(self, width=60, height=25, font=("Aria", 15))
    data_folder_stills.grid(row=3, column=3, rowspan=16, columnspan=2, padx=(5, 0), pady=(0, 10), sticky="ew")
    
    #select data dir
    tk.Button(self, text="Select all sub-folder(s)", width =16, height=1,font=("Arial", 12), command = lambda:folder_content_folder(data_folder_stills)).grid(row=2, column=3, padx=(5, 0), pady=(0, 5))
    tk.Button(self, text="Add a single folder", width =16, height=1,font=("Arial", 12), command = lambda: add_folder_textbox(data_folder_stills)).grid(row=2, column=4, padx=(5, 0), pady=(0, 5))
    
    #scroll bar data dir
    scroll= tk.Scrollbar(self, orient="vertical", width=20, elementborderwidth=3, command=data_folder_stills.yview)
    scroll.grid(row=3, column=5, rowspan=16, padx=(0, 20), pady=(0, 10), sticky="wns")
    data_folder_stills['yscrollcommand'] = scroll.set
    
    #Sample tags
    tk.Label(self, text="Sample tag", font=("Arial", 15)).grid(row=20, column=3, columnspan=2, padx=(5, 0), sticky="ew")
    sample_tag = tk.Entry(self, width=60, font=("Aria", 15), justify="center")
    sample_tag.grid(row=21, column=3, padx=(5, 0), pady=(0, 10), columnspan=2, sticky="ew")
    
    #give weight to extra columns, to make the widgets at the center
    self.grid_columnconfigure([0, 2, 4, 5, 6], weight=1)
    self.grid_columnconfigure([1, 3], weight=4)
    
    #buttons for job submission
    tk.Button(self, text="Submit job", width =12, height=3,font=("Arial", 12), command = lambda: generate_and_process(file_format=file_format.get(), \
    data_dir=data_folder_stills.get("1.0","end").splitlines(), processing_dir=output_dir.get(), sample_tag=sample_tag.get(), cluster_option=cluster_option.get(), \
    geom=reference_geometry.get(), mask=mask.get(), min_spot_size=min_spot_size.get(), max_spot_size=max_spot_size.get(), resolution=resolution.get(), \
    space_group=space_group.get(), unit_cell=unit_cell.get(), phil_file_extra=phil_file_extra.get("1.0","end"), cpu_diamond_processing=cpu_processing.get(), \
    composite=composite.get(), output_all=output_all.get(), dials_path=dials_path.get()).submit_job()).grid(row=22, column=1, columnspan=1, pady=20)


#plot tab
class plot_stills(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)
    tk.Label(self, text="Plot data processing statistic and unit cell distuibution \n(UC only works when processing finished)\nChoose the folder that contains \"debug\" folder", \
             font=("Arial", 18)).grid(row=0, column=2, pady=(0, 15))
    
    #select/show the processing folder
    check_dir = tk.Text(self, width=90, height=25, font=("Aria", 15))
    check_dir.grid(row=2, column=1, columnspan=3, pady=(0, 10), sticky="ew")
    
    #select button
    tk.Button(self, text="Select all data \nprocessing sub-folder(s)", width =18, height=2,font=("Arial", 12), \
              command = lambda:folder_content_folder(check_dir)).grid(row=1, column=1, padx=(5, 0), pady=(0, 5), sticky="e")
    tk.Button(self, text="Add a data \nprocessing folder", width =18, height=2,font=("Arial", 12), \
              command = lambda: add_folder_textbox(check_dir)).grid(row=1, column=2, padx=(5, 0), pady=(0, 5), sticky="e")
    
    #scroll bar 
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=check_dir.yview)
    scroll.grid(row=2, column=4, padx=(0, 20), pady=(0, 10), sticky="wns")
    check_dir['yscrollcommand'] = scroll.set
  
    #Choose plot data one-by-one or stack
    tk.Label(self, text="Plot option, recommend stack", font=("Arial", 15)).grid(row=3, column=2)
    option_list = ["single", "stack"]
    plot_name = tk.StringVar(self)
    plot_name.set("stack")
    plot_option = tk.OptionMenu(self, plot_name, *option_list, command = lambda selected: plot.read_option(plot_name.get()))
    plot_option.grid(row=4, column=2, pady=(0, 25))

    #give weight to extra columns, to make the widgets at the center
    self.grid_columnconfigure([0, 4], weight=1)
    self.grid_columnconfigure([1, 2, 3], weight=4)

    #plot options and buttons
    tk.Button(self, text="Plot dot", width =16, height=2,font=("Arial", 12), \
              command = lambda: plot.dot(plot_name.get(), check_dir.get("1.0","end").splitlines())).grid(row=5, column=1, pady=(0, 5)) #convert text to a list
    tk.Button(self, text="Plot bar", width =16, height=2,font=("Arial", 12), \
              command = lambda: plot.bar(plot_name.get(), check_dir.get("1.0","end").splitlines())).grid(row=5, column=2, pady=(0, 5))
    tk.Button(self, text="uc plot", width =16, height =2,font=("Arial", 12), \
              command = lambda: uc_plot(check_dir.get("1.0","end").splitlines(), plot_name.get()).plot_uc()).grid(row=5, column=3, pady=(0, 5))
    #tk.Button(self, text="Plot pie", width =12, height=4,font=("Arial", 12), \
    #          command = lambda: plot.pie(plot_name.get(), check_dir.get("1.0","end").splitlines())).grid(row=6, column=3, pady=20)


#geo tab
class geo(tk.Frame):
  def __init__(self, master, output_dir):
    tk.Frame.__init__(self, master)
    
    #set title
    tk.Label(self, text="Geometry refinementm run at login node\nDo not touch the GUI when job is running", font=("Arial", 18)).grid(row=0, column=2, pady=(0, 15))

    #select processing folder
    tk.Label(self, text="Processing Data dir (give one folder or manually add * for multiple folders)", font=("Arial", 15)).grid(row=1, column=2, pady=(0, 10))
    data_folder_georefine = tk.Entry(self, width=90, font=("Aria", 15))
    data_folder_georefine.grid(row=3, column=1, columnspan=3, pady=(0, 25), sticky=("we"))

    """
    #scroll bar 1
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=data_folder_georefine.yview)
    scroll.grid(row=3, column=4, pady=(0, 25), sticky="wns")
    data_folder_georefine['yscrollcommand'] = scroll.set
    """

    #Select folder button
    #tk.Button(self, text="Select all data \nprocessing sub-folder(s)", width =18, height=2,font=("Arial", 12), \
    #          command = lambda:folder_content_folder(data_folder_georefine)).grid(row=2, column=1, padx=(5, 0), pady=(0, 5), sticky="e")
    tk.Button(self, text="Add a data \nprocessing folder", width =18, height=2,font=("Arial", 12), \
              command = lambda: select_folder(data_folder_georefine)).grid(row=2, column=2, padx=(5, 0), pady=(0, 5), sticky="w")

    #set default phil file 
    tk.Label(self, text="Phil file for geometry refinement \n Change it only if needed", font=("Arial", 15)).grid(row=4, column=2)
    phil_file_georefine = tk.Text(self, width=90, height=20, font=("Aria", 15))
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
    phil_file_georefine.grid(row=5, column=1, columnspan=3, pady=(0, 25), sticky="ew")

    #scroll bar 2
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=phil_file_georefine.yview)
    scroll.grid(row=5, column=4, pady=(0, 25), sticky="wns")
    phil_file_georefine['yscrollcommand'] = scroll.set

    #tag
    tk.Label(self, text="Process tag for geo refinement", font=("Arial", 15)).grid(row=6, column=2)
    tag_geo = tk.Entry(self, width=30, font=("Aria", 15), justify="center")
    tag_geo.grid(row=7, column=2, pady=(0, 25), sticky="we")
    
    #give weight to extra columns, to make the widgets at the center
    self.grid_columnconfigure([0, 4], weight=1)
    self.grid_columnconfigure([1], weight=2)
    self.grid_columnconfigure([2, 3], weight=4)
    #self.grid_rowconfigure(list(range(7)), weight=4)

    #buttons for submitting job
    tk.Button(self, text="Submit georefine job", width =16, height=2,font=("Arial", 12), command = lambda: geometry_refinement(data_dir=data_folder_georefine.get(), output_dir=output_dir.get(), \
              tag_geo=tag_geo.get(), phil_file=phil_file_georefine.get("1.0","end")).run_job()).grid(row=8, column=1, sticky="e")
    tk.Button(self, text="Compare geometry", width =16, height=2,font=("Arial", 12), command = lambda: geometry_refinement(data_dir=data_folder_georefine.get(), output_dir=output_dir.get(),\
              tag_geo=tag_geo.get(), phil_file=phil_file_georefine.get("1.0","end")).run_compare()).grid(row=8, column=2, sticky="e")


#scaling tab
class scaling(tk.Frame):
  def __init__(self, master, cluster_option, dials_path, output_dir, cpu_scaling):
    tk.Frame.__init__(self, master)
    #scaling tab
    tk.Label(self, text="Scaling", font=("Arial", 18)).grid(row=0, column=3, pady=(0, 15))

    #set up phil file
    tk.Label(self, text="Phil file scaling", font=("Arial", 15)).grid(row=1, column=1, pady=(0, 5), sticky="e")
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
    phil_file_scaling.grid(row=2, column=1, columnspan=2, rowspan=2, pady=(0, 30), sticky="wens")

    #scroll bar phil file
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=phil_file_scaling.yview)
    scroll.grid(row=2, column=3, rowspan=2, sticky="wns", pady=(0, 30))
    phil_file_scaling['yscrollcommand'] = scroll.set

    #data dir
    tk.Label(self, text="Processing ouput dir", font=("Arial", 15)).grid(row=1, column=4, pady=(0, 5), sticky="e")
    data_folder_scaling = tk.Text(self, width=60, height=18, font=("Aria", 15))
    data_folder_scaling.grid(row=3, column=4, columnspan=2, pady=(0, 20), sticky="wens")

    #select data dir(s)
    tk.Button(self, text="Select all data \nprocessing sub-folder(s)", width =18, height=2,font=("Arial", 12), \
              command = lambda:folder_content_folder(data_folder_scaling)).grid(row=2, column=4, pady=(0, 5), sticky="w")
    tk.Button(self, text="Add a data \nprocessing folder", width =18, height=2,font=("Arial", 12), \
              command = lambda: add_folder_textbox(data_folder_scaling)).grid(row=2, column=5, pady=(0, 5), sticky="e")

    #scroll bar data folder
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=data_folder_scaling.yview)
    scroll.grid(row=3, column=6, pady=(0, 20), sticky="wns")
    data_folder_scaling['yscrollcommand'] = scroll.set
    
    """
    #process folder
    tk.Label(self, text="Process folder scaling", font=("Arial", 15)).grid(row=2, column=2, padx=20)
    process_folder_scaling = tk.Entry(self, width=50, font=("Aria", 15))
    process_folder_scaling.grid(row=3, column=2, padx=20)
    """

    #reference pdb
    tk.Label(self, text="Reference pdb scaling", font=("Arial", 15)).grid(row=4, column=3, pady=(30, 0))
    ref_pdb_scaling = tk.Entry(self, width=50, font=("Aria", 15),  justify="center")
    ref_pdb_scaling.grid(row=5, column=2, columnspan=3, pady=(0, 10), sticky="we")
    tk.Button(self, text="select reference pdb/mtz", width =12, height=1,font=("Arial", 12), \
              command = lambda:select_file(ref_pdb_scaling)).grid(row=5, column=5, padx=(5, 0), pady=(0, 10), sticky="we")
    
    #tag
    tk.Label(self, text="Sample tag scaling", font=("Arial", 15)).grid(row=6, column=3, padx=20)
    sample_tag_scaling = tk.Entry(self, width=50, font=("Aria", 15), justify="center")
    sample_tag_scaling.grid(row=7, column=2, columnspan=3, pady=(0, 10), sticky="we")
    
    #resolution
    tk.Label(self, text="Resolution scaling", font=("Arial", 15)).grid(row=8, column=3)
    resolution_scaling = tk.Entry(self, width=50, font=("Aria", 15), justify="center")
    resolution_scaling.grid(row=9, column=2, columnspan=3, pady=(0, 30), sticky="we")
    
    #give weight to extra columns, to make the widgets at the center
    self.grid_columnconfigure([0, 3, 6, 7], weight=1)
    self.grid_columnconfigure([1, 2, 4, 5], weight=4)

    #buttons
    tk.Button(self, text="Submit scaling job", width =16, height=2,font=("Arial", 12), command = lambda: scaling_job(data_dir=data_folder_scaling.get("1.0","end").splitlines(), \
    cluster_option=cluster_option.get(), phil_file_scaling=phil_file_scaling.get("1.0","end"), sample_tag_scaling=sample_tag_scaling.get(), \
    resolution_scaling=resolution_scaling.get(), cpu_diamond_scaling=cpu_scaling.get(), ref_pdb_scaling=ref_pdb_scaling.get(), output_dir=output_dir.get(), \
    dials_path=dials_path.get()).submit_job()).grid(row=10, column=3)


#merging tab
class merging(tk.Frame):
  def __init__(self, master, cluster_option, dials_path, output_dir, cpu_merging):
    tk.Frame.__init__(self, master)

    #merging tab
    tk.Label(self, text="Merging", font=("Arial", 18)).grid(row=0, column=3, pady=(0, 15))

    #set up phil file
    tk.Label(self, text="Phil file merging", font=("Arial", 15)).grid(row=1, column=1, pady=(0, 5), sticky="e")
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
    phil_file_merging.grid(row=2, column=1, columnspan=2, rowspan=2, pady=(0, 30), sticky="wens")

    #scroll bar phil file
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=phil_file_merging.yview)
    scroll.grid(row=2, column=3, rowspan=2, sticky="wns", pady=(0, 30))
    phil_file_merging['yscrollcommand'] = scroll.set

    #data dir
    tk.Label(self, text="Scaling ouput dir", font=("Arial", 15)).grid(row=1, column=4, pady=(0, 5), sticky="e")
    data_folder_merging = tk.Text(self, width=60, height=18, font=("Aria", 15))
    data_folder_merging.grid(row=3, column=4, columnspan=2, pady=(0, 20), sticky="wens")
    
    #select data dir(s)
    tk.Button(self, text="Select all data \nscaling sub-folder(s)", width =18, height=2,font=("Arial", 12), \
              command = lambda:folder_content_folder(data_folder_merging)).grid(row=2, column=4, pady=(0, 5), sticky="w")
    tk.Button(self, text="Add a data \nscaling folder", width =18, height=2,font=("Arial", 12), \
              command = lambda: add_folder_textbox(data_folder_merging)).grid(row=2, column=5, pady=(0, 5), sticky="e")

    #scroll bar data folder
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=data_folder_merging.yview)
    scroll.grid(row=3, column=6, pady=(0, 20), sticky="wns")
    data_folder_merging['yscrollcommand'] = scroll.set

    """
    #process folder
    tk.Label(self, text="Process folder merging", font=("Arial", 15)).grid(row=2, column=2, padx=20)
    process_folder_merging = tk.Entry(self, width=50, font=("Aria", 15))
    process_folder_merging.grid(row=3, column=2, padx=20)
    """

    #reference pdb
    tk.Label(self, text="Reference pdb merging", font=("Arial", 15)).grid(row=4, column=3, pady=(30, 0))
    ref_pdb_merging = tk.Entry(self, width=50, font=("Aria", 15))
    ref_pdb_merging.grid(row=5, column=2, columnspan=3, pady=(0, 10), sticky="we")
    tk.Button(self, text="select reference pdb/mtz", width =12, height=1,font=("Arial", 12), \
          command = lambda:select_file(ref_pdb_merging)).grid(row=5, column=5, padx=(5, 0), pady=(0, 10), sticky="we")
    
    #tag
    tk.Label(self, text="Sample tag merging", font=("Arial", 15)).grid(row=6, column=3, padx=20)
    sample_tag_merging = tk.Entry(self, width=50, font=("Aria", 15), justify="center")
    sample_tag_merging.grid(row=7, column=2, columnspan=3, pady=(0, 10), sticky="we")
    
    #resolution
    tk.Label(self, text="Resolution merging", font=("Arial", 15)).grid(row=8, column=3)
    resolution_merging = tk.Entry(self, width=50, font=("Aria", 15), justify="center")
    resolution_merging.grid(row=9, column=2, columnspan=3, pady=(0, 30), sticky="we")

    #give weight to extra columns, to make the widgets at the center
    self.grid_columnconfigure([0, 3, 6, 7], weight=1)
    self.grid_columnconfigure([1, 2, 4, 5], weight=4)
    
    #buttons
    tk.Button(self, text="Submit merging job", width =16, height=2,font=("Arial", 12), command = lambda: merging_job(data_dir=data_folder_merging.get("1.0","end").splitlines(), \
    cluster_option=cluster_option.get(), phil_file_merging=phil_file_merging.get("1.0","end"), sample_tag_merging=sample_tag_merging.get(), \
    resolution_merging=resolution_merging.get(), cpu_diamond_merging=cpu_merging.get(), ref_pdb_merging=ref_pdb_merging.get(), output_dir=output_dir.get(), \
    dials_path=dials_path.get()).submit_job()).grid(row=10, column=3)


#merging plot
class plot_merging(tk.Frame):
  def __init__(self, master):
    tk.Frame.__init__(self, master)

    #plot merging
    tk.Label(self, text="Plot merging stats), ONE DIR only", font=("Arial", 18)).grid(row=0, column=2,pady=(0, 20))
    
    """
    #merging dir (Text)
    tk.Label(self, text="merging dir (absolute path), ONE DIR only", font=("Arial", 15)).grid(row=1, column=2)
    merging_dir = tk.Text(self, width=100, height=25, font=("Aria", 15))
    merging_dir.grid(row=1, column=0, rowspan=5)    
    
    #scroll bar phil file
    scroll= tk.Scrollbar(self, orient="vertical",  width=20, elementborderwidth=3, command=merging_dir.yview)
    scroll.grid(row=1, column=1, rowspan=5, sticky="ns")
    merging_dir['yscrollcommand'] = scroll.set

    """

    #merging dir
    tk.Label(self, text="merging dir (absolute path), ONE DIR only", font=("Arial", 15)).grid(row=1, column=2)
    merging_dir = tk.Entry(self, width=70, font=("Aria", 15), justify="center")
    merging_dir.grid(row=2, column=1, columnspan=3, pady=(0, 10), sticky="we") #select_folder_entry
    tk.Button(self, text="select merging FOLDER", width =12, height=1,font=("Arial", 12), \
          command = lambda:select_folder(merging_dir)).grid(row=2, column=4, pady=(0, 10), sticky="we")

    #plot_1 option
    tk.Label(self, text="Plot stats 1", font=("Arial", 15)).grid(row=3, column=1, pady=(0, 5))
    stats_1_list = ["CC1/2", "Rsplit", "I/sigma", "Multiplicity", "Completeness"]
    stats_1 = tk.StringVar(self)
    stats_1.set("CC1/2")
    stats_1_choice = tk.OptionMenu(self, stats_1, *stats_1_list, command = lambda selected: plot.read_merging_stats(stats_1.get())).grid(row=4, column=1)

    #plot_2 option
    tk.Label(self, text="Plot stats 2", font=("Arial", 15)).grid(row=3, column=3, pady=(0, 5))
    stats_2_list = ["CC1/2", "Rsplit", "I/sigma", "Multiplicity", "Completeness"]
    stats_2 = tk.StringVar(self)
    stats_2.set("Multiplicity")
    stats_2_choice = tk.OptionMenu(self, stats_2, *stats_2_list, command = lambda selected: plot.read_merging_stats(stats_2.get())).grid(row=4, column=3)

    #give weight to extra columns, to make the widgets at the center
    self.grid_columnconfigure([0, 5], weight=1)
    self.grid_columnconfigure([1, 2, 3, 4], weight=4)

    #button
    tk.Button(self, text="Plot merging stats", width =16, height=2,font=("Arial", 12), command = lambda: \
    plot_mergingstat(merging_dir.get().splitlines()).plot_stats(stats_1.get(), stats_2.get())).grid(row=6, column=2, pady=(50, 0))


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







