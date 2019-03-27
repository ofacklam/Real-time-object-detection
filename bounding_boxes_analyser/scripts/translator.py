#!/usr/bin/env python
# Revision $Id$

# Ce noeud trie les objets renvoyes par yolo et les transforment en ObstacleArrayMsg

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

#Reste a faire
    # rajouter de quoi evaluer temporellement les performances

FOV = math.pi/2 # field of view en radian
repere = 'asus_camera_link'
profondeur = 1 #profondeur de la boite renvoyee
prob_personne = 0.7 #sueil de detection pour les personnes

def callback(image_yolo,prof,pub,pub_pers,pubRViz):
    l = len(image_yolo.bounding_boxes)
    tab = []
    tab_pers=[]
    tabRViz = []
    depth_time = []
    yolo_time = []
    mark = Marker()
    mark.action = Marker.DELETEALL
    markers = MarkerArray()
    markers.markers = [mark]
    pubRViz.publish(markers)
    for i in range(l):
        # camera -> robot
        # x -> -y
        # y -> -z
        # z -> x
        # les messages sont enregistres dans le repere de la camera nomme: 'zed_left_camera_frame' stocke dans repere
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

        depth_time.append(end - start)
        yolo_time.append(image_yolo.image_header.stamp - image_yolo.header.stamp)
        print('depth: ' + str(depth))
        print('depth time (en s): ' + str(depth_time[-1]))
        print('yolo_time (en ns): ' + str(yolo_time[-1]))
        # Cette valeur est souvent negative => ont ne compare pas les bonnes images 
        # => continuite donc a une ou deux image pres ce n est pas tres grave
        # Une selection par image plutot que par temps n'est pas top
        # On peut changer l'integration de ros pour avoir les 2 memes time stamp
        print 
        
        if box.Class == "person" and box.probability > prob_personne:
            tab_pers.append(obs)
            #Pour la visualisation sous RViz - les personnes sont en rouge
            mark = Marker()
            mark.id = i
            mark.header = obs.header
            mark.ns = 'obstacles'
            mark.type = Marker.LINE_STRIP
            mark.action = Marker.ADD
            mark.points = poly.points
            mark.scale.x = 0.2
            mark.color.r = 1
            mark.color.a = 1
            tabRViz.append(mark)
        else:
            tab.append(obs)
            #Pour la visualisation sous RViz - les obstacles sont en vert
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

    msg = ObstacleArrayMsg()
    msg.header = prof.header
	msg.header.frame_id = repere
    msg.obstacles = tab

    msg_pers = ObstacleArrayMsg()
    msg_pers.header = prof.header
    msg_pers.obstacles = tab_pers

    pub.publish(msg)
    pub_pers.publish(msg_pers)
    
    msgRViz = MarkerArray()
    msgRViz.markers = tabRViz
    pubRViz.publish(msgRViz)

def depth(x,y,prof):
    #Renvoie la profondeur du point de coordonees (x,y)
    index = 4*(y * prof.width + x)
    ba = bytearray(prof.data[index : index+4])
    depth = struct.unpack('<f', ba)[0]
    if numpy.isnan(depth) or numpy.isinf(depth):
        return numpy.inf
    return depth

def depthNumpy(box,prof):
    #Renvoie la profondeur minimale
    ba = bytearray(prof.data)
    depthmap = numpy.frombuffer(ba,dtype=numpy.float32)
    depthmap = depthmap.reshape((prof.height,prof.width))
    depthmap = depthmap[box.ymin:box.ymax,box.xmin:box.xmax]
    return numpy.nanmin(numpy.abs(depthmap))

def depth1(box,prof):
    #Renvoie la profondeur du centre
    xcentre = (box.xmax + box.xmin)/2
    ycentre = (box.ymax + box.ymin)/2
    # verifier la nature de l indexation de data
    return depth(xcentre,ycentre,prof)

def depth2(box,prof):
    #Renvoie la profondeur minimale
    mini = depth(box.xmin,box.ymin,prof)
    for x in range(box.xmin,box.xmax):
        for y in range(box.ymin,box.ymax):
            current_depth = depth(x,y,prof)
            if current_depth < mini:
                mini = current_depth
    return mini

def depth3(box,prof):
    #Renvoie la profondeur minimale sur une croix +
    xcentre = (box.xmax + box.xmin)/2
    ycentre = (box.ymax + box.ymin)/2
    mini = depth(xcentre,ycentre,prof)
    for x in range(box.xmin,box.xmax):
        current_depth = depth(x,ycentre,prof)
        if current_depth < mini:
            mini = current_depth
    for y in range(box.ymin,box.ymax):
            current_depth = depth(xcentre,y,prof)
            if current_depth < mini:
                mini = current_depth
    return mini
    
def depth4(box,prof):
    #Renvoie la profondeur minimale sur une croix x
    mini = depth(box.xmin,box.ymin,prof)
    m = (box.ymax - box.ymin)/float(box.xmax - box.xmin)
    y1 = box.ymin
    y2 = box.ymax - 1
    x = box.xmin
    while y1 < box.ymax and y2 > box.ymin and x < box.xmax:
        current_depth1 = depth(x,int(y1),prof)
        current_depth2 = depth(x,int(y2),prof)
        current_depth = min (current_depth1,current_depth2)
        if current_depth < mini:
            mini = current_depth
        y1 += m
        y2 -= m
        x += 1
    return mini

def depth5(box,prof):
    #Renvoie la profondeur minimale sur 100 points aleatoires
    mini = depth(box.xmin,box.ymin,prof)
    for i in range(100):
        x = random.randint(box.xmin,box.xmax-1)
        y = random.randint(box.ymin,box.ymax-1)
        current_depth = depth(x,y,prof)
        if current_depth < mini:
            mini = current_depth
    return mini

def depth6(box,prof):
    #Renvoie la profondeur minimale sur une colonne aleatoire
    x = random.randint(box.xmin,box.xmax-1)
    mini = depth(x,box.ymin,prof)
    for y in range(box.ymin,box.ymax):
            current_depth = depth(x,y,prof)
            if current_depth < mini:
                mini = current_depth
    return mini

def depth7(box,prof):
    #Renvoie la profondeur minimale sur une ligne aleatoire
    y = random.randint(box.ymin,box.ymax-1)
    mini = depth(box.xmin,y,prof)
    for x in range(box.xmin,box.xmax):
            current_depth = depth(x,y,prof)
            if current_depth < mini:
                mini = current_depth
    return mini
        
def translator():
    rospy.init_node('translator', anonymous=True)
    pub = rospy.Publisher('bounding_boxes_analyser/yolo_obstacles_messages', ObstacleArrayMsg, queue_size=10)
    pub_pers = rospy.Publisher('bounding_boxes_analyser/yolo_persons_messages', ObstacleArrayMsg, queue_size=10)
    pubRViz = rospy.Publisher('bounding_boxes_analyser/marker_vision', MarkerArray, queue_size=10)
    # Publie a la reception de chaque message
    image_yolo = message_filters.Subscriber('bounding_boxes_analyser/bounding_boxes_converted', BoundingBoxes)
    prof = message_filters.Subscriber('/zed/depth/depth_registered', Image)
    
    ts = message_filters.TimeSynchronizer([image_yolo, prof], 10)
                                                             # queue_size
    ts.registerCallback(lambda x,y: callback(x,y,pub,pub_pers,pubRViz))

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
    translator()

