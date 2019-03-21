#-*- coding: utf-8 -*-
#KodiStream https://github.com/KodiStream/xbmc-adult-addons
# type
# https://www.youtube.com/embed/etc....
# https://www.youtube.com/watch?v=etc...
# http://www.youtube-nocookie.com/v/etc...
# https://youtu.be/etc...

from resources.lib.handler.requestHandler import cRequestHandler
from resources.hosters.hoster import iHoster
from resources.lib.parser import cParser
from resources.lib.comaddon import dialog, VSlog
from resources.lib import util
import re
import json

URL_MAIN = 'https://keepvid.app/videos?url='

class cHoster(iHoster):

    def __init__(self):
        self.__sDisplayName = 'Youtube'
        self.__sFileName = self.__sDisplayName
        self.__sHD = ''

    def getDisplayName(self):
        return  self.__sDisplayName

    def setDisplayName(self, sDisplayName):
        self.__sDisplayName = sDisplayName + ' [COLOR skyblue]' + self.__sDisplayName + '[/COLOR]'

    def setFileName(self, sFileName):
        self.__sFileName = sFileName

    def getFileName(self):
        return self.__sFileName

    def getPluginIdentifier(self):
        return 'youtube'

    def setHD(self, sHD):
        self.__sHD = ''

    def getHD(self):
        return self.__sHD

    def isDownloadable(self):
        return True

    def isJDownloaderable(self):
        return True

    def getPattern(self):
        return ''

    def __getIdFromUrl(self, sUrl):
        return ''

    def setUrl(self, sUrl):
        self.__sUrl = sUrl
        self.__sUrl = self.__sUrl.rsplit('/', 1)[1]
        self.__sUrl = self.__sUrl.replace('watch?v=', '')
        self.__sUrl = 'https://www.youtube.com/watch?v=' + str(self.__sUrl)

    def checkUrl(self, sUrl):
        return True

    def __getUrl(self, sUrl):
        return

    def getMediaLink(self):
        first_test = self.__getMediaLinkForGuest2()
        if first_test != False:
            return first_test
        else:
            return self.__getMediaLinkForGuest()

    def __getMediaLinkForGuest2(self):

        oRequestHandler = cRequestHandler(self.__sUrl)
        sHtml = oRequestHandler.request()

        try:
            #note doit etre '{'sHtmlcontent'}'  | 18 premier '{'
            player_conf = sHtml[18 + sHtml.find("ytplayer.config = "):sHtml.find(";ytplayer.load =")]
            bracket_count = 0
            for i, char in enumerate(player_conf):
                if char == "{":
                    bracket_count += 1
                elif char == "}":
                    bracket_count -= 1
                    if bracket_count == 0:
                        break
            else:
                VSlog("Cannot get JSON from HTML")

            index = i + 1
            data = json.loads(player_conf[:index])

        except Exception as e:
            VSlog("Cannot decode JSON: {0}" + str(e))


        stream_map = parse_stream_map(data["args"]["url_encoded_fmt_stream_map"])

        if not (stream_map == False):
            video_urls = zip(stream_map["url"], stream_map["quality"])
            #initialisation des tableaux
            url=[]
            qua=[]
            #Remplissage des tableaux
            for i in video_urls:
                url.append(str(i[0]))
                qua.append(str(i[1]))

            #dialogue qualité
            api_call = dialog().VSselectqual(qua, url)
            if api_call:
                return True, api_call
        else:
            return False

    def __getMediaLinkForGuest(self):

        oParser = cParser()

        sUrl = util.QuotePlus(self.__sUrl)

        oRequest = cRequestHandler(URL_MAIN + sUrl)
        sHtmlContent = oRequest.request()

        sPattern = 'class="al">([^<]+)</td>.+?href="([^"]+)"'

        aResult = oParser.parse(sHtmlContent, sPattern)

        if (aResult[0] == True):
            #initialisation des tableaux
            url=[]
            qua=[]
            #Remplissage des tableaux
            for i in aResult[1]:
                url.append(str(i[1]))
                qua.append(str(i[0]))

            #dialogue qualité
            api_call = dialog().VSselectqual(qua, url)

        if (api_call):
            return True, api_call

        return False, False


def parse_stream_map(sHtml):

    if not '&sp=signature' in sHtml:

        videoinfo = {"itag": [],
                     "url": [],
                     "quality": [],
                     "fallback_host": [],
                     "s": [],
                     "type": [] }

        # Split individual videos
        videos = sHtml.split(",")
        # Unquote the characters and split to parameters
        videos = [video.split("&") for video in videos]
        for video in videos:
            for kv in video:
                key, value = kv.split("=")
                videoinfo.get(key, []).append(util.Unquote(value))

        return videoinfo

    else:
        return False
