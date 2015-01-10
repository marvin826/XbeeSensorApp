import time
import logging
import PluginBase as pb

class WeatherPlugin(pb.PluginBase):
	"""docstring for WeatherPlugin"""
	def __init__(self):
		super(WeatherPlugin, self).__init__()

		self.temperature_log = None
		self.options = None
	
	def init(self, logger, options):
		super(WeatherPlugin, self).init(logger, options)

		self.logger.debug("WeatherPlugin : init")
		self.options = options

		logFileName = options["logFileName"]
		temperature_log = logging.getLogger("temperatures")
		t_log_file = logging.FileHandler(logFileName)
		temperature_log.addHandler(t_log_file)
		temperature_log.setLevel(logging.INFO)
		self.temperature_log = temperature_log

	def handlePacket(self, packet, environment):
		self.logger.debug("WeatherPlugin:handlePacket")

		updateTime = time.localtime()

		comps = packet["Components"]
		packetTimeStamp = packet["TimeStamp"]
		packetTime = packetTimeStamp.split("T")[1]
		packetDate = packetTimeStamp.split("T")[0]

		analog_values = comps["Analog Samples"]["values"]

		rTempReading = analog_values["AD0"]
		self.logger.debug("temp raw: " + str(rTempReading))
		rVoltage = analog_values["Supply Voltage"]
		self.logger.debug("supply raw: " + str(rVoltage))

		tempReading = (rTempReading * 1200.0) / 1023.0
		tempReading = (tempReading - 500.0) / 10.0
		tempReading = ((tempReading * 9.0) / 5.0) + 32.0
		self.logger.debug("temperature (F): " + str(tempReading))

		supplyVoltage = (rVoltage * 1200.0) / 1023.0
		supplyVoltage = supplyVoltage / 1000.0
		self.logger.debug("supply voltage (V): " + str(supplyVoltage))

		tempLogMessage = "{0},{1},{2},{3}"
		tempLogMessage = tempLogMessage.format(packetTime,
		                                       packetDate,
		                                       tempReading,
		                                       supplyVoltage)
		self.temperature_log.info(tempLogMessage)

		if self.follower is not None:
			messageObject = {}

			messageObject["name"] = "WeatherSensor"
			messageObject["address"] = packet['Components']['64-bit Source Address']['address']
			messageObject["time_stamp"] = packetTimeStamp
			messageObject["supply_voltage"] = { "value" : supplyVoltage, "units": "volts" }
			readings = {}
			readings["temperature"] = { "value" : tempReading, "units" : "degrees F" }
			messageObject["readings"] = readings

			self.follower.handleMessage(messageObject)

	def close(self):

		return
