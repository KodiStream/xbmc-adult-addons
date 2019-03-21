# -*- coding: utf-8 -*-

from resources.lib.comaddon import addon, dialog, VSlog, xbmc
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.scrapers.gl import cGL
# from resources.lib.scrapers.ade import cADE
from urllib import quote_plus

import os, urlparse, re, unicodedata
import xbmcvfs

class cAFDB:
    UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'

    BASE_URL = 'http://www.adultfilmdatabase.com'
    MOVIE_SEARCH = urlparse.urljoin(BASE_URL, '/lookup.cfm')	

    #enlève les tags html d'une string
    TAG_RE = re.compile(r'<[^>]+>')

    def __init__(self):
    	self.poster = 'http://www.adultfilmdatabase.com/graphics/Boxes/350/Front/%s.jpg'

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
        movie_name = movie_name.replace("'", "")
        movie_name = movie_name.replace(":", "-")
        

        VSlog('---------- SEARCH MOVIE DETAILS FROM AFDB ----------')

        oRequestHandler = cRequestHandler(self.MOVIE_SEARCH)
        oRequestHandler.setRequestType(1)
        oRequestHandler.addHeaderEntry('User-Agent', self.UA)
        oRequestHandler.addHeaderEntry('Referer', self.BASE_URL)
        oRequestHandler.addParameters('action', 'post')   
        oRequestHandler.addParameters('find', movie_name)
        oRequestHandler.addParameters('exact', 1)
        oRequestHandler.addParameters('searchType', 'All')                          
        sHtmlContent = oRequestHandler.request()

        sPattern = '<div class="w3-twothirds">(.+?)</p>'
        sResult = oParser.parse(sHtmlContent, sPattern)

        if (sResult[0] == True):
            sPattern = '<a href="([^"]+)"'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
        	movie_url = str(aResult[1][0])
        	movie_url2 = movie_url

                movie_url2 = movie_url2.split('/', 4)[3]
                movie_name = quote_plus(movie_name)
                movie_name = movie_name.replace('+', '-')
                movie_name = movie_name.replace('--', '---')
                movie_name = movie_name.lower()

                VSlog('MOVIE URL: %s' % (str(movie_url)))
                VSlog('MOVIE URL 2: %s' % (str(movie_url2)))                
                VSlog('MOVIE NAME: %s' % (str(movie_name)))                 

                if (movie_url2 != movie_name):
                    # meta = {}
                    meta = cGL().search_movie_name(media_type, name)
                else:
        	    movie_id = str(aResult[1][0])
        	    movie_id = movie_id.split('/', 3)[2]
        	    meta = self.search_movie_id(media_type, movie_id, movie_url)

        if (sResult[0] == False):
            # meta = {}
            meta = cGL().search_movie_name(media_type, name)
            
        return meta

    def _call(self, media_type, movie_id, movie_url):

        oParser = cParser()
        data = {}
        data['aebn_id'] = movie_id	        

    	sUrl = urlparse.urljoin(self.BASE_URL, movie_url)	

        oRequestHandler = cRequestHandler(sUrl) 
        oRequestHandler.addHeaderEntry('User-Agent', self.UA)
        oRequestHandler.addHeaderEntry('Referer', self.BASE_URL)        
        oRequestHandler.addHeaderEntry('Content-Type', 'text/html; charset=UTF-8')     	
        sHtmlContent = oRequestHandler.request()

        sPattern = '<div itemscope itemtype="http://schema.org/Movie" class="w3-row w3-padding-small">(.+?)Starring</div>'        
        sResult = oParser.parse(sHtmlContent, sPattern)

        if (sResult[0] == True):
            sPattern = '<h1 itemprop="name" class="w3-xxlarge">(.+?)</h1>'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                sTitle = unicode(aResult[1][0], 'utf-8')
                sTitle = unicodedata.normalize('NFD', sTitle).encode('ascii', 'ignore')
                sTitle = sTitle.encode( "utf-8")    
                data['title'] = sTitle

                VSlog('MOVIE TITLE: %s' % (data['title']))

    		sPattern = 'Studio: <a.+?>(.+?)</a>(.+?)<br>'
    		aResult = oParser.parse(sResult[1][0], sPattern)

    		if (aResult[0] == True):
                    sCount = len(aResult[1])                
    		    sStudio = str(aResult[1][0])
    		    data['studio'] = sStudio

                if (sCount > 1):
                    sYear = str(aResult[1][1])
                    sYear = sYear.replace('(', '').replace(')', '')
                    sYear = sYear.strip()
                    data['year'] = int(sYear)

                    VSlog('MOVIE YEAR: %s' % (data['year']))                    

                VSlog('STUDIO: %s' % (str(data['studio'])))				

            sPattern = '<p itemprop="description">(.+?)</p>'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                sOverview = unicode(aResult[1][0], 'utf-8')
                sOverview = unicodedata.normalize('NFD', sOverview).encode('ascii', 'ignore')
                sOverview = sOverview.encode( "utf-8")
                sOverview = sOverview.strip()
                sOverview = self.TAG_RE.sub('', sOverview)
                data['overview'] = sOverview

                VSlog('OVERVIEW: %s' % (data['overview']))

            sPattern = '<span itemprop="duration">Runtime:(.+?)</span>'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                sRuntime = str(aResult[1][0])
                sHours = sRuntime.split(':', 2)[0]
                sMinutes = sRuntime.split(':', 2)[1]
                sRuntime = (int(sHours))*60+int(sMinutes)
                data['runtime'] = sRuntime

                VSlog('RUNTIME: %s' % (data['runtime']))

            sPattern = '<span class="w3-tag w3-small w3-theme-l4 w3-padding-small" style="margin:2px;">(.+?)</span>'
            aResult = oParser.parse(sHtmlContent, sPattern)

            if (aResult[0] == True):
                category = []
                sCount = len(aResult[1])
                i = 0

                while i < sCount:
                    category.append({'name': str(aResult[1][i])})
                    i += 1

                data['genres'] = category

                VSlog('MOVIE GENRES: %s' % (str(data['genres'])))

            data['poster_path'] = self.poster % movie_id     

        return data
