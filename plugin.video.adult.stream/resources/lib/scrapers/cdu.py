# -*- coding: utf-8 -*-

from resources.lib.comaddon import addon, dialog, VSlog, xbmc
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from urllib import quote_plus

import os, urlparse, re, unicodedata
import xbmcvfs

class cCDU:
    UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'

    BASE_URL = 'https://www.cduniverse.com'
    MOVIE_SEARCH = urlparse.urljoin(BASE_URL, '/sresult.asp?SF=1&HT_Search=TITLE&HT_Search_Info=%s&style=ice')
    MOVIE_INFO = urlparse.urljoin(BASE_URL, '/productinfo.asp?pid=%s&style=ice')
    GAY_MOVIE_SEARCH = urlparse.urljoin(BASE_URL, '/sresult.asp?SF=1&HT_Search=TITLE&HT_Search_Info=%s&style=gay')
    GAY_MOVIE_INFO = urlparse.urljoin(BASE_URL, '/productinfo.asp?pid=%s&style=gay')

    #enlève les tags html d'une string
    TAG_RE = re.compile(r'<[^>]+>')

    def __init__(self):
        self.poster = 'https://c8.cduniverse.ws/resized/380x570/ice/%s/%s.jpg'

    def search_movie_id(self, media_type, movie_id):
        result = self._call(media_type, movie_id)
        return result        

    def search_movie_name(self, media_type, name):

        oParser = cParser()
        meta = {}

        movie_name = unicode(name, 'utf-8')
        movie_name = unicodedata.normalize('NFD', movie_name).encode('ascii', 'ignore')
        movie_name = movie_name.encode( 'utf-8') 
        movie_name = movie_name.replace('!', '')
        movie_name = movie_name.replace("'", "")        

        if (media_type == 'gaymovie'):
            sUrl = self.GAY_MOVIE_SEARCH % (quote_plus(movie_name))
        else:
            sUrl = self.MOVIE_SEARCH % (quote_plus(movie_name))

        VSlog('---------- SEARCH MOVIE DETAILS FROM CDUNIVERSE ADULT ----------')

        VSlog('SEARCH URL: %s' % (str(sUrl)))

        oRequestHandler = cRequestHandler(sUrl) 
        oRequestHandler.addHeaderEntry('User-Agent', self.UA)
        oRequestHandler.addHeaderEntry('Content-Type', 'text/html; charset=UTF-8')           
        sHtmlContent = oRequestHandler.request()   

        sPattern = '<table.*id="chunky".+?(.+?)</table>'
        sResult = oParser.parse(sHtmlContent, sPattern)    	

        if (sResult[0] == True):
            sPattern = '<a href="([^"]+)">'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                movie_url = str(aResult[1][0])
                sPattern = 'pid=(.+?)&'
                aResult = oParser.parse(movie_url, sPattern)

                if (aResult[0] == True):
                    movie_id = str(aResult[1][0])
                    meta = self.search_movie_id(media_type, movie_id)

                    VSlog('MOVIE URL: %s' % (str(movie_url)))
                    VSlog('MOVIE ID: %s' % (str(movie_id)))

        if (sResult[0] == False):
            meta = {}

        return meta

    def _call(self, media_type, movie_id):

        oParser = cParser()
        data = {}

        data['aebn_id'] = movie_id

        if (media_type == 'gaymovie'):
            sUrl = self.GAY_MOVIE_INFO % movie_id
        else:
            sUrl = self.MOVIE_INFO % movie_id

        oRequestHandler = cRequestHandler(sUrl) 
        oRequestHandler.addHeaderEntry('User-Agent', self.UA)
        oRequestHandler.addHeaderEntry('Content-Type', 'text/html; charset=UTF-8')         
        sHtmlContent = oRequestHandler.request()

        sPattern = '<div class="product-view".+?>(.+)<div.+?id="SimilarProducts">'
        sResult = oParser.parse(sHtmlContent, sPattern)

        if (sResult[0] == True):
            sPattern = '<h1.+?>(.+?)</h1>'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                sTitle = unicode(aResult[1][0], 'utf-8')
                sTitle = unicodedata.normalize('NFD', sTitle).encode('ascii', 'ignore')
                sTitle = sTitle.encode( "utf-8")   
                sTitle = sTitle.replace('#', '').replace('DVD', '')
                data['title'] = str(movie_name)

                VSlog('MOVIE TITLE: %s' % (data['title']))

            sPattern = 'Release Date</td><td>(.+?)</td>'
            aResult = oParser.parse(sHtmlContent, sPattern)

            if (aResult[0] == True):
                sYear = str(aResult[1][0])
                sYear = sYear.replace(' ', '')
                sYear = sYear.split(',', 1)[1]
                data['year'] = int(sYear)

                VSlog('MOVIE YEAR: %s' % (data['year']))

            sPattern = '<span id="description">(.+?)</span>'
            aResult = oParser.parse(sHtmlContent, sPattern)

            if (aResult[0] == True):
                sOverview = unicode(aResult[1][0], 'utf-8')
                sOverview = unicodedata.normalize('NFD', sOverview).encode('ascii', 'ignore')
                sOverview = sOverview.encode( "utf-8")
                sOverview = sOverview.strip()
                sOverview = self.TAG_RE.sub('', sOverview)
                data['overlay'] = sOverview

                VSlog('OVERVIEW: %s' % (data['overview']))

            sPattern = 'Running Time</td><td>(.+?)</td>'
            aResult = oParser.parse(sHtmlContent, sPattern)

            if (aResult[0] == True):
                sRuntime = str(aResult[1][0])
                sRuntime = sRuntime.replace(' ', '').replaces('minutes', '')
                data['runtime'] = int(sRuntime)

                VSlog('RUNTIME: %s' % (data['runtime']))

            sPattern = 'Category</td>(.+?)</td>'
            aResult = oParser.parse(sHtmlContent, sPattern)

            if (aResult[0] == True):
                sPattern = '<a.+?>(.+?)</a>'
                aResult = oParser.parse(aResult[1][0], sPattern)

                if (aResult[0] == True):
                    category = []
                    sCount = len(aResult[1])
                    i = 0

                    while i < sCount:
                        category.append({'name': str(aResult[1][i])})
                    i += 1

                    data['genres'] = category

                    VSlog('MOVIE GENRES: %s' % (str(data['genres'])))

            page_id = movie_id[-3:]
            poster_url = self.poster % (page_id, movie_id)
            data['poster_path'] = poster_url

        return data
