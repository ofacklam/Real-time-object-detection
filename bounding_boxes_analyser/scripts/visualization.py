#!/usr/bin/env python
# Revision $Id$

# Ce noeud permet la visualisation sur Rviz des bounding boxes analysees
# Les personnes sont representees en rouge et les obstacles en vert
# La personne a suivre est representee en bleu

import rospy
from std_msgs.msg import Header
from costmap_converter.msg import ObstacleArrayMsg, ObstacleMsg
from geometry_msgs.msg import Polygon, Point32
from visualization_msgs.msg import Marker, MarkerArray
#Identifiant pour les obstacles
FOLLOWING = 2
PERSON = 1
OBSTACLE = 0

def callback(obstacle_array, pub):
	# Les anciennes boxes ne sont pas effacees
	# On recupere les boxes par type (1 msg pour les personnes et 1 message pour les obstacles)
	#	ce qui permet de factoriser le code mais empeche la suppression a chaque callback
	mark = Marker()
	mark.ns = 'obstacles'
	mark.type = Marker.LINE_STRIP
	mark.action = Marker.ADD
	mark.scale.x = 0.2
	mark.color.g = 1
	mark.color.a = 1
	if (obstacle_array.obstacles[0].id == PERSON):
		mark.color.r = 1
		mark.color.g = 0
	if (obstacle_array.obstacles[0].id == FOLLOWING):
		mark.color.b = 1
		mark.color.g = 0
	for i in range (len(obstacle_array.obstacles)):
		obs = obstacle_array.obstacles[i]
		mark.header = obs.header
		mark.id = i
		mark.points = obs.polygon.points
		tab.append(mark)
	msgRViz = MarkerArray()
	msgRViz.markers = tab
	pub.publish(msgRviz)
	


def visualization():
	rospy.init_node('visualization', anonymous=True)
	pubRViz = rospy.Publisher('/bounding_boxes_analyser/marker_vision', MarkerArray, queue_size=10)
	# Publie a la reception de chaque message
	rospy.Subscriber('/bounding_boxes_analyser/yolo_persons_messages', ObstacleArrayMsg, lambda x: callback(x,pub))
	rospy.Subscriber('/bounding_boxes_analyser/yolo_obstacles_messages', ObstacleArrayMsg, lambda x: callback(x,pub))

	# spin() simply keeps python from exiting until this node is stopped
	rospy.spin()


if __name__ == '__main__':
    visualization()
