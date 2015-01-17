import FollowerBase as fb
import paho.mqtt.client as mqttc
import json


class MQTTClient(fb.FollowerBase):
	"""docstring for MQTTClient"""

	def __init__(self):
		super(MQTTClient, self).__init__()
		self.server = None
		self.port = None
		self.timeout = 60 # default to 60 second timeout
		self.topic = None
		self.mqttc = None
		self.connected = False

		return


	def init(self, logger, options):
		super(MQTTClient, self).init(logger, options)


		self.getOptions(options)
		self.connect()

		return

	def connect(self) :

		self.logger.debug("MTTQClient:connect : Trying to connect")
		self.logger.debug("MTTQClient:connect : Server : " + str(self.server))
		self.logger.debug("MTTQClient:connect : Port : " + str(self.port))
		self.logger.debug("MTTQClient:connect : Topic : " + str(self.topic))
		self.logger.debug("MTTQClient:connect : Topic : " + str(self.timeout))

		self.mqttc = mqttc.Client()

		self.mqttc.will_set("/event/dropped", "MQTTClient: client died")

		try:
			self.mqttc.on_connect = self.onConnect
			self.mqttc.connect(self.server, self.port, self.timeout)

		except Exception, e:
			logMessage = "MQTTClient:init : Error connecting client : " + str(e)
			self.logger.critical(logMessage)

			self.mqttc = None

			return

		return


	def getOptions(self, options) :

		required = [ "server", "port", "topic" ]
		optional = [ "timeout" ]
		for key in required:
			if key not in options:
				logMessage = "MQTTClient:getOptions : option " + \
				             key + " not provided"
				self.logger.critical(logMessage)
				return

			setattr(self, key, options[key])

		for key in optional:
			if key in options:
				setattr(self, key, options[key])

		return

	def handleMessage(self, message):
		super(MQTTClient, self).handleMessage(message)

		if not self.connected:
			self.connect()

		if self.mqttc is not None:
			mStr = json.dumps(message)

			try:
				self.mqttc.publish(self.topic, mStr)
			except Exception, e:
				self.logger.critical("MQTTClient:handleMessage : Publish error: " + str(e))

		return

	def onConnect(self, client, message, rc):
		self.logger.info("MTTQClient:onConnect : Connected : " + str(rc))
		self.logger.info("MTTQClient:onConnect : Server : " + self.server)
		self.logger.info("MTTQClient:onConnect : Port : " + self.port)
		self.logger.info("MTTQClient:onConnect : Topic : " + self.topic)
		self.logger.info("MTTQClient:onConnect : Topic : " + self.timeout)

		self.connected = True

		return


