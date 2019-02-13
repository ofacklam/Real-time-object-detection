#!/usr/bin/env python
# Revision $Id$


import rospy
from darknet_ros_msgs.msg import BoundingBoxes
from std_msgs.msg import Header
from costmap_converter.msg import ObstacleArrayMsg, ObstacleMsg
from geometry_msgs.msg import Polygon, Point32
import message_filters
from sensor_msgs.msg import Image
import math
import struct
from visualization_msgs.msg import Marker, MarkerArray

#Reste à faire
    # trouver une profondeur plus précise (faire plusieurs essais avec des tables)
    # detecter les personnes pour en faire une exception avec un seuil d'acceptation

FOV = math.pi/2 # field of view en radian
repere = 'zed_left_camera_frame'

def callback(image_yolo,prof,pub,pubRViz):
    l = len(image_yolo.bounding_boxes)
    tab = []
    tabRViz = []
    for i in range(l):
        # camera -> robot
        # x -> -y
        # y -> -z
        # z -> x
        # les messages sont enregistrés dans le repère de la caméra nommé: 'zed_left_camera_frame' stacké dans repere
        box = image_yolo.bounding_boxes[i]

        point1 = Point32()
        point2 = Point32()

        point1.z = 0
        point2.z = 0

        xcentre = (box.xmax + box.xmin)/2
        ycentre = (box.ymax + box.ymin)/2
        # verifier la nature de l indexation de data
        index = 4*(ycentre * prof.width + xcentre)
        ba = bytearray(prof.data[index : index+4])
        depth = struct.unpack('<f', ba)[0]
        print(depth)
        point1.x = depth
        point2.x = depth

        widthm = 2*depth    #On ne multiplie pas par tan(FOV/2) car cette quantite vaut 1 ici
        point1.y = widthm*(0.5-box.xmin/float(prof.width))
        point2.y = widthm*(0.5-box.xmax/float(prof.width))

        poly = Polygon()
        poly.points = [point1, point2]

        obs = ObstacleMsg()
        obs.header = prof.header
        obs.header.frame_id = repere
        obs.polygon = poly
        # d autres champs de l instance a completer
        
        #Pour la visualisation sous RViz
        mark = Marker()
        mark.id = i
        mark.header = obs.header
        mark.ns = 'obstacles'
        mark.type = Marker.LINE_STRIP
        mark.action = Marker.ADD
        mark.points = poly.points
        mark.scale.x = 0.2
        mark.color.g = 1
        mark.color.a = 1
        tabRViz.append(mark)

        tab.append(obs)

    msg = ObstacleArrayMsg()
    msg.header = prof.header
    msg.obstacles = tab

    pub.publish(msg)
    
    msgRViz = MarkerArray()
    msgRViz.markers = tabRViz
    pubRViz.publish(msgRViz)
            
    
def translator():
    rospy.init_node('translator', anonymous=True)
    pub = rospy.Publisher('bounding_boxes_analyser/yolo_obstacles_messages', ObstacleArrayMsg, queue_size=10)
    pubRViz = rospy.Publisher('bounding_boxes_analyser/marker_vision', MarkerArray, queue_size=10)
    # Publie a la reception de chaque message
    image_yolo = message_filters.Subscriber('/darknet_ros/bounding_boxes', BoundingBoxes)
    prof = message_filters.Subscriber('/zed/depth/depth_registered', Image)
    
    ts = message_filters.ApproximateTimeSynchronizer([image_yolo, prof], 10, 1, allow_headerless=True)
                                                                # queue_size, slop (delta t en s)
    ts.registerCallback(lambda x,y: callback(x,y,pub,pubRViz))

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
    translator()

