#!/usr/bin/env python
# Revision $Id$

# Ce noeud effectue un changement de repere pour publie dans le repere "odom"
# et publie dans le topic analyser par le gestionnaire de trajectoire du robot

from uai_utils.ros_utils.tf_manager import NavTFManager
import rospy
from std_msgs.msg import Header
from costmap_converter.msg import ObstacleArrayMsg, ObstacleMsg

def callback(obstacle_array, pub):
	tf_manager = NavTFManager()
	repere = obstacle_array.header.frame_id
	transform_repere_to_odom = tf_manager.lookup_transform_stamped("/odom",repere)
	permanent_obstacles_odom = tf_manager.transformObstArrayFrame(transform_repere_to_odom, obstacle_array)
	pub.publish(permanent_obstacles_odom)

def transformer():
    rospy.init_node('transformer', anonymous=True)
    pub = rospy.Publisher('/ultrasonic_sensors/obstacles', ObstacleArrayMsg, queue_size=10)
    # Publie a la reception de chaque message
    rospy.Subscriber('/bounding_boxes_analyser/yolo_persons_messages', ObstacleArrayMsg, lambda x: callback(x,pub))
    rospy.Subscriber('/bounding_boxes_analyser/yolo_obstacles_messages', ObstacleArrayMsg, lambda x: callback(x,pub))

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
    transformer()