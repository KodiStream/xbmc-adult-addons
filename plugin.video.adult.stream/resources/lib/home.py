#-*- coding: utf-8 -*-
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
#from resources.lib.handler.pluginHandler import cPluginHandler
#from resources.lib.handler.rechercheHandler import cRechercheHandler
from resources.lib.handler.siteHandler import cSiteHandler
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.db import cDb
from resources.lib.comaddon import addon, window


SITE_IDENTIFIER = 'cHome'
SITE_NAME = 'Home'

#temp d'execution
# import time, random

# l = range(100000) 

# tps1 = time.clock() 
# random.shuffle(l) 
# l.sort() 
# tps2 = time.clock() 
# print(tps2 - tps1)

class cHome:

    ADDON = addon()


    def load(self):

        oGui = cGui()

        if (self.ADDON.getSetting('home_update') == 'true'):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'http://kodistream')
            oGui.addDir(SITE_IDENTIFIER, 'showUpdate', '%s (%s)' % (self.ADDON.VSlang(30418), self.ADDON.getSetting('service_futur')), 'update.png', oOutputParameterHandler)

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', 'http://kodistream')
        oGui.addDir(SITE_IDENTIFIER, 'showMovies', self.ADDON.VSlang(30120), 'films.png', oOutputParameterHandler)

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', 'http://kodistream')
        oGui.addDir(SITE_IDENTIFIER, 'showSearchText', self.ADDON.VSlang(30076), 'search.png', oOutputParameterHandler)

        if (self.ADDON.getSetting("history-view") == 'true'):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'http://kodistream')
            oGui.addDir('cHome', 'showHistory', self.ADDON.VSlang(30308), 'annees.png', oOutputParameterHandler)

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', 'http://kodistream')
        oGui.addDir(SITE_IDENTIFIER, 'showParentalCode', '[COLOR gold]Contrôle Parental[/COLOR]', 'update.png', oOutputParameterHandler)

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', 'http://kodistream')
        oGui.addDir('cFav', 'getFavourites', self.ADDON.VSlang(30207), 'mark.png', oOutputParameterHandler)

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', 'http://kodistream')
        oGui.addDir('globalSources', 'globalSources', self.ADDON.VSlang(30138), 'host.png', oOutputParameterHandler)

        view = False
        if (self.ADDON.getSetting("active-view") == 'true'):
            view = self.ADDON.getSetting('accueil-view')

        oGui.setEndOfDirectory(view)


    def showUpdate(self):
        try:
            from resources.lib.about import cAbout
            cAbout().checkdownload()
        except:
            pass
        return

    def showMovies(self):
        oGui = cGui()

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', 'MOVIE_NEWS')
        oGui.addDir(SITE_IDENTIFIER, 'callpluging', '%s (%s)' % (self.ADDON.VSlang(30120), self.ADDON.VSlang(30101)), 'news.png', oOutputParameterHandler)

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', 'MOVIE_HD')
        oGui.addDir(SITE_IDENTIFIER, 'callpluging', '%s (%s)' % (self.ADDON.VSlang(30120), self.ADDON.VSlang(30160)), 'hd.png', oOutputParameterHandler)

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', 'MOVIE_GENRES')
        oGui.addDir(SITE_IDENTIFIER, 'callpluging', '%s (%s)' % (self.ADDON.VSlang(30120), self.ADDON.VSlang(30105)), 'genres.png', oOutputParameterHandler)

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', 'MOVIE_MOVIE')
        oGui.addDir(SITE_IDENTIFIER, 'callpluging', self.ADDON.VSlang(30138), 'host.png', oOutputParameterHandler)

        oGui.setEndOfDirectory()

    # def showSources(self):
    #     oGui = cGui()

    #     oPluginHandler = cPluginHandler()
    #     aPlugins = oPluginHandler.getAvailablePlugins()
    #     for aPlugin in aPlugins:
    #         oOutputParameterHandler = cOutputParameterHandler()
    #         oOutputParameterHandler.addParameter('siteUrl', 'http://kodistream')
    #         icon = 'sites/%s.png' % (aPlugin[1])
    #         oGui.addDir(aPlugin[1], 'load', aPlugin[0], icon, oOutputParameterHandler)

    #     oGui.setEndOfDirectory()

    def showSearchText(self):
        oGui = cGui()
        sSearchText = oGui.showKeyBoard()
        if sSearchText:
            self.showSearch(sSearchText)
            oGui.setEndOfDirectory()
        else :
            return False

    def showSearch(self, searchtext=cInputParameterHandler().getValue('searchtext')):

        if not searchtext:
            return self.showSearchText()

        #n'existe plus mais pas sure.
        #xbmcgui.Window(10101).clearProperty('search_text')
        window(10101).clearProperty('search_text')

        oGui = cGui()

        #print xbmc.getInfoLabel('ListItem.Property(Category)')

        oGui.addText('globalSearch', self.ADDON.VSlang(30077) % (searchtext), 'none.png')

        #utilisation de guielement pour ajouter la bonne catégories

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', 'http://kodistream')
        oOutputParameterHandler.addParameter('searchtext', searchtext)

        oGuiElement = cGuiElement()
        oGuiElement.setSiteName('globalSearch')
        oGuiElement.setFunction('showSearch')
        oGuiElement.setTitle(self.ADDON.VSlang(30078))
        oGuiElement.setFileName(self.ADDON.VSlang(30078))
        oGuiElement.setIcon('search.png')
        oGuiElement.setMeta(0)
        #oGuiElement.setThumbnail(sThumbnail)
        #oGuiElement.setFanart(sFanart)
        oGuiElement.setCat(1)

        oGui.addFolder(oGuiElement, oOutputParameterHandler)

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', 'http://kodistream')
        oOutputParameterHandler.addParameter('searchtext', searchtext)

        oGuiElement = cGuiElement()
        oGuiElement.setSiteName('globalSearch')
        oGuiElement.setFunction('showSearch')
        oGuiElement.setTitle(self.ADDON.VSlang(30079))
        oGuiElement.setFileName(self.ADDON.VSlang(30079))
        oGuiElement.setIcon('search.png')
        oGuiElement.setMeta(0)
        #oGuiElement.setThumbnail(sThumbnail)
        #oGuiElement.setFanart(sFanart)
        oGuiElement.setCat(2)

        oGui.addFolder(oGuiElement, oOutputParameterHandler)

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', 'http://kodistream')
        oOutputParameterHandler.addParameter('searchtext', searchtext)

        oGuiElement = cGuiElement()
        oGuiElement.setSiteName('globalSearch')
        oGuiElement.setFunction('showSearch')
        oGuiElement.setTitle(self.ADDON.VSlang(30080))
        oGuiElement.setFileName(self.ADDON.VSlang(30080))
        oGuiElement.setIcon('search.png')
        oGuiElement.setMeta(0)
        #oGuiElement.setThumbnail(sThumbnail)
        #oGuiElement.setFanart(sFanart)
        oGuiElement.setCat(3)

        oGui.addFolder(oGuiElement, oOutputParameterHandler)

        oGui.setEndOfDirectory()


    def showHistory(self):

        oGui = cGui()

        row = cDb().get_history()
        if row:
            oGui.addText(SITE_IDENTIFIER, self.ADDON.VSlang(30416))
        else :
            oGui.addText(SITE_IDENTIFIER)
        for match in row:
            oOutputParameterHandler = cOutputParameterHandler()

            #code to get type with disp
            type = self.ADDON.getSetting('search' + match[2][-1:] + '_type')
            if type:
                oOutputParameterHandler.addParameter('type', type)
                #xbmcgui.Window(10101).setProperty('search_type', type)
                window(10101).setProperty('search_type', type)

            oOutputParameterHandler.addParameter('siteUrl', 'http://kodistream')
            oOutputParameterHandler.addParameter('searchtext', match[1])
            #oOutputParameterHandler.addParameter('disp', match[2])
            #oOutputParameterHandler.addParameter('readdb', 'False')


            oGuiElement = cGuiElement()
            oGuiElement.setSiteName('globalSearch')
            oGuiElement.setFunction('globalSearch')
            oGuiElement.setTitle("- "+match[1])
            oGuiElement.setFileName(match[1])
            oGuiElement.setCat(match[2])
            oGuiElement.setIcon("search.png")
            oGui.CreateSimpleMenu(oGuiElement,oOutputParameterHandler,SITE_IDENTIFIER,'cHome','delSearch', self.ADDON.VSlang(30412))
            oGui.addFolder(oGuiElement, oOutputParameterHandler)

        if row:

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'http://kodistream')
            oGui.addDir(SITE_IDENTIFIER, 'delSearch', self.ADDON.VSlang(30413), 'search.png', oOutputParameterHandler)


        oGui.setEndOfDirectory()

    def delSearch(self):
        cDb().del_history()
        return True


    def callpluging(self):
        oGui = cGui()

        oInputParameterHandler = cInputParameterHandler()
        sSiteUrl = oInputParameterHandler.getValue('siteUrl')

        oPluginHandler = cSiteHandler()
        aPlugins = oPluginHandler.getAvailablePlugins(sSiteUrl)
        for aPlugin in aPlugins:
            try:
                #exec "import "+aPlugin[1]
                #exec "sSiteUrl = "+aPlugin[1]+"."+sVar
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', aPlugin[0])
                icon = 'sites/%s.png' % (aPlugin[2])
                oGui.addDir(aPlugin[2], aPlugin[3], aPlugin[1], icon, oOutputParameterHandler)
            except:
                pass

        oGui.setEndOfDirectory()
