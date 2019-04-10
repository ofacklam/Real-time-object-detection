#!/usr/bin/env python
# Revision $Id$

# Ce noeud effectue un changement de repere pour publie dans le repere "odom"
# et publie dans le topic analyser par le gestionnaire de trajectoire du robot

import tf
import numpy as np
import rospy
from std_msgs.msg import Header
from costmap_converter.msg import ObstacleArrayMsg, ObstacleMsg
from geometry_msgs.msg import Polygon, Point32

def calc(R, T, p):
    arr = np.array([p.x, p.y, p.z])
    tmp = np.matmul(R, arr) + T
    
    res = Point32()
    res.x = tmp[0]
    res.y = tmp[1]
    res.z = tmp[2]
    return res

def callback(obstacle_array, pub, listener):
    repere = obstacle_array.header.frame_id
    (trans, quat) = listener.lookupTransform("/odom",repere, rospy.Time(0))
    rot_mat = tf.transformations.quaternion_matrix(quat)

    for i in range(len(obstacle_array.obstacles)):
        for j in range(len(obstacle_array.obstacles[i].polygon.points)):
            obstacle_array.obstacles[i].polygon.points[j] = calc(rot_mat, trans, obstacle_array.obstacles[i].polygon.points[j])

    pub.publish(obstacle_array)

def transformer():
    rospy.init_node('transformer', anonymous=True)
    pub = rospy.Publisher('/ultrasonic_sensors/obstacles', ObstacleArrayMsg, queue_size=10)
    listener = tf.TransformListener()
    # Publie a la reception de chaque message
    rospy.Subscriber('/bounding_boxes_analyser/yolo_persons_messages', ObstacleArrayMsg, lambda x: callback(x,pub, listener))
    rospy.Subscriber('/bounding_boxes_analyser/yolo_obstacles_messages', ObstacleArrayMsg, lambda x: callback(x,pub, listener))

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
    transformer()
