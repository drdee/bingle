#!/usr/bin/env python

import feedparser, requests, sys, ConfigParser, pickle, datetime
bugzilla_atom_feed = 'https://bugzilla.wikimedia.org/buglist.cgi?f1=creation_ts&list_id=194515&o1=greaterthan&resolution=---&resolution=LATER&resolution=DUPLICATE&chfieldto=Now&query_format=advanced&chfield=%5BBug%20creation%5D&v1=2013-03-23%2000%3A00&component=MobileFrontend&product=MediaWiki%20extensions&ctype=atom'
debug = True

class Mingle:
	auth = ()
	apiBaseUrl = ''

	def __init__( self, auth=None, apiBaseUrl=None ):
		if auth is not None:
			self.setAuth( auth )
		if apiBaseUrl is not None:
			self.setApiBaseUrl( apiBaseUrl )

	def setAuth( self, auth ):
		if not isinstance(auth, dict):
			info( 'bad auth' )
		if not ( auth.has_key('username') or auth.has_key('password')):
			info( 'bad auth' )
		self.auth = ( auth['username'], auth['password'] )

	def setApiBaseUrl( self, apiBaseUrl ):
		self.apiBaseUrl = apiBaseUrl

	def executeMql( self, mql ):
		payload = { 'mql': mql }
		url = '%s/cards/execute_mql.json' % self.apiBaseUrl
		debug = "URL: %s" % url
		info( debug )
		r = requests.get( url, auth=self.auth, params=payload )
		debug = "Status: %d" % r.status_code
		info( debug )
		if r.status_code is not 200:
			info( 'something wrong' )
		info( r.json() )
		return r.json()

	def findCardByName( self, cardType, name ):
		mql = 'SELECT number WHERE Type=\'%s\' AND name=\'%s\'' % ( cardType, name.replace("'", "\\'"))
		debug = "MQL: %s" % mql
		info( debug )
		return self.executeMql( mql )

	def addCard( self, cardParams ):
		url = '%s/cards.xml' % self.apiBaseUrl
		debug = "URL: %s" % url
		info( debug )
		r = requests.post( url, auth=self.auth, params=cardParams )
		info( cardParams )
		debug = "Status: %d" % r.status_code
		info( debug )
		if r.status_code is not 201:
			info( 'something wrong' )
	
		
def info( out ):
	if debug is True:
		print "[INFO] %s" % out

def getBugzillaFeedUrl( feedUrl ):
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
	fromTime = getTimeFromPickle()
	if fromTime is not None:
		feedUrl = feedUrl + '&v1=%s' % fromTime
	pickleTime( now )
	return feedUrl

def getTimeFromPickle():
	pFile = open( 'bingle.pickle', 'rb' )
	try:
		fromTime = pickle.load( pFile )
	except:
		fromTime = None
	info( fromTime )
	pFile.close()
	return fromTime

def pickleTime( timeToPickle ):
	pFile = open( 'bingle.pickle', 'w+b' )
	pickle.dump( timeToPickle, pFile )
	pFile.close()

if __name__ == "__main__":
	config = ConfigParser.ConfigParser()
	# FIXME make this configurable by runtime arg
	config.read( 'bingle.ini' )
	auth = {'username': config.get('auth','username'), 'password': config.get('auth','password')}
	apiBaseUrl = config.get('urls','mingleApiBase')
	mingle = Mingle( auth, apiBaseUrl )

	# update bugzilla feed link
	feedUrl = getBugzillaFeedUrl( config.get('urls','bugzillaFeed') )
	info( feedUrl )
	feed = feedparser.parse( feedUrl )
	info( len(feed.entries) )
	for entry in feed.entries:
		# look for card
		foundBugs = mingle.findCardByName( 'Bug', entry.title )
		if len( foundBugs ) > 0:
			continue
		cardParams = {
			'card[name]': str( entry.title ),
			'card[card_type_name]':'bug',
			'card[description]': str( entry.id ), # URL to bug
			'card[properties][][name]': 'Iteration',
			'card[properties][][value]': '(Current iteration)',
			'card[created_by]': auth['username']
			#'card[properties][][name]': 'Status',
			#'card[properties][][value]': 'In Analysis'
		}
		mingle.addCard( cardParams )
		#sys.exit(0)	
