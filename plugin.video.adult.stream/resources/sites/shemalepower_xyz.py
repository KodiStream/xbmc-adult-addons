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

SITE_IDENTIFIER = 'shemalepower_xyz' 
SITE_NAME = '[COLOR violet]ShemalePower[/COLOR]'
SITE_DESC = 'XXX Movies'

URL_MAIN = 'https://shemalepower.xyz/'

MOVIE_MOVIE = (URL_MAIN + 'category/full-movies-international/', 'showMovies')
MOVIE_HD = (URL_MAIN + 'category/full-movies-international/', 'showMovies')
MOVIE_NEWS = (URL_MAIN + 'category/full-movies-international/', 'showMovies')

def load(): 
    oGui = cGui() 

    oOutputParameterHandler = cOutputParameterHandler() 
    oOutputParameterHandler.addParameter('siteUrl', 'http://kodistream/') 
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Recherche', 'search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_NEWS[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_NEWS[1], 'Films (Derniers ajouts)', 'news.png', oOutputParameterHandler)    

    oGui.setEndOfDirectory() 

def showSearch(): 
    oGui = cGui()

    sSearchText = oGui.showKeyBoard() 
    if (sSearchText != False):
        sUrl = URL_SEARCH[0] + sSearchText 
        showMovies(sUrl) 
        oGui.setEndOfDirectory()
        return

def showMovies(sSearch = ''):
    oGui = cGui() 
    oParser = cParser()

    if sSearch: 
      sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl') 

    oRequestHandler = cRequestHandler(sUrl) 
    sHtmlContent = oRequestHandler.request() 

    sPattern = '<ul class="listing-videos listing-tube">(.+?)</ul>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):

    	sPattern = '<img.+?src="([^"]+)".+?title="(.+?)".+?<a href="([^"]+)"'
    	aResult = oParser.parse(aResult[1][0], sPattern)

    #VSlog(str(aResult)) 

    #xbmc.log('Result: %s' % str(aResult), xbmc.LOGNOTICE)

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True):
        total = len(aResult[1])
        
        progress_ = progress().VScreate(SITE_NAME)

        for aEntry in aResult[1]:

            progress_.VSupdate(progress_, total) 
            if progress_.iscanceled():
                break
 
            sTitle = unicode(aEntry[1], 'utf-8')
            sTitle = unicodedata.normalize('NFD', sTitle).encode('ascii', 'ignore').decode("unicode_escape")
            sTitle = sTitle.encode("latin-1")                  

            sThumb = aEntry[0]
            sUrl2 = aEntry[2]

            sDesc = ''

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2) 
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle) 
            oOutputParameterHandler.addParameter('sThumb', sThumb) 

            oGui.addTransMovie(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

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
    sHtmlContent = oRequestHandler.request() 

    oParser = cParser()
    sPattern = '<iframe src="([^"]+)"'
    
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