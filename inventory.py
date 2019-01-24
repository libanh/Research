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
		self.readData 	= 0

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

				self.readData = 0
				

				logger.info('Saw Tag(s): {}'.format(pprint.pformat(tags)))			
				self.tagReport.getData(epc, rssi, snr, time, self.readData)


	def access (self, proto):
		'''Function to configure read and write parameters'''
		readSpecParam = None
		readSpecParam = {
	        'OpSpecID': 0,
	        'MB': 0, 					
	        'WordPtr': globals.wordPtr, 
	        'AccessPassword': 0,
	        'WordCount': 15 
	        }
	    
		proto.startAccess(readWords = readSpecParam) #removed return
	    #tag.retreive = 0
	    #return proto.startAccess(readWords=readSpecParam)


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

		#self.factory.addStateCallback(llrp.LLRPClient.STATE_SENT_DELETE_ACCESSSPEC, self.access)
		self.factory.addTagReportCallback(self.tagReportCallback)
		reactor.connectTCP(args['host'], args['port'], self.factory, timeout=3)
		reactor.addSystemEventTrigger('before', 'shutdown', self.politeShutdown, self.factory)
		reactor.run()

