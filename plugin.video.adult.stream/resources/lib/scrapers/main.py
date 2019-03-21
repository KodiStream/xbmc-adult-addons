# -*- coding: utf-8 -*-

from resources.lib.comaddon import addon, dialog, VSlog, xbmc
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.scrapers.aebn import cAEBN
from urllib import quote_plus

import os, urlparse, re, unicodedata
import xbmcvfs

try:
    from sqlite3 import dbapi2 as sqlite
    VSlog('SQLITE 3 as DB engine')
except:
    from pysqlite2 import dbapi2 as sqlite
    VSlog('SQLITE 2 as DB engine')

class cDEFAULT:
    CACHE = "special://userdata/addon_data/plugin.video.adult.stream/video_cache.db"
    CACHE_FILE = xbmc.translatePath(os.path.join('special://home/userdata/addon_data/plugin.video.adult.stream/', 'video_cache.db'))

    #important seul xbmcvfs peux lire le special
    REALCACHE = xbmc.translatePath(CACHE).decode("utf-8")

    #enlève les tags html d'une string
    TAG_RE = re.compile(r'<[^>]+>')
    #SMALL_RE = re.compile()

    ADDON = addon()
    DIALOG = dialog()

    def __init__(self, debug=False):

        self.debug = debug

        # if xbmcvfs.exists(self.CACHE_FILE):
        #     statInfo = os.stat(self.CACHE_FILE)
        #     statInfo = float(statInfo.st_size/1000)
        #     if (statInfo > 10):
        #         os.remove(self.CACHE_FILE)
        #     xbmc.log('DB SIZE: %s' % (str(statInfo)), xbmc.LOGNOTICE)

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

        sql_create = "CREATE TABLE IF NOT EXISTS porn_movie ("\
                           "aebn_id INTEGER, "\
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
                           "UNIQUE(aebn_id, title, year)"\
                           ");"

        try:
            self.dbcur.execute(sql_create)
            VSlog("Table créée")
        except:
            VSlog("erreur: Impossible de créer la table")        

        sql_create = "CREATE TABLE IF NOT EXISTS trans_movie ("\
                           "aebn_id INTEGER, "\
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
                           "UNIQUE(aebn_id, title, year)"\
                           ");"

        try:
            self.dbcur.execute(sql_create)
            VSlog("Table créée")
        except:
            VSlog("erreur: Impossible de créer la table")

        sql_create = "CREATE TABLE IF NOT EXISTS gay_movie ("\
                           "aebn_id INTEGER, "\
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
                           "UNIQUE(aebn_id, title, year)"\
                           ");"

        try:
            self.dbcur.execute(sql_create)
            VSlog("Table créée")
        except:
            VSlog("erreur: Impossible de créer la table")            

    def __del__(self):
        ''' Cleanup db when object destroyed '''
        try:
            self.dbcur.close()
            self.dbcon.close()
        except:
            pass    

    # Search movie by title.
    def search_movie_name(self, media_type, name):

        meta = cAEBN().search_movie_name(media_type, name)           
        return meta          

    def __set_playcount(self, overlay):
        if int(overlay) == 7:
            return 1
        else:
            return 0  

    def __set_playcount(self, overlay):
        if int(overlay) == 7:
            return 1
        else:
            return 0

    def _format(self, meta, name):
        _meta = {}
        _meta['aebn_id'] = ''
        _meta['title'] = name
        _meta['runtime'] = ''
        _meta['plot'] = ''
        _meta['year'] = ''
        _meta['trailer_url'] = ''
        _meta['genre'] = ''
        _meta['studio'] = ''
        _meta['status'] = ''
        # _meta['cast'] = []
        _meta['cover_url'] = ''
        _meta['backdrop_url'] = ''
        _meta['overlay'] = 6
        _meta['playcount'] = 0

        if not 'title' in meta:
            _meta['title'] = name
        else:
            _meta['title'] = meta['title']
        if 'aebn_id' in meta:
            _meta['aebn_id'] = meta['aebn_id']
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
            i = 1
            for genre in eval(meta['genre']):
                if (i < 6):
                    if _meta['genre'] == "":
                        _meta['genre'] += genre['name']
                    else:
                        _meta['genre'] += ' / '+genre['name']
                    i += 1

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

        # if 'credits' in meta:
        #     meta['credits'] = eval(str(meta['credits']))
        #     licast = []
        #     for cast in meta['credits']['cast']:
        #         licast.append((cast['name'], urlparse.urljoin(self.AEBN_URL, str(cast['actor_img']))))
        #     _meta['cast'] = licast

        return _meta                       

    def _clean_title(self, title):
        title = title.replace(' ', '')
        title = title.replace("'", "")
        title = title.lower()
        return title

    def _cache_search(self, media_type, name, aebn_id='', year=''):
        
        if media_type == "pornmovie":
            sql_select = "SELECT * FROM porn_movie"
        elif media_type == "transmovie":
            sql_select = "SELECT * FROM trans_movie"            
        elif media_type == "gaymovie":
            sql_select = "SELECT * FROM gay_movie"            
        
        if aebn_id:
            sql_select = sql_select + " WHERE aebn_id = '%s'" % aebn_id
        else:
            sql_select = sql_select + " WHERE title = '%s'" % name

        # if year:
            # sql_select = sql_select + " AND year = '%s'" % year

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

        # if 'credits' in meta:
        #     meta['credits'] = str(meta['credits'])

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
            if (media_type == 'pornmovie'):
                movieDB = 'porn_movie'
            if (media_type == 'transmovie'):
                movieDB = 'trans_movie'
            if (media_type == 'gaymovie'):
                movieDB = 'gay_movie'
            # sql = "INSERT INTO %s (aebn_id, title, year, credits, runtime, overview, genre, studio, status, poster_path, trailer, backdrop_path, playcount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" % movieDB
            sql = "INSERT INTO %s (aebn_id, title, year, runtime, overview, genre, studio, poster_path, playcount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)" % movieDB
            # self.dbcur.execute(sql, (meta['aebn_id'], meta['title'], meta['year'], meta['credits'], meta['runtime'], meta['overview'], meta['genre'], meta['studio'], meta['status'], meta['poster_path'], meta['trailer'], meta['backdrop_path'], 6))

            self.dbcur.execute(sql, (meta['aebn_id'], meta['title'], meta['year'], meta['runtime'], meta['overview'], meta['genre'], meta['studio'], meta['poster_path'], 6))
            self.db.commit()
            VSlog('SQL INSERT Successfully')
        except Exception, e:
            VSlog('************* SQL INSERT ERROR: %s' % e, 4)
            pass
        # self.db.close()    
        
    def get_meta(self, media_type, name, aebn_id='', year='', overlay=6, update=False):
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
        VSlog('Attempting to retrieve meta data for %s: %s %s %s' % (media_type, name, year, aebn_id))
        #recherchedans la base de données
        if not update:
            meta = self._cache_search(media_type, self._clean_title(name), aebn_id, year)
        else:
            meta = {}

        if not meta:
            if (media_type == 'pornmovie' or media_type == 'transmovie' or media_type == 'gaymovie'):
                if name:
                    meta = self.search_movie_name(media_type, name)
                else:
                    meta = {}

            #transform les metas
            if meta:
                #ecrit dans le cache
                self._cache_save(meta, self._clean_title(name), media_type, overlay)
            else:
                meta['title'] = name

        meta = self._format(meta, name)

        return meta                
