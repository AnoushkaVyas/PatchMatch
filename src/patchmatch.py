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

    def propagation(self, patch_index, is_even = False):
        '''
        Propagation step of patch match
        Arguments:
            is_even: True if it is an even iteration
                     False otherwise
        '''
        if is_even:
            indices =   deepcopy([
                        [patch_index[0]+1, patch_index[1]], 
                        [patch_index[0], patch_index[1]+1]])

            for index in range(len(indices)-1,-1,-1):
                if indices[index][0]+1 >= self.image.shape[0]-self.patch_size or indices[index][1]+1 >= self.image.shape[1]-self.patch_size:
                    indices.pop(index)
            
        else:
            indices =   deepcopy([
                        [patch_index[0]-1, patch_index[1]], 
                        [patch_index[0], patch_index[1]-1]])

            for index in range(len(indices)-1,-1,-1):
                if indices[index][0]-1 < 0 or indices[index][1]-1 < 0:
                    indices.pop(index)

        min_dist = self.nearest_patch_distance[patch_index[0], patch_index[1]]
        min_loc = deepcopy(patch_index)
            
        for index in indices:
            dist = self.calulate_distance(
                self.image[patch_index[0]:patch_index[0]+self.patch_size, patch_index[1]:patch_index[1]+self.patch_size],
                self.image2[index[0]:index[0]+self.patch_size, index[1]:index[1]+self.patch_size]
            )
            if dist<min_dist:
                min_dist = dist
                min_loc = deepcopy(index)
            
        self.nearest_patch_distance[patch_index[0], patch_index[1]] = min_dist
        self.nearest_patch_location[patch_index[0],patch_index[1],:] = np.array(min_loc)    


    def random_search(self, patch_index, alpha = 0.5):
        '''
        Random search step of patch match
        '''
        Ri = np.random.uniform(-1,1,(1,2))
        random_search_magnitude = np.max(self.image.shape)*alpha
        random_search_distance = np.ceil(random_search_magnitude*Ri)
        current_nearest_patch_location = deepcopy(self.nearest_patch_location[patch_index])
        current_nearest_patch_distance = deepcopy(self.nearest_patch_distance[patch_index])

        while any(random_search_distance>1):
            if (current_nearest_patch_location[0]+random_search_distance[0])>self.image.shape[0] - self.patch_size) or (current_nearest_patch_location[1]+random_search_distance[1])>self.image.shape[1] - self.patch_size) or (current_nearest_patch_location[0]+random_search_distance[0])<0) or (current_nearest_patch_location[1]+random_search_distance[1])<0):
                random_search_magnitude = random_search_magnitude*alpha
                Ri = np.random.uniform(-1,1,(1,2))
                random_search_distance = np.ceil(random_search_magnitude*Ri)
                continue

            dist = self.calulate_distance(
                self.image[patch_index[0]:patch_index[0]+self.patch_size, patch_index[1]:patch_index[1]+self.patch_size],
                self.image2[current_nearest_patch_location[0]+random_search_distance[0]:current_nearest_patch_location[0]+random_search_distance[0]+self.patch_size, current_nearest_patch_location[1]+random_search_distance[1]:current_nearest_patch_location[1]+random_search_distance[1]+self.patch_size]
            )
            if dist< self.nearest_patch_distance:
                self.nearest_patch_distance[patch_index] = dist
                self.nearest_patch_location[patch_index] = current_nearest_patch_location+random_search_distance

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


    
    