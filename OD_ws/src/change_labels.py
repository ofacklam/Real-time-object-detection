#!/usr/bin/env python

import os

LABELS_1 = '/home/ofacklam/Documents/PSC/Real-time-object-detection/OD_ws/src/darknet_ros/darknet/COCO_data/coco/labels/train2014'
LABELS_2 = '/home/ofacklam/Documents/PSC/Real-time-object-detection/OD_ws/src/darknet_ros/darknet/COCO_data/coco/labels/val2014'

IMAGES_1 = '/home/ofacklam/Documents/PSC/Real-time-object-detection/OD_ws/src/darknet_ros/darknet/COCO_data/coco/images/train2014'
IMAGES_2 = '/home/ofacklam/Documents/PSC/Real-time-object-detection/OD_ws/src/darknet_ros/darknet/COCO_data/coco/images/val2014'

for file in os.listdir(LABELS_1):
    f = open(os.path.join(LABELS_1, file), 'r')
    lines = f.readlines()
    target = open(os.path.join(IMAGES_1, file), 'w')
    for l in lines:
        a = l.split(' ')
        target.write(('1' if int(a[0]) > 0 else '0') + ' ' + a[1] + ' ' + a[2] + ' ' + a[3] + ' ' + a[4] + '\n')
    target.close()
    f.close()
    
for file in os.listdir(LABELS_2):
    f = open(os.path.join(LABELS_2, file), 'r')
    lines = f.readlines()
    target = open(os.path.join(IMAGES_2, file), 'w')
    for l in lines:
        a = l.split(' ')
        target.write(('1' if int(a[0]) > 0 else '0') + ' ' + a[1] + ' ' + a[2] + ' ' + a[3] + ' ' + a[4] + '\n')
    target.close()
    f.close()
    
