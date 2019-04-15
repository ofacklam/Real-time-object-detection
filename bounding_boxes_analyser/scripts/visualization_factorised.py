#!/usr/bin/env python
# Revision $Id$

# Ce noeud trie les objets renvoyes par yolo et les transforment en ObstacleArrayMsg
# Ce noeud permet aussi la visualisation sur Rviz des bounding boxes analysees
# Les personnes sont representees en rouge et les obstacles en vert
# La personne a suivre est representee en bleu


import rospy
from darknet_ros_msgs.msg import BoundingBoxes
from std_msgs.msg import Header
from costmap_converter.msg import ObstacleArrayMsg, ObstacleMsg
from geometry_msgs.msg import Polygon, Point32
import message_filters
from sensor_msgs.msg import Image
import math
import struct
import random
import numpy
import time
from visualization_msgs.msg import Marker, MarkerArray

FOV = math.pi/2 # field of view en radian
repere = "zed_left_camera_frame"
profondeur = 1 #profondeur de la boite renvoyee
prob_personne = 0.7 #sueil de detection pour les personnes

#Identifiant pour les obstacles
FOLLOWING = 2
PERSON = 1
OBSTACLE = 0
#Memoire du nombre de marker affiches
nb_person_marker = 0
nb_obs_marker = 0

MAX_OBS = 100

def callback(image_yolo,prof,pub,pub_pers,pub_viz):
    l = len(image_yolo.bounding_boxes)
    tab = []
    tab_pers = []
    tab_viz = [] 

    for i in range(l):
        # image -> repere de la camera
        # x -> -y
        # y -> -z
        # z -> x
        # les messages sont enregistres dans le repere de la camera nomme: 'zed_left_camera_frame'/'asus_camera_link' stocke dans repere
        box = image_yolo.bounding_boxes[i]

        point1 = Point32()
        point2 = Point32()
        point3 = Point32()
        point4 = Point32()
       
        point1.z = 0
        point2.z = 0
        point3.z = 0
        point4.z = 0
        
        start = time.time()
        depth = depthNumpy(box,prof)
        point1.x = depth
        point2.x = depth
        point3.x = depth+profondeur
        point4.x = depth+profondeur
        end = time.time()

        widthm = 2*depth    #On ne multiplie pas par tan(FOV/2) car cette quantite vaut 1 ici
        point1.y = widthm*(0.5-box.xmin/float(prof.width))
        point2.y = widthm*(0.5-box.xmax/float(prof.width))
        point3.y = point2.y
        point4.y = point1.y

        poly = Polygon()
        poly.points = [point1, point2, point3, point4, point1]

        obs = ObstacleMsg()
        obs.header = prof.header
        obs.header.frame_id = repere
        obs.polygon = poly
        # d autres champs de l instance a completer

        print('depth: ' + str(depth))
        print('depth time (en s): ' + str(end - start))
        print('yolo_time (en ns): ' + str(image_yolo.image_header.stamp - image_yolo.header.stamp))
        # Cette valeur est souvent negative => ont ne compare pas les bonnes images 
        # => continuite donc a une ou deux image pres ce n est pas tres grave
        # Une selection par image plutot que par temps n'est pas top
        # On peut changer l'integration de ros pour avoir les 2 memes time stamp
        print

        # Default marker for following
        mark = Marker()
        mark.ns = 'obstacles'
        mark.header = image_yolo.header
        mark.header.frame_id = repere # On change le repere pour la visualisation
        mark.type = Marker.LINE_STRIP
        mark.action = Marker.ADD
        mark.scale.x = 0.2
        mark.color.b = 1
        mark.color.a = 1
        
        #Tri dichotomique entre les personnes et les obstacles
        if box.Class == "person" and box.probability > prob_personne:
            obs.id = PERSON
            tab_pers.append(obs)
            mark.color.r = 1
            mark.color.b = 0
        else:
            obs.id = OBSTACLE
            tab.append(obs)
            mark.color.g = 1
            mark.color.b = 0

		#Pour la visualisation
        mark.id = obs.id * MAX_OBS + i
        mark.points = poly.points
        tab_viz.append(mark)

    #Semble etre bon mais un seul marker afficher a chaque fois...
    #Verifier le numero d'identifiant ?

	#Actualisation de la memoire
    global nb_person_marker
    global nb_obs_marker
    nb_person_marker = len(tab_pers)
    nb_obs_marker = len(tab)

	#Envoi des messages
    msg = ObstacleArrayMsg()
    msg.header = prof.header
    msg.header.frame_id = repere
    msg.obstacles = tab
	
    msg_pers = ObstacleArrayMsg()
    msg_pers.header = prof.header
    msg_pers.header.frame_id = repere
    msg_pers.obstacles = tab_pers

    delete = Marker()
    delete.action = Marker.DELETEALL
    msg_del = MarkerArray()
    msg_del.markers = [delete]

    msg_viz = MarkerArray()
    msg_viz.markers = tab_viz

    pub.publish(msg)
    pub_pers.publish(msg_pers)
    pub_viz.publish(msg_del)
    pub_viz.publish(msg_viz)

def depthNumpy(box,prof):
    #Renvoie la profondeur minimale
    ba = bytearray(prof.data)
    depthmap = numpy.frombuffer(ba,dtype=numpy.float32)
    depthmap = depthmap.reshape((prof.height,prof.width))
    depthmap = depthmap[box.ymin:box.ymax,box.xmin:box.xmax]
    return numpy.nanmin(numpy.abs(depthmap))
        
def visualization():
    rospy.init_node('visualization', anonymous=True)
    pub = rospy.Publisher('/bounding_boxes_analyser/yolo_obstacles_messages', ObstacleArrayMsg, queue_size=10)
    pub_pers = rospy.Publisher('/bounding_boxes_analyser/yolo_persons_messages', ObstacleArrayMsg, queue_size=10)
    pub_viz = rospy.Publisher('/bounding_boxes_analyser/marker_vision', MarkerArray, queue_size=10)
	# Publie a la reception de chaque message
    image_yolo = message_filters.Subscriber('/bounding_boxes_analyser/bounding_boxes_converted', BoundingBoxes)
    prof = message_filters.Subscriber('/zed/depth/depth_registered', Image)
    
    ts = message_filters.TimeSynchronizer([image_yolo, prof], 10)
                                                             # queue_size
    ts.registerCallback(lambda x,y: callback(x,y,pub,pub_pers,pub_viz))

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
    visualization()