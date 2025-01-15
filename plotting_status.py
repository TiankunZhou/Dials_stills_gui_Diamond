import glob
from matplotlib import pyplot as plt
import os
import sys
from pathlib import Path
from processing_stills import colors
import subprocess
import matplotlib.animation as animation
"""
Plot DIALS stills processing statistics, reading from the debug files

"""

###define the value###
class count:
  def images(file_name):
    count = 0
    image =[]
    for f in glob.glob(str(file_name)):
      files = open(f, "r")
      for line in files:
        if str("spotfind_start") in line:
          count += 1
          image.append(count)
    return(image)

  def spots(file_name):
    spots =[]
    for f in glob.glob(str(file_name)):
      files = open(f, "r")
      for line in files:
        if str(",done,") in line:
          spot = int(line.split("_")[-1].strip())
          spots.append(spot)
        elif str(",fail,") in line:
          try:
            spot = int(line.split("_")[-1].strip())
            spots.append(spot)
          except ValueError:
            spots.append(0)
        elif str(",stop,") in line:
          spot = int(line.split("_")[-1].strip())
          spots.append(spot)
    return(spots)

  def color(file_name):
    color =[]
    for f in glob.glob(str(file_name)):
      files = open(f, "r")
      for line in files:
        if str(",done,") in line:
          color.append("blue")
        elif str(",fail,") in line:
          color.append("orange")
        elif str(",stop,") in line:
          if str(",indexing_failed") in line:
            color.append("red")
          else:
            color.append("gray")
    return color

  def experiments(filename, keywords):
      count = 0
      for f in glob.glob(filename):
          count += Path(f).read_text().count(str(keywords))
      return count

class dot:
  def __init__(self, **kwargs):
    self.dir = kwargs["dir"]
    self.real_time_plot = kwargs["real_time_plot"]
    #self.refreshing_time = kwargs["refreshing_time"]

  def dot_single(self):
    def get_data():
      for line in self.dir:
        for i in glob.glob(line):
          if not os.path.isdir(i + "/debug"):
            print("debug folder not exitst " + str(i))
            break
          elif os.path.isdir(i + "/debug"):
            print("Plot dot: " + i + "/debug")
            x = count.images(i + "/debug/debug*")
            y = count.spots(i + "/debug/debug*")
            colors = count.color(i + "/debug/debug*")
            a = len(x)
            b = len(y)
            color_len = len(colors)
            #print(a)
            #print(b)
            #print(color_len)
            if a > b:
              c = b - a
              if color_len == b:
                del x[c:]
              elif color_len < b:
                d = c - a
                del x[d:]
                del y[d:]
              else:
                del x[c:]
                del colors[c:]
            elif a < b:
              c = a - b
              if color_len == a:
                del x[c:]
              elif color_len < a:
                d = c - b
                del x[d:]
                del y[d:]
              else:
                del x[c:]
                del colors[c:]
          images_total = int(count.experiments(i + "/debug/debug*", "spotfind_start"))
          images_integr = int(count.experiments(i + "/debug/debug*", "integrate_ok"))
          images_ind_f = int(count.experiments(i + "/debug/debug*", "indexing_failed") + count.experiments(i + "/debug/debug*", ",integrate_failed"))
          images_hits = int(count.experiments(i + "/debug/debug*", ",index_start"))
          image_title = "Plot processing statistics for " + str(os.path.abspath(i))
      return x, y, images_total, images_integr, images_ind_f, images_hits, image_title, colors
    
    def plot_single_norealtime():
      x, y, images_total, images_integr, images_ind_f, images_hits, image_title, colors = get_data()
      fig = plt.figure(figsize=(16, 10))
      plt.xlabel("Images", fontsize=14)
      plt.ylabel("Spots", fontsize=14)
      plt.title(image_title, fontsize=16)
      if images_hits == 0:
        images_hits_pcnt = 0
        images_integr_pcnt = 0
        images_ind_f_pcnt = 0
      else:
        images_hits_pcnt = round((images_hits/images_total)*100, 1)
        images_integr_pcnt = round((images_integr/images_hits)*100, 1)
        images_ind_f_pcnt = round((images_ind_f/images_hits)*100, 1)
      text_str = "\n".join(
                          ("Imported images: {}".format(images_total),
                          "Hits found: {} ({}%)".format(images_hits, images_hits_pcnt),
                          "Indexed and integrated images: {} ({}% of hits)".format(images_integr, images_integr_pcnt),
                          "Indexing failed images: {} ({}% of hits)".format(images_ind_f, images_ind_f_pcnt),))          
      plt.text(0.01, 0.99, text_str, fontsize=14, va="top", ha="left", transform=plt.gca().transAxes)
      plt.scatter(x, y, marker="o", color=colors)
      plt.show()
    
    def plot_single_realtime(i):
      x, y, images_total, images_integr, images_ind_f, images_hits, _, colors = get_data()
      #fig = plt.figure(figsize=(16, 10))
      if images_hits == 0:
        images_hits_pcnt = 0
        images_integr_pcnt = 0
        images_ind_f_pcnt = 0
      else:
        images_hits_pcnt = round((images_hits/images_total)*100, 1)
        images_integr_pcnt = round((images_integr/images_hits)*100, 1)
        images_ind_f_pcnt = round((images_ind_f/images_hits)*100, 1)
      text_str = "\n".join(
                          ("Imported images: {}".format(images_total),
                          "Hits found: {} ({}%)".format(images_hits, images_hits_pcnt),
                          "Indexed and integrated images: {} ({}% of hits)".format(images_integr, images_integr_pcnt),
                          "Indexing failed images: {} ({}% of hits)".format(images_ind_f, images_ind_f_pcnt),))          
      figure_text = plt.text(0.01, 0.99, text_str, fontsize=14, va="top", ha="left", transform=plt.gca().transAxes)
      figure_plot = plt.scatter(x, y, marker="o", color=colors)
      return figure_text, figure_plot

    def init_plot():
      x, y, _, _, _, _, _, _ = get_data()
      figure_text = plt.text(0.01, 0.99, "", fontsize=14, va="top", ha="left", transform=plt.gca().transAxes)
      figure_plot = plt.scatter(x, y, marker="o", color=[])
      return figure_text, figure_plot

    if self.real_time_plot == "no":
      plot = plot_single_norealtime()
    elif self.real_time_plot == "yes":
      print(f"Real-time plot for dot is currently bugged, use bar plot please")
      #create blank window
      """
      image_title = get_data()[6]
      fig = plt.figure(figsize=(16, 10))
      plt.xlabel("Images", fontsize=14)
      plt.ylabel("Spots", fontsize=14)
      plt.title(f"Real time {image_title}", fontsize=16)
      #figure_text = plt.text(0.01, 0.99, "", fontsize=14, va="top", ha="left", transform=plt.gca().transAxes)
      #figure_plot = plt.scatter([], [], marker="o", color=[])
      #plot update
      anim = animation.FuncAnimation(fig, plot_single_realtime, init_func=init_plot, frames= 1, interval= 1000, cache_frame_data=False, blit=True)
      return anim
      """
    #plt.show()

  def dot_stack(self):
    def get_data():    
      x = []
      y = []
      colors = []
      images_total = 0
      images_integr = 0
      images_ind_f = 0
      images_hits = 0
      for line in self.dir:
        for i in glob.glob(line):
          if not os.path.isdir(i + "/debug"):
            print("debug folder not exitst " + str(i))
            break
          elif os.path.isdir(i + "/debug"):
            print("Plot dot: " + i + "/debug")
            x_1 = [i + len(x) for i in count.images(i + "/debug/debug*")]
            y_1 = count.spots(i + "/debug/debug*")
            x += x_1
            y += y_1
            colors_1 = count.color(i + "/debug/debug*")
            colors += colors_1
            images_total += int(count.experiments(i + "/debug/debug*", "spotfind_start"))
            images_integr += int(count.experiments(i + "/debug/debug*", "integrate_ok"))
            images_ind_f += int(count.experiments(i + "/debug/debug*", "indexing_failed") + count.experiments(i + "/debug/debug*", ",integrate_failed"))
            images_hits += int(count.experiments(i + "/debug/debug*", ",index_start"))
      a = len(x)
      b = len(y)
      color_len = len(colors)
      #print(a)
      #print(b)
      #print(color_len)
      if a > b:
        c = b - a
        if color_len == b:
          del x[c:]
        elif color_len < b:
          d = c - a
          del x[d:]
          del y[d:]
        else:
          del x[c:]
          del colors[c:]
      elif a < b:
        c = a - b
        if color_len == a:
          del x[c:]
        elif color_len < a:
          d = c - b
          del x[d:]
          del y[d:]
        else:
          del x[c:]
          del colors[c:]
      if images_hits == 0:
        images_hits_pcnt = 0
        images_integr_pcnt = 0
        images_ind_f_pcnt = 0
      else:
        images_hits_pcnt = round((int(images_hits)/int(images_total))*100, 1)
        images_integr_pcnt = round((images_integr/images_hits)*100, 1)
        images_ind_f_pcnt = round((images_ind_f/images_hits)*100, 1)
      return x, y, images_hits_pcnt, images_hits_pcnt, images_ind_f_pcnt, images_integr_pcnt, \
      images_total, images_hits, images_integr, images_ind_f, colors
    
    def plot_stuck_noraltime():
      x, y, images_hits_pcnt, images_hits_pcnt, images_ind_f_pcnt, images_integr_pcnt, \
      images_total, images_hits, images_integr, images_ind_f, colors = get_data()
      fig = plt.figure(figsize=(16, 10))
      plt.xlabel("Images", fontsize=14)
      plt.ylabel("Spots", fontsize=14)
      plt.title("Plot processing statistics for " + "all data together", fontsize=16)
      text_str = "\n".join(
                          ("Imported images: {}".format(images_total),
                          "Hits found: {} ({}%)".format(images_hits, images_hits_pcnt),
                          "Indexed and integrated images: {} ({}% of hits)".format(images_integr, images_integr_pcnt),
                          "Indexing failed images: {} ({}% of hits)".format(images_ind_f, images_ind_f_pcnt),))          
      plt.text(0.01, 0.99, text_str, fontsize=14, va="top", ha="left", transform=plt.gca().transAxes)
      plt.scatter(x, y, marker="o", color=colors)
      plt.show()
    
    if self.real_time_plot == "no":
      plot_stuck_noraltime()
    elif self.real_time_plot == "yes":
      print(f"Real-time plot for dot is currently bugged, use bar plot please")
    #plt.show()

class bar:
  def __init__(self, **kwargs):
    self.dir = kwargs["dir"]
    self.real_time_plot = kwargs["real_time_plot"]
    #self.refreshing_time = kwargs["refreshing_time"]

  def bar_single(self):
    def get_data():
      for line in self.dir:
        for i in glob.glob(line):
          if not os.path.isdir(i + "/debug"):
            print("debug folder not exitst " + str(i))
            break
          elif os.path.isdir(i + "/debug"):
            print("Plot bar: " + i + "/debug")
            step = ["Total images", "Number of hits", "Integrated", "Failed"]
            total_image = int(count.experiments(i + "/debug/debug*", "spotfind_start"))
            number_of_hits = int(count.experiments(i + "/debug/debug*", ",index_start"))
            integrated = int(count.experiments(i + "/debug/debug*", "integrate_ok"))
            failed = int(count.experiments(i + "/debug/debug*", "indexing_failed") + count.experiments(i + "/debug/debug*", ",integrate_failed"))
            image_number = [total_image, number_of_hits, integrated, failed]
            image_title = "Processing statistic bar for " + str(os.path.abspath(i))
      return step, total_image, number_of_hits, integrated , failed, image_number, image_title
    
    def plot_single_norealtime():
      step, total_image, number_of_hits, integrated , failed, image_number, image_title = get_data()
      plt.figure(figsize=(16, 10))
      ax = plt.subplot(1, 1, 1)
      plt.title(image_title, fontsize=18)
      text_str = "\n".join(
        ("Total images: {}".format(total_image),
        "Hits: {} ({:.2f}%)".format(number_of_hits, float(number_of_hits*100/total_image)),
        "Integrate: {} ({:.2f}%)".format(integrated, float(integrated*100/number_of_hits)),
        "Failed: {} ({:.2f}%)".format(failed, float((failed)*100/number_of_hits))))
      plt.xticks(fontsize=16)
      plt.yticks(fontsize=16)
      figure_text = plt.text(0.99, 0.99, text_str, fontsize=16, va="top", ha="right", transform=plt.gca().transAxes)
      figure_plot = ax.bar(step, image_number, color=['black', 'blue', 'orange', 'grey'])
      ax.bar_label(figure_plot, fmt='{:,.0f}', padding=1, fontsize=16)
      plt.show()

    def plot_single_realtime(i):
      step, total_image, number_of_hits, integrated , failed, image_number, image_title = get_data()
      text_str = "\n".join(
        ("Total images: {}".format(total_image),
        "Hits: {} ({:.2f}%)".format(number_of_hits, float(number_of_hits*100/total_image)),
        "Integrate: {} ({:.2f}%)".format(integrated, float(integrated*100/number_of_hits)),
        "Failed: {} ({:.2f}%)".format(failed, float((failed)*100/number_of_hits))))
      ax.cla()
      plt.title(image_title, fontsize=18)
      plt.xticks(fontsize=16)
      plt.yticks(fontsize=16)
      figure_text = plt.text(0.99, 0.99, text_str, fontsize=16, va="top", ha="right", transform=plt.gca().transAxes)
      figure_plot = ax.bar(step, image_number, color=['black', 'blue', 'orange', 'grey'])
      ax.bar_label(figure_plot, fmt='{:,.0f}', padding=1, fontsize=16)
      #return figure_text, figure_plot

    if self.real_time_plot == "no":
      plot = plot_single_norealtime()
    elif self.real_time_plot == "yes":
      #create blank window
      fig = plt.figure(figsize=(16, 10))
      ax = plt.subplot(1, 1, 1)
      anim = animation.FuncAnimation(fig, plot_single_realtime, frames= 50, interval= 200, cache_frame_data=False)
      plt.show()

  def bar_stack(self):
    def get_data():
      number_of_hits = 0
      integrated = 0
      failed = 0
      total_image = 0
      image_title = "Processing statistic bar for all data together"
      for line in self.dir:
        for i in glob.glob(line):
          if not os.path.isdir(i + "/debug"):
            print("debug folder not exitst: " + str(i))
            pass
          elif os.path.isdir(i + "/debug"):
            print("Plot bar stack: " + i + "/debug")
            number_of_hits += int(count.experiments(i + "/debug/debug*", ",index_start"))
            integrated += int(count.experiments(i + "/debug/debug*", "integrate_ok"))
            failed += int(count.experiments(i + "/debug/debug*", "indexing_failed") + count.experiments(i + "/debug/debug*", ",integrate_failed"))
            total_image += int(count.experiments(i + "/debug/debug*", "spotfind_start"))
      step = ["Total images", "Number of hits", "Integrated", "Failed"]
      image_number = [total_image, number_of_hits, integrated, failed]
      return number_of_hits, integrated, failed, total_image, step, image_number, image_title
    
    def plot_stuck_norealtime():
      number_of_hits, integrated, failed, total_image, step, image_number, image_title = get_data()
      if total_image == 0 or number_of_hits == 0:
        print("No data to plot")
      else:
        text_str = "\n".join(
          ("Total images: {}".format(total_image),
          "Hits: {} ({:.2f}%)".format(number_of_hits, float(number_of_hits*100/total_image)),
          "Integrate: {} ({:.2f}%)".format(integrated, float(integrated*100/number_of_hits)),
          "Failed: {} ({:.2f}%)".format(failed, float((failed)*100/number_of_hits))))
        plt.figure(figsize=(16, 10))
        ax = plt.subplot(1, 1, 1)
        plt.title(image_title, fontsize=18)
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        figure_text = plt.text(0.99, 0.99, text_str, fontsize=16, va="top", ha="right", transform=plt.gca().transAxes)
        figure_plot = ax.bar(step, image_number, color=['black', 'blue', 'orange', 'grey'])
        ax.bar_label(figure_plot, fmt='{:,.0f}', padding=1, fontsize=16)
      plt.show()

    def plot_stuck_realtime(i):
      number_of_hits, integrated, failed, total_image, step, image_number, image_title = get_data()
      text_str = "\n".join(
        ("Total images: {}".format(total_image),
        "Hits: {} ({:.2f}%)".format(number_of_hits, float(number_of_hits*100/total_image)),
        "Integrate: {} ({:.2f}%)".format(integrated, float(integrated*100/number_of_hits)),
        "Failed: {} ({:.2f}%)".format(failed, float((failed)*100/number_of_hits))))
      ax.cla()
      plt.title(f"Realtime {image_title}", fontsize=18)
      plt.xticks(fontsize=16)
      plt.yticks(fontsize=16)
      figure_text = plt.text(0.99, 0.99, text_str, fontsize=16, va="top", ha="right", transform=plt.gca().transAxes)
      figure_plot = ax.bar(step, image_number, color=['black', 'blue', 'orange', 'grey'])
      ax.bar_label(figure_plot, fmt='{:,.0f}', padding=1, fontsize=16)
      #return figure_text, figure_plot
      
    if self.real_time_plot == "no":
      plot_stuck_norealtime()
    elif self.real_time_plot == "yes":
      #create blank window
      fig = plt.figure(figsize=(16, 10))
      ax = plt.subplot(1, 1, 1)
      #plot update
      anim = animation.FuncAnimation(fig, plot_stuck_realtime, frames= 50, interval= 200, cache_frame_data=False)
      plt.show()
    

"""
class pie:
  def print(dir):
    for line in dir:
      for i in glob.glob(line):
        if not os.path.isdir(i + "/debug"):
          print("debug folder not exitst " + str(i))
          break
        elif os.path.isdir(i + "/debug"):
          print("Plot pie: " + i + "/debug")
          total_image = int(count.experiments(i + "/debug/debug*", "spotfind_start"))
          number_of_hits = int(count.experiments(i + "/debug/debug*", ",index_start"))
          non_hit = int(total_image - number_of_hits)
          integrated = int(count.experiments(i + "/debug/debug*", "integrate_ok"))
          failed = int(count.experiments(i + "/debug/debug*", "indexing_failed") + count.experiments(i + "/debug/debug*", ",integrate_failed"))
          image_number = [non_hit, integrated, failed]
          step = ["Non_hit: " + str(non_hit), "Integrated: " + str(integrated), "Failed: " + str(failed)]
          plt.figure(figsize=(16, 10))
          plt.title("Processing statistic bar for " + str(os.path.abspath(i)), fontsize=16)
          text_str = "\n".join(
            ("Total images: {}".format(total_image),
            "Hits: {} ({:.2f}%)".format(number_of_hits, float(number_of_hits*100/total_image)),
            "Integrate: {} ({:.2f}%)".format(integrated, float(integrated*100/number_of_hits)),
            "Failed: {} ({:.2f}%)".format(failed, float((failed)*100/number_of_hits))))
          plt.text(0.99, 0.99, text_str, fontsize=14, va="top", ha="right", transform=plt.gca().transAxes)
          plt.pie(image_number, labels=step, colors=['black', 'orange', 'grey'])
    #plt.show()

  def print_stack(dir):
    number_of_hits = 0
    integrated = 0
    failed = 0
    total_image = 0
    non_hit = 0
    for line in dir:
      for i in glob.glob(line):
        if not os.path.isdir(i + "/debug"):
          print("debug folder not exitst: " + str(i))
          pass
        elif os.path.isdir(i + "/debug"):
          print("Plot pie stack: " + i + "/debug")
          number_of_hits += int(count.experiments(i + "/debug/debug*", ",index_start"))
          integrated += int(count.experiments(i + "/debug/debug*", "integrate_ok"))
          failed += int(count.experiments(i + "/debug/debug*", "indexing_failed") + count.experiments(i + "/debug/debug*", ",integrate_failed"))
          total_image += int(count.experiments(i + "/debug/debug*", "spotfind_start"))

    non_hit += int(total_image - number_of_hits)
    step = ["Non_hit: " + str(non_hit), "Integrated: " + str(integrated), "Failed: " + str(failed)]
    image_number = [non_hit, integrated, failed]
    if total_image == 0 or number_of_hits == 0:
      print("No data to plot")
    else:
      text_str = "\n".join(
        ("Total images: {}".format(total_image),
        "Hits: {} ({:.2f}%)".format(number_of_hits, float(number_of_hits*100/total_image)),
        "Integrate: {} ({:.2f}%)".format(integrated, float(integrated*100/number_of_hits)),
        "Failed: {} ({:.2f}%)".format(failed, float((failed)*100/number_of_hits))))
      plt.figure(figsize=(16, 10))
      plt.title("Processing statistic bar for all data together", fontsize=16)
      plt.text(0.99, 0.99, text_str, fontsize=14, va="top", ha="right", transform=plt.gca().transAxes)
      plt.pie(image_number, labels=step, colors=['black', 'orange', 'grey'])
      #plt.show()
"""

class uc_plot:
  def __init__(self, data_dir, option):
    self.data_dir = data_dir
    self.option = option
  def plot_stack(self):
    command_stack = "cctbx.xfel.plot_uc_cloud_from_experiments combine_all_input=True "
    for line in self.data_dir:
      for i in glob.glob(line):
        if os.path.isdir(os.path.join(i, "debug")):
          command_stack += str(i) + "/*_refined.expt "
        elif not os.path.isdir(os.path.join(line, "debug")):
          print("Job " + str(i) + " is not exist, please check")

    print("Runnung command: " + command_stack)
    subprocess.call(command_stack, shell=True)
  
  def plot_single(self):
    for line in self.data_dir:
      for i in glob.glob(line):
        if os.path.isdir(os.path.join(i, "debug")):
          command_single = "cctbx.xfel.plot_uc_cloud_from_experiments combine_all_input=True " + str(i) + "/*_refined.expt"
          print("Running command: " + command_single)
          subprocess.call(command_single, shell=True)
        elif not os.path.isdir(os.path.join(i, "debug")):
          print("Job " + str(i) + " is not exist, please check")
  
  def plot_uc(self):
    if self.option == "single":
      self.plot_single()
    elif self.option == "stack":
      self.plot_stack()

class plot:
  def read_option(option):
    print("Select plot option: " + option + colors.RED + colors.BOLD + " (single plot option is not recommand for uc plot, please use stack)" + colors.ENDC)

  def read_file_format(option):
    print("File format: " + option)

  def read_cluster_option(option):
    print("Cluster option: " + option)

  def read_merging_stats(option):
    print("plot merging_stats: " + option)
  
  def read_composite(option):
    print(f"composite output: {option}")

  def read_all_output(option):
    print(f"output all files: {option}")

  def read_realtime(option):
    if option == "yes":
      print(f"realtime plot: {option}, please do not plot a HUGE amount of dataset")
    elif option == "no":
      print(f"realtime plot: {option}")

  def dot(option, dir, real_time_plot):
    if option == "single":
      plot = dot(dir=dir, real_time_plot=real_time_plot).dot_single()
    elif option == "stack":
      plot = dot(dir=dir, real_time_plot=real_time_plot).dot_stack()

  def bar(option, dir, real_time_plot):
    if option == "single":
      plot = bar(dir=dir, real_time_plot=real_time_plot).bar_single()
    elif option == "stack":
      plot = bar(dir=dir, real_time_plot=real_time_plot).bar_stack()
  
  """
    def pie(option, dir):
    if option == "single":
      pie.print(dir)
      plt.show()
    elif option == "stack":
      pie.print_stack(dir)
      plt.show()
  """
  
  




