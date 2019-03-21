# -*- coding: utf-8 -*-

from resources.lib.comaddon import addon, dialog, VSlog, xbmc
from resources.lib.handler.requestHandler import cRequestHandler

import json, urllib2, collections
import urlparse, re, client, dom_parser2

from urllib import quote_plus, urlopen, urlencode
import xbmcvfs

try:
    from sqlite3 import dbapi2 as sqlite
    VSlog('SQLITE 3 as DB engine')
except:
    from pysqlite2 import dbapi2 as sqlite
    VSlog('SQLITE 2 as DB engine')

class cTVTSvod:
    BASE_URL = "https://www.tvtsvod.com/"
    SEARCH_MOVIES = urlparse.urljoin(BASE_URL, "/search.php?search_string=%s")
    MOVIE_INFO = urlparse.urljoin(BASE_URL, "/video/%s/")
    CACHE = "special://userdata/addon_data/plugin.video.adult.stream/trans_video_cache.db"
    #important seul xbmcvfs peux lire le special
    REALCACHE = xbmc.translatePath(CACHE).decode("utf-8")

    #enlève les tags html d'une string
    TAG_RE = re.compile(r'<[^>]+>')
    #SMALL_RE = re.compile()

    ADDON = addon()
    DIALOG = dialog()

    def __init__(self, debug=False):

        self.debug = debug
        self.poster = 'https://img2.vod.com/image2/xfront/%s/%s.xfront.0.jpg'
        # self.fanart = 'https://caps1cdn.adultempire.com/r/%s/1280/%s_00500_1280.jpg'
        #self.poster_actor = 'https://imgs1cdn.adultempire.com/actors/%sh.jpg'

        try:
            if not xbmcvfs.exists(self.CACHE):
                self.db = sqlite.connect(self.REALCACHE)
                self.db.row_factory = sqlite.Row
                self.dbcur = self.db.cursor()
                self.__createdb()
        except:
            #VSlog("erreur: Impossible d'écrire sur %s" % self.REALCACHE)
            pass

        try:
            self.db = sqlite.connect(self.REALCACHE)
            self.db.row_factory = sqlite.Row
            self.dbcur = self.db.cursor()
        except:
            VSlog("erreur: Impossible de se connecter sur %s" % self.REALCACHE)
            pass    

    def __createdb(self):

        sql_create = "CREATE TABLE IF NOT EXISTS trans_movie ("\
                           "tvtsvod_id TEXT, "\
                           "title TEXT, "\
                           "year INTEGER,"\
                           "director TEXT, "\
                           "writer TEXT, "\
                           "tagline TEXT, "\
                           "credits TEXT,"\
                           "vote_average FLOAT, "\
                           "vote_count TEXT, "\
                           "runtime TEXT, "\
                           "overview TEXT,"\
                           "mpaa TEXT, "\
                           "premiered TEXT, "\
                           "genre TEXT, "\
                           "studio TEXT,"\
                           "status TEXT,"\
                           "poster_path TEXT, "\
                           "trailer TEXT, "\
                           "backdrop_path TEXT,"\
                           "playcount INTEGER,"\
                           "UNIQUE(tvtsvod_id, title, year)"\
                           ");"

        try:
            self.dbcur.execute(sql_create)
            VSlog("Table créée")
        except:
            VSlog("erreur: Impossible de créer la table")  

    # cherche dans les films ou serie l'id par le nom return ID ou False
    def get_idbyname(self, name, page=1):

        meta = {}

        url = self.SEARCH_MOVIES % (page, name)
        html = client.request(url)
        fragment = dom_parser2.parse_dom(html, 'div', {'class': 'movie_box'})

        if not fragment:
            return False

        if fragment:
            movie_url = dom_parser2.parse_dom(fragment, 'a', req='href')
            tvtsvod_id = (movie_url[0].attrs['href']).split('/',5)[4]
            return tvtsvod_id            

    # Search movie by title.
    def search_movie_name(self, name):

        meta = {}

        name = name.replace('!', '')
        url = self.SEARCH_MOVIES % (quote_plus(name))
        html = client.request(url)
        fragment = dom_parser2.parse_dom(html, 'div', {'class': 'movie_box'})

        if not fragment:
            meta = {}

        if fragment:
            movie_url = dom_parser2.parse_dom(fragment, 'a', req='href')
            tvtsvod_id = (movie_url[0].attrs['href']).split('/', 5)[4]
            meta = self.search_movie_id(tvtsvod_id)


        xbmc.log('DATA URL: %s' % (str(url)), xbmc.LOGNOTICE)
        xbmc.log('MOVIE NAME: %s' % (str(name)), xbmc.LOGNOTICE)
        # xbmc.log('MOVIE ID: %s' % (str(tvtsvod_id)), xbmc.LOGNOTICE)

        return meta          

    # Get the basic movie information for a specific movie id.
    def search_movie_id(self, movie_id):
        result = self._call(self.MOVIE_INFO, str(movie_id))
        return result

    def __set_playcount(self, overlay):
        if int(overlay) == 7:
            return 1
        else:
            return 0          

    def _format(self, meta, name):
        _meta = {}
        _meta['tvtsvod_id'] = ''
        _meta['title'] = name
        _meta['runtime'] = ''
        _meta['plot'] = ''
        _meta['year'] = ''
        _meta['trailer_url'] = ''
        _meta['genre'] = ''
        _meta['studio'] = ''
        _meta['status'] = ''
        _meta['cast'] = []
        _meta['cover_url'] = ''
        _meta['backdrop_url'] = ''
        _meta['overlay'] = 6
        _meta['playcount'] = 0

        if not 'title' in meta:
            _meta['title'] = name
        else:
            _meta['title'] = meta['title']
        if 'tvtsvod_id' in meta:
            _meta['tvtsvod_id'] = meta['tvtsvod_id']
        if 'year' in meta:
            _meta['year'] = meta['year']
        if 'runtime' in meta:
            if meta['runtime'] > 0:
                _meta['runtime'] = int(meta['runtime'])
            else:
                _meta['runtime'] = 0
        if 'overview' in meta:
            _meta['plot'] = meta['overview']

        if 'studio' in meta:
            _meta['studio'] = meta['studio']

        if 'genre' in meta:
            _meta['genre'] = ""
            for genre in meta['genre']:
                if _meta['genre'] == "":
                    _meta['genre'] += genre['name']
                else:
                    _meta['genre'] += ' / '+genre['name']

        if 'trailer' in meta:
            _meta['trailer'] = meta['trailer']
        else:
            _meta['trailer'] = ""

        if 'backdrop_path' in meta:
            _meta['backdrop_url'] = meta['backdrop_path']
        if 'poster_path' in meta:
            _meta['cover_url'] = meta['poster_path']

        if not 'playcount' in meta:
            _meta['playcount'] = self.__set_playcount(6)
        else:
            _meta['playcount'] = meta['playcount']

        if 'credits' in meta:
            meta['credits'] = eval(str(meta['credits']))
            licast = []
            for cast in meta['credits']['cast']:
                licast.append((cast['name'], str(cast['actor_url'])))
            _meta['cast'] = licast

        return _meta                

    def _clean_title(self, title):
        title = title.replace(' ', '')
        title = title.lower()
        return title

    def _cache_search(self, media_type, name, tvtsvod_id='', year=''):
        if media_type == "transmovie":
            sql_select = "SELECT * FROM trans_movie"
            if tvtsvod_id:
                sql_select = sql_select + " WHERE tvtsvod_id = '%s'" % tvtsvod_id
            else:
                sql_select = sql_select + " WHERE title = '%s'" % name

            if year:
                sql_select = sql_select + " AND year = '%s'" % year   

        #print sql_select
        try:
            self.dbcur.execute(sql_select)
            matchedrow = self.dbcur.fetchone()
        except Exception, e:
            VSlog('************* Error selecting from cache db: %s' % e, 4)
            return None

        if matchedrow:
            VSlog('Found meta information by name in cache table')
            return dict(matchedrow)
        else:
            VSlog('No match in local DB')
            return None             
            
    def _cache_save(self, meta, name, media_type, overlay):

        meta['title'] = name

        if 'credits' in meta:
            meta['credits'] = str(meta['credits'])

        if 'genres' in meta:
            meta['genre'] = str(meta['genres'])

        if 'production_companies' in meta:
            meta['studio'] = str(meta['production_companies'])

        if 'runtime' in meta:
            meta['runtime'] = meta['runtime']

        if 'year' in meta:
            meta['year'] = int(meta['year'])
        else:
            meta['year'] = 0

        meta['trailer'] = ""

        try:
            sql = "INSERT INTO %s (tvtsvod_id, title, year, credits, runtime, overview, genre, studio, status, poster_path, trailer, backdrop_path, playcount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" % media_type
            self.dbcur.execute(sql, (meta['tvtsvod_id'], meta['title'], meta['year'], meta['credits'], meta['runtime'], meta['overview'], meta['genre'], meta['studio'], meta['status'], meta['poster_path'], meta['trailer'], meta['backdrop_path'], 6))

            self.db.commit()
            VSlog('SQL INSERT Successfully')
        except Exception, e:
            VSlog('SQL INSERT ERROR')
            pass
        self.db.close()

    def get_meta(self, media_type, name, tvtsvod_id='', year='', overlay=6, update=False):
        '''
        Main method to get meta data for movie or tvshow. Will lookup by name/year
        if no IMDB ID supplied.

        Args:
            media_type (str): 'movie' or 'tvshow'
            name (str): full name of movie/tvshow you are searching
        Kwargs:
            imdb_id (str): IMDB ID
            tmdb_id (str): TMDB ID
            year (str): 4 digit year of video, recommended to include the year whenever possible
                        to maximize correct search results.
            season (int)
            episode (int)
            overlay (int): To set the default watched status (6=unwatched, 7=watched) on new videos

        Returns:
            DICT of meta data or None if cannot be found.
        '''

        #xbmc.log('Adult Stream Meta', 0)
        VSlog('Attempting to retrieve meta data for %s: %s %s %s' % (media_type, name, year, tvtsvod_id))
        #recherchedans la base de données
        if not update:
            meta = self._cache_search(media_type, self._clean_title(name), tvtsvod_id, year)
        else:
            meta = {}

        #recherche online
        # if not meta:

        #     if media_type == 'movie':
        #         meta = self.search_movie_id(tvtsvod_id)
        #     elif name:
        #         meta = self.search_movie_name(name)
        #     else:
        #         meta = {}
        if not meta:
            if media_type == 'transmovie':
                if tvtsvod_id:
                    meta = self.search_movie_id(tvtsvod_id)
                elif name:
                    meta = self.search_movie_name(name)
                else:
                    meta = {}

        #transform les metas
        if meta:
            #ecrit dans le cache
            self._cache_save(meta, self._clean_title(name), media_type, overlay)
        else:
            meta['title'] = name

        meta = self._format(meta, name)

        xbmc.log('META DATA: %s' % (str(meta)), xbmc.LOGNOTICE)  

        return meta        

    def _call(self, action, movie_id):

        url = action % movie_id
        html = client.request(url)

        data = {}

        data['tvtsvod_id'] = movie_id

        #récupère le titre du film
        fragment = dom_parser2.parse_dom(html, 'td', {'id': 'videoinfotd'})
        fragment = dom_parser2.parse_dom(fragment, 'span', {'itemprop': 'name'})
        data['title'] = str(fragment[0][1])

        #récupère l'année de production
        details_container = dom_parser2.parse_dom(html, 'div', {'class': 'page_video_info'})
        fragment = dom_parser2.parse_dom(details_container, 'span', {'itemprop': 'copyrightYear'})

        try:
            sYear = fragment[0][1]
        except Exception as e:
            data['year'] = '2002'
            pass

        #récupère le résumé du film
        fragment = dom_parser2.parse_dom(html, 'div', {'class': 'desc_wrap'})
        fragment = dom_parser2.parse_dom(fragment, 'div', {'class': 'video_description'})

        try:
            data['overview'] = str(self.TAG_RE.sub('', fragment[0][1]))
        except:
            data['overview'] = ''
            pass        

        xbmc.log('OVERVIEW: %s' % (str(data['overview'])), xbmc.LOGNOTICE)

        #récupére les informations de production
        fragment = dom_parser2.parse_dom(details_container, 'span', {'itemprop': 'productionCompany'})
        fragment = dom_parser2.parse_dom(fragment, 'a', req='title')
        data['studio'] = fragment[0][1]

        fragment = dom_parser2.parse_dom(details_container, 'span', {'itemprop': 'duration'})
        data['runtime'] = fragment[0][1]

        #convertion de la durée du film en minutes
        try:
            runtime = str(data['runtime'])
            heures = runtime.split(':', 2)[0]
            minutes = runtime.split(':', 2)[1]
            runtime = (int(heures))*60+int(minutes)
        except Exception as e:
            runtime = '120'
            pass

        data['runtime'] = runtime
        xbmc.log('RUNTIME: %s' % (str(runtime)), xbmc.LOGNOTICE) 

        #récupère les catégories du film
        fragment = dom_parser2.parse_dom(html, 'div', {'class': 'categories'})
        fragment = dom_parser2.parse_dom(fragment, 'span', {'itemprop': 'genre'})

        # xbmc.log('CATEGORIES: %s' % (str(fragment)), xbmc.LOGNOTICE)

        category = []
        sCount = len(fragment)
        i = 0

        while i < sCount:
            category.append({'name': str(fragment[i].content)})
            i += 1

        data['genre'] = category
        xbmc.log('DATA META: %s' % (str(category)), xbmc.LOGNOTICE) 

        #récupère le poster du film
        page_id = movie_id[:3]
        poster_url = self.poster % (page_id, movie_id)
        data['poster_path'] = poster_url

        #récupére de la liste des acteurs
        fragment = dom_parser2.parse_dom(html, 'div', {'class': 'video_info'})
        actor_info = dom_parser2.parse_dom(fragment, 'div', {'itemprop': 'actors'})
        actor_url = dom_parser2.parse_dom(actor_info, 'img', {'class': 'sm_star_image'})
        actor_url = [(i.attrs['key']) for i in actor_url]

        xbmc.log('ACTOR URL: %s' % (str(actor_url)), xbmc.LOGNOTICE)  

        actor_name = dom_parser2.parse_dom(actor_info, 'a', req='title')
        actor_name = dom_parser2.parse_dom(actor_name, 'span', {'itemprop': 'name'})
        actor_name = [(i.content) for i in actor_name]  

        xbmc.log('ACTOR NAME: %s' % (str(actor_name)), xbmc.LOGNOTICE) 

        cast = []
        actors = {}

        for name, url in zip(actor_name, actor_url):
            cast.append({'name': str(name), 'actor_url': str(url)})

        actors['cast'] = cast

        data['credits'] = actors

        xbmc.log('DATA META: %s' % (str(data)), xbmc.LOGNOTICE)  
        return data