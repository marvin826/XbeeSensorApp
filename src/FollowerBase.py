
class FollowerBase(object):
	"""docstring for FollwerBase"""

	def __init__(self):
		super(FollowerBase, self).__init__()
		self.logger = None
		self.options = None


	def init(self, logger, options):
		self.logger = logger
		self.options = options


	def handleMessage(self, message):
		pass

