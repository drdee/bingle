import pickle, feedparser
from datetime import datetime

class Bingle:

	def __init__( self, picklePath='bingle.pickle', debug=False, feedUrl=None ):
		self.setDebug( debug )
		self.setPicklePath( picklePath )
		if feedUrl is not None:
		 self.setFeedUrl( feedUrl )

	def setPicklePath( self, picklePath ):
		self.picklePath = picklePath

	def setDebug( self, debug ):
		if not isinstance( debug, bool ):
			raise TypeError( 'Debug param must be a boolean' )
		self.debug = debug

	def info( self, out ):
		if self.debug is True:
			print "[INFO] %s" % out

	def getBugzillaFeedUrl( self, feedUrl ):
		now = datetime.now().strftime('%Y-%m-%d %H:%M')
		fromTime = self.getTimeFromPickle()
		if fromTime is not None:
			feedUrl = feedUrl + '&v1=%s' % fromTime
		self.pickleTime( now )
		return feedUrl

	def getTimeFromPickle( self ):
		try:
			pFile = open( self.picklePath, 'rb' )
			fromTime = pickle.load( pFile )
			pFile.close()
		except:
			fromTime = None
		debug = "From time: %s" % fromTime
		self.info( debug )
		return fromTime

	def pickleTime( self, timeToPickle ):
		pFile = open( 'bingle.pickle', 'w+b' )
		pickle.dump( timeToPickle, pFile )
		pFile.close()

	def getFeedEntries( self ):
		feed = feedparser.parse( self.feedUrl )
		self.info( "Feed length: %d" % len(feed.entries) )
		return feed.entries

	def setFeedUrl( self, feedUrl ):
		self.feedUrl = feedUrl
		self.info( feedUrl )
