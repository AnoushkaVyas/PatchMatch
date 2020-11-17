import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image
import cv2

'''
Authors:


Rahul Sajnani
Ajay Shrihari
Anoushka Vyas
Chaitanya Kharyal
'''

def read_image(image_path):
    '''
    Function to read image
    '''

    image = np.asarray(Image.open(image_path))

    return image

    
def plot_images(images_list, plot_dim, cmap="viridis", title = None, subplot_names = None):
    '''
    Function to plot images
    '''
    assert len(images_list) <= (plot_dim[0] * plot_dim[1]), "Number of images is more than the plot dimensions"
    
    fig = plt.figure(figsize=(10,7), dpi= 100, facecolor='w', edgecolor='k')
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.5)
    
    if title is not None:
        fig.suptitle(title, fontsize=15)
    
    index = 1
        
    for image in images_list:
        
        plt.subplot(plot_dim[0], plot_dim[1], index)
        if subplot_names is not None:
            plt.gca().set_title(subplot_names[index - 1])
        plt.imshow(image, cmap = cmap)
        plt.axis("off")
        index += 1
        
    plt.show()

def reconstruct_image(locations, image, image_2):

    loc = locations
    b_cpy = image_2.copy()

    reconstructed_image = np.zeros(image.shape)
    
    for i in range(loc.shape[0]):
        for j in range(loc.shape[1]):
            reconstructed_image[i,j,:] = b_cpy[loc[i,j,0],loc[i,j,1],:]
        reconstructed_image = reconstructed_image.astype(int)

    return reconstructed_image

def get_frames_vid(inp_path, out_path, name_prefix = "frame_",num_images = 80):
    cap = cv2.VideoCapture(inp_path)
    ret, frame = cap.read()
    num_images_count = 0
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    plt.imsave(os.path.join(out_path, name_prefix + str(num_images_count) + ".png"), img)
    while(1):
        num_images_count = num_images_count + 1
        if num_images_count == num_images:
            break
        ret, frame2 = cap.read()
        if ret is False:
            break
        img_next = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
        plt.imsave(os.path.join(out_path, name_prefix + str(num_images_count)+".png"), img_next)




if __name__== "__main__":
    
    pass