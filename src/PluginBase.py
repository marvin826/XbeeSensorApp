
class PluginBase(object):
	"""Serves as the base class for the plugins used by XbeeMain"""
	def __init__(self):
		super(PluginBase, self).__init__()
		self.logger = None
		self.options = None


	def init(self, logger, options):
		self.logger = logger
		self.options = options

		self.logger.debug("PluginBase:init")

	def handlePacket(self, packet, environment):
		self.logger.debug("PluginBase:handlePacket")

	def close(self):
		self.logger.debug("PluginBase:close")
