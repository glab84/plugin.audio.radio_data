# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import os
import threading
import time
import urlparse
import urllib
import web_pdb
import re
import json
import xbmcaddon
from urllib import urlencode
from urlparse import parse_qsl

def InfoDaemon():
   xbmc.log("Radio_data: InfoDeamon is starting...")
   periode = 10
   while 1:
       if xbmc.Player().isPlayingAudio():
           playing_file = xbmc.Player().getPlayingFile()
           xbmc.log("Radio_data: InfoDeamon playingfile is %s" % playing_file)
           set_info(playing_file)
           xbmc.Monitor().waitForAbort(periode)

def set_info(playing_file):
    artist,song,fanart,year,duration,album=get_info_playing_file(playing_file)
    if song != "" or artist != "" or album != "":
      try:
        li = xbmcgui.ListItem()
        li.setPath(xbmc.Player().getPlayingFile())
        li.setArt({"thumb":fanart, "fanart":fanart})
        li.setInfo("music", {"title": song, "artist": artist, "year": year, "duration": duration, "album": album})
        xbmc.Player().updateInfoTag(li)
        artist_debug = xbmc.Player().getMusicInfoTag().getArtist()
        if artist_debug == "":
            xbmc.log("Radio_data: Issue artist : %s" % artist)
      except:
        xbmc.log("Radio_data: Can't update InfoTag !")

# menu.json management
def radiodata_menu_radiodata(menujson, url):
    with open(menujson) as json_file:
        menu = json.load(json_file)

    for p1 in menu['menu']:
        for p2 in p1['contents']['menuitem']:
           if p2['stream_url'] == url:
               return p2['radiodata_type'], p2['radiodata_url']
    return '',''

def get_info_playing_file(playing_file):
    xbmc.log("Radio_data: playing_file %s" % playing_file)
    radiodata_type, radiodata_file = radiodata_menu_radiodata(pathfilemenu, playing_file)
    if radiodata_type != "" and radiodata_file != "" : 
        xbmc.log("Radio_data: type %s " % radiodata_type)
        xbmc.log("Radio_data: file %s " % radiodata_file)
        
        try:
            if radiodata_type == "rf_json" :
                artist,song,fanart,year,duration,album=get_info_radiofrance(radiodata_file)
            elif radiodata_type == "rf_json_graphql" :
                artist,song,fanart,year,duration,album=get_info_radiofrance_graphql(radiodata_file)
            elif radiodata_type == "rf_json_basic" :
                artist,song,fanart,year,duration,album=get_info_radiofrance_basic(radiodata_file)
            elif radiodata_type == "rfm_json" :
                artist,song,fanart,year,duration,album=get_info_rfm(radiodata_file)
            else:
                xbmc.log("Radio_data: Fail to found type !")
                artist=""
                song=""
                fanart=""
                year=""
                duration=""
                album=""

        except:
              artist=""
              song=""
              fanart=""
              year=""
              duration=""
              album=""
    else:
          artist=""
          song=""
          fanart=""
          year=""
          duration=""
          album=""
    return artist,song,fanart,year,duration,album

def get_info_radiofrance(url):
    xbmc.log("Radio_data: get_info url is %s" % url)
    try:
      r=requests.get(url)
      info=r.json()
      c1=info["levels"][0]["items"][3]
      v1 = info["steps"][c1]
      try:
        song = v1["title"].title().encode('utf-8')
      except:
        song = ""
      try:
        artist = v1["authors"]
      except:
        artist = ""
      try:
        album = v1["titreAlbum"]
      except:
        album = ""
      try:
        year = v1["anneeEditionMusique"]
      except:
        year = ""
      try:
        fanart = v1["visual"]
      except:
        fanart = "http://mediateur.radiofrance.fr/wp-content/themes/radiofrance/img/fip.png"
      try:
        start = v1["start"]
      except:
        start = 0
      try:
        end = v1["end"]
      except:
        end = 0
      i = song.find('en session live')
      if i != -1 and artist == "" :
          artist = song.replace('en session live', '') # work ?
          song = 'Session live'           
          try:
            album = v1["titleConcept"]
          except:
            album = ""
      duration = end - start
      xbmc.log("Radio_data: Artists is %s" % artist)
    except:
      song = ""
      artist = ""
      album = ""
      year = ""
      fanart = ""
      start = 0
      end = 0
      duration = end - start
    return artist,song,fanart,year,duration,album

def get_info_radiofrance_graphql(url):
    xbmc.log("Radio_data: get_info graphql url is %s" % url)
    try:
      r=requests.get(url)
      info=r.json()
      v1 = info["data"]["nowList"][0]
      try:
        song = v1["song"]["title"].title().encode('utf-8')
      except:
        song = ""
      try:
        artist = v1["song"]["interpreters"][0]
      except:
        artist = ""
      try:
        album = v1["song"]["album"]
      except:
        album = ""
      try:
        year = v1["song"]["year"]
      except:
        year = ""
      try:
        fanart = v1["song"]["cover"]
      except:
        fanart = "http://mediateur.radiofrance.fr/wp-content/themes/radiofrance/img/fip.png"
      try:
        start = v1["playing_item"]["start_time"]
      except:
        start = 0
      try:
        end = v1["playing_item"]["end_time"]
      except:
        end = 0
      i = song.find('en session live')
      if i != -1 and artist == "" :
          artist = song.replace('en session live', '') # work ?
          song = 'Session live'           
          album = ""
      duration = end - start
      xbmc.log("Radio_data: Artists is %s" % artist)
    except:
      song = ""
      artist = ""
      album = ""
      year = ""
      fanart = ""
      start = 0
      end = 0
      duration = end - start
    return artist,song,fanart,year,duration,album

def get_info_radiofrance_basic(url):
    xbmc.log("Radio_data: get_info basic url is %s" % url)
    try:
      r=requests.get(url)
      info=r.json()
      v1 = info["data"]["now"]["playing_item"]
      try:
        #song = v1["title"].title().encode('utf-8')
        song = v1["title"]
      except:
        song = ""
      try:
        artist = v1["subtitle"]
      except:
        artist = ""
      album = ""
      year = ""
      try:
        fanart = v1["cover"]
      except:
        fanart = "http://mediateur.radiofrance.fr/wp-content/themes/radiofrance/img/fip.png"
      try:
        start = v1["start_time"]
      except:
        start = 0
      try:
        end = v1["end_time"]
      except:
        end = 0
      i = song.find('en session live')
      if i != -1 and artist == "" :
          artist = song.replace('en session live', '') # work ?
          song = 'Session live'           
          album = ""
      duration = end - start
      xbmc.log("Radio_data: Artists is %s" % artist)
    except:
      song = ""
      artist = ""
      album = ""
      year = ""
      fanart = ""
      start = 0
      end = 0
      duration = end - start
    return artist,song,fanart,year,duration,album

def get_info_rfm(url):
    xbmc.log("Radio_data: get_info rfm url is %s" % url)
    # try ...
    r=requests.get(url)
    info=r.json()
    c1=info["current"]
    year = ""
    try:
      song = c1["title"].title().encode('utf-8')
    except:
      song = ""
    try:
      artist = c1["artist"]
    except:
      artist = ""
    try:
      album = c1[""]
    except:
      album = ""
    try:
      fanart = c1["cover"]
    except:
      fanart = ""
    try:
      duration = v1["duration"]
    except:
      duration = ""
    xbmc.log("Radio_data: Artists is %s" % artist)
    return artist,song,fanart,year,duration,album

def build_url(query):
    base_url = sys.argv[0]
    return base_url + '?' + urllib.urlencode(query)

def build_menu_contents(menujson, id):
    with open(menujson) as json_file:
        menu = json.load(json_file)

    song_list = []

    n = 0
    for p1 in menu['menu']:
        if p1['id'] == id:
            for p2 in p1['contents']['menuitem']:
               n += 1
               title = p2['value']
               flux = p2['stream_url']
               if p2['fanart'] != '' :
                  visual = p2['fanart']
               else:
                  artist,song,fanart,year,duration,album=get_info_playing_file(flux)
                  visual = fanart
               li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
               li.setProperty('fanart_image', visual)
               li.setProperty('IsPlayable', 'true')
               li.setInfo('music', {'title': title, 'genre': title})
               url = build_url({'mode': 'stream', 'url': flux, 'title': title})
               song_list.append((url, li, False))

    xbmcplugin.addDirectoryItems(addon_handle, song_list, len(song_list))
    xbmcplugin.setContent(addon_handle, 'songs')
    xbmcplugin.endOfDirectory(addon_handle)

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def build_menu(menujson):
    xbmcplugin.setPluginCategory(addon_handle, 'Main Menu')
    xbmcplugin.setContent(addon_handle, 'stream')
    
    with open(menujson) as json_file:
        menu = json.load(json_file)

    for p in menu['menu']:
        list_item = xbmcgui.ListItem(label=p['value'])
        list_item.setArt({'thumb': p['fanart'],
                          'icon': p['fanart'],
                          'fanart': p['fanart']})
        list_item.setInfo('stream', {'title': p['value'],
                                    'genre': p['value'],
                                    'mediatype': 'stream'})
        url = get_url(action='listing', menuid=p['id'])
        is_folder = True
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, is_folder)

    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(addon_handle)

def build_song_list(menuitem):
    build_menu_contents(pathfilemenu, menuitem)
    
def play_song(url):
    xbmc.executebuiltin("ActivateWindow(12006)")
    xbmc.Monitor().waitForAbort(1)
    WINDOW = xbmcgui.Window(12006)
    xbmc.Monitor().waitForAbort(1)

    li = xbmcgui.ListItem()
    li.setPath(url)
    xbmc.log("Radio-data: Play_url is %s" % url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True , listitem=li)
    xbmc.Player().play(item=url, listitem=li)
    xbmc.Monitor().waitForAbort(1)
    set_info(url)

    if WINDOW.getProperty("Radio-data") == "true":
        exit(0)
    else:
        WINDOW.setProperty("Radio-data", "true")
        InfoDaemon()

def main():

    xbmc.executebuiltin("ActivateWindow(12006)")

    args = urlparse.parse_qs(sys.argv[2][1:])
    mode = args.get('mode', None)
    menuid = args.get('menuid', None)
    
    # initial launch of add-on
    if mode is None:
        if menuid is None:
            build_menu(pathfilemenu)
        else:
            build_menu_contents(pathfilemenu, menuid[0])

    elif mode[0] == 'stream':
        # pass the url of the song to play_song
        play_song(args['url'][0])

if __name__ == '__main__':
    _addon_ = xbmcaddon.Addon()
    path = _addon_.getAddonInfo('path').decode('utf-8')
    xbmc.log("Radio-data: path is %s" % path)
    filemenu = 'menu.json'
    pathfilemenu = os.path.join(path, filemenu)

    _url = sys.argv[0]
    addon_handle = int(sys.argv[1])
    main()
