# Real-time-object-detection
Projet de détection et suivi d'objet en temps réel pour permettre l'évitement d'obstacle et le suivi de personnes, en collaboration avec Unsupervised.AI.

# Guide de prise en main

## Configuration du projet

- Installer les dépendances : OpenCV et caméra (cf. ci-dessous)
- Cloner le repository en executant `git clone https://github.com/ofacklam/Real-time-object-detection.git`
- Aller dans le dossier source `cd Real-time-object-detection/OD_ws/src`
- Cloner le repository de zed-ros-wrapper (le module qui integre la caméra ZED dans ROS) `git clone https://github.com/stereolabs/zed-ros-wrapper.git`
- Cloner le repository de `darknet_ros` récursivement : `git clone --recursive https://github.com/leggedrobotics/darknet_ros.git`
- Revenir dans le workspace `cd ..`
- Compiler le projet `catkin_make -DCMAKE_BUILD_TYPE=Release`
	- Si on obtient une erreur `no module named em`, il faut désinstaller `em` avec `pip uninstall em` et install `empy` avec `pip install empy`
- Activer l'environnement (cf Tutoriel ROS) en rajoutant `source ~/Real-time-object-detection/OD_ws/devel/setup.bash` a la fin du fichier `~/.bashrc`

## Configuration de `darknet_ros`

- Le répertoire `src/darknet_ros/darknet_ros/config` contient les fichiers de configuration du wrapper ROS pour YOLO et de l'algo YOLO lui-meme.
- Dans le fichier `ros.yaml` : 
	- il faut modifier le topic que YOLO va lire : affecter a `camera_reading` le topic `/zed/rgb/image_raw_color`
	- dans la section `image_view` le champ `enable_opencv` permet d'activer la vidéo en temps réel (a désactiver en production).
- [Optionnel] On peut rajouter des fichiers de configuration de YOLO (par exemple pour utiliser des configs et poids différents). Il faut alors aussi réécrire les fichiers de lancement. (cf docu de `darknet_ros`)

## Lancer le projet

- Pour lancer la caméra : 
	- seule : `roslaunch zed_wrapper zed.launch`
	- avec rViz pour la visualisation : `roslaunch zed_display_rviz display.launch`
- Pour lancer YOLO :
	- yolov2-tiny : `roslaunch darknet_ros darknet_ros.launch`
	- yolov3 : `roslaunch darknet_ros yolo_v3.launch`
- Lien stratus vers les rosbags tests : https://stratus.binets.fr/s/QCEoQPeoXkrRcJP
	Lancer le rosbag puis YOLO

## Installation de OpenCV

- Installer les dépendences de OpenCV : 
```
sudo apt-get install build-essential
sudo apt-get install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
```
- Cloner le repository OpenCV dans un endroit quelconque
```
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git
```
- Créer un répertoire dans opencv
```
cd opencv
mkdir build
cd build
```
- Executer `cmake` pour la configuration : `cmake -D CMAKE_BUILD_TYPE=Release -D OPENCV_EXTRA_MODULES_PATH=<path/vers/opencv_contrib/modules> ..`
- Build avec la commande `make -j7`
- Installer les librairies avec `sudo make install`

## Installation de la caméra ZED utilisée par le robot Maryam

La caméra a besoin du kit ZED SDK qui a lui-meme besoin du Toolkit CUDA de nVidia.

### Installation du Driver nVidia

- Vérifier sur cette page https://launchpad.net/~graphics-drivers/+archive/ubuntu/ppa quelle est la derniere version du driver nVidia. Actuellement (24/10/2018) c'est la nvidia-410.
- Vérifier sur cette page https://www.nvidia.com/object/unix.html que cette version est compatible avec la carte graphique. Il faut cliquer sur la version puis sur "supported products". 
- Désinstaller les éventuelles vieilles versions de nVidia : `sudo apt-get purge nvidia*`.
- Lancer les commandes suivantes :
```
sudo add-apt-repository ppa:graphics-drivers
sudo apt-get update
```
- Installer la derniere version du driver nVidia : `sudo apt-get install nvidia-410` par exemple.
- Redémarrer l'ordinateur.
- Vérifier que ca s'est bien passé. La ligne `lsmod | grep nvidia` doit renvoyer quelque chose alors que la ligne `lsmod | grep nouveau` ne doit rien renvoyer.
- On peut éventuellement bloquer les mises a jour automatiques avec `sudo apt-mark hold nvidia-410`.

### Installation du Toolkit CUDA

- Télécharger sur cette page https://developer.nvidia.com/cuda-92-download-archive l'installateur CUDA. Il faut sélectionner Linux -> x86_64 -> Ubuntu -> 16.04 -> runfile (local) puis cliquer sur Download. 
- Lancer le fichier en tapant `sudo sh [nom_du_fichier]`, par exemple `sudo sh cuda_9.2.148_396.37_linux.run`
- Suivre les instructions de l'installateur EN REFUSANT d'installer le Driver nVidia.
- Eventuellement installer le Patch qui est téléchargeable a la meme adresse.
- Pour terminer, ajouter les commandes suivantes a la fin du ~/.bashrc
```
export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

### Installation du ZED SDK

- Télécharger l'installateur sur https://www.stereolabs.com/developers/release/2.6/
- Le lancer (avec le bon nom de fichier bien sur) avec 
```
chmod +x ZED_SDK_Linux_*.run 
./ZED_SDK_Linux_*.run
```
- Redémarrer l'ordinateur.
