#!/usr/bin/env python
# Revision $Id$

# Ce noeud effectue un changement de repere pour publie dans le repere "odom"
# et publie dans le topic analyser par le gestionnaire de trajectoire du robot

from uai_utils.ros_utils.tf_manager import NavTFManager
tf_manager = NavTFManager()

def callback(obstacle_array, pub):
	repere = obstacle_array.header.frame_id
	transform_repere_to_odom = tf_manager.lookout_transform_stamped(repere,"/odom")
	permanent_obstacles_odom = tf_manager.transformObstArrayFrame(transform_repere_to_odom, obstacle_array)
	pub.publish(permanent_obstacles_odom)

def transfomer():
    rospy.init_node('transformer', anonymous=True)
    pub = rospy.Publisher('/ultrasonic_sensors/obstacles', ObstacleArrayMsg, queue_size=10)
    # Publie a la reception de chaque message
    rospy.Suscriber('/bounding_boxes_analyser/yolo_persons_messages', ObstacleArrayMsg, lambda x: callback(x,pub))
    rospy.Suscriber('/bounding_boxes_analyser/yolo_obstacles_messages', ObstacleArrayMsg, lambda x: callback(x,pub))

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
    transformer()
