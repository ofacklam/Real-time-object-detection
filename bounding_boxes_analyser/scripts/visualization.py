#!/usr/bin/env python
# Revision $Id$

# Ce noeud permet la visualisation sur Rviz des bounding boxes analysees

def callback(obstacle_array, pub):
	


def visualization():
    rospy.init_node('visualization', anonymous=True)
	pubRViz = rospy.Publisher('/bounding_boxes_analyser/marker_vision', MarkerArray, queue_size=10)
    # Publie a la reception de chaque message
   	rospy.Suscriber('/bounding_boxes_analyser/yolo_persons_messages', ObstacleArrayMsg, lambda x: callback(x,pub))
   	rospy.Suscriber('/bounding_boxes_analyser/yolo_obstacles_messages', ObstacleArrayMsg, lambda x: callback(x,pub))

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
    visualization()
