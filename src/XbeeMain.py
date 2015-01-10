from xbeeframework import XBeeReader as xbr
from xbeeframework import XBeeConnection as xbc
from xbeeframework import XBeePacketHandler as xbph
from xbeeframework import XBeeFrameDatabase as xbfdb
import PluginHandler as ph
import logging
import argparse
import traceback
import time
import signal
import sys

class XbeeMain():
	"""Class representing the main process for the Xbee interface"""
	def __init__(self):

		self.message_log = None
		self.arguments = None
		self.pluginHandler = None

		# read our configuration file; path given in arguments
		self.arguments = self.parseArguments()
		
		self.message_log = self.createMessageLog()

		signal.signal(signal.SIGINT, self.handleSignals)

		self.message_log.info("XbeeMain created")

	def init(self):

		self.message_log.debug("XbeeMain:init")

		self.pluginHandler = ph.PluginHandler()
		self.pluginHandler.init(self.arguments.pluginDB,self.message_log)
		if not self.pluginHandler.loadPlugins():
			self.message_log.critical("XbeeMain:init : Error loading plugins. Exiting.")
			self.shutdown()

		return

	def run(self):

		self.message_log.debug("XbeeMain::run")

		conn = xbc.XBeeConnection()

		try:

			conn.open(self.arguments.commPort)
			logString = "Successfully opened COMM port : " \
			            + self.arguments.commPort
			self.message_log.info(logString)

			# initialize the frame database
			frameDB = xbfdb.XBeeFrameDatabase()
			frameDB.setLogger(self.message_log)
			frameDB.read(self.arguments.frameDBFile)

			logString = "Successfully read database: " \
			    + self.arguments.frameDBFile
			self.message_log.info(logString)

			# create our reader
			reader = xbr.XBeeReader()
			reader.setLogger(self.message_log)

			# create our packet handler
			handler = xbph.XBeePacketHandler()
			handler.setLogger(self.message_log)
			handler.setDatabase(frameDB)

			reader.setConnection(conn)
			reader.setHandler(handler)
			reader.setPacketCallback(self.packetCallback)
			reader.read(True)

		except Exception, e:
		    logString = "XbeeMain: Caught exception: " + str(e)
		    traceback.print_exc()
		    self.message_log.critical(logString)
		else:
		    pass
		finally:
		    conn.close()
		return

	def shutdown(self):

		self.message_log.info("XbeeMain::shutdown")

		sys.exit(0)

		return

	def packetCallback(self, packet, env):

		self.message_log.debug("XbeeMain::packetCallback")
		self.message_log.debug("packet: " + str(packet))

		# check the frame type and make sure it's what we want
		frameType = packet["FrameType"]
		address = packet['Components']['64-bit Source Address']['address']

		self.message_log.debug("received frame type: " + frameType)
		self.message_log.debug("from address: " + address)

		try:
			plugins = self.pluginHandler.getPlugin(address)
			for plugin in plugins :
				plugin.handlePacket(packet, env)
		except Exception, e:
			print "XbeeMain:packetCallback : " + str(e)

		return

	def createMessageLog(self):

	    message_log = logging.getLogger("messages")
	    m_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	    m_log_file = logging.FileHandler(self.arguments.logFile)
	    m_log_file.setFormatter(m_formatter)
	    m_streamHandler = logging.StreamHandler()
	    message_log.addHandler(m_log_file)
	    message_log.addHandler(m_streamHandler)
	    message_log.setLevel(logging.INFO)

	    return message_log

	def parseArguments(self):
		
		parser = argparse.ArgumentParser(description="Xbee network interface")
		parser.add_argument('--logFile', 
							required=True,
			                help="Path to file where log messages are directed")
		parser.add_argument('--commPort', 
							required=True,
			                help="Serial port attached to Xbee radio")
		parser.add_argument('--pluginDB', 
							required=True,
			                help="Path to file that contains plugin information")
		parser.add_argument('--frameDBFile', 
							required=True,
			                help="Path to file that contains the frame databases")
		arguments = parser.parse_args()

		return arguments

	def handleSignals(self, signal, frame):
		self.message_log.info("XbeeMain:handleSignals: Received signal: " + str(signal))
		self.shutdown()

main = XbeeMain()
main.init()
main.run()
main.shutdown()

