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
#repere pour la visualisation
repere = '/zed_left_camera_frame'

MAX_OBS = 1000

def callback(obstacle_array, pub):
	# Les anciennes boxes ne sont pas effacees
	# On recupere les boxes par type (1 msg pour les personnes et 1 message pour les obstacles)
	#	ce qui permet de factoriser le code mais empeche la suppression a chaque callback
	tab = []

	mark = Marker()
	mark.ns = 'obstacles'
	mark.type = Marker.LINE_STRIP
	mark.action = Marker.ADD
	mark.scale.x = 0.2
	mark.color.g = 1
	mark.color.a = 1

	# Find obstacle type
	obstacle_type = OBSTACLE
	if (len(obstacle_array.obstacles) > 0 and obstacle_array.obstacles[0].id == PERSON):
		obstacle_type = PERSON
		mark.color.r = 1
		mark.color.g = 0
	if (len(obstacle_array.obstacles) > 0 and obstacle_array.obstacles[0].id == FOLLOWING):
		obstacle_type = FOLLOWING
		mark.color.b = 1
		mark.color.g = 0
	
	# Delete old markers
	delete = Marker()
	mark.action = Marker.DELETE
	for i in range(obstacle_type * MAX_OBS, (obstacle_type+1) * MAX_OBS):
		mark.id = i
		tab.append(delete)
	msgDelete = MarkerArray()
	msgDelete.markers = tab
	pub.publish(msgDelete)

	# Add new objects
	tab = []
	for i in range (len(obstacle_array.obstacles)):
		obs = obstacle_array.obstacles[i]
		mark.header = obs.header
		mark.header.frame_id = repere # On change le repere pour la visualisation
		mark.id = obstacle_type * MAX_OBS + i
		mark.points = obs.polygon.points
		tab.append(mark)
	msgRViz = MarkerArray()
	msgRViz.markers = tab
	pub.publish(msgRViz)
	


def visualization():
	rospy.init_node('visualization', anonymous=True)
	pub = rospy.Publisher('/bounding_boxes_analyser/marker_vision', MarkerArray, queue_size=10)
	# Publie a la reception de chaque message
	rospy.Subscriber('/bounding_boxes_analyser/yolo_persons_messages', ObstacleArrayMsg, lambda x: callback(x,pub))
	rospy.Subscriber('/bounding_boxes_analyser/yolo_obstacles_messages', ObstacleArrayMsg, lambda x: callback(x,pub))

	# spin() simply keeps python from exiting until this node is stopped
	rospy.spin()


if __name__ == '__main__':
    visualization()
