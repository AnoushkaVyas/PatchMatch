import numpy as np
import cv2
import matplotlib.pyplot as plt
import os, argparse
from helper_functions import *
from copy import deepcopy


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

    def __init__(self, iterations = 5, patch_size = 3):

        self.iterations = iterations
        self.patch_size = patch_size


    def calulate_distance(self, patch_1, patch_2):
        '''
        Function to calulate distance between two given patches

        '''

        dist = np.mean(np.abs(patch_1 - patch_2))
        return dist
    
    def random_init(self, image, image_2):
        '''
        Randomly initialize patches
        '''

        rows = np.random.randint(image.shape[0] - self.patch_size, size = image.shape[:2])
        columns = np.random.randint(image.shape[1] - self.patch_size, size = image.shape[:2])

        h, w, c = image.shape
        self.nearest_patch_location = np.stack([rows, columns], axis = 2)
        self.nearest_patch_distance = np.ones(image.shape[:2])

        for i in range(h - self.patch_size):
            for j in range(w - self.patch_size):

                patch_location = self.nearest_patch_location[i, j, :]
                self.nearest_patch_distance[i, j] = self.calulate_distance(image[i: i + self.patch_size, j:j + self.patch_size, :], image_2[patch_location[0]: patch_location[0] + self.patch_size, patch_location[1]: patch_location[1] + self.patch_size, :])

        # print(np.max(self.nearest_patch_distance), np.min(self.nearest_patch_distance))
        
    def run(self, image, image_2):
        '''
        Patch match run script
        '''
        
        self.random_init(image, image_2)

        pass

    def padding(self, im, filt_sz, pad_type = 'constant'):
        '''
        Padding function
        '''
        f_h,f_w = filt_sz
        if (f_h-1)%2 != 0:
            pad_r = ((f_h-1)//2+1,(f_h-1)//2)
        else :
            pad_r = ((f_h-1)//2,(f_h-1)//2)
        if (f_w-1)%2 != 0:
            pad_w = ((f_w-1)//2+1,(f_w-1)//2)
        else :
            pad_w = ((f_w-1)//2,(f_w-1)//2)
        pad_sz = (pad_r,pad_w)
        im1 = np.pad(im,pad_sz,mode = pad_type)
        return im1

    def col_for_conv(self, is_even = False):
        '''
        Helper for convolution_for_propogation
        '''
        k_h = 2; k_w = 2 
        im = self.padding(deepcopy(self.nearest_patch_distance), (2,2))
        if is_even:
            im = np.rot90(im, 2)
        im_h,im_w = im.shape
        a = np.transpose(((np.arange(im_h - k_h+1)[:,None] + np.arange(im_w - k_w+1)*im_h).ravel(order='F')[:,None]+ np.arange(k_h))[:,:,None],(1,2,0))
        a = np.reshape(a+im_h*np.arange(k_w)[None,:,None],(k_h*k_w,-1),order='F')
        return im.ravel(order='F')[a]
    
    def convolution_for_propogation(self, is_even = False):
        '''
        Does propagation step faster
        '''
        kernel = np.array([[np.inf, 1],[1, 1]])
        im_w, im_h = self.nearest_patch_distance.shape
        k_h,k_w = kernel.shape
        kernel_col = kernel.ravel()[:,None]
        col_dist = self.col_for_conv(is_even)*kernel_col
        patch_distance = np.reshape(np.min(col_dist, axis=0),  (im_h - k_h+1, im_w - k_w+1) ,order='F')
        patch_index = np.reshape(np.argmin(col_dist, axis=0),  (im_h - k_h+1, im_w - k_w+1) ,order='F')
        return patch_distance, patch_index
        

    def propagation(self, is_even = False):
        '''
        Propagation step of patch match
        Arguments:
            is_even: True if it is an even iteration
                     False otherwise
        '''
        patch_distance, patch_index = self.convolution_for_propogation(is_even)
        if is_even:
            patch_distance = np.rot90(patch_distance,2)
            patch_index = np.rot90(patch_distance,2)
            self.nearest_patch_distance = patch_distance        
            for i in range(patch_distance.shape[0]):
                for j in range(patch_distance.shape[1]):
                    if i+1 < patch_distance.shape[0] and j+1<patch_distance.shape[1]:
                        if patch_index[i,j] == 1:
                            self.nearest_patch_distance[i,j,:] = self.nearest_patch_distance[i+1,j,:]
                        elif patch_index[i,j] == 2:
                            self.nearest_patch_distance[i,j,:] = self.nearest_patch_distance[i,j+1,:]
        
        else:
            self.nearest_patch_distance = patch_distance        
            for i in range(patch_distance.shape[0]):
                for j in range(patch_distance.shape[1]):
                    if i-1>=0 and j-1>=0:
                        if patch_index[i,j] == 1:
                            self.nearest_patch_distance[i,j,:] = self.nearest_patch_distance[i-1,j,:]
                        elif patch_index[i,j] == 2:
                            self.nearest_patch_distance[i,j,:] = self.nearest_patch_distance[i,j-1,:]

    def random_search(self):
        '''
        Random search step of patch match
        '''
        pass

if __name__=="__main__":

    #################### Argument Parser #################################

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help = "Input image path", required = True)
    parser.add_argument("--input_2", help = "Input image path 2", required = True)
    args = parser.parse_args()

    ######################################################################

    image = read_image(args.input)
    image_2 = read_image(args.input_2)
    # plot_images([image], (1,1))
    pm = PatchMatch()
    pm.run(image, image_2)

    # pm.run(image)


    
    