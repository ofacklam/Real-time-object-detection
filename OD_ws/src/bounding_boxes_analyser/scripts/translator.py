#!/usr/bin/env python
# Revision $Id$

## Simple talker demo that listens to std_msgs/Strings published 
## to the 'chatter' topic

import rospy
from darknet_ros_msgs.msg import BoundingBoxes
from std_msgs.msg import Header
from costmap_converter.msg import ObstacleArrayMsg
import message_filters
from sensor_msgs.msg import Image
import math

FOV = math.pi/2 # field of view en radian

def callback(image_yolo, prof, pub):
	l = len(image_yolo.bounding_boxes)
	tab = []
	for i in range(l):
		# camera -> robot
		# x -> -y
		# y -> -z
		# z -> x
		box = image_yolo.bounding_boxes[i]

		point1 = Point32()
		point2 = Point32()

		point1.z = 0
		point2.z = 0

		xcentre = (box.xmax + box.xmin)/2
		ycentre = (box.ymax + box.ymin)/2
		# verifier la nature de l indexation de data
		depth = prof.data[ycentre*prof.step + xcentre]
		point1.x = depth
		ponit2.x = depth

		widthm = 2*depth*math.tan(FOV/2)
		point1.y = widthm*(0.5-box.xmin/prof.width)
		point2.y = widthm*(0.5-box.xmax/prof.width)

		poly = Polygon()
		poly.points = [point1, point2]

		obs = ObstacleMsg()
		obs.header = prof.header
		obs.polygon = poly
		# d autres champs de l instance a completer

		tab.append(obs)

	msg = ObstacleArrayMsg()
	msg.header = prof.header
	msg.obstacles = tab

	pub.publish(msg)
			
	

def translator():
    rospy.init_node('translator', anonymous=True)
    pub = rospy.Publisher('bounding_boxes_analyser/yolo_messages', ObstacleArrayMsg, queue_size=10)
	# Publie a la reception de chaque message
    image_yolo = message_filters.Subscriber('/darknet_ros/bounding_boxes', BoundingBoxes)
	prof = message_filters.Subscriber('/zed/depth/depth_registered', Image)

	ts = message_filters.ApproximateTimeSynchronizer([image_yolo, prof], 30, 0.1, allow_headerless=True)
	ts.registerCallback(lambda x,y: callback(x,y,pub))

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
    translator()

