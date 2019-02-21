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
import random
import numpy
from visualization_msgs.msg import Marker, MarkerArray

#Reste a faire
    # rajouter de quoi evaluer temporellement les performances
    # detecter les personnes pour en faire une exception avec un seuil d'acceptation

FOV = math.pi/2 # field of view en radian
repere = 'zed_left_camera_frame'

def callback(image_yolo,prof,pub,pubRViz):
    l = len(image_yolo.bounding_boxes)
    tab = []
    tabRViz = []
    depth_time = []
    yolo_time = []
    for i in range(l):
        # camera -> robot
        # x -> -y
        # y -> -z
        # z -> x
        # les messages sont enregistres dans le repere de la camera nomme: 'zed_left_camera_frame' stocke dans repere
        box = image_yolo.bounding_boxes[i]

        point1 = Point32()
        point2 = Point32()

        point1.z = 0
        point2.z = 0
        
        start = rospy.get_rostime()
        depth = depth3(box,prof)
        point1.x = depth
        point2.x = depth
        end = rospy.get_rostime()

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
#        mark = Marker()
#        mark.id = i
#        mark.header = obs.header
#        mark.ns = 'obstacles'
#        mark.type = Marker.LINE_STRIP
#        mark.action = Marker.ADD
#        mark.points = poly.points
#        mark.scale.x = 0.2
#        mark.color.g = 1
#        mark.color.a = 1
#        tabRViz.append(mark)

        tab.append(obs)
        depth_time.append(end - start)
        yolo_time.append(image_yolo.header.stamp - prof.header.stamp)
        print('depth: ' + str(depth))
        print('depth time: ' + str(depth_time[-1]))
        # Cette valeur est souvent nulle mais la depth change bien
        # Le reste des temps sont plutot de l ordre du million
        print ('yolo_time: ' + str(yolo_time[-1]))
        # Cette valeur est souvent negative => ont ne compare pas les bonnes images 
        # => continuite donc a une ou deux image pres ce n est pas tres grave
        # Une selection par image plutot que par temps n'est pas top
        # On peut changer l'integration de ros pour avoir les 2 memes time stamp
        print
        

    msg = ObstacleArrayMsg()
    msg.header = prof.header
    msg.obstacles = tab

    pub.publish(msg)
    
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

