import numpy as np
import cv2
import matplotlib.pyplot as plt
import os, argparse
from helper_functions import *

'''
Authors:


Rahul Sajnani
Ajay Shrihari
Anoushka Vyas
Chaitanya Kharyal
'''


class PatchMatch(object):
    '''
    PatchMatch class
    '''

    def __init__(self):

        pass

    def run(self, image, iterations = 5):
        '''
        Patch match run script
        '''
        
        pass

    def propagation(self):
        '''
        Propagation step of patch match
        '''
        pass

    def random_search(self):
        '''
        Random search step of patch match
        '''
        pass

if __name__=="__main__":

    #################### Argument Parser #################################

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help = "Input image path", required = True)
    args = parser.parse_args()

    ######################################################################

    image = plt.imread(args.input)
    
    plot_images([image], (1,1))
    pm = PatchMatch()
    pm.run(image)

    # pm.run(image)


    
    