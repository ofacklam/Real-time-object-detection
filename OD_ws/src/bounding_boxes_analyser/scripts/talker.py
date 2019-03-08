#!/usr/bin/env python
# Revision $Id$

## Simple talker demo that published std_msgs/Header messages
## to the 'yolo_messages' topic

import rospy
from std_msgs.msg import Header
from costmap_converter.msg import ObstacleArrayMsg

def talker():
    pub = rospy.Publisher('bounding_boxes_analyser/yolo_messages', ObstacleArrayMsg, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        #msg = 
        #rospy.loginfo(msg)
        #pub.publish(msg)
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
