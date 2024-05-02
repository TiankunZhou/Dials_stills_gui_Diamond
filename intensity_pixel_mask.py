import numpy as np
import math
import argparse
from pathlib import Path
import dxtbx
import pickle
#from plot_image_intensity import read_cbf, check_inputs


"""

This script will convert the pixel on the detector into resolution value, based on the 
detector distance, the distance between the pixel and the beam centre and the wavelength

It will also generate a resolution mask if required, the mask file canbe used for the intensity
calculation (plot_image_intensity.py)

How to use it:



"""
def process_args():
    input_args = argparse.ArgumentParser()

    #input file(s) as list
    input_args.add_argument("-i","--input_file",
        type=str,
        help="give the data file, ONE image is enough (cbf)"
        )

    input_args.add_argument("-dt","--detector",
        type=str,
        help="give the detector, e.g. pilatus6m, jungfrau4m, default is pliatus6m"
        )

    input_args.add_argument("-lr","--low_resolution",
        type=float,
        help="give the low resolution limit, default is 50",
        default = 50
        )
        
    input_args.add_argument("-hr","--high_resolution",
        type=float,
        help="give the high resolution limit, default is 1.2",
        default = 
        )
    
    input_args.add_argument("-c","--centre_pixel",
        type=str,
        help="give the pixel position of the centre of the detector, separate x, \
        and y with a comma. e.g. 1234,2345; It uses the centre of the detector as default"
        )

    #save args
    args = input_args.parse_args()
    return args


#defines the detector parameters
class detector_param:
    def __init__(self):
        pass
    
    def pliatus6m(self, centre_pixel, pixel_size=0.172):
        pixel_size = pixel_size
        center = centre_pixel
        #resolution = 2463 x 2527 #(W x H; 423.63mm x 434.64mm)
        pass


def find_bargg_angle():
    """
    2dsin(x) = nλ; 2dsin(x) = λ
    sin(x) = λ/2d;
    cos(x) = (1 - sin(x)^2)^1/2
    sin(2x) = 2sin(x)cos(x)
    """
    pass

#create a dict with the distance and the pixel position (distance: [x, y])
def pixel_distance(self):
    """
    math.dist([x1, y1[], [x2, y2]]) * pixel_size (edge length as square)

    for ix, iy in np.ndindex(i_array.shape):
            print(math.dist([ix, iy], [1263, 1230]) * 0.172)
    """

    pass

#convert the distance to the resolution per pixel, as a dict (resolution: [x, y])
def generate_resolution():
    """
    2x_value = math.atan2(detector_dist, pixel_dist) #get 2x in radiants
    x = math.degrees(2x_value)/2 #get x in degree
    resolution = wavelength/(2 * math.sin(math.radians(x)))

    """
    pass

#mask class, including generate mask, plot mask and save mask
class mask:
    def __init__(self):
        pass

    def generate_mask(self):
        pass

    #plot the mask if requested
    def plot_mask(self):
        pass

    def save_mask(self):
        pass


def main():
    args = process_args()


if __name__ ==  "__main__" :
    main()

