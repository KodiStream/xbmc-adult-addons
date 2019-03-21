# -*- coding: utf-8 -*-

from resources.lib.comaddon import addon, dialog, VSlog, xbmc
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.scrapers.ade import cADE
from urllib import quote_plus

import os, urlparse, re, unicodedata
import xbmcvfs

class cAEBN:
    UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'

    BASE_URL = 'https://vod.aebn.com'
    MOVIE_SEARCH = urlparse.urljoin(BASE_URL, '/straight/search?&sysQuery=%s')	

    #enlève les tags html d'une string
    TAG_RE = re.compile(r'<[^>]+>')

    def __init__(self):
    	self.poster = 'https://pic.aebn.net/Stream/Movie/BoxCovers/a%s_xlf.jpg'

    def search_movie_id(self, media_type, movie_id, movie_url):
    	result = self._call(media_type, movie_id, movie_url)
    	return result

    def search_movie_name(self, media_type, name):

        oParser = cParser()
        meta = {}

        movie_name = unicode(name, 'utf-8')
        movie_name = unicodedata.normalize('NFD', movie_name).encode('ascii', 'ignore')
        movie_name = movie_name.encode( 'utf-8') 
        movie_name = movie_name.replace('!', '')
        movie_name = movie_name.replace('Trips', 'Trip') 
        movie_name = movie_name.replace("'", "")
        
        sUrl = self.MOVIE_SEARCH % (quote_plus(movie_name))

        if (media_type == 'gaymovie'):
            sUrl = sUrl.replace('straight', 'gay')

        VSlog('---------- SEARCH MOVIE DETAILS FROM AEBN ----------')

        VSlog('SEARCH URL: %s' % (str(sUrl)))

        oRequestHandler = cRequestHandler(sUrl) 
        oRequestHandler.addHeaderEntry('User-Agent', self.UA)
        oRequestHandler.addHeaderEntry('Content-Type', 'text/html; charset=UTF-8')        
        sHtmlContent = oRequestHandler.request()

        sPattern = '<section class="dts-panel dts-panel-exact-match dts-panel-exact-match-movie ".+?>(.+?)</section>'
        sResult = oParser.parse(sHtmlContent, sPattern)

        if (sResult[0] == True):
            sPattern = '<h1><a href="([^"]+)">'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                movie_url = str(aResult[1][0])
                movie_id = str(aResult[1][0])
                movie_id = movie_id.split('/',4)[3]
                meta = self.search_movie_id(media_type, movie_id, movie_url)

                VSlog('MOVIE URL: %s' % (str(movie_url)))
                VSlog('MOVIE ID: %s' % (str(movie_id)))

        if (sResult[0] == False):
            page = 1
            meta = cADE().search_movie_name(media_type, name, page)  
            
        return meta     

    def _call(self, media_type, movie_id, movie_url):

        oParser = cParser() 
        data = {}

        data['aebn_id'] = movie_id		

        sUrl = urlparse.urljoin(self.BASE_URL, movie_url)

        if (media_type == 'gaymovie'):
            sUrl = sUrl.replace('straight', 'gay')        

        oRequestHandler = cRequestHandler(sUrl) 
        oRequestHandler.addHeaderEntry('User-Agent', self.UA)
        oRequestHandler.addHeaderEntry('Content-Type', 'text/html; charset=UTF-8')         
        sHtmlContent = oRequestHandler.request()


        sPattern = '<section class="dts-section-page-detail dts-section-page-detail-movie">(.+)</section>'
        sResult = oParser.parse(sHtmlContent, sPattern)

        if (sResult[0] == True):

            sPattern = '<h1>(.+?)</h1>'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                sTitle = unicode(aResult[1][0], 'utf-8')
                sTitle = unicodedata.normalize('NFD', sTitle).encode('ascii', 'ignore')
                sTitle = sTitle.encode( "utf-8")        
                sTitle = sTitle.replace('Trips', 'Trip') 
                data['title'] = sTitle

                VSlog('MOVIE TITLE: %s' % (data['title']))

            sPattern = '<li class="section-detail-list-item-release-date">.+?</span>.+?(.+?)</li>'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                sYear = str(aResult[1][0])
                sYear = sYear.split(',', 1)[1]
                sYear = sYear.replace(' ', '')
                data['year'] = int(sYear)

                VSlog('MOVIE YEAR: %s' % (data['year']))

            sPattern = '<div class="dts-section-page-detail-description-body">(.+?)</div>'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                sOverview = unicode(aResult[1][0], 'utf-8')
                sOverview = unicodedata.normalize('NFD', sOverview).encode('ascii', 'ignore')
                sOverview = sOverview.encode( "utf-8")               
                sOverview = sOverview.strip()
                sOverview = self.TAG_RE.sub('', sOverview)
                data['overview'] = sOverview

                VSlog('OVERVIEW: %s' % (data['overview']))

            sPattern = '<div class="dts-studio-name-wrapper">.+?<a.+?>(.+?)</a>'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                sStudio = str(aResult[1][0])
                data['studio'] = sStudio

                VSlog('STUDIO: %s' % (str(data['studio'])))

            sPattern = '<li class="section-detail-list-item-duration">.+?</span>.+?(.+?)</li>'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                sRuntime = str(aResult[1][0])
                sHours = sRuntime.split(':', 2)[0]
                sMinutes = sRuntime.split(':', 2)[1]
                sRuntime = (int(sHours))*60+int(sMinutes)
                data['runtime'] = sRuntime

                VSlog('RUNTIME: %s' % (data['runtime']))

            sPattern = '<div class="dts-image-overlay-container">(.+?)</div>'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                sPattern = 'alt="(.+?)"'
                aResult = oParser.parse(aResult[1], sPattern)                                  

                if (aResult[0] == True):
                    category = []
                    sCount = len(aResult[1])
                    i = 0

                    while i < sCount:
                        if ('New Release' not in aResult[1][i] or 'Sale' in aResult[1][i]):
                            category.append({'name': str(aResult[1][i])})
                        i += 1

                    data['genres'] = category

                    VSlog('MOVIE GENRES: %s' % (str(data['genres'])))

            data['poster_path'] = self.poster % movie_id     

        return data