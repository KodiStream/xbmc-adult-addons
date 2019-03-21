# -*- coding: utf-8 -*-

from resources.lib.comaddon import addon, dialog, VSlog, xbmc
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
# from resources.lib.scrapers.tvts import cTVTS
# from resources.lib.scrapers.cdu import cCDU
from resources.lib.scrapers.afdb import cAFDB
from urllib import quote_plus

import os, urlparse, re, unicodedata
import xbmcvfs

class cADE:
    UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'

    BASE_URL = 'http://www.adultdvdempire.com'
    MOVIE_SEARCH = urlparse.urljoin(BASE_URL, '/dvd/search?m=false&pageSize=%s&view=list&q=%s')
    MOVIE_INFO = urlparse.urljoin(BASE_URL, '/%s/')

    GAY_URL = 'https://www.gaydvdempire.com'
    GAY_MOVIE_SEARCH = urlparse.urljoin(BASE_URL, '/dvd/search?m=false&pageSize=%s&view=list&q=%s')
    GAY_MOVIE_INFO = urlparse.urljoin(BASE_URL, '/%s/')    

    #enlève les tags html d'une string
    TAG_RE = re.compile(r'<[^>]+>')

    def __init__(self):
    	self.poster = 'https://imgs1cdn.adultempire.com/products/%s/%sh.jpg'

    def search_movie_id(self, media_type, movie_id):
    	result = self._call(media_type, movie_id)
    	return result 

    def search_movie_name(self, media_type, name, page): 

        oParser = cParser()
        meta = {}
        movies = []

        movie_name = unicode(name, 'utf-8')
        movie_name = unicodedata.normalize('NFD', movie_name).encode('ascii', 'ignore')
        movie_name = movie_name.encode( 'utf-8') 
        movie_name = movie_name.replace('!', '')
        movie_name = movie_name.replace("'", "")
        movie_name = movie_name.replace('Trips', 'Trip')   
        
        if (media_type == 'gaymovie'):
            sUrl = self.GAY_MOVIE_SEARCH % (page, quote_plus(movie_name))
        else:
            sUrl = self.MOVIE_SEARCH % (page, quote_plus(movie_name))

        VSlog('---------- SEARCH MOVIE DETAILS FROM ADULTDVDEMPIRE ----------')

        VSlog('SEARCH URL: %s' % (str(sUrl)))

        oRequestHandler = cRequestHandler(sUrl) 
        oRequestHandler.addHeaderEntry('User-Agent', self.UA)
        oRequestHandler.addHeaderEntry('Content-Type', 'text/html; charset=UTF-8')         
        sHtmlContent = oRequestHandler.request()   
            
        sPattern = '<div class="col-xs-5 col-sm-2 list-view-item-cover"><a href="([^"]+)"'
        sResult = oParser.parse(sHtmlContent, sPattern)

        if (sResult[0] == True):
            movie_id = str(sResult[1][0])
            movie_id = movie_id.split('/', 2)[1]

            VSlog('MOVIE ID: %s' % (str(movie_id)))            

            movie_url = str(sResult[1][0])
            movie_url = movie_url.replace('joey-silveras-big-ass-', '')
            movie_url = movie_url.replace('joey-silveras-', '')
            movie_url = movie_url.replace('the-porn-movies.html', 'porn-movies.html')
            movie_url = movie_url.replace('--', '-')
            movie_url = movie_url.replace('the-best', 'best')  
            movie_url = movie_url.replace('-vol', '')     

            movie_name = quote_plus(movie_name)
            movie_name = movie_name.replace('The+Best', 'Best')
            movie_name = movie_name.replace('The+Art', 'art')
            movie_name = movie_name.replace('%2527', '')
            movie_name = movie_name.replace('%3A', '')

            sPattern = '(.+?)\+-'
            aResult = oParser.parse(movie_name, sPattern)

            if (aResult[0] == True):
                movie_name = aResult[1][0]

            movie_name = movie_name.replace('+', '-')
            movie_name = movie_name.lower()

            sPattern = '/.+?/(.+?)-porn-movies\.html'
            aResult = oParser.parse(movie_url, sPattern)

            if (aResult[0] == True):
                movie_url = aResult[1][0]

            # sPattern = '(.+?)-vol'
            # aResult = oParser.parse(movie_url, sPattern)

            # if (aResult[0] == True):
            #     movie_url = aResult[1][0]            

            VSlog('MOVIE URL: %s' % (str(movie_url)))
            VSlog('MOVIE NAME: %s' % (str(movie_name)))                

            if (movie_url != movie_name):
                if (media_type == 'pornmovie'):
                    # meta = cCDU().search_movie_name(media_type, name)
                    meta = cAFDB().search_movie_name(media_type, name)
                # else:
                #     meta = cTVTS().search_movie_name(name)   
            else:
                meta = self.search_movie_id(media_type, movie_id) 

        if  (sResult[0] == False):
            if (media_type == 'pornmovie'):
                # meta = cCDU().search_movie_name(media_type, name)
                meta = cAFDB().search_movie_name(media_type, name)
            else:
                meta = {}
            # else:            
            #     meta = cTVTS().search_movie_name(name) 

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

        sPattern = 'data-tid="' + movie_id + '".+?>(.+)'   
        sResult = oParser.parse(sHtmlContent, sPattern)

        if (sResult[0] == True):
            sPattern = '<h1>(.+?)</h1>'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                sTitle = unicode(aResult[1][0], 'utf-8')
                sTitle = unicodedata.normalize('NFD', sTitle).encode('ascii', 'ignore')
                sTitle = sTitle.encode( "utf-8") 
                sTitle = sTitle.replace(', The', '')
                sTitle = sTitle.replace('- On Sale!', '')
                data['title'] = sTitle

                VSlog('MOVIE TITLE: %s' % (data['title']))

            sPattern = '<ul class="list-unstyled m-b-2">(.+?)</ul>'
            aResult = oParser.parse(sResult[1][0], sPattern)

            if (aResult[0] == True):
                productInfo = str(aResult[1][0])
                productInfo = productInfo.replace('<small>', '|').replace('</small>', '')
                productInfo = productInfo.replace('<li>', '').replace('</li>', '')

                for div in productInfo.split('|'):
                    if ':' in div:
                        name, value = div.split(':')
                        if name == 'Length':
                            name = 'runtime'
                            sRuntime = str(value.strip())
                            sRuntime = sRuntime.replace(' ', '')
                            sRuntime = sRuntime.replace('hrs', '').replace('mins', '')
                            sHours = sRuntime.split('.', 2)[0]
                            sMins = sRuntime.split('.', 2)[1]
                            sRuntime = (int(sHours))*60 + int(sMins)
                            data[name] = sRuntime

                            VSlog('RUNTIME: %s' % (data['runtime']))

                        if name == 'Studio':
                            name = 'studio'
                            data[name] = self.TAG_RE.sub('', str(value.strip()))

                            VSlog('STUDIO: %s' % (data['studio']))

                        if name == 'Production Year':
                            name = 'year'
                            data[name] = int(value.strip())

                            VSlog('MOVIE YEAR: %s' % (data['year']))

            # sPattern = '<div class="product-details-container">(.+?)</div>'
            sPattern = '<div class="product-details-container">(.+?)</small>'
            aResult = oParser.parse(sHtmlContent, sPattern)

            if (aResult[0] == True):
                # sPattern = '<h4.+?">(.+?)</h4>'   
                sPattern = '<h4 class=".+?text-dark synopsis">(.+?)</h4>'   
                aResult = oParser.parse(aResult[1][0], sPattern)

                if (aResult[0] == True):
                    sOverview = str(aResult[1][0])
                    sOverview = sOverview.replace('</p>', '\n')   
                    sOverview = self.TAG_RE.sub('', sOverview)
                    sOverview = unicode(sOverview, 'utf-8')
                    sOverview = unicodedata.normalize('NFD', sOverview).encode('ascii', 'ignore')
                    sOverview = sOverview.encode( "utf-8")
                    data['overview'] = sOverview

                    VSlog('OVERVIEW: %s' % (data['overview']))                                

            sPattern = '<ul class="list-unstyled spacing-bottom">(.+?)</ul>'
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

            page_id = movie_id[-2:]
            poster_url = self.poster % (page_id, movie_id)
            data['poster_path'] = poster_url

        return data
