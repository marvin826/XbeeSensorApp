class TwitterHelper():
	"""TwitterHelper wraps the python_twitter api to
	   keep state and handle connection issues"""
	def __init__(self):
		self.api = None
		self.messageQueue = None
		self.nextMessage = None
		self.message_log = None
		self.credentials = None

	def init(self, message_log, credentials):

		self.message_log = message_log

		if ('consumer_key' not in credentials) :
			self.message_log.critical("TwitterHelper.init consumer_key missing")	
			return
		if ('consumer_secret' not in credentials) :
			self.message_log.critical("TwitterHelper.init consumer_secret missing")	
			return
		if ('access_token_key' not in credentials) :
			self.message_log.critical("TwitterHelper.init access_token_key missing")	
			return
		if('access_token_secret' not in credentials) :
			self.message_log.critical("TwitterHelper.init access_token_secret missing")
			return


		self.credentials = credentials	

		self.api = twitter.Api(self.consumer_key = credentials['consumer_key'],
							   self.consumer_secret = credentials['consumer_secret'],
							   self.access_token_key = credentials['access_token_key'],
							   self.access_token_secret = credentials['access_token_secret'])

		self.messageQueue = Queue.Queue(25)
		self.message_log.info("TwitterHelper initialized successfully")

	def tweetMessage(self, message):

		if (self.messageQueue is not None):
			self.messageQueue.put(message)

		try:
			while not self.messageQueue.empty():
				if self.nextMessage is None:
					self.nextMessage = self.messageQueue.get(False)

				self.api.PostUpdate(self.nextMessage)
				self.nextMessage = None
		except twitter.error.TwitterError, te:
			self.message_log.info("TwitterHelper : PostUpdate failed. Tweet queued.")
		except Exception, e:
			self.message_log.critical("TwitterHelper : Exception : " + str(e))
		else:
			self.message_log.debug("TwitterHelper : message tweeted successfully")