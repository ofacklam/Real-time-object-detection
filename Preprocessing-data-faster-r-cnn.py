
# coding: utf-8

# Data preprocessing
# =====

# In order to train our algorithm, we first need to preprocess the data. Indeed, we need to select and download the relevant data for our purpose then split it into a training and testing set.

# In order to train our algorithm, we will use the OpenImages Dataset V4 provided by Google.

# In[80]:


import numpy as np
import time
from tqdm import tqdm_notebook
import sys
import os
import random
from skimage import io
import pandas as pd
from matplotlib import pyplot as plt
from shutil import copyfile

import cv2
import tensorflow as tf


# ### Opening and formatting the .csv data files

# We begin by opening the different data files with `pandas`.

# In[81]:


base_path = '/Data/jon'
images_boxable_fname = 'train-images-boxable.csv'
annotations_bbox_fname = 'train-annotations-bbox.csv'
class_descriptions_fname = 'class-descriptions-boxable.csv'


# First, we open the file `images_boxable` containing the urls of all the images.

# In[82]:


images_boxable = pd.read_csv(os.path.join(base_path, images_boxable_fname))
images_boxable.head()


# Next, we open the file `annotations_bbox` containing the different bouding boxes with the images they are linked to and their coordinates on these images.

# In[83]:


annotations_bbox = pd.read_csv(os.path.join(base_path, annotations_bbox_fname))
annotations_bbox.head()


# Finally, we open the file `class_descriptions` containing the different classes the bouding boxes refer to.

# In[84]:


class_descriptions = pd.read_csv(os.path.join(base_path, class_descriptions_fname),names=['name','class'])
class_descriptions.head()


# In[85]:


print('Number of images in the dataset: %d' %(len(images_boxable))) 
print('Random image in images_boxable')
r = int(1000 * random.random())
img_name = images_boxable['image_name'][r]
img_url = images_boxable['image_url'][r]
print('\t image_name: %s' % (img_name))
print('\t img_url: %s' % (img_url))
print('')
print('Number of bounding boxes: %d' %(len(annotations_bbox)))
print('')
print('Number of classes: %d' % (len(class_descriptions)-1))
img = io.imread(img_url)


# Here's an example of what the dataset looks like

# In[86]:


height, width, _ = img.shape
plt.figure(figsize=(15,10))
plt.subplot(1,2,1)
plt.title('Original image')
plt.imshow(img)
img_id = img_name[:16]
bboxs = annotations_bbox[annotations_bbox['ImageID']==img_id]
img_bbox = img.copy()
for index, row in bboxs.iterrows():
    xmin = row['XMin']
    xmax = row['XMax']
    ymin = row['YMin']
    ymax = row['YMax']
    xmin = int(xmin*width)
    xmax = int(xmax*width)
    ymin = int(ymin*height)
    ymax = int(ymax*height)
    label_name = row['LabelName']
    class_series = class_descriptions[class_descriptions['name']==label_name]
    class_name = class_series['class'].values[0]
    cv2.rectangle(img_bbox,(xmin,ymin),(xmax,ymax),(0,255,0),2)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img_bbox,class_name,(xmin,ymin-10), font, 1,(0,255,0),2)
plt.subplot(1,2,2)
plt.title('Image with bounding boxes')
plt.imshow(img_bbox)
plt.show()


# ### Selecting the relevant data

# In our situation, we don't need to consider all the classes. Therefore, we only select a few relevant classes to train our model.

# In this case, we consider three classes: `Person`, `Obstacle` and `Vehicle`.

# In[87]:


# We find the label_name for 'Person', 'Obstacle' and 'Vehicle' classes
person_pd = class_descriptions[class_descriptions['class']=='Person']
vehicle_pd = class_descriptions[class_descriptions['class']=='Vehicle']
obstacle_pd = class_descriptions[class_descriptions['class']=='Table']

label_name_person = person_pd['name'].values[0]
label_name_vehicle = vehicle_pd['name'].values[0]
label_name_obstacle = obstacle_pd['name'].values[0]


# In[88]:


print(person_pd)
print(vehicle_pd)
print(obstacle_pd)


# Next, we select the bounding boxes then the images that contain one of the three classes we chose to keep.

# In[89]:


person_bbox = annotations_bbox[annotations_bbox['LabelName']==label_name_person]
vehicle_bbox = annotations_bbox[annotations_bbox['LabelName']==label_name_vehicle]
obstacle_bbox = annotations_bbox[annotations_bbox['LabelName']==label_name_obstacle]


# In[90]:


print('There are %d persons in the dataset.' %(len(person_bbox)))
print('There are %d vehicles in the dataset.' %(len(vehicle_bbox)))
print('There are %d obstacles in the dataset.' %(len(obstacle_bbox)))
person_img_id = person_bbox['ImageID']
vehicle_img_id = vehicle_bbox['ImageID']
obstacle_img_id = obstacle_bbox['ImageID']


# In[91]:


person_img_id = np.unique(person_img_id)
vehicle_img_id = np.unique(vehicle_img_id)
obstacle_img_id = np.unique(obstacle_img_id)
print('There are %d images which contain persons.' % (len(person_img_id)))
print('There are %d images which contain vehicles.' % (len(vehicle_img_id)))
print('There are %d images which contain obstacles.' % (len(obstacle_img_id)))


# The OpenImages Dataset V4 is too big to handle. In fact, it would take us several days and a lot of memory space, even if we use computer clustering, to train our model with all the data provided. Therefore, we only select `n = 4000` images per class. The selection is made randomly.

# In[119]:


# We shuffle the ids and pick the first 4000 ids
copy_person_id = person_img_id.copy()
random.seed(1)
random.shuffle(copy_person_id)

copy_vehicle_id = vehicle_img_id.copy()
random.seed(1)
random.shuffle(copy_vehicle_id)

copy_obstacle_id = obstacle_img_id.copy()
random.seed(1)
random.shuffle(copy_obstacle_id)

n = 20    # Number of images per class
subperson_img_id = copy_person_id[:n]
subvehicle_img_id = copy_vehicle_id[:n]
subobstacle_img_id = copy_obstacle_id[:n]


# Now that we know which images we are going to use for training our model, we store their url in separate files for each class.

# In[120]:


# This might take a while to search all these urls
subperson_img_url = [images_boxable[images_boxable['image_name']==name+'.jpg'] for name in subperson_img_id]
print("Person: done.")
subvehicle_img_url = [images_boxable[images_boxable['image_name']==name+'.jpg'] for name in subvehicle_img_id]
print("Vehicle: done.")
subobstacle_img_url = [images_boxable[images_boxable['image_name']==name+'.jpg'] for name in subobstacle_img_id]
print("Obstacle: done.")
print("")
print("All done.")


# In[121]:


subperson_pd = pd.DataFrame()
subvehicle_pd = pd.DataFrame()
subobstacle_pd = pd.DataFrame()
storing_iter = tqdm_notebook(range(len(subperson_img_url)), desc='Storing image data...')
for i in storing_iter:
    subperson_pd = subperson_pd.append(subperson_img_url[i], ignore_index = True)
    subvehicle_pd = subvehicle_pd.append(subvehicle_img_url[i], ignore_index = True)
    subobstacle_pd = subobstacle_pd.append(subobstacle_img_url[i], ignore_index = True)
subperson_pd.to_csv(os.path.join(base_path, 'subperson_img_url.csv'))
subvehicle_pd.to_csv(os.path.join(base_path, 'subvehicle_img_url.csv'))
subobstacle_pd.to_csv(os.path.join(base_path, 'subobstacle_img_url.csv'))
storing_iter.set_description('Storing completed successfully')


# In[122]:


subperson_img_url = [url['image_url'].values[0] for url in subperson_img_url]
subvehicle_img_url = [url['image_url'].values[0] for url in subvehicle_img_url]
subobstacle_img_url = [url['image_url'].values[0] for url in subobstacle_img_url]
urls = [subperson_img_url, subvehicle_img_url, subobstacle_img_url]


# In[123]:


subperson_pd = pd.read_csv('subperson_img_url.csv')
subvehicle_pd = pd.read_csv('subvehicle_img_url.csv')
subobstacle_pd = pd.read_csv('subobstacle_img_url.csv')

subperson_img_url = subperson_pd['image_url'].values
subvehicle_img_url = subvehicle_pd['image_url'].values
subobstacle_img_url = subobstacle_pd['image_url'].values

urls = [subperson_img_url, subvehicle_img_url, subobstacle_img_url]


# In[124]:


# Directories in which our image files will be stored
saved_dirs = [os.path.join(base_path,'Person'),os.path.join(base_path,'Vehicle'),os.path.join(base_path,'Obstacle')]


# In[125]:


# Name of the classes we consider
classes = ['Person', 'Vehicle', 'Obstacle']


# In[126]:


print("Number of urls: ", len(urls[0]))
for i in range(len(urls)):
    if len(urls[i]) == n:
        print("    Creating the url file for class ", classes[i], " was successful.")
    else:
        print("    Error in creating the url file for class ", classes[i], ":")
        print("        ", len(urls[i]), "/", n, " images considered.")
    time.sleep(0.25)


# ### Downloading the images

# Now that we have selected the images we'll use for training our model, we download them.

# In[127]:


# Download images
classes_iter = tqdm_notebook(range(len(classes)), desc='Downloading files...')
for i in classes_iter:
    if not os.path.exists(saved_dirs[i]):
        # Create the directory
        os.mkdir(saved_dirs[i])
    saved_dir = saved_dirs[i]
    pbar = tqdm_notebook(urls[i], desc='Downloading images for class %s...' % classes[i], leave=False)
    for url in pbar:
        img = io.imread(url)
        saved_path = os.path.join(saved_dir, url[-20:])
        if not os.path.exists(saved_path):
            io.imsave(saved_path, img)
classes_iter.set_description('Download successful')


# ### Formatting the data for training

# Now that all the images have been downloaded, we split them into a training and a testing set.

# In[157]:


# Save images to train and test directory
train_path = os.path.join(base_path, 'train')
if not os.path.exists(train_path):
    os.mkdir(train_path)
test_path = os.path.join(base_path, 'test')
if not os.path.exists(test_path):
    os.mkdir(test_path)

t_iter = tqdm_notebook(range(len(classes)))
for i in t_iter:
    t_iter.set_description('Processing class %s...' % classes[i])
    all_imgs = os.listdir(os.path.join(base_path, classes[i]))
    all_imgs = [f for f in all_imgs if not f.startswith('.')]
    random.seed(1)
    random.shuffle(all_imgs)
    
    len_a = len(all_imgs)
    train_imgs = all_imgs[:(3 * len_a) // 4]
    test_imgs = all_imgs[(3 * len_a) // 4:]
    
    # Copy each classes' images to train directory
    for j in range(len(train_imgs)):
        original_path = os.path.join(os.path.join(base_path, classes[i]), train_imgs[j])
        new_path = os.path.join(train_path, train_imgs[j])
        copyfile(original_path, new_path)
    
    # Copy each classes' images to test directory
    for j in range(len(test_imgs)):
        original_path = os.path.join(os.path.join(base_path, classes[i]), test_imgs[j])
        new_path = os.path.join(test_path, test_imgs[j])
        copyfile(original_path, new_path)
t_iter.set_description('Data processed successfully')


# We begin with storing the data relative to the training set in a file `train.csv`

# In[158]:


label_names = [label_name_person, label_name_vehicle, label_name_obstacle]

train_df = pd.DataFrame(columns=['FileName', 'XMin', 'XMax', 'YMin', 'YMax', 'ClassName'])

# Find boxes in each image and put them in a dataframe
train_imgs = os.listdir(train_path)
train_imgs = [name for name in train_imgs if not name.startswith('.')]

train_iter = tqdm_notebook(range(len(train_imgs)), desc='Parse train_imgs')
for i in train_iter:
    img_name = train_imgs[i]
    img_id = img_name[0:16]
    tmp_df = annotations_bbox[annotations_bbox['ImageID']==img_id]
    for index, row in tmp_df.iterrows():
        labelName = row['LabelName']
        for i in range(len(label_names)):
            if labelName == label_names[i]:
                train_df = train_df.append({'FileName': img_name, 
                                            'XMin': row['XMin'], 
                                            'XMax': row['XMax'], 
                                            'YMin': row['YMin'], 
                                            'YMax': row['YMax'], 
                                            'ClassName': classes[i]}, 
                                           ignore_index=True)
train_iter.set_description('train_imgs parsed successfully')


# Then we store the data relative to the testing set in a file `test.csv`

# In[159]:


test_df = pd.DataFrame(columns=['FileName', 'XMin', 'XMax', 'YMin', 'YMax', 'ClassName'])

# Find boxes in each image and put them in a dataframe
test_imgs = os.listdir(test_path)
test_imgs = [name for name in test_imgs if not name.startswith('.')]

test_iter = tqdm_notebook(range(len(test_imgs)), desc='Parse test_imgs')
for i in test_iter:
    img_name = test_imgs[i]
    img_id = img_name[0:16]
    tmp_df = annotations_bbox[annotations_bbox['ImageID']==img_id]
    for index, row in tmp_df.iterrows():
        labelName = row['LabelName']
        for i in range(len(label_names)):
            if labelName == label_names[i]:
                test_df = test_df.append({'FileName': img_name, 
                                            'XMin': row['XMin'], 
                                            'XMax': row['XMax'], 
                                            'YMin': row['YMin'], 
                                            'YMax': row['YMax'], 
                                            'ClassName': classes[i]}, 
                                           ignore_index=True)
test_iter.set_description('test_imgs parsed successfully')


# In[160]:


train_df.to_csv(os.path.join(base_path, 'train.csv'))
test_df.to_csv(os.path.join(base_path, 'test.csv'))


# Now we store all the data in `.txt` files, with reshaping all the bounding boxes.

# Finally, we print the first rows of each of `train.csv` and `test.csv` to check that the data is well formatted.

# In[161]:


print(train_df.head())
train_df = pd.read_csv(os.path.join(base_path, 'train.csv'))

# For training
f= open(base_path + "/annotation.txt","w+")
for idx, row in train_df.iterrows():
    img = cv2.imread((base_path + '/train/' + row['FileName']))
    height, width = img.shape[:2]
    x1 = int(row['XMin'] * width)
    x2 = int(row['XMax'] * width)
    y1 = int(row['YMin'] * height)
    y2 = int(row['YMax'] * height)
    
    google_colab_file_path = 'train'
    fileName = os.path.join(google_colab_file_path, row['FileName'])
    className = row['ClassName']
    f.write(fileName + ',' + str(x1) + ',' + str(y1) + ',' + str(x2) + ',' + str(y2) + ',' + className + '\n')
f.close()
print('')
print('Done.')


# In[162]:


print(test_df.head())
test_df = pd.read_csv(os.path.join(base_path, 'test.csv'))

# For test
f= open(base_path + "/test_annotation.txt","w+")
for idx, row in test_df.iterrows():
    img = cv2.imread((base_path + '/test/' + row['FileName']))
    height, width = img.shape[:2]
    x1 = int(row['XMin'] * width)
    x2 = int(row['XMax'] * width)
    y1 = int(row['YMin'] * height)
    y2 = int(row['YMax'] * height)
    
    google_colab_file_path = 'test'
    fileName = os.path.join(google_colab_file_path, row['FileName'])
    className = row['ClassName']
    f.write(fileName + ',' + str(x1) + ',' + str(y1) + ',' + str(x2) + ',' + str(y2) + ',' + className + '\n')
f.close()
print('')
print('Done.')


# Now that the data has been well preprocessed, we can move to training our algorithm.
