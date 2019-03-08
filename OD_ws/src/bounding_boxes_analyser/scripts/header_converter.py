#!/usr/bin/env python
# Revision $Id$

#Ce noeud echange image header et header d une image renvoyee par yolo

import rospy
from darknet_ros_msgs.msg import BoundingBoxes

def callback(boxes,pub):
    tmp = boxes.header
    boxes.header = boxes.image_header
    boxes.image_header = tmp
    pub.publish(boxes)
    
def header_converter():
    rospy.init_node('header_converter', anonymous=True)
    pub = rospy.Publisher('bounding_boxes_analyser/bounding_boxes_converted', BoundingBoxes, queue_size=10)
    # Publie a la reception de chaque message
    rospy.Subscriber('/darknet_ros/bounding_boxes', BoundingBoxes, lambda x: callback(x,pub))
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
   header_converter()