#-*- coding: utf-8 -*-
# https://github.com/KodiStream/xbmc-adult-addons

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import progress, VSlog

from resources.lib.packer import cPacker

import unicodedata, xbmc

SITE_IDENTIFIER = 'porngaydvd_com' 
SITE_NAME = '[COLOR royalblue]DVDGayPorn[/COLOR]'
SITE_DESC = 'XXX Gay Movies'

URL_MAIN = 'https://dvdgayporn.com'

MOVIE_MOVIE = (URL_MAIN + '/movies/', 'showMovies')
MOVIE_HD = (URL_MAIN + '/movies/', 'showMovies')
# MOVIE_NEWS = (URL_MAIN + '/trending/?get=movies', 'showMovies')
MOVIE_NEWS = (URL_MAIN + '/movies/', 'showMovies')

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

    sPattern = '<div id="archive-content" class="animation-2 items">(.+?)<div class="pagination">'
    sResult = oParser.parse(sHtmlContent, sPattern)

    #xbmc.log('RESULT: %s' % str(sResult), xbmc.LOGNOTICE)

    if (sResult[0] == True):
        sPattern = '<img src="([^"]+)" alt="(.+?)">.+?<span class="quality">(.+?)</span>.+?<a href="([^"]+)">'
        aResult = oParser.parse(sResult[1][0], sPattern)

        #VSlog(str(aResult)) 

        #xbmc.log('RESULT: %s' % str(aResult), xbmc.LOGNOTICE)

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
                sTitle = sTitle.replace('&#8216;', '&#8217;')
                sTitle = unicodedata.normalize('NFD', sTitle).encode('ascii', 'ignore').decode("unicode_escape")
                sTitle = sTitle.encode("latin-1")

                xbmc.log('ENTRY: %s' % str(aEntry), xbmc.LOGNOTICE)

                sThumb = aEntry[0]
                sUrl2 = aEntry[3]

                sDesc = ''

                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sUrl2) 
                oOutputParameterHandler.addParameter('sMovieTitle', sTitle) 
                oOutputParameterHandler.addParameter('sThumb', sThumb) 

                oGui.addGayMovie(SITE_IDENTIFIER, 'showHosters', sTitle, '', sThumb, sDesc, oOutputParameterHandler)

            progress_.VSclose(progress_) 

            sNextPage = __checkForNextPage(sHtmlContent) 
            if (sNextPage != False):
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sNextPage)
                oGui.addNext(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Next >>>[/COLOR]', oOutputParameterHandler)

    if not sSearch:
        oGui.setEndOfDirectory() 

def __checkForNextPage(sHtmlContent): 
    sPattern = '''<a class='arrow_pag' href="(.+?)">'''
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        return aResult[1][0]

    return False

def showHosters():
    UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'
    oGui = cGui()
    oParser = cParser()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb  = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    sPattern = '<input type="hidden" name="idpost" value="(.+?)">'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        idFilm = aResult[1][0]

    oRequestHandler = cRequestHandler(URL_MAIN + "/wp-admin/admin-ajax.php")
    oRequestHandler.setRequestType(1)
    oRequestHandler.addHeaderEntry('User-Agent',UA)
    oRequestHandler.addHeaderEntry('Referer',sUrl)
    oRequestHandler.addParameters('action','doo_player_ajax')
    oRequestHandler.addParameters('post',idFilm)
    oRequestHandler.addParameters('nume','1')
    oRequestHandler.addParameters('type','movie')
    sHtmlContent2 = oRequestHandler.request()

    xbmc.log('sHtmlContent2: %s' % str(sHtmlContent2), xbmc.LOGNOTICE)

    sPattern2 = '''src='([^']+)'''''
    aResult = oParser.parse(sHtmlContent2, sPattern2)

    if (aResult[0] == True):
        VSlog('Url : ' + str(aResult[1][0]))
        url = aResult[1][0]

    url2 = url.split('/', 5)[4]
    sHosterUrl = 'https://openload.co/embed/' + url2

    oHoster = cHosterGui().checkHoster(sHosterUrl)
    if (oHoster != False):
        oHoster.setDisplayName(sMovieTitle)
        oHoster.setFileName(sMovieTitle)
        cHosterGui().showHoster(oGui, oHoster, sHosterUrl, '')
    oGui.setEndOfDirectory()
