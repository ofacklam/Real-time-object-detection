# Real-time-object-detection
Projet de détection et suivi d'objet en temps réel pour permettre l'évitement d'obstacle et le suivi de personnes, en collaboration avec Unsupervised.AI.

# Guide de prise en main

## Configuration du projet

- Installer les dépendances de la caméra (cf. partie ci-dessous sur l'installation de la caméra)
- Cloner le repository en executant `git clone https://github.com/ofacklam/Real-time-object-detection.git`
- Aller dans le dossier source `cd Real-time-object-detection/OD_ws/src`
- Cloner le repository de zed-ros-wrapper (le module qui integre la caméra ZED dans ROS) `git clone https://github.com/stereolabs/zed-ros-wrapper.git`
- Revenir dans le workspace `cd ..`
- Compiler le projet `catkin_make`
	- Si on obtient une erreur `no module named em`, il faut désinstaller `em` avec `pip uninstall em` et install `empy` avec `pip install empy`
- Activer l'environnement (cf Tutoriel ROS) en rajoutant `source ~/Real-time-object-detection/OD_ws/devel/setup.bash` a la fin du fichier `~/.bashrc`

- Pour lancer la caméra : 
	- seule : `roslaunch zed_wrapper zed.launch`
	- avec rViz pour la visualisation : `roslaunch zed_display_rviz display.launch`


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

### Installation du ZED SDK

- Télécharger l'installateur sur https://www.stereolabs.com/developers/release/2.6/
- Le lancer (avec le bon nom de fichier bien sur) avec 
```
chmod +x ZED_SDK_Linux_*.run 
./ZED_SDK_Linux_*.run
```
- Redémarrer l'ordinateur.

Augustin
