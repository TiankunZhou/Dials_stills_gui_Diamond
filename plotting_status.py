import glob
from matplotlib import pyplot as plt
import os
import sys
from pathlib import Path
from processing_stills import colors
import subprocess
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
  def print(dir):
    for line in dir:
      for i in glob.glob(line):
        if not os.path.isdir(i + "/debug"):
          print("debug folder not exitst " + str(i))
          break
        elif os.path.isdir(i + "/debug"):
          print("Plot dot: " + i + "/debug")
          x = count.images(i + "/debug/debug*")
          y = count.spots(i + "/debug/debug*")
          a = len(x)
          b = len(y)
          print(a)
          print(b)
          if a > b:
            c = b - a
            del x[c:]
          elif a < b:
            c = a - b
            del y[c:]
          colors = count.color(i + "/debug/debug*")
          plt.figure(figsize=(16, 10))
          plt.xlabel("Images", fontsize=14)
          plt.ylabel("Spots", fontsize=14)
          plt.title("Plot processing statistics for " + str(os.path.abspath(i)), fontsize=16)
          images_total = int(count.experiments(i + "/debug/debug*", "spotfind_start"))
          images_integr = int(count.experiments(i + "/debug/debug*", "integrate_ok"))
          images_ind_f = int(count.experiments(i + "/debug/debug*", "indexing_failed") + count.experiments(i + "/debug/debug*", ",integrate_failed"))
          images_hits = int(count.experiments(i + "/debug/debug*", ",index_start"))
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

  def print_stack(dir):
    x = []
    y = []
    colors = []
    images_total = 0
    images_integr = 0
    images_integr = 0
    images_ind_f = 0
    images_ind_f = 0
    images_hits = 0
    for line in dir:
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
    print(a)
    print(b)
    if a > b:
      c = b - a
      del x[c:]
      del colors[c:]
    elif a < b:
      c = a - b
      del y[c:]
      del colors[c:]
    plt.figure(figsize=(16, 10))
    plt.xlabel("Images", fontsize=14)
    plt.ylabel("Spots", fontsize=14)
    plt.title("Plot processing statistics for " + "all data together", fontsize=16)
    if images_hits == 0:
      images_hits_pcnt = 0
      images_integr_pcnt = 0
      images_ind_f_pcnt = 0
    else:
      images_hits_pcnt = round((int(images_hits)/int(images_total))*100, 1)
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

class bar:
  def print(dir):
    for line in dir:
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
          plt.figure(figsize=(16, 10))
          plt.title("Processing statistic bar for " + str(os.path.abspath(i)), fontsize=16)
          text_str = "\n".join(
            ("Total images: {}".format(total_image),
            "Hits: {} ({:.2f}%)".format(number_of_hits, float(number_of_hits*100/total_image)),
            "Integrate: {} ({:.2f}%)".format(integrated, float(integrated*100/number_of_hits)),
            "Failed: {} ({:.2f}%)".format(failed, float((failed)*100/number_of_hits))))
          plt.text(0.99, 0.99, text_str, fontsize=14, va="top", ha="right", transform=plt.gca().transAxes)
          plt.bar(step, image_number, color=['black', 'blue', 'orange', 'grey'])
    plt.show()

  def print_stack(dir):
    number_of_hits = 0
    integrated = 0
    failed = 0
    total_image = 0
    for line in dir:
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
      plt.bar(step, image_number, color=['black', 'blue', 'orange', 'grey'])
      plt.show()

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
    plt.show()

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
      plt.show()

class uc_plot():
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

  def read_queue_option(option):
    print("Queue option: " + option)

  def read_merging_stats(option):
    print("plot merging_stats: " + option)

  def dot(option, dir):
    if option == "single":
      dot.print(dir)
    elif option == "stack":
      dot.print_stack(dir)

  def bar(option, dir):
    if option == "single":
      bar.print(dir)
    elif option == "stack":
      bar.print_stack(dir)
  
  def pie(option, dir):
    if option == "single":
      pie.print(dir)
    elif option == "stack":
      pie.print_stack(dir)
    
  def real_time_bar(option, dir):
    print("under construction")




