# -*- coding: utf-8 -*-

from resources.lib.comaddon import addon, dialog, VSlog, xbmc
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from urllib import quote_plus

import os, urlparse, re, unicodedata
import xbmcvfs

class cGL:
    UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'

    BASE_URL = 'https://www.gamelink.com/s'
    MOVIE_SEARCH = urlparse.urljoin(BASE_URL, '/search?type=movies&query=%s')
    MOVIE_INFO = urlparse.urljoin(BASE_URL, '/adult-movies/p/%s')

    GAY_URL = 'https://www.gamelink.com/g'
    GAY_MOVIE_SEARCH = urlparse.urljoin(GAY_URL, '/search?type=movies&query=%s')
    GAY_MOVIE_INFO = urlparse.urljoin(GAY_URL, '/adult-movies/p/%s')    

    #enlève les tags html d'une string
    TAG_RE = re.compile(r'<[^>]+>')

    def __init__(self):
    	self.poster = 'https://ecdn.hs.llnwd.net/e1/GLImages/prodimages/%s.jpg'

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
        movie_name = movie_name.replace(":", "")

        if (media_type == 'gaymovie'):
            sUrl = self.GAY_MOVIE_SEARCH % (quote_plus(movie_name))
        else:
            sUrl = self.MOVIE_SEARCH % (quote_plus(movie_name))

        VSlog('---------- SEARCH MOVIE DETAILS FROM GAMELINK ----------')

        VSlog('SEARCH URL: %s' % (str(sUrl)))

        oRequestHandler = cRequestHandler(sUrl) 
        oRequestHandler.addHeaderEntry('User-Agent', self.UA)
        oRequestHandler.addHeaderEntry('Content-Type', 'text/html; charset=UTF-8')         
        sHtmlContent = oRequestHandler.request()

        sPattern = '<div class="image-inner"><a href="([^"]+)" >'
        sResult = oParser.parse(sHtmlContent, sPattern)

        if (sResult[0] == True):
            movie_id = str(sResult[1][0])

            VSlog('MOVIE URL ID: %s' % (str(movie_id)))

            movie_id = movie_id.split('/', 5)[4]

            VSlog('MOVIE ID: %s' % (str(movie_id)))

            meta = self.search_movie_id(media_type, movie_id)

        if (sResult[0] == False):
            meta = {}

        return meta

    def _call(self, media_type, movie_id):

        oParser = cParser()
        data = {}

        data['aebn_id'] = movie_id  

        if (media_type == 'gaymovie'):
            sUrl = self._GAY_MOVIE_INFO % movie_id
        else:
            sUrl = self.MOVIE_INFO % movie_id

        oRequestHandler = cRequestHandler(sUrl) 
        oRequestHandler.addHeaderEntry('User-Agent', self.UA)
        oRequestHandler.addHeaderEntry('Content-Type', 'text/html; charset=UTF-8')         
        sHtmlContent = oRequestHandler.request()

        sPattern = '<div class="prod-page" id="movie" itemscope="" itemtype="http://schema.org/Movie">(.+?)<div class="prod-stars">'
        sResult = oParser.parse(sHtmlContent, sPattern)

        if (sResult[0] == True):
            sPattern = '<h1 itemprop="name">(.+?)</h1>'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                sTitle = unicode(aResult[1][0], 'utf-8')
                sTitle = unicodedata.normalize('NFD', sTitle).encode('ascii', 'ignore')
                sTitle = sTitle.encode( "utf-8")
                sTitle = sTitle.replace('#', '')
                data['title'] = sTitle

                VSlog('MOVIE TITLE: %s' % (data['title']))

            data['year'] = int('2010')

            sPattern = '<div class="description">(.+?)</div>'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                sOverview = unicode(aResult[1][0], 'utf-8')
                sOverview = unicodedata.normalize('NFD', sOverview).encode('ascii', 'ignore')
                sOverview = sOverview.encode( "utf-8")               
                sOverview = sOverview.strip()
                sOverview = self.TAG_RE.sub('', sOverview)
                data['overview'] = sOverview            

                VSlog('OVERVIEW: %s' % (data['overview']))

            sPattern = '<p>Studio: <a href=".+?">(.+?)</a>'
            aResult = oParser.parse(sResult[1][0], sPattern)          

            if (aResult[0] == True):
                sStudio = str(aResult[1][0])
                data['studio'] = sStudio

                VSlog('STUDIO: %s' % (str(data['studio'])))

            sPattern = '<p>Runtime:(.+?)</p>'       
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                sRuntime = str(aResult[1][0])
                sRuntime = sRuntime.replace('minutes', '')
                sRuntime = sRuntime.replace(' ', '')    
                data['runtime'] = int(sRuntime)

                VSlog('RUNTIME: %s' % (data['runtime']))

            sPattern = '<ul class="parent-categories">(.+?)</ul>'
            aResult = oParser.parse(sHtmlContent, sPattern)

            if (aResult[0] == True):
                sPattern = '<a href=".+?">(.+?)</a>'
                aResult = oParser.parse(aResult[1][0], sPattern)

                if (aResult[0] == True):
                    category = []
                    sCount = len(aResult[1])
                    i = 0

                    while i < sCount:
                        VSlog('GENRE: %s' % (str(aResult[1][i])))
                        if (aResult[1][i] != 'Adult Movies' and aResult[1][i] != 'Porn Trailers' and aResult[1][i] != 'Movies With Trailers'):
                            category.append({'name': str(aResult[1][i])})
                        i += 1

                    data['genres'] = category

                    VSlog('MOVIE GENRES: %s' % (str(data['genres'])))

            data['poster_path'] = self.poster % movie_id

        return data                     