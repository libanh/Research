from __future__ import print_function
import logging
import pkg_resources
import pprint
from ast import literal_eval
import threading
from twisted.internet import reactor, defer

import sllurp.llrp as llrp
from sllurp.llrp_proto import LLRPROSpec, Modulation_Name2Type, DEFAULT_MODULATION, \
     Modulation_DefaultTari

from updateTagReport import UpdateTagReport

tagsSeen = 0
global_stop_param = {'AccessSpecStopTriggerType': 1, 'OperationCountValue': int(1)}

logger = logging.getLogger('sllurp')
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler('logfile.log'))


class Reader(threading.Thread):
	def __init__(self, tagReport, wispApp):
		threading.Thread.__init__(self)
		impinj 			= reactor
		self.impinj 	= impinj
		self.tagReport 	= tagReport
		self.wispApp 	= wispApp
		self.finishedAccess = False;

	def run(self):
		self.initReader() 

	def readerConfig(self):
		'''Function to get reader settings from user'''
		host 		= str("%s" % self.wispApp.ipAddress.currentText())
		modtari 	= str("%s" % self.wispApp.modSelect.currentText())
		modtari 	= modtari.split(" : ") 
		modulation 	= str(modtari[0])
		tari 		= int(modtari[1])

		settings = {'modulation' : modulation,
					'tari'		 : tari,
					'port'		 : llrp.LLRP_PORT, 
					'time'		 : None,
					'debug'		 : False, 
					'every_n'	 : 1,
					'reconnect'  : True,
					'logfile' 	 : 'logfile.log',
					'tx_power' 	 : 0, 
					'antennas'	 : '1', 
					'host'	 	 : host
					}
		
		return settings

	def politeShutdown(self, factory):
		return factory.politeShutdown()


	def tagReportCallback(self, llrpMsg):
		"""Function to run each time the reader reports seeing tags."""
			
		global tagsSeen
		tags = llrpMsg.msgdict['RO_ACCESS_REPORT']['TagReportData']
		tags.reverse()
			
		if len(tags):
			for tag in tags:
				tagsSeen 	  += tag['TagSeenCount'][0]
				epc 		  = tag['EPC-96']
				rssi 		  = tag['PeakRSSI'][0]
				time 		  = tag['LastSeenTimestampUTC'][0]
				snr 		  = "N/A"

				logger.info('Saw Tag(s): {}'.format(pprint.pformat(tags)))	

				if self.tagReport.imageFinished() and self.finishedAccess:

					self.sendNextWrite()


					#try:
					#	self.sendNextWrite()	
					#except: 
					#	print("Failed DISABLE_ACCESSSPEC")
					#	continue

				self.tagReport.getData(epc, rssi, snr, time)


	def access (self, proto):
		'''Function to configure read and write parameters'''
		writeSpecParam = None
		writeSpecParam = {
	        'OpSpecID': 0,
	        'MB': 0, 					
	        'WordPtr': 0, 
	        'AccessPassword': 0,
	        'WriteDataWordCount': 1,
	        'WriteData': '\x01\x01' #write random data to initialize AccessSpec
	        }
	    
		proto.startAccess(readWords = None, writeWords = writeSpecParam, accessStopParam = global_stop_param)
		self.finishedAccess = True
		
	def sendNextWrite(self):
		#writeData = self.tagReport.getWriteData()
		writeData = self.tagReport.writeRectCoor()
		writeSpecParam = None
		writeSpecParam = {
			'OpSpecID': 0,
			'MB': 3, 					
			'WordPtr': 0, 
			'AccessPassword': 0,
			'WriteDataWordCount': 2,
			'WriteData': writeData
	        }
		self.factory.nextAccess(readParam = None, writeParam = writeSpecParam, stopParam = global_stop_param)
	    

	def initReader(self):
		args = self.readerConfig()
		enabled_antennas = map(lambda x: int(x.strip()), args['antennas'].split(','))

		self.factory = llrp.LLRPClientFactory(
			duration			 = args['time'],
			report_every_n_tags  = args['every_n'],
			antennas 			 = enabled_antennas,
			tx_power 			 = args['tx_power'],
			modulation 			 = args['modulation'],
			tari 				 = args['tari'],
			start_inventory 	 = True,
			disconnect_when_done = (args['time'] > 0),
			reconnect 			 = args['reconnect'],
			tag_content_selector = {
				'EnableROSpecID' 				 : True,
				'EnableSpecIndex' 				 : True,
				'EnableInventoryParameterSpecID' : True,
				'EnableAntennaID' 				 : True,
				'EnableChannelIndex' 			 : False,
				'EnablePeakRRSI' 				 : True,
				'EnableFirstSeenTimestamp' 		 : False,
				'EnableLastSeenTimestamp' 		 : True,
				'EnableTagSeenCount' 			 : True,
				'EnableAccessSpecID' 			 : True 
				})

		
		self.factory.addTagReportCallback(self.tagReportCallback)
		self.factory.addStateCallback(llrp.LLRPClient.STATE_INVENTORYING, self.access)
		reactor.connectTCP(args['host'], args['port'], self.factory, timeout=3)
		reactor.addSystemEventTrigger('before', 'shutdown', self.politeShutdown, self.factory)
		reactor.run()

