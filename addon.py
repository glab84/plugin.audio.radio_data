# -*- coding: utf-8 -*-

import os
import re
import threading
import time
import json
import requests
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.request import urlopen 
from urllib.parse import urlencode
from urllib.parse import parse_qsl
from kodi_six import xbmc, xbmcgui, xbmcvfs, xbmcplugin, xbmcaddon

def InfoDaemon():
   xbmc.log("Radio_data: InfoDeamon is starting...")
   periode = 10
   while 1:
       if xbmc.Player().isPlayingAudio():
           playing_file = xbmc.Player().getPlayingFile()
           xbmc.log("Radio_data: InfoDeamon playingfile is %s" % playing_file)
           xbmc.Monitor().waitForAbort(1)
           dt_end = set_info(playing_file)
           dt_now = datetime.now()
           
           if dt_end == datetime.min:
              xbmc.Monitor().waitForAbort(periode)
           else:
              delta = dt_end - dt_now 
              xbmc.log("Radio_data: InfoDeamon dt_end is %s" % dt_end.strftime("%d/%m/%Y %H:%M:%S %Z"))
              xbmc.log("Radio_data: InfoDeamon now is %s" % dt_now.strftime("%d/%m/%Y %H:%M:%S %Z"))
              xbmc.log("Radio_data: InfoDeamon delta is %s" % delta.seconds)
              # 3600 = Jazz a fip => to be ignore.
              if delta.seconds > 0 and dt_end > dt_now and delta.seconds < 3000 :
                  # The song end in delta.seconds
                  # But perhaps the user change the stream.
                  previus_playing_file = playing_file
                  for i in range(delta.seconds):
                     if not xbmc.Player().isPlayingAudio():
                         break
                     playing_file = xbmc.Player().getPlayingFile()
                     xbmc.log("Radio_data: InfoDeamon (for) playingfile is %s" % playing_file)
                     if playing_file != previus_playing_file:
                         break
                     xbmc.Monitor().waitForAbort(1)
              else:
                  xbmc.Monitor().waitForAbort(1)

def set_info(playing_file):
    artist, song, fanart, year, duration, album, dt_end = get_info_playing_file(playing_file)
    if song != "" or artist != "" or album != "":
       try:
           list_item = xbmcgui.ListItem()
           list_item.setPath(xbmc.Player().getPlayingFile())
           list_item.setArt({"thumb":fanart, "fanart":fanart})
           list_item.setInfo("music", {"title": song, "artist": artist, "year": year, "duration": duration, "album": album})
           xbmc.Player().updateInfoTag(list_item)
           artist_debug = xbmc.Player().getMusicInfoTag().getArtist()
           if artist_debug == "":
               xbmc.log("Radio_data: Issue artist : %s" % artist)
       except:
           xbmc.log("Radio_data: Can't update InfoTag !")
    xbmc.log("Radio_data: dt_end %s" % dt_end)
    if duration == 3600:
       # 3600 = Jazz a fip => to be ignore.
       dt_end = datetime.now()
    return dt_end

# menu.json management
def radiodata_menu_radiodata(menujson, url):
    xbmc.log("radiodata_menu_radiodata: menujson %s" % menujson)
    xbmc.log("radiodata_menu_radiodata: url %s" % url)

    if url == "" :
      return "", "", "", ""

    with open(menujson) as json_file:
        menu = json.load(json_file)

    for p1 in menu["menu"]:
        # si json
        try:
          rf_url_json = p1["rf_url_json"]
          xbmc.log("radiodata_menu_radiodata: rf_url_json %s" % rf_url_json)
          response = urlopen(rf_url_json) 
          data_json = json.loads(response.read()) 
  
          for p2 in data_json:
            try: 
              if p2["streams"]["live"][0]["url"] == url:
                visual = p2["logo"]["webpSrc"]
                name = p2["name"]
                return name, "rf_url_json", rf_url_json, visual
              xbmc.log("radiodata_menu_radiodata: url %s" % p2["streams"]["live"][0]["url"] )
            except:
              visual = ""
              name = ""
        except:
          for p2 in p1["contents"]["menuitem"]:
             if p2["stream_url"] == url:
                 return "", p2["radiodata_type"], p2["radiodata_url"], p2["fanart"]
    return "", "", "", ""

def get_info_playing_file(playing_file):
    xbmc.log("Radio_data: playing_file %s" % playing_file)
    radio_name, radiodata_type, radiodata_file, radiodata_fanart = radiodata_menu_radiodata(pathfilemenu, playing_file)
    dt_end = datetime.min
    if radiodata_type != "" and radiodata_file != "" : 
        xbmc.log("Radio_data: type %s " % radiodata_type)
        xbmc.log("Radio_data: file %s " % radiodata_file)
        
        try:
            if radiodata_type == "rf_url_json" :
                artist, song, fanart, year, duration, album, dt_ent = get_info_radiofrance_url_json(radiodata_file, radio_name)
            elif radiodata_type == "rfm_json" :
                artist, song, fanart, year, duration, album, dt_ent = get_info_rfm(radiodata_file)
            elif radiodata_type == "jazzradio_xml" :
                artist, song, fanart, year, duration, album, dt_ent = get_info_jazzradio_xml(radiodata_file)
            else:
                xbmc.log("Radio_data: Fail to found type !")
                artist = ""
                song = ""
                fanart = ""
                year = ""
                duration = ""
                album = ""
                dt_end = datetime.min
        except:
              artist = ""
              song = ""
              fanart = ""
              year = ""
              duration = ""
              album = ""
              dt_end = datetime.min
    else:
          artist = ""
          song = ""
          fanart = ""
          year = ""
          duration = ""
          album = ""
          dt_end = datetime.min
    xbmc.log("Radio_data if : fanart %s " % fanart)
    if fanart == "" and radiodata_fanart != "":
        xbmc.log("Radio_data: fall back %s " % radiodata_fanart)
        fanart = radiodata_fanart
    return artist, song, fanart, year, duration, album, dt_end

def get_info_rf_transitor(radio_id):                                                                      
    xbmc.log("Radio_data: get_info transitor id is %s" % radio_id)
    try:                                                                                              
        url = "https://api.radiofrance.fr/livemeta/live/%s/transistor_musical_player?preset=400x400" % radio_id
        xbmc.log("Radio_data: get_info transitor url is %s" % url)
        r = requests.get(url)                               
        info = r.json()                                                                                         
        v1 = info["now"]                                
        try:                                                                                                    
            secondLine = v1["secondLine"]            
            xbmc.log("Radio_data: get_info transitor secondLine is %s" % secondLine)        
            # secondLine : artist . song
            # Sample : IJulia Fischer • Caprice pour violon en mi min op 1 n°15
            m = re.search('(.*) • (.*)', secondLine)
            artist = m.group(1)
            song = m.group(2)
            xbmc.log("Radio_data: get_info transitor song is %s" % song)        
        except:                                                                                   
            secondLine = ""                                                
            song = ""
            artist = ""                
        try:                                                      
            fanart = v1["cover"]                   
        except:                                               
            fanart = ""                           
        try:                                                  
            start = v1["startTime"]                  
        except:                                                                                        
            start = 0
        try:                                                                
            end = v1["endTime"]                                              
            dt_end = datetime.fromtimestamp(end)                                 
        except:                                       
            end = 0                                        
            dt_end = datetime.min                         
        
        duration = end - start                    
        xbmc.log("Radio_data: get_info transitor Artists is %s" % artist)        
        xbmc.log("Radio_data: get_info transitor fanart is %s" % fanart)        
    except:                                                      
        artist = ""                                                                                 
        song = ""                                                                                      
        fanart = ""                                                              
        start = 0                                     
        end = 0                                            
        duration = end - start                            
        dt_end = datetime.min                                                                              
    return artist, song, fanart, duration, dt_end   

def get_info_radiofrance_basic(url):
    xbmc.log("Radio_data: get_info basic url is %s" % url)
    try:
        r = requests.get(url)
        info = r.json()
        v1 = info["data"]["now"]["playing_item"]
        try:
            song = v1["subtitle"]
        except:
            song = ""
        try:
            artist = v1["title"]
        except:
            artist = ""
        album = ""
        year = ""
        try:
            fanart = v1["cover"]
        except:
            fanart = ""
        try:
            start = v1["start_time"]
        except:
            start = 0
        try:
            end = v1["end_time"]
            dt_end = datetime.fromtimestamp(end)
        except:
            end = 0
            dt_end = datetime.min
        i = song.find("en session live")
        if i != -1 and artist == "" :
            artist = song.replace("en session live", "") # work ?
            song = "Session live"           
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
        dt_end = datetime.min
    return artist, song, fanart, year, duration, album, dt_end

def get_info_radiofrance_url_json(url, name):
    xbmc.log("Radio_data: get_info url json is %s" % url)
    xbmc.log("Radio_data: get_info url json name is %s" % name)
    try:
       response = urlopen(url) 
       data_json = json.loads(response.read()) 
  
       for p2 in data_json:
         xbmc.log("Radio_data: get_info for %s" % p2["name"])
         if name == p2["name"]:
           radio_id = p2["id"]
           p3 = p2["live"]["now"]
           song = p3["firstLine"]
           artist = p3["secondLine"]
           try:
             fanart = p3["cardVisual"]["webpSrc"]
             try:
               album = p3["song"]["release"]["title"]
               year = p3["song"]["year"]
             except:		
               album = p3["secondLine"]
               year = ""
             try:
               copy_right = p3["cardVisual"]["copyright"]
             except:  
               copy_right = ""
             xbmc.log("Radio_data: get_info url json copy_right is %s" % copy_right)
             xbmc.log("Radio_data: get_info url json album is %s" % album)
             xbmc.log("Radio_data: get_info url json year is %s" % year)
             xbmc.log("Radio_data: get_info url json song is %s" % song)
             if copy_right != None or p3["song"] == None:
               artist, song, fanart, duration, dt_ent = get_info_rf_transitor(radio_id)
               # during live broadcasts falldown on transitor infos. Works ?

           except:
             artist, song, fanart, duration, dt_ent = get_info_rf_transitor(radio_id)
             # during live broadcasts falldown on transitor infos. Works ?
             album = ""
             year = ""

           try:
             start = p3["startTime"]
             end = p3["endTime"]
             dt_end = datetime.fromtimestamp(end)
             duration = end - start
           except:
             start = 0
             end = 0
             dt_end = 0
             duration = 0
           break  

       xbmc.log("Radio_data: get_info fanart is %s" % fanart)
       xbmc.log("Radio_data: get_info album is %s" % album)
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
       dt_end = datetime.min
    return artist, song, fanart, year, duration, album, dt_end

def get_info_jazzradio_xml(url):
    xbmc.log("Radio_data: get_info jazzradio url is %s" % url)
    try:
        r = requests.get(url)
        root = ET.fromstring(r.content)

        album = ""
        year = ""
        start = 0
        end = 0
        try:
            for child in root:
                for child2 in child:
                    if child2.tag == "chanteur":
                        artist = child2.text
                    if child2.tag == "chanson":
                        song = child2.text
                    if child2.tag == "pochette":
                        fanart = child2.text
                break
        except:
            song = ""
            artist = ""
            fanart = ""
        duration = end - start
        xbmc.log("Radio_data: Artists is %s" % artist)
        xbmc.log("Radio_data: Fan Art is %s" % fanart)
    except:
        song = ""
        artist = ""
        album = ""
        year = ""
        fanart = ""
        start = 0
        end = 0
        duration = end - start
    dt_end = datetime.min
    return artist, song, fanart, year, duration, album, dt_end

def get_info_rfm(url):
    xbmc.log("Radio_data: get_info rfm url is %s" % url)
    # try ...
    r = requests.get(url)
    info = r.json()
    c1 = info["current"]
    year = ""
    try:
        song = c1["title"].encode("utf-8")
    except:
        song = ""
    try:
        artist = c1["artist"]
        artist.rstrip() # Don't work !
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
        duration = c1["duration"]
    except:
        duration = ""
    dt_end = datetime.min
    xbmc.log("Radio_data: Artists is %s" % artist)
    return artist, song, fanart, year, duration, album, dt_end

def build_url(query):
    base_url = sys.argv[0]
    return base_url + "?" + urllib.parse.urlencode(query)

def build_menu(menujson):
    xbmcplugin.setPluginCategory(addon_handle, "Main Menu")
    xbmcplugin.setContent(addon_handle, "stream")
    
    with open(menujson) as json_file:
        menu = json.load(json_file)

    for p in menu["menu"]:
        list_item = xbmcgui.ListItem(label=p["value"])
        list_item.setArt({"thumb": p["fanart"],
                          "icon": p["fanart"],
                          "fanart": p["fanart"]})
        list_item.setInfo("stream", {"title": p["value"],
                                    "genre": p["value"],
                                    "mediatype": "stream"})
        url = build_url({"action": "listing", "menuid": p["id"]})
        is_folder = True
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, is_folder)

    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(addon_handle)

def build_menu_contents(menujson, id):
    with open(menujson) as json_file:
        menu = json.load(json_file)

    song_list = []

    n = 0
    for p1 in menu["menu"]:
        if p1["id"] == id:
            # si json
            try:
              rf_url_json = p1["rf_url_json"]
              response = urlopen(rf_url_json) 
              data_json = json.loads(response.read()) 
  
              for p2 in data_json:
                 try:
                   n += 1
                   title = p2["name"]
                   flux = p2["streams"]["live"][0]["url"]
                   visual = p2["logo"]["webpSrc"]
                   list_item = xbmcgui.ListItem(label=title)

                   list_item.setArt({"thumb": visual, "fanart": p1["fanart"]})
                   list_item.setProperty("IsPlayable", "true")
                   list_item.setInfo("music", {"title": title, "genre": title})
                   url = build_url({"mode": "stream", "url": flux, "title": title})
                   song_list.append((url, list_item, False))
                 except:
                   flux = ""  
                   # no thing to do, how to check define value ?
            except:
              # sinon
              for p2 in p1["contents"]["menuitem"]:
                 n += 1
                 title = p2["value"]
                 flux = p2["stream_url"]
                 if p2["fanart"] != "" :
                    visual = p2["fanart"]
                 else:
                    artist, song, fanart, year, duration, album, dt_end = get_info_playing_file(flux)
                    visual = fanart
                 list_item = xbmcgui.ListItem(label=title)
                 #list_item = xbmcgui.ListItem(label=title, thumbnailImage=visual)
                 # setArt

                 list_item.setArt({"thumb": visual, "fanart": p1["fanart"]})
                 list_item.setProperty("IsPlayable", "true")
                 list_item.setInfo("music", {"title": title, "genre": title})
                 url = build_url({"mode": "stream", "url": flux, "title": title})
                 song_list.append((url, list_item, False))

    xbmcplugin.addDirectoryItems(addon_handle, song_list, len(song_list))
    xbmcplugin.setContent(addon_handle, "songs")
    xbmcplugin.endOfDirectory(addon_handle)

def play_song(url):

    xbmc.executebuiltin("ActivateWindow(12006)")
    xbmc.Monitor().waitForAbort(1)
    WINDOW = xbmcgui.Window(12006)
    xbmc.Monitor().waitForAbort(1)

    list_item = xbmcgui.ListItem()
    list_item.setPath(url)
    xbmc.log("Radio-data: Play_url is %s" % url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True , listitem = list_item)
    xbmc.log("Radio-data: pathfilemenu is %s" % pathfilemenu)
    radio_name, radiodata_type, radiodata_file, radiodata_fanart = radiodata_menu_radiodata(pathfilemenu, url)
    xbmc.log("Radio-data: fanart is %s" % radiodata_fanart)
    xbmcvfs.copy(radiodata_fanart, pathfilefallback)
    xbmc.Player().play(item = url, listitem = list_item)
    xbmc.Monitor().waitForAbort(1)
    set_info(url)

    if WINDOW.getProperty("Radio-data") == "true":
        exit(0)
    else:
        WINDOW.setProperty("Radio-data", "true")
        InfoDaemon()

def main():

    args = urllib.parse.parse_qs(sys.argv[2][1:])
    mode = args.get("mode", None)
    menuid = args.get("menuid", None)
    
    # initial launch of add-on
    if mode is None:
        if menuid is None:
            build_menu(pathfilemenu)
        else:
            build_menu_contents(pathfilemenu, menuid[0])

    elif mode[0] == "stream":
        # pass the url of the song to play_song
        play_song(args["url"][0])

if __name__ == "__main__":
    _addon_ = xbmcaddon.Addon()
    setfilemenu = xbmcaddon.Addon("plugin.audio.radio_data").getSettingBool("custom_json")
    xbmc.log("Radio-data: setfilemenu is %s" % setfilemenu)
    if setfilemenu :
        pathfilemenu = xbmcaddon.Addon("plugin.audio.radio_data").getSetting("custom_json_file")
    else :
        filemenu = "radio_data.json"
        path = _addon_.getAddonInfo("path")
        pathfilemenu = os.path.join(path, filemenu)
    xbmc.log("Radio-data: pathfilemenu is %s" % pathfilemenu)
    setfallback = xbmcaddon.Addon("plugin.audio.radio_data").getSettingBool("fallback")
    xbmc.log("Radio-data: setfallback is %s" % setfallback)
    if setfallback :
        pathfallback = xbmcaddon.Addon("plugin.audio.radio_data").getSetting("fallback_path")
        # Temporary file for Artist slide show.
        fallback = "fallback.jpg" 
        pathfilefallback = os.path.join(pathfallback, fallback)
    else :
        pathfilefallback = ""
    xbmc.log("Radio-data: pathfilefallback is %s" % pathfilefallback)

    _url = sys.argv[0]
    addon_handle = int(sys.argv[1])
    main()
