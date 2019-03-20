#!/usr/bin/env python
# Revision $Id$

# Ce noeud trie les personnes renvoyees par translator pour ne garder que la personne a suivre

import rospy
from costmap_converter.msg import ObstacleArrayMsg, ObstacleMsg
from geometry_msgs.msg import Polygon, Point32
import numpy

# Mettre un identifiant sur la personne suivie
# Trouver un processus de validation de la personne choisie pour etre suivie

# Valeurs initiales du centre et de la vitesse de la personne suivie
global speed
global center
speed = numpy.array([0,0])
center = numpy.array([0,0])

def callback(persons,pub,pub_obs):
    tab_pers = persons.obstacles
    if len(tab_pers == 1):
        #Chooses the only person available
        pub.publish(tab_pers[0])
        tmp = center
        center = calculate_center(tab_pers[0].poly)
        speed = center - tmp
    if len(tab_pers) > 1:
        #Finding the person to follow
        expected_center = numpy.add(center,speed)
        centers = numpy.array([calculate_center(obs) for obs in tab_pers])
        delta = numpy.abs(numpy.substract(centers,expected_center))
        index = numpy.argmin(delta)
        #Updating info about the target
        tmp = center
        center = centers[index]
        speed = center - tmp
        tab_pers[index].id = 1
        #Publishing the target as following and the others as obstacles
        pub.publish(tab_pers[index])
        persons.obstacles = tab_pers[:index] + tab_pers[index+1:]
        pub_obs.publish(persons)
        
def calculate_center(obs):
    polygon = obs.polygon
    if (len(polygon.points) >= 4):
        x,y = 0,0
        for i in range(4):
            x+=polygon.points[i].x/4
            y+=polygon.points[i].y/4
        return numpy.array([x,y])
    return (0,0)
        
def follower():
    rospy.init_node('follower', anonymous=True)
    pub = rospy.Publisher('bounding_boxes_analyser/following', ObstacleMsg, queue_size=10)
    pub_obs = rospy.Publisher('bounding_boxes_analyser/yolo_obstacles_messages', ObstacleArrayMsg, queue_size=10)
    # Publie a la reception de chaque message
    rospy.Subscriber('bounding_boxes_analyser/yolo_persons_messages', ObstacleArrayMsg, lambda x: callback(x,pub,pub_obs))
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
    follower()