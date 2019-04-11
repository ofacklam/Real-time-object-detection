#Ce script enregistre dles graphiques des differents temps qui ont ete 
#   enregistre sur la video test 12

#Remarque 1: Sur le plot des distances les "manques de donnees a la fin"
# sont dus a la presence d'infinis dans le tableau

#Remarque 2: Sur le plot des distances toutes les lignes sont triees donc 
# on ne sait pas vraiment ce qu'on compare...

#Remarque 3: Sur le plot des distances numpy est bien toujours la distance
# minimale

import matplotlib.pyplot as plt
import numpy as np

#Recuperation des donnees
path = "/home/augustin/psc/catkin_ws/src/Real-time-object-detection/tests/svg/"
depth_numpy = np.loadtxt(path+"DepthNumpy.txt")
depth_center = np.loadtxt(path+"Depth1.txt")
depth_min = np.loadtxt(path+"Depth2.txt")
depth_cross = np.loadtxt(path+"Depth3.txt")
depth_crossx = np.loadtxt(path+"Depth4.txt")
depth_random = np.loadtxt(path+"Depth5.txt")
depth_random_column = np.loadtxt(path+"Depth6.txt")
depth_random_row = np.loadtxt(path+"Depth7.txt")
depth_numpy_time = np.loadtxt(path+"DepthNumpyTime.txt")
depth_center_time = np.loadtxt(path+"Depth1Time.txt")
depth_min_time = np.loadtxt(path+"Depth2Time.txt")
depth_cross_time = np.loadtxt(path+"Depth3Time.txt")
depth_crossx_time = np.loadtxt(path+"Depth4Time.txt")
depth_random_time = np.loadtxt(path+"Depth5Time.txt")
depth_random_column_time = np.loadtxt(path+"Depth6Time.txt")
depth_random_row_time = np.loadtxt(path+"Depth7Time.txt")
yolo  = np.loadtxt(path+"YoloTime.txt") #est en ns
name = ["numpy.min", "centre", "coix +", "croix x", "100 points aleatoires", "colonne aleatoire", "ligne aleatoire", "yolo"]

#Mise en rapport des profondeurs
#Les profondeurs ne designent pas les memes objets donc la courbe n'est pas continue !!!
#Une solution est de trier depth_numpy puis de reordonner les autres selon les indices de numpy
depth_tab = []
depth_tab.append(depth_numpy)
depth_tab.append(depth_center)
#depth_tab.append(depth_min)
# Cette donnee doit etre enlevee car la lenteur de min python fait que le nombre de box annalysees
# est ridiculement faible (23 contre plus de 1000 pour les autres fonctions)
depth_tab.append(depth_cross)
depth_tab.append(depth_crossx)
depth_tab.append(depth_random)
depth_tab.append(depth_random_column)
depth_tab.append(depth_random_row)
l = []
for i in range(len(depth_tab)):
    l.append(np.size(depth_tab[i]))
mini = np.min(l)
X = range(mini)
for i in range(len(depth_tab)):
    depth_tab[i] = depth_tab[i][:mini]
depth_tab = np.transpose(depth_tab)
depth_tab = np.sort(depth_tab,axis=0)
depth_tab = np.transpose(depth_tab)
for i in range(len(depth_tab)):
    plt.plot(X,depth_tab[i],label=name[i])
plt.title("Profondeur renvoyee par les differentes fonction de calcul")
plt.ylabel("Profondeur (en m)")
plt.legend(loc='best')
plt.savefig(path+"Profondeur", dpi=500, bbox_inches='tight')
plt.cla()

#Mise en rapport des temps
time_tab = []
time_tab.append(depth_numpy_time)
time_tab.append(depth_center_time)
#time_tab.append(depth_min_time)
# Cette donnee doit etre enlevee car la lenteur de min python fait que le nombre de box annalysees
# est ridiculement faible (23 contre plus de 1000 pour les autres fonctions)
time_tab.append(depth_cross_time)
time_tab.append(depth_crossx_time)
time_tab.append(depth_random_time)
time_tab.append(depth_random_column_time)
time_tab.append(depth_random_row_time)
l = []
for i in range(len(time_tab)):
    l.append(np.size(time_tab[i]))
mini = np.min(l)
X = range(mini)
for i in range(len(time_tab)):
    time_tab[i] = time_tab[i][:mini]
time_tab = np.transpose(time_tab)
time_tab = np.sort(time_tab,axis=0)
time_tab = np.transpose(time_tab)
for i in range(len(time_tab)):
    m = np.mean(time_tab[i])
    Y = [m for x in X]
    plt.plot(X,Y,label="moyenne: " + name[i])
plt.title("Temps moyen d execution des differentes fonction de calcul")
plt.ylabel("Temps d'execution (en s)")
plt.legend(loc='best')
plt.ylim(ymin=0)
plt.savefig(path+"Temps moyen", dpi=500, bbox_inches='tight')
plt.cla()
for i in range(len(time_tab)):
    plt.plot(X,time_tab[i],label=name[i])
plt.title("Temps d execution des differentes fonction de calcul")
plt.ylabel("Temps d'execution (en s)")
plt.legend(loc='best')
plt.ylim(ymin=0)
plt.savefig(path+"Temps", dpi=500, bbox_inches='tight')
plt.cla()

#Comparaison avec le temps que yolo prend
time_tab = []
time_tab.append(depth_numpy_time)
time_tab.append(depth_center_time)
#time_tab.append(depth_min_time)
# Cette donnee doit etre enlevee car la lenteur de min python fait que le nombre de box annalysees
# est ridiculement faible (23 contre plus de 1000 pour les autres fonctions)
time_tab.append(depth_cross_time)
time_tab.append(depth_crossx_time)
time_tab.append(depth_random_time)
time_tab.append(depth_random_column_time)
time_tab.append(depth_random_row_time)
yolo /= 1000000000
time_tab.append(yolo)
l = []
for i in range(len(time_tab)):
    l.append(np.size(time_tab[i]))
mini = np.min(l)
X = range(mini)
for i in range(len(time_tab)):
    time_tab[i] = time_tab[i][:mini]
time_tab = np.transpose(time_tab)
time_tab = np.sort(time_tab,axis=0)
time_tab = np.transpose(time_tab)
for i in range(len(time_tab)):
    m = np.mean(time_tab[i])
    Y = [m for x in X]
    plt.plot(X,Y,label="moyenne: " + name[i])
plt.title("Temps moyen d execution des differentes fonction de calcul et de yolo")
plt.ylabel("Temps d'execution (en s)")
plt.legend(loc='best')
plt.ylim(ymin=0)
plt.savefig(path+"Temps moyen yolo", dpi=500, bbox_inches='tight')
plt.cla()
for i in range(len(time_tab)):
    plt.plot(X,time_tab[i],label=name[i])
plt.title("Temps d execution des differentes fonction de calcul et de yolo")
plt.ylabel("Temps d'execution (en s)")
plt.ylim(ymin=0)
plt.legend(loc='best')
plt.savefig(path+"Temps yolo", dpi=500, bbox_inches='tight')
plt.cla()

#Comparaison yolo et min
m = np.mean(depth_min_time)
Y = [m for x in X]
plt.plot(X,Y,label="min")
m = np.mean(yolo)
Y = [m for x in X]
plt.plot(X,Y,label="yolo")
plt.title("Temps moyen d execution de min et de yolo")
plt.ylabel("Temps d'execution (en s)")
plt.legend(loc='best')
plt.ylim(ymin=0)
plt.savefig(path+"Temps moyen yolo vs min", dpi=500, bbox_inches='tight')
plt.cla()