import json
import PluginBase as pb

class PluginHandler():
	"""Used by XbeeMain to manage plugins"""
	def __init__(self):

		self.pluginFileName = None
		self.logger = None
		self.pluginDB = None
		self.plugins = None

	def init(self, pluginFileName, logger):

		self.pluginFileName = pluginFileName
		self.logger = logger

	def getPlugin(self, address) :
		return self.plugins[address]

	def loadPlugins(self):

		self.logger.debug("PluginHandler:loadPlugins")

		try:

			pluginConfig = open(self.pluginFileName)

			self.pluginDB = json.load(pluginConfig)
			#print self.pluginDB

			pluginDescList = self.pluginDB["plugins"]
			#print pluginDescList

			self.plugins = {}
			for pluginDesc in pluginDescList:
				pluginName = pluginDesc["name"]
				self.logger.debug("Trying to load plugin : " + pluginName)

				pluginObject = self.loadModule(pluginName)

				self.logger.debug("Initializing plugin")
				pluginObject.init(self.logger, pluginDesc["options"])

				if "follower" in pluginDesc:
					followerName = pluginDesc["follower"]["name"]
					followerOptions = pluginDesc["follower"]["options"]

					followerObject = self.loadModule(followerName)
					followerObject.init(self.logger, followerOptions)

					pluginObject.setFollower(followerObject)

				addresses = pluginDesc["addresses"]
				for address in addresses:
					if address in self.plugins :
						self.plugins[address].append(pluginObject)
					else:
						self.plugins[address] = [ pluginObject ]

			for key, value in self.plugins.iteritems() :
				self.logger.debug(str(key) + ", " + str(value))

			return True

		except Exception, e:
			self.logger.critical("PluginHandler:loadPlugins Caught Exception: " + str(e))
			return False

	def loadModule(self, module_name):

		self.logger.debug("PluginHandler.loadModule")
		self.logger.debug("loading module: " + module_name)

		try:
			module = __import__(module_name)
			class_ = getattr(module, module_name)
			return class_()

		except Exception, e:
		    logMessage = "PluginHandler:loadModule Caught Exception:" + \
		        str(e)
		    self.logger.critical(logMessage)
			