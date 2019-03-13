# Tutoriel ROS

## Quand on commence a travailler

- Aller dans le workspace (dossier) dans lequel on travaille
`cd /home/monnom/unsupervised`

- Activer l'environnement (a faire dans chaque nouveau terminal)
`source devel/setup.bash`
ou le faire une fois pour toutes en rajoutant 
`source ~/unsupervised/devel/setup.bash`
a la fin du fichier `~/.bashrc`

## Structure de ROS

- Nodes: A node is an executable that uses ROS to communicate with other nodes.
- Messages: ROS data type used when subscribing or publishing to a topic.
- Topics: Nodes can publish messages to a topic as well as subscribe to a topic to receive messages.
- Master: Name service for ROS (i.e. helps nodes find each other)
- rosout: ROS equivalent of stdout/stderr
- roscore: Master + rosout + parameter server (parameter server will be introduced later)

## Utilisation

### Pour lancer le serveur ROS (Master)
`roscore`

### Pour lancer le node d'un package
`rosrun [package_name] [node_name] __name:=identifiant-custom`
La partie `__name` est optionnelle

### Pour lancer un ensemble de nodes

`roslaunch [package] [filename.launch]`
Pour voir la tête du `filename.launch`: http://wiki.ros.org/ROS/Tutorials/UsingRqtconsoleRoslaunch

### Pour des interfaces graphiques
Le mieux est de lancer l'interface rqt avec la commande `rqt` puis de sélectionner les éléments a visualiser par le menu `Plugin`

Sinon, via ligne de commande :
 - le graphe reliant les différents nodes : `rosrun rqt_graph rqt_graph` ou`rqt_graph`
 - un outil pour tracer des graphes a partir des messages : `rosrun rqt_plot rqt_plot`
 - une console graphique avec les messages de debug et warnings : 
```
rosrun rqt_console rqt_console
rosrun rqt_logger_level rqt_logger_level
```


### Pour obtenir des informations sur un node
- la liste de tous les nodes actifs : `rosnode list`
- des infos sur le node `mon-node` : `rosnode info /mon-node`

### Pour obtenir des infos sur un topic
```
rostopic bw [topic]                        display bandwidth used by topic
rostopic echo [topic]                      print messages to screen
rostopic hz [topic]                        display publishing rate of topic    
rostopic list                              print information about active topics
rostopic pub  [topic] [msg_type] [args]    publish data to topic
    en option -r [frequency of repetition]
rostopic type [topic]                      print topic type
```
et pour les détails sur le type d'un message
`rosmsg show [type_du_message]` ou
`rostopic type [nom_du_topic] | rosmsg show`


### Pour interagir avec des services
```
rosservice list         print information about active services
rosservice call         call the service with the provided args
rosservice type         print service type
rosservice find         find services by service type
rosservice uri          print service ROSRPC uri
```
et pour les détails sur le type d'un service
`rossrv show [type_du_service]` ou
`rosservice type [nom_du_service] | rossrv show`

### Pour utiliser les parametres globaux
```
rosparam list                           list parameter names
rosparam set [param_name]               set parameter
rosparam get [param_name]               get parameter
    en option / pour param_name pour obtenir la liste des paramètres et leur valeur
rosparam load [file_name] [namespace]   load parameters from file
rosparam dump [file_name] [namespace]   dump parameters to file
rosparam delete                         delete parameter
```

## Création de nouveaux packages

### Pour créer un nouveau package

```
cd src
catkin_create_pkg <package_name> [depend1] [depend2] [depend3]
```
Dépendances utiles : `std_msgs` `rospy` `roscpp` `message_generation` `message_runtime`

`package.xml` contient les métadonnées du package. En l'éditant on peut y apporter les informations telles que l'auteur et les licences du package.

### Création de types message et service

#### Définition d'un type message dans le dossier `msg` du package
```
Header header #optionnel mais apparemment utile
type_du_champ nom_du_champ
```

Les types autorisés : 
- int8, int16, int32, int64 (plus uint*)
- float32, float64
- string
- time, duration
- other msg files
- variable-length array[] and fixed-length array[C] 

Pour la configuration nécessaire cf. http://wiki.ros.org/ROS/Tutorials/CreatingMsgAndSrv

#### Définition d'un type service
```
int64 A    # la requete
int64 B
---
int64 Sum    # la réponse
```

### Pour compiler tous les packages dans `src`
`catkin_make`

## Gestion des rosbags
```
rosbag record -a                          enregistre un rosbag avec tous les topics
rosbag topic_1 topic_2 -o nom_du_rosbag   enregistre un rosbag avec les topics 1 et 2
```
Ctrl+C pour arrêter l'enregistrement
```
rosbag info nom_du_rosbag            donne les info sur le rosbag comme la date de prise ou sa taille
rosbag play -s 5 -r 2 nom_du_rosbag  joue le rosbag depuis l'instant 5 à la vitesse x2
```

### Temps simulé
- Avant de lancer des noeuds (mais apres avoir lancer `roscore`), activer le temps simulé : `rosparam set use_sim_time true`
- Lancer les bags avec l'option `--clock`
