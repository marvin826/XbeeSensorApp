import FollowerBase as fb


class MTTQClient(fb.FollowerBase):
	"""docstring for MTTQClient"""

	def __init__(self):
		super(MTTQClient, self).__init__()


	def init(self, logger, options):
		super(MTTQClient, self).init(logger, options)

	def handleMessage(self, message):
		super(MTTQClient, self).handleMessage(message)



