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

class It(xbmcgui.ListItem):
    def __init__(self):
        xbmcgui.ListItem.__init__(self)

    def update_info_radiofrance(self, url_json):
        artist,song,fanart,year,duration,album=get_info_radiofrance(url_json)
        self.setArt({"thumb":fanart, "fanart":fanart})
        self.setInfo("music", {"title": song, "artist": artist, "year": year, "duration": duration, "album": album})

    def update_info_rfm(self, url_json):
        artist,song,fanart,year,duration,album=get_info_rfm(url_json)
        self.setArt({"thumb":fanart, "fanart":fanart})
        self.setInfo("music", {"title": song, "artist": artist, "year": year, "duration": duration, "album": album})

class Radio(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self)

    def PlayRadio(self, stream):
       xbmc.log("PlayerRadio stream is %s" % stream, xbmc.LOGNOTICE)
       it=It()
       it.setPath(stream)
       # in a script only ???
       self.play(item=stream, listitem=it)
       xbmcplugin.setResolvedUrl(int(sys.argv[1]), True , listitem=it)
       xbmc.Monitor().waitForAbort(1)

    def InfoDaemon(self):
       periode = 10
       while 1:
           if self.isPlayingAudio():
               playing_file = xbmc.Player().getPlayingFile()
               xbmc.log("InfoDeamon playingfile is %s" % playing_file, xbmc.LOGNOTICE)
               set_info(playing_file)
               xbmc.Monitor().waitForAbort(periode)

def set_info(playing_file):
    xbmc.log("get_info url is %s" % playing_file, xbmc.LOGNOTICE)
    json = ""
    #if playing_file == "http://direct.fipradio.fr/live/fip-midfi.mp3": # FIP National
    if playing_file == "http://icecast.radiofrance.fr/fip-midfi.mp3": # FIP National
        xbmc.log("InfoDeamon FIP National", xbmc.LOGNOTICE)
        json = "https://api.radiofrance.fr/livemeta/pull/7"
    elif playing_file == "http://direct.fipradio.fr/live/fip-webradio1.mp3": # FIP autour du rock
        xbmc.log("InfoDeamon FIP rock", xbmc.LOGNOTICE)
        json = "https://api.radiofrance.fr/livemeta/pull/64"
    elif playing_file == "http://chai5she.cdn.dvmr.fr:80/fip-webradio5.mp3": # FIP Tout nouveau
        xbmc.log("InfoDeamon FIP nouveau", xbmc.LOGNOTICE)
        json = "https://api.radiofrance.fr/livemeta/pull/70"
    elif playing_file == "http://direct.fipradio.fr/live/fip-webradio4.mp3": # FIP Monde
        xbmc.log("InfoDeamon FIP Monde", xbmc.LOGNOTICE)
        json = "https://api.radiofrance.fr/livemeta/pull/69"
    elif playing_file == "http://direct.fipradio.fr/live/fip-webradio2.mp3": # FIP Jazz
        xbmc.log("InfoDeamon FIP Jazz", xbmc.LOGNOTICE)
        json = "https://api.radiofrance.fr/livemeta/pull/65"
    elif playing_file == "http://direct.fipradio.fr/live/fip-webradio6.mp3": # FIP Reggae
        xbmc.log("InfoDeamon FIP Reggae", xbmc.LOGNOTICE)
        json = "https://api.radiofrance.fr/livemeta/pull/71"
    elif playing_file == "http://rfm-live-mp3-128.scdn.arkena.com/rfm.mp3": # RFM
        xbmc.log("InfoDeamon RFM", xbmc.LOGNOTICE)
        json = "http://directradio.rfm.fr/rfm/now/3"
    if json != "":
        xbmc.log("Json %s" % json, xbmc.LOGNOTICE)
        try:
          if json == "http://directradio.rfm.fr/rfm/now/3":
              artist,song,fanart,year,duration,album=get_info_rfm(json)
          else:
              artist,song,fanart,year,duration,album=get_info_radiofrance(json)
          test = xbmcgui.ListItem()
          test.setPath(xbmc.Player().getPlayingFile())
          test.setArt({"thumb":fanart, "fanart":fanart})
          test.setInfo("music", {"title": song, "artist": artist, "year": year, "duration": duration, "album": album})
          xbmc.Player().updateInfoTag(test)
          artist_debug = xbmc.Player().getMusicInfoTag().getArtist()
          xbmc.log("InfoDeamon Test Artist debug %s" % artist_debug, xbmc.LOGNOTICE)
        except:
          xbmc.log("Can't update json", xbmc.LOGNOTICE)

def get_info_radiofrance(url):
    xbmc.log("get_info url is %s" % url, xbmc.LOGNOTICE)
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
      if i <> -1 and artist == "" :
          artist = song.replace('en session live', '') # work ?
          song = 'Session live'           
          try:
            album = v1["titleConcept"]
          except:
            album = ""
      duration = end - start
      xbmc.log("Artists is %s" % artist, xbmc.LOGNOTICE)
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
    xbmc.log("get_info url is %s" % url, xbmc.LOGNOTICE)
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
    xbmc.log("Artists is %s" % artist, xbmc.LOGNOTICE)
    return artist,song,fanart,year,duration,album

def build_url(query):
    base_url = sys.argv[0]
    return base_url + '?' + urllib.urlencode(query)

def build_song_list():
    song_list = []

    title = "Fip Nationale"
    #flux = "http://direct.fipradio.fr/live/fip-midfi.mp3"
    flux = "http://icecast.radiofrance.fr/fip-midfi.mp3"
    visual = "http://mediateur.radiofrance.fr/wp-content/themes/radiofrance/img/fip.png"
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    song_list.append((url, li, False))

    title = "Fip Tout nouveau"
    flux = "http://chai5she.cdn.dvmr.fr:80/fip-webradio5.mp3"
    visual = "https://cdn.radiofrance.fr/s3/cruiser-production/2019/06/e061141c-f6b4-4502-ba43-f6ec693a049b/200x200_fip-nouveau_ok.jpg"
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    song_list.append((url, li, False))

    title = "Fip Rock"
    flux = "http://direct.fipradio.fr/live/fip-webradio1.mp3"
    visual = "https://cdn.radiofrance.fr/s3/cruiser-production/2019/06/f5b944ca-9a21-4970-8eed-e711dac8ac15/200x200_fip-rock_ok.jpg"
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    song_list.append((url, li, False))

    title = "Fip Monde"
    flux = "http://direct.fipradio.fr/live/fip-webradio4.mp3"
    visual = "https://cdn.radiofrance.fr/s3/cruiser-production/2019/06/9a1d42c5-8a36-4253-bfae-bdbfb85cbe14/200x200_fip-monde_ok.jpg"
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    song_list.append((url, li, False))

    title = "Fip Jazz"
    flux = "http://direct.fipradio.fr/live/fip-webradio2.mp3"
    visual = "https://cdn.radiofrance.fr/s3/cruiser-production/2019/06/840a4431-0db0-4a94-aa28-53f8de011ab6/200x200_fip-jazz-01.jpg"
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    song_list.append((url, li, False))

    title = "Fip Reggae"
    flux = "http://direct.fipradio.fr/live/fip-webradio6.mp3"
    visual = "https://cdn.radiofrance.fr/s3/cruiser-production/2019/06/15a58f25-86a5-4b1a-955e-5035d9397da3/200x200_fip-reggae_ok.jpg"
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    song_list.append((url, li, False))

    title = "RFM"
    flux = "http://rfm-live-mp3-128.scdn.arkena.com/rfm.mp3"
    visual = "https://cdn-rfm.lanmedia.fr/bundles/rfmintegration/images/logoRFM.png"
    li = xbmcgui.ListItem(label=title, thumbnailImage=visual)
    li.setProperty('fanart_image', visual)
    li.setProperty('IsPlayable', 'true')
    url = build_url({'mode': 'stream', 'url': flux, 'title': title})
    song_list.append((url, li, False))

    xbmcplugin.addDirectoryItems(addon_handle, song_list, len(song_list))
    xbmcplugin.setContent(addon_handle, 'songs')
    xbmcplugin.endOfDirectory(addon_handle)
    
def play_song(url):
    xbmc.log("url is %s" % url, xbmc.LOGNOTICE)
    xbmc.executebuiltin("ActivateWindow(12006)")
    WINDOW = xbmcgui.Window(12006)

    radio=Radio()
    xbmc.log("PlayerRadio stream is %s" % url, xbmc.LOGNOTICE)
    test = xbmcgui.ListItem()
    test.setPath(url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True , listitem=test)
    xbmc.Player().play(item=url, listitem=test)
    xbmc.Monitor().waitForAbort(1)
    set_info(url)

    if WINDOW.getProperty("Radio-France-Running") == "true":
        xbmc.log("Script already running - Not starting a new instance", xbmc.LOGNOTICE)
        exit(0)
    else:
        WINDOW.setProperty("Radio-France-Running", "true")
        radio.InfoDaemon()

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