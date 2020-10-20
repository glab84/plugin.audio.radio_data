# plugin.audio.radio_data
Only for Kodi v18.

Kodi music addon, webradio with web information provide by Json, xml files...

The goal : get information from json file provide by the webradio.
For example : Artist, Title, Album, Fanart, Duration...

Know issue :
sometime information not show... Not get focus ?
the InfoDeamon provide good information but "updateInfoTag" not work.

Installation :
Depencies : You need to install Add-on:Web-PDB.
from terminal :
cd .kodi/addons
git clone https://github.com/glab84/plugin.audio.radio_data
Activate the plugin in the kodi extensions.
go in "Music Extensions" "Radio data"

Currently Work with french radio fip and rfm.

Ce plugin obtient les informations du titre encours de diffusion à partir du fichier json fourni par la weradio.
Fonctionne avec les radios fip (et potentionnellement toutes les radios de france inter) et rfm.

Fonctionne avec la version v18 de Kodi.
cf install ppa https://doc.ubuntu-fr.org/kodi pour la v18.
Prerequis : l'addon Web-PDB.
Installation du plugin kodi depuis  le terminal :
cd .kodi/addons
git clone https://github.com/glab84/plugin.audio.radio_data
Activer ensuite le plugin dans les extensions de kodi.
Il se trouve dans "Extensions musique" "Radio data"

Il subsiste un bug :  parfois les infos ne s'affichent pas, c'est aléatoire, est-ce du à ma mauvaise connexion ? (1 fois sur 10 environ)

Utilisation : choisir la radio fip de son choix, puis passer en plein écran (tabulation) : l'image de l'album est affiché, les fanart de l'artist, la bio, les paroles... : ce sont les fonctionnalitées standard de Kodi qui entrent en action.
Il faut 10 secondes environ pour que cela s'affiche.
Je conseille le skin "aeon mq 8". 
