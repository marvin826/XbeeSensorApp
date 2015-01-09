import time
import logging
import PluginBase as pb

class GarageSensor(pb.PluginBase):
	"""Handles packets from a set of door sensors"""
	def __init__(self):
		super(GarageSensor, self).__init__()

		self.garage_log = None
		self.options = None
		
	def init(self, logger, options):
		super(GarageSensor, self).init(logger, options)

		self.logger.debug("GarageSensor:init")

		self.options = options

		logFileName = options["logFileName"]
		garage_log = logging.getLogger("garage")
		g_log_file = logging.FileHandler(logFileName)
		garage_log.addHandler(g_log_file)
		garage_log.setLevel(logging.INFO)

		self.garage_log = garage_log

	def handlePacket(self, packet, environment):
		self.logger.debug("GarageSensor:handlePacket")

		updateTime = time.localtime()

		comps = packet["Components"]
		packetTimeStamp = packet["TimeStamp"]
		packetTime = packetTimeStamp.split("T")[1]
		packetDate = packetTimeStamp.split("T")[0]

		analog_values = comps["Analog Samples"]["values"]
		rVoltage = analog_values["Supply Voltage"]
		self.logger.debug("supply raw: " + str(rVoltage))
		rTempReading = analog_values["AD2"]
		self.logger.debug("temp raw: " + str(rTempReading))

		tempReading = (rTempReading * 1200.0) / 1023.0
		tempReading = (tempReading - 500.0) / 10.0
		tempReading = ((tempReading * 9.0) / 5.0) + 32.0
		self.logger.debug("temperature (F): " + str(tempReading))

		supplyVoltage = (rVoltage * 1200.0) / 1023.0
		supplyVoltage = supplyVoltage / 1000.0
		self.logger.debug("supply voltage (V): " + str(supplyVoltage))

		digital_values = comps["Digital Samples"]["values"]
		doorA = "Open"
		if(digital_values["AD1/DI O1"]):
		    doorA = "Closed"
		doorB = "Open"
		if(digital_values["AD0/DI O0"] ):
		    doorB = "Closed"

		garageLogMessage = "{0},{1},{2},{3},{4},{5}"
		garageLogMessage = garageLogMessage.format(packetTime,
		                                           packetDate,
		                                           tempReading,
		                                           doorA,
		                                           doorB,
		                                           supplyVoltage)
		self.garage_log.info(garageLogMessage)

	def close(self):
		self.logger.debug("GarageSensor:close")