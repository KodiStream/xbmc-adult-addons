#coding: utf-8
#KodiStream https://github.com/KodiStream/xbmc-adult-addons
from resources.lib.comaddon import addon, dialog, VSlog, xbmc
from resources.lib.comaddon import dialog
import hashlib, xbmcvfs, time

try:
    from sqlite3 import dbapi2 as sqlite
    VSlog('SQLITE 3 as DB engine')
except:
    from pysqlite2 import dbapi2 as sqlite
    VSlog('SQLITE 2 as DB engine')

class cParentalCheck:
	CACHE = "special://userdata/addon_data/plugin.video.adult.stream/parental_cache.db"
	REALCACHE = xbmc.translatePath(CACHE).decode("utf-8")

	ADDON = addon()
	DIALOG = dialog()

	def __init__(self):	

		try:
			if not xbmcvfs.exists(self.CACHE):
				self.db = sqlite.connect(self.REALCACHE)
				self.db.row_factory = sqlite.Row
				self.dbcur = self.db.cursor()
				self.__createdb()  
		except:
			VSlog("erreur: Impossible d'écrire sur %s" % self.REALCACHE)
			pass

		try:
			self.db = sqlite.connect(self.REALCACHE)
			self.db.row_factory = sqlite.Row
			self.dbcur = self.db.cursor()
		except:
			VSlog("erreur: Impossible de se connecter sur %s" % self.REALCACHE)
			pass    

	def __createdb(self):

		sql_create = "CREATE TABLE IF NOT EXISTS parental (password TEXT, timeset INTEGER);"

		try:
			self.dbcur.execute(sql_create)
			VSlog("Table créée")
		except:
			VSlog("erreur: Impossible de créer la table")

	def _cache_search(self):

		timestamp  = None
		password   = None
		matchedrow = None

		sql_select = "SELECT * FROM parental"
        
        #print sql_select
		try:
			self.dbcur.execute(sql_select)
			matchedrow = self.dbcur.fetchone()
		except Exception, e:
			VSlog('************* Error selecting from cache db: %s' % e, 4)

		if matchedrow:
			session_time = 180
			sMatchedrow = dict(matchedrow)

			VSlog('MATCHEDROW: %s' % (str(sMatchedrow)))

			timestamp = sMatchedrow['timeset']
			password = sMatchedrow['password']

			if password:
				try:
					now = time.time()
					check = now - 60*session_time
					if (not timestamp): timestamp = 0
				except:
					now = time.time()
					check = now - 60*session_time
					timestamp = 0

			VSlog('TIMESTAMP: %s' % (str(timestamp)))
			VSlog('CHECK: %s' % (str(check)))					

			if (timestamp < check):
				sCheckParental = self.checkParental()
				return sCheckParental
			else:
				return True

		else:
			sCheckParental = self.checkParental()
			return sCheckParental

	def checkParental(self):
		now = time.time()

		content = '[COLOR crimson][B]ATTENTION: CONTENU STRICTEMENT RESERVE AUX ADULTES[/B][/COLOR] [CR][CR]Le contenu disponible ici ne convient pas à un public mineur.'
		self.DIALOG.VSok(content)	

		input = self.getKeyboard('[COLOR crimson]Veuillez introduire le code parental[/COLOR]', hidden=True)

		if (not input):
			return False

		password = hashlib.sha256(addon('plugin.video.kodibox').getSetting('vanemakood')).hexdigest()
		pass_one = hashlib.sha256(input).hexdigest()

		if (password != pass_one):
			content = 'Désolé, le code parental entré est incorrect !'
			self.DIALOG.VSok(content)
			return False
		else:
			self.delEntry()
			self.addEntry(password, now)
			return True

	def getKeyboard(self, heading, default='', hidden=False):
	    keyboard = xbmc.Keyboard()
	    if hidden: keyboard.setHiddenInput(True)
	    keyboard.setHeading(heading)
	    if default: keyboard.setDefault(default)
	    keyboard.doModal()
	    if keyboard.isConfirmed():
	        return keyboard.getText()
	    else:
	        return None

	def delEntry(self):
		try:
			sql = "DELETE FROM parental"
			self.dbcur.execute(sql)
			self.db.commit()
			VSlog('SQL DELETE Successfully')
		except Exception, e:
			VSlog('SQL DELETE ERROR')
			pass

	def addEntry(self, passwd, timestamp):	
		xbmc.log('TIMESTAMP: %s' % (timestamp), xbmc.LOGNOTICE)
		try:
			sql = "INSERT INTO parental (password, timeset) VALUES (?, ?)"
			self.dbcur.execute(sql, (passwd, timestamp))
			self.db.commit()
			VSlog('SQL INSERT Successfully')
		except Exception, e:
			VSlog('SQL INSERT ERROR')
			pass