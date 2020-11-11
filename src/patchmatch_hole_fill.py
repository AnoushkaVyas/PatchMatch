import numpy as np
import cv2
import matplotlib.pyplot as plt
import os, argparse
from helper_functions import *
from copy import deepcopy
from tqdm import tqdm
import mahotas
from skimage.morphology import binary_dilation, rectangle
from skimage.color import lab2rgb, rgb2lab

import sys
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
        self.sigma = patch_size * patch_size

    def calculate_distance(self, patch_1, patch_2, mask):
        '''
        Function to calculate distance between two given patches

        '''

        if np.sum(mask) * 10 > self.patch_size * self.patch_size:
           return 10000

        dist = np.sqrt(np.sum(np.square(patch_1 - patch_2)))
        return dist
    
    def index_in_mask(self, index, mask_bbox):
        '''
        Function to check if index is in mask
        '''

        y = index[0]
        x = index[1]

        if ((x >= mask_bbox["w_min"]) and (x <= mask_bbox["w_max"])) and ((y >= mask_bbox["h_min"]) and (y <= mask_bbox["h_max"])):
            return True        

        else:
            return False


    def random_init_mask(self, image, mask, mask_bbox):
        '''
        Randomly initialize patches
        '''

        
        random_assign = np.random.randint(2, size = image.shape[:2])
        image_indices = np.indices(image.shape[:2])
        rows = image_indices[0]
        columns = image_indices[1]
        mask_new = np.zeros(mask.shape)
        mask_new[mask_bbox["h_min"]: mask_bbox["h_max"], mask_bbox["w_min"]:mask_bbox["w_max"]] = 1
        

        rand_x = (np.random.randint(mask_bbox["h_min"] - self.patch_size, size = image.shape[:2]) * (random_assign < 0.5) + (random_assign >= 0.5) * (mask_bbox["h_max"] + np.random.randint(image.shape[0] - mask_bbox["h_max"] - self.patch_size, size = image.shape[:2])))

        rows[mask_new== 1] = rand_x[mask_new== 1]
        random_assign = np.random.randint(2, size = image.shape[:2])

        rand_y = (np.random.randint(mask_bbox["w_min"] - self.patch_size, size = image.shape[:2]) * (random_assign < 0.5) + (random_assign >= 0.5) * (mask_bbox["w_max"] + np.random.randint(image.shape[1] - mask_bbox["w_max"] - self.patch_size, size = image.shape[:2])))

        columns[mask_new== 1] = rand_y[mask_new== 1]        
        rows[rows < 0] = 0
        columns[columns < 0] = 0

        rows[rows >= image.shape[0]] = image.shape[0]
        columns[columns >= image.shape[1]] = image.shape[1]
        
        h, w, c = image.shape

        self.nearest_patch_location = np.stack([rows, columns], axis = 2)
        self.nearest_patch_distance = np.ones(image.shape[:2])

        
        for i in range(h - self.patch_size):
            for j in range(w - self.patch_size):

                
                patch_location = self.nearest_patch_location[i, j, :]
                self.nearest_patch_distance[i, j] = self.calculate_distance(
                image[i: i + self.patch_size, j:j + self.patch_size, :],
                
                image[patch_location[0]: patch_location[0] + self.patch_size, patch_location[1]: patch_location[1] + self.patch_size, :], 
                
                self.mask[patch_location[0]: patch_location[0] + self.patch_size, patch_location[1]: patch_location[1] + self.patch_size])

                # if self.nearest_patch_distance[i, j] > 0  and (self.index_in_mask(self.nearest_patch_location[i, j], mask_bbox)):
                #     print(i, j, self.nearest_patch_distance[i, j])
                    
    def run_with_resizing(self, image, image2):

        sizes1 = [[int(image.shape[0]/4), int(image.shape[1]/4)], [int(image.shape[0]/2), int(image.shape[1]/2)], [image.shape[0], image.shape[1]]]
        sizes2 = [[int(image2.shape[0]/4), int(image2.shape[1]/4)], [int(image2.shape[0]/2), int(image2.shape[1]/2)], [image2.shape[0], image2.shape[1]]]
        image_cpy = deepcopy(image)
        image2_cpy = deepcopy(image2)

        init_required = True
        k = 0
        for size1, size2 in zip(sizes1, sizes2):
            image = cv2.resize(image_cpy, (size1[1],size1[0]))
            image_2 = cv2.resize(image2_cpy, (size2[1],size2[0]))
            
            if init_required:
                # print(image.shape, image_2.shape)
                self.random_init(image, image_2)
                init_required = False

            else:
                self.nearest_patch_distance = cv2.resize(self.nearest_patch_distance.astype('float32'), (size1[1],size1[0]))
                self.nearest_patch_location = cv2.resize(self.nearest_patch_location.astype('float32'), (size1[1],size1[0]))

                self.nearest_patch_location[:,:,0] = ((self.nearest_patch_location[:,:,0]/sizes1[k-1][0])*(size1[0]-self.patch_size)).astype(int)
                self.nearest_patch_location[:,:,1] = ((self.nearest_patch_location[:,:,1]/sizes1[k-1][1])*(size1[1]-self.patch_size)).astype(int)
                self.nearest_patch_location = (self.nearest_patch_location).astype(int)
                
                for i in range(image.shape[0] - self.patch_size):
                    for j in range(image.shape[1] - self.patch_size):
                        patch_location = self.nearest_patch_location[i, j, :]
                        self.nearest_patch_distance[i, j] = self.calculate_distance(image[i: i + self.patch_size, j:j + self.patch_size, :], 
                        image_2[patch_location[0]: patch_location[0] + self.patch_size, patch_location[1]: patch_location[1] + self.patch_size, :], 
                        self.mask[patch_location[0]: patch_location[0] + self.patch_size, patch_location[1]: patch_location[1] + self.patch_size])



            is_even = False
            for iteration in tqdm(range(self.iterations)):

                if iteration%2 == 0:
                    is_even = True
                else:
                    is_even = False
                # print(size1)
                for i in range(image.shape[0] - self.patch_size):
                    for j in range (image.shape[1] - self.patch_size):
                        # print(i,j)
                        self.propagation(image, image_2, [i,j], is_even)
                        self.random_search(image, image_2, [i,j])
            k = k+1

        return self.nearest_patch_distance, self.nearest_patch_location


    def get_bbox(self, mask):

        '''
        Obtain bounding box for mask
        '''
        
        bbox = {}
        bbox["h_min"] = np.min( np.where(mask == 1)[0])
        bbox["w_min"] = np.min( np.where(mask == 1)[1])
        bbox["h_max"] = np.max( np.where(mask == 1)[0])
        bbox["w_max"] = np.max( np.where(mask == 1)[1])
        
        return bbox
        

    def run_hole_filling(self, image, mask, with_resize = False):
        '''
        Patch match run script
        '''

        np.random.seed(1024)
        masked_image = np.random.uniform(0, 255, size = image.shape)
        masked_image[mask == 0] = image[mask == 0].copy()
        
        masked_image = rgb2lab(masked_image.copy())
        image = rgb2lab(image.copy())



        self.mask = mask
        self.mask_bbox = self.get_bbox(mask)

        self.random_init_mask(image, mask, self.mask_bbox)
        is_even = False
        # masked_image = image.copy()
        # masked_image[mask == 1] = 0
        # plot_images([masked_image], (1,1))
        for iteration in tqdm(range(self.iterations)):
            
            if iteration%2 == 0:
                is_even = True
            else:
                is_even = False

            for i in range(self.mask_bbox["h_min"], self.mask_bbox["h_max"]):
                for j in range (self.mask_bbox["w_min"], self.mask_bbox["w_max"]):
                    
                    self.propagation(masked_image, image, [i,j], is_even)
                    self.random_search(masked_image, image, [i,j])

        return self.voting_image(image)
        # return self.nearest_patch_distance, self.nearest_patch_location

    def propagation(self, image, image2, patch_index, is_even = False):
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
                if indices[index][0] >= image.shape[0]-self.patch_size or indices[index][1] >= image.shape[1]-self.patch_size:
                    indices.pop(index)
            
        else:
            indices =   deepcopy([
                        [patch_index[0]-1, patch_index[1]], 
                        [patch_index[0], patch_index[1]-1]])

            for index in range(len(indices)-1,-1,-1):
                if indices[index][0] < 0 or indices[index][1] < 0:
                    indices.pop(index)

        min_dist = deepcopy(self.nearest_patch_distance[patch_index[0], patch_index[1]])
        min_loc = deepcopy(self.nearest_patch_location[patch_index[0],patch_index[1]])
            
        for index in indices:
            if not self.index_in_mask(index, self.mask_bbox):
                # print(self.nearest_patch_location[index[0], index[1]])
                dist = self.calculate_distance(
                    image[patch_index[0]:patch_index[0]+self.patch_size, patch_index[1]:patch_index[1]+self.patch_size],
                    image2[self.nearest_patch_location[index[0], index[1]][0]:self.nearest_patch_location[index[0], index[1]][0]+self.patch_size, self.nearest_patch_location[index[0], index[1]][1]:self.nearest_patch_location[index[0], index[1]][1]+self.patch_size], 
                    self.mask[self.nearest_patch_location[index[0], index[1]][0]:self.nearest_patch_location[index[0], index[1]][0]+self.patch_size, self.nearest_patch_location[index[0], index[1]][1]:self.nearest_patch_location[index[0], index[1]][1]+self.patch_size]
                    #####################
                )
                if dist<min_dist:
                    min_dist = dist
                    min_loc = deepcopy(self.nearest_patch_location[index[0],index[1]])
                
        self.nearest_patch_distance[patch_index[0], patch_index[1]] = min_dist
        self.nearest_patch_location[patch_index[0],patch_index[1],:] = np.array(min_loc)    


    def random_search(self, image, image2, patch_index, alpha = 0.5):
        '''
        Random search step of patch match
        '''
        patch_index = np.array(patch_index)
        Ri = np.random.uniform(-1,1,(1,2)); Ri = Ri[0]
        random_search_magnitude = np.max(image2.shape)*alpha
        random_search_distance = np.ceil(random_search_magnitude*Ri).astype(int)
        current_nearest_patch_location = deepcopy(self.nearest_patch_location[patch_index[0], patch_index[1]])
        current_nearest_patch_distance = deepcopy(self.nearest_patch_distance[patch_index[0], patch_index[1]])

        while random_search_distance[0]>1 or random_search_distance[1]>1:
            if ((current_nearest_patch_location[0]+random_search_distance[0])>image2.shape[0] - self.patch_size -1) or ((current_nearest_patch_location[1]+random_search_distance[1])>image2.shape[1] - self.patch_size -1) or ((current_nearest_patch_location[0]+random_search_distance[0])<0) or ((current_nearest_patch_location[1]+random_search_distance[1])<0):
                random_search_magnitude = random_search_magnitude*alpha
                Ri = np.random.uniform(-1,1,(1,2)); Ri = Ri[0]
                random_search_distance = np.ceil(random_search_magnitude*Ri).astype(int)
                continue
            
            if not self.index_in_mask((current_nearest_patch_location[0]+random_search_distance[0], current_nearest_patch_location[1]+random_search_distance[1]), self.mask_bbox):
                dist = self.calculate_distance(
                    image[patch_index[0]:patch_index[0]+self.patch_size, patch_index[1]:patch_index[1]+self.patch_size],
                    image2[current_nearest_patch_location[0]+random_search_distance[0]:current_nearest_patch_location[0]+random_search_distance[0]+self.patch_size, current_nearest_patch_location[1]+random_search_distance[1]:current_nearest_patch_location[1]+random_search_distance[1]+self.patch_size],
                    self.mask[current_nearest_patch_location[0]+random_search_distance[0]:current_nearest_patch_location[0]+random_search_distance[0]+self.patch_size, current_nearest_patch_location[1]+random_search_distance[1]:current_nearest_patch_location[1]+random_search_distance[1]+self.patch_size]
                )
                if dist< self.nearest_patch_distance[patch_index[0], patch_index[1]]:
                    self.nearest_patch_distance[patch_index[0],patch_index[1]] = dist
                    self.nearest_patch_location[patch_index[0],patch_index[1],:] = current_nearest_patch_location+random_search_distance
                
            random_search_magnitude = random_search_magnitude*alpha
            Ri = np.random.uniform(-1,1,(1,2)); Ri = Ri[0]
            random_search_distance = np.ceil(random_search_magnitude*Ri).astype(int)

    def voting_image(self, image):
        
        image_bp = image.copy()
        
        out_image = np.zeros(image.shape)
        out_image_count = np.zeros(image.shape)
        
        for i in range(self.mask_bbox["h_min"], self.mask_bbox["h_max"] ):
            for j in range (self.mask_bbox["w_min"], self.mask_bbox["w_max"] ):

                loc = self.nearest_patch_location[i, j]    
                d = self.nearest_patch_distance[i, j]
                sim = np.exp(-d / (2*self.sigma**2))
                out = out_image[i:i+self.patch_size, j:j+self.patch_size] + image[loc[0]:loc[0]+self.patch_size, loc[1]:loc[1] + self.patch_size].copy() * sim

                out_image[i:i+self.patch_size, j:j+self.patch_size] = out
                out_image_count[i:i+self.patch_size, j:j+self.patch_size] += sim

        for i in range(self.mask_bbox["h_min"], self.mask_bbox["h_max"] ):
            for j in range (self.mask_bbox["w_min"], self.mask_bbox["w_max"] ):
                if out_image_count[i, j, 0] > 0:

                    out_image[i, j, 0] = (out_image[i, j, 0] / out_image_count[i, j, 0])
                    out_image[i, j, 1] = (out_image[i, j, 1] / out_image_count[i, j, 1])
                    out_image[i, j, 2] = (out_image[i, j, 2] / out_image_count[i, j, 2])

        out_image = out_image
        mask_new = np.zeros(image.shape[:2])
        mask_new[self.mask_bbox["h_min"]: self.mask_bbox["h_max"], self.mask_bbox["w_min"]: self.mask_bbox["w_max"]] = 1
        out_image[mask_new == 0] = image_bp[mask_new == 0]
        
        return lab2rgb(out_image)
        
if __name__=="__main__":

    #################### Argument Parser #################################

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help = "Input image path", required = True)
    parser.add_argument("--input_2", help = "Input image path 2", required = True)
    args = parser.parse_args()

    ######################################################################

    image = read_image(args.input)
    
    image_2 = read_image(args.input_2)
    
    if image_2.max() != 0:
        image_2 = image_2 / image_2.max()
        image_2 = (image_2 > 0.5)*1

    image_2 = binary_dilation(image_2, rectangle(5, 5))

    pm = PatchMatch(50, 3)
    image_out = pm.run_hole_filling(image, image_2)
    # dist, loc = pm.run_hole_filling(image_new, image_2)

    # image_out = reconstruct_image(loc, image, image)
    plot_images([image_out], (1,1))
    
    # pm.run(image)


    
    