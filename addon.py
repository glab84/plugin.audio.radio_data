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

def get_info_playing_file(playing_file):
    json = ""
    if playing_file == "https://icecast.radiofrance.fr/fip-hifi.aac?id=radiofrance": # FIP National
        json = "https://api.radiofrance.fr/livemeta/pull/7"
    elif playing_file == "https://icecast.radiofrance.fr/fipnouveautes-hifi.aac?id=radiofrance": # FIP Tout nouveau
        json = "https://api.radiofrance.fr/livemeta/pull/70"
    elif playing_file == "https://icecast.radiofrance.fr/fiprock-hifi.aac?id=radiofrance": # FIP Rock
        json = "https://api.radiofrance.fr/livemeta/pull/64"
    elif playing_file == "https://icecast.radiofrance.fr/fipworld-hifi.aac?id=radiofrance": # FIP Monde
        json = "https://api.radiofrance.fr/livemeta/pull/69"
    elif playing_file == "https://icecast.radiofrance.fr/fipjazz-hifi.aac?id=radiofrance": # FIP Jazz
        json = "https://api.radiofrance.fr/livemeta/pull/65"
    elif playing_file == "https://icecast.radiofrance.fr/fipreggae-hifi.aac?id=radiofrance": # FIP Reggae
        json = "https://api.radiofrance.fr/livemeta/pull/71"
    elif playing_file == "https://icecast.radiofrance.fr/fipgroove-hifi.aac?id=radiofrance": # FIP Groove
        json = "https://api.radiofrance.fr/livemeta/pull/66"
    elif playing_file == "https://icecast.radiofrance.fr/fipelectro-hifi.aac?id=radiofrance": # FIP Electro
        json = "https://api.radiofrance.fr/livemeta/pull/74"
    elif playing_file == "https://icecast.radiofrance.fr/fippop-hifi.aac?id=radiofrance": # FIP Pop
        json = "https://www.fip.fr/latest/api/graphql?operationName=NowList&variables=%7B%22bannerPreset%22%3A%22266x266%22%2C%22stationIds%22%3A%5B78%5D%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22151ca055b816d28507dae07f9c036c02031ed54e18defc3d16feee2551e9a731%22%7D%7D"
    elif playing_file == "https://ais-live.cloud-services.paris:8443/rfm.mp3": # RFM
        json = "http://directradio.rfm.fr/rfm/now/3"

    if json != "":
        xbmc.log("Radio_data: Json %s" % json)
        try:
          if json == "http://directradio.rfm.fr/rfm/now/3":
              artist,song,fanart,year,duration,album=get_info_rfm(json)
          else:
              graphgl=re.compile('.*graphql.*')
              if graphgl.match(json):
                  artist,song,fanart,year,duration,album=get_info_radiofrance_graphql(json)
              else:
                  artist,song,fanart,year,duration,album=get_info_radiofrance(json)
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

def build_song_list():
    song_list = []

    title = "Fip Nationale"
    flux = "https://icecast.radiofrance.fr/fip-hifi.aac?id=radiofrance"
    artist,song,fanart,year,duration,album=get_info_playing_file(flux)
    visual = fanart
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    li.setInfo('music', {'title': title, 'genre': title})
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    song_list.append((url, li, False))

    title = "Fip Nouveautés"
    flux = "https://icecast.radiofrance.fr/fipnouveautes-hifi.aac?id=radiofrance"
    artist,song,fanart,year,duration,album=get_info_playing_file(flux)
    visual = fanart
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    li.setInfo('music', {'title': title, 'genre': title})
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    song_list.append((url, li, False))

    title = "Fip Rock"
    flux = "https://icecast.radiofrance.fr/fiprock-hifi.aac?id=radiofrance"
    artist,song,fanart,year,duration,album=get_info_playing_file(flux)
    visual = fanart
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    li.setInfo('music', {'title': title, 'genre': title})
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    song_list.append((url, li, False))

    title = "Fip Monde"
    flux = "https://icecast.radiofrance.fr/fipworld-hifi.aac?id=radiofrance"
    artist,song,fanart,year,duration,album=get_info_playing_file(flux)
    visual = fanart
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    li.setInfo('music', {'title': title, 'genre': title})
    song_list.append((url, li, False))

    title = "Fip Jazz"
    flux = "https://icecast.radiofrance.fr/fipjazz-hifi.aac?id=radiofrance"
    artist,song,fanart,year,duration,album=get_info_playing_file(flux)
    visual = fanart
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    li.setInfo('music', {'title': title, 'genre': title})
    song_list.append((url, li, False))

    title = "Fip Reggae"
    flux = "https://icecast.radiofrance.fr/fipreggae-hifi.aac?id=radiofrance"
    artist,song,fanart,year,duration,album=get_info_playing_file(flux)
    visual = fanart
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    li.setInfo('music', {'title': title, 'genre': title})
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    song_list.append((url, li, False))

    title = "Fip Groove"
    flux = "https://icecast.radiofrance.fr/fipgroove-hifi.aac?id=radiofrance"
    artist,song,fanart,year,duration,album=get_info_playing_file(flux)
    visual = fanart
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    li.setInfo('music', {'title': title, 'genre': title})
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    song_list.append((url, li, False))

    title = "Fip Electro"
    flux = "https://icecast.radiofrance.fr/fipelectro-hifi.aac?id=radiofrance"
    artist,song,fanart,year,duration,album=get_info_playing_file(flux)
    visual = fanart
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    li.setInfo('music', {'title': title, 'genre': title})
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    song_list.append((url, li, False))

    title = "Fip Pop"
    flux = "https://icecast.radiofrance.fr/fippop-hifi.aac?id=radiofrance"
    artist,song,fanart,year,duration,album=get_info_playing_file(flux)
    visual = fanart
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    li.setInfo('music', {'title': title, 'genre': title})
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    song_list.append((url, li, False))

    title = "RFM"
    flux = "https://ais-live.cloud-services.paris:8443/rfm.mp3"
    visual = "https://cdn-rfm.lanmedia.fr/bundles/rfmintegration/images/logoRFM.png"
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    li.setInfo('music', {'title': title, 'genre': title})
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    song_list.append((url, li, False))

    xbmcplugin.addDirectoryItems(addon_handle, song_list, len(song_list))
    xbmcplugin.setContent(addon_handle, 'songs')
    xbmcplugin.endOfDirectory(addon_handle)
    
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
    
    # initial launch of add-on
    if mode is None:
        # display the list of songs in Kodi
        build_song_list()
        # a song from the list has been selected
    elif mode[0] == 'stream':
        # pass the url of the song to play_song
        play_song(args['url'][0])
    
if __name__ == '__main__':
    addon_handle = int(sys.argv[1])
    main()
