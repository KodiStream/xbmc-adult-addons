#-*- coding: utf-8 -*-
# https://github.com/KodiStream/xbmc-adult-addons
from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import progress, VSlog

import unicodedata, xbmc

UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'

SITE_IDENTIFIER = 'losporn_org' 
SITE_NAME = '[COLOR violet]LosPorn[/COLOR]'
SITE_DESC = 'XXX Movies'

URL_MAIN = 'https://losporn.org'

MOVIE_MOVIE = (URL_MAIN + '/quality/HD/', 'showMovies')
MOVIE_HD = (URL_MAIN + '/quality/HD/', 'showMovies')
MOVIE_NEWS = (URL_MAIN + '/category/new-release', 'showMovies')
MOVIE_GENRES = (True, 'showGenres')

GENRES_PATH = ('genres/')

URL_SEARCH = (URL_MAIN + '?s=', 'showMovies')
URL_SEARCH_MOVIES = (URL_MAIN + '?s=', 'showMovies')

FUNCTION_SEARCH = 'showMovies'

def load(): 
    oGui = cGui() 

    oOutputParameterHandler = cOutputParameterHandler() 
    oOutputParameterHandler.addParameter('siteUrl', 'http://kodistream/') 
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Recherche', 'search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_NEWS[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_NEWS[1], 'Films (Derniers ajouts)', 'news.png', oOutputParameterHandler)    

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_GENRES[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_GENRES[1], 'Films (Genres)', 'genres.png', oOutputParameterHandler)

    oGui.setEndOfDirectory() 

def showSearch(): 
    oGui = cGui()

    sSearchText = oGui.showKeyBoard() 
    if (sSearchText != False):
        sUrl = URL_SEARCH[0] + sSearchText 
        showMovies(sUrl) 
        oGui.setEndOfDirectory()
        return

def showGenres():
    oGui = cGui()

    liste = []
    liste.append( ['Anal', URL_MAIN + '/category/anal', GENRES_PATH + 'anal.png'])
    liste.append( ['Big Boobs', URL_MAIN + '/category/big-boobs', GENRES_PATH + 'big-boobs.png'])
    liste.append( ['Big Dicks', URL_MAIN + '/category/big-dicks', GENRES_PATH + 'big-dicks.png'])
    liste.append( ['Double Penetration', URL_MAIN + 'category/double-penetration', GENRES_PATH + 'dp.png'])
    # liste.append( ['Shemale', URL_MAIN + '/category/transsexual', GENRES_PATH + 'shemale.png'])

    for sTitle, sUrl, sImg in  liste:

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oGui.addDir(SITE_IDENTIFIER, 'showMovies', sTitle, sImg, oOutputParameterHandler)

    oGui.setEndOfDirectory()

def showMovies(sSearch = ''):
    oGui = cGui() 
    oParser = cParser()

    if sSearch: 
      sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl') 

    oRequestHandler = cRequestHandler(sUrl) 
    oRequestHandler.addHeaderEntry('User-Agent', UA)
    oRequestHandler.addHeaderEntry('Content-Type', 'text/html; charset=UTF-8')
    sHtmlContent = oRequestHandler.request() 

    sPattern = '<ul class="MovieList.+?">(.+?)</ul>'
    sResult = oParser.parse(sHtmlContent, sPattern)

    if (sResult[0] == True):
        sPattern = '<li class=".+?">.+?<a href="([^"]+)">.+?<img .+?src="([^"]+)".+?<div class="Title">(.+?)</div>'
        aResult = oParser.parse(sResult[1][0], sPattern)

        if (aResult[0] == False):
            oGui.addText(SITE_IDENTIFIER)

        if (aResult[0] == True):
            total = len(aResult[1])
            
            progress_ = progress().VScreate(SITE_NAME)

            for aEntry in aResult[1]:

                progress_.VSupdate(progress_, total) 
                if progress_.iscanceled():
                    break   

                sTitle = aEntry[2]    
                sThumb = aEntry[1]
                sUrl2 = aEntry[0]

                sDesc = ''

                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sUrl2) 
                oOutputParameterHandler.addParameter('sMovieTitle', sTitle) 
                oOutputParameterHandler.addParameter('sThumb', sThumb) 

                oGui.addPornMovie(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

            progress_.VSclose(progress_) 

            sNextPage = __checkForNextPage(sHtmlContent) 
            if (sNextPage != False):
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sNextPage)
                oGui.addNext(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Next >>>[/COLOR]', oOutputParameterHandler)

    if not sSearch:
        oGui.setEndOfDirectory() 

def __checkForNextPage(sHtmlContent): 
    sPattern = '''<link\s*rel=['"]next['"]\s*href=['"]([^'"]+)['"]\s*\/>'''
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        return aResult[1][0]

    return False

def showHosters(): 
    oGui = cGui() 
    oInputParameterHandler = cInputParameterHandler() 
    sUrl = oInputParameterHandler.getValue('siteUrl') 
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle') 
    sThumb = oInputParameterHandler.getValue('sThumb') 

    oRequestHandler = cRequestHandler(sUrl) 
    oRequestHandler.addHeaderEntry('User-Agent', UA)
    oRequestHandler.addHeaderEntry('Content-Type', 'text/html; charset=UTF-8')    
    sHtmlContent = oRequestHandler.request() 

    oParser = cParser()
    sPattern = '<li class="hosts-buttons-wpx">.+?href="(.+?)"'
    
    aResult = oParser.parse(sHtmlContent, sPattern)
    
    if (aResult[0] == True):
        for aEntry in aResult[1]:

            sHosterUrl = aEntry
            oHoster = cHosterGui().checkHoster(sHosterUrl) 
            if (oHoster != False):
                oHoster.setDisplayName(sMovieTitle) 
                oHoster.setFileName(sMovieTitle) 
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    oGui.setEndOfDirectory() 