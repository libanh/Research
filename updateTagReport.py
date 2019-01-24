#!/usr/bin/env python
"""
 Created on Thursday July, 10, 2014
 @author Zerina Kapetanovice
"""

import sllurp.llrp as llrp
import numpy as np
import time
#from skimage import exposure
#import cv2
#import cv2.cv as cv


class UpdateTagReport:
	def __init__(self, saturnThread, wispApp):
		#Entry
		self.idEntry 	  = {}
		self.entry 		  = ()
		self.data 		  = []
		self.entryCount	  = 0
		self.sensorData   = None
		self.newRow		  = 0

		#Accel
		self.currentX 	  = 1
		self.currentY 	  = 1
		self.currentZ 	  = 1
		self.flipX		  = 0
		self.flipY 		  = 0
		self.xcorr		  = 0.87
		self.ycorr		  = 0.886
		self.zcorr		  = 1.034

		#Tag Data
		self.time 		  = None
		self.tmp 		  = None
		self.tagType 	  = None 
		self.hwVersion 	  = None
		self.wispID 	  = None
		self.snr 		  = None
		self.rssi 		  = None
		self.readData 	  = None
		self.epc 		  = None

		#Temp
		self.tempValue	  = None
		self.plotData	  = []

		#WISPCam
		self.x 			  = 0
		self.y  		  = 50
		self.currSeq 	  = 0
		self.prevSeq 	  = 0 					#previous EPC sequence
		self.sequence 	  = 0 					#counter for the number of EPC sequences
		self.index 		  = 0
		self.dataCount 	  = 0
		self.camTag 	  = 0
		self.packetCount  = 0
		self.epcPacket 	  = 0
		self.getPacket	  = []
		self.retrieve 	  = 0
		self.readData 	  = 0
		self.wordPtr	  = 0
		self.mat_image 	  = None
		self.imageReady   = False
		self.imArray	  = [128 for x in range(25200)]
		self.imgFace 	  = [128 for x in range(19200)]

		#Threads
		self.saturnThread = saturnThread
		self.wispApp 	  =  wispApp

		### For testing purposes ###
		self.data1 = 0

	def getData(self, epc, rssi, snr, time, readData):
		self.epc 			= epc	
		self.tmp 			= "%02X" % int(epc[0:24], 16)
		self.tagType 		= "%02X" % int(epc[0:2], 16)
		self.charge 		= "%02X" % int(epc[4:6], 16)
		self.hwVersion 		= "%02X" % int(epc[18:20], 16)
		self.wispID	 		= "%02X" % int(epc[0:2], 16)
		self.snr 			= snr
		self.rssi 			= rssi
		self.time 			= time	#microseconds
		self.readData		= readData

		if self.epc != None:
			self.parseData(self.tagType, self.hwVersion, self.wispID, self.epc)
		else:
			print ("Tag seen, no data recieved")

	def parseData(self, tagType, hwVersion, wispID, epc):

		if hwVersion is None:
			return

		#Store all tag IDs
		if wispID not in self.idEntry.keys():
			self.idEntry[wispID] = self.newRow
			self.newRow += 1

		#Accelerometer WISP
		if tagType == "0B" or tagType == "0D": 
			self.getAccel(epc, tagType)

		#Temperature WISP
		elif tagType == "0E" or tagType == "0F": 
			self.getTemp(epc, tagType)

		#WISPCam
		elif tagType == "CA": 
			#self.saveData()
			if int(self.epc[2:4], 16) != 254:
				self.imageCaptureEPC() 
			else:
				self.camCharge()

		elif tagType == "DE":
			if int(self.epc[2:4], 16) != 254:
				self.imgFaceDetect()
			else:
				self.camCharge()

		else: 
			self.sensorData = None
			self.updateEntry()

	def saveData(self):
		log = [[self.epx, self.time]]
		fileHandle = open('camLog.txt', 'a')
		np.savetxt(fileHandle, log, '%10s')
		fileHandle.close()

	def getAccel(self, epc, tagType):
		alpha = 0.9

		x = int(epc[8:10], 16)
		y = int(epc[4:6], 16)
		z = int(epc[12:14], 16)

		if x < 0 or x > 1024: x = 0
		if y < 0 or y > 1024: y = 0
		if z < 0 or z > 1024: z = 0

		x = 100.0 * x / 1024.0
		y = 100.0 * y / 1024.0
		z = 100.0 * z / 1024.0

		self.accelerometer(alpha, x, y, z, tagType)

	def getTemp(self, epc, tagType):
		self.temp = int(tag.epc[2:6], 16)
		self.temperature(self.temp)

	def quickAccelCorrection(self, xcorr, ycorr, zcorr):
		self.xcorr, self.ycorr, self.zcorr = xcorr, ycorr, zcorr
		print str("New X correction factor: ") + str(self.xcorr)
		print str("New Y correction factor: ") + str(self.ycorr)
		print str("New Z correction factor: ") + str(self.zcorr)

	def accelerometer(self, alpha, x, y, z, tagType):	
		self.flipX, self.flipY = self.checkFlip()
		if self.flipX == 2:
			x = 100. - x
			self.flipX = 0

		if self.flipY == 2:
			y = 100. - y
			self.flipY = 0

		if tagType == "0B":
			x = x * self.xcorr
			y = y * self.ycorr
			z = z * self.zcorr

		self.currentX = self.currentX * alpha + x * (1 - alpha)
		self.currentY = self.currentY * alpha + y * (1 - alpha)
		self.currentZ = self.currentZ * alpha + z * (1 - alpha)
		
		self.sensorData = '%6.2f%%, %6.2f%%, %6.2f%%' % (self.currentX, self.currentY, self.currentZ)

		if self.saturnThread:
			self.saturnThread.setAngles(self.currentX, self.currentY, self.currentZ)

		self.updateEntry()

	def checkFlip(self):
		self.flipX = self.wispApp.xFlip.checkState()
		self.flipY = self.wispApp.yFlip.checkState()

		return self.flipX, self.flipY

	def temperature(self, temp):
		if temp < 0 or temp > 1024: temp = 0

		self.tempValue = ((temp - 673.) * 423.) / 1024.
		self.sensorData = self.tempValue
		self.plotData.append(self.tempValue)
		self.updateEntry()

	def updateAccel(self):
		return self.currentX, self.currentY, self.currentZ

	def updateTemp(self):
		return self.tagType, self.plotData

	def imageCaptureReadCMD(self):
 		begin 	= 0
 		end 	= 2
 	
	 	if tag.index < 25200 and tag.wordPtr < 12600:
			for x in range(30): #32 bytes of data
				tag.imArray[tag.index] = int(tag.readData[begin:end], 16)
				begin = end
				end = end + 2
				tag.index = tag.index + 1
			
			tag.wordPtr = tag.wordPtr + 15
			print (tag.index)

		self.updateEntry()		

	def imageCaptureEPC(self):
		#self.test()
		self.wispApp.statusLabel.setText("<b>Status</b>: Transmitting")
		self.sensorData = int(self.epc[2:24], 16)
		self.prevSeq = self.currSeq
		self.currSeq = int(self.epc[2:4], 16)
		self.index = 10 * (200 * self.sequence + self.currSeq)

		if self.currSeq < self.prevSeq: self.sequence += 1

		if self.currSeq != 255 or self.index <= 25199:
			begin = 4
			end = 6
			for x in range(10):
				self.imArray[10 * (200 * self.sequence + self.currSeq) + x] = int(self.epc[begin:end], 16)
				begin = end
				end = begin + 2

			if x == 9: x = 0
		self.updateEntry()
		
		if self.index % 175 == 0:
			self.configureImage(self.imArray)
			return

		if self.currSeq == 255 or self.index >= 25199:
			#self.wispApp.statusLabel.setText("Status: Data received")
			self.configureImage(self.imArray)
			self.sequence, self.currSeq, self.prevSeq, self.count = 0, 0, 0, 0

			return

	def imgFaceDetect(self):
		self.sensorData = int(self.epc[2:24], 16)
		self.prevSeq = self.currSeq
		self.currSeq = int(self.epc[2:4], 16)
		self.index = 10 * (200 * self.sequence + self.currSeq)
		rect = self.faceDetect()


		if self.currSeq < self.prevSeq: self.sequence += 1

		if self.currSeq != 255 or self.index <= 19199:
			begin = 4
			end = 6
			for x in range(10):
				self.imgFace[10 * (200 * self.sequence + self.currSeq) + x] = int(self.epc[begin:end], 16)
				begin = end
				end = begin + 2

			if x == 9: x = 0
		self.updateEntry()
		
		if self.index % 175 == 0:
			self.configureImage(self.imArray)
			return

		if self.currSeq == 255 or self.index >= 19199:
			#self.wispApp.statusLabel.setText("Status: Data received")
			self.configureImage(self.imArray)
			self.sequence, self.currSeq, self.prevSeq, self.count = 0, 0, 0, 0

			return


	def imageFinished(self):
		#if self.currSeq == 255 or self.index >= 25199:
		#	return True
		return True

	def getWriteData(self):
		wordPtr = 0
		MB = 0
		##### Dummy data #####
		if self.data1 == 0:
			writeData = '\x00\x00\x00\x00'
			self.data1 = 1
		if self.data1 == 1:
			writeData = '\xFF\xFF\xFF\xFF'
			self.data1 = 0

		return wordPtr, MB, writeData

	def getCamProgress(self):
		x = int(self.epc[4:8],16)
		voltage = (x*4000)/1024;
		percentage = (((voltage*100)/3800)*100)/102;
		return percentage

	def configureImage(self, imArray):
		rows, columns = 144, 175
		x = 50
		y = 0
		self.mat_image = np.reshape(imArray, (rows, columns)) / 255.0
		self.mat_image = exposure.equalize_hist(self.mat_image)
		self.imageReady = True
		self.faceDetect(self.mat_image)

	def faceDetect(self, img):
		cascade = cv2.CascadeClassifier('')
		rects = cascade.detectMultiScale(img, 
										 scaleFactor 	= 1.3, 
										 minNeighbors 	= 8, 
										 minSize 		= (20,20), 
										 flags 			= cv.CV_HAAR_SCALE_IMAGE)

		#if len(rects) == 0:
		#	return = []
		rects[:, 2] += rects[:, :2]
		self.getWindow(rects)
		return rects

	def drawRects(self, img, rects, color):
		for x1, y1, x2, y2 in rects:
			cv2.rectangle(img, (x1, x2), (x2, y2), color, 2)
			return img

	def getWindow(self, rects):
		for x1, y1, x2, y2 in rects:
			d1 = abs(x2-x1)
			d2 = abs(y2-y1)
			window = d1*d2
		self.imgFace = [128 for x in range(window)]
	'''
	def writeRectCoord(self, rects):
		rects = faceDetect()
		for x1, y1, x2, y2 in rects:
			coord = struct.pack(>IIII, x1, y1, x2, y2)			
		return coord
	'''
	def updateImage(self):
		return self.mat_image, self.imageReady, self.index

	def updateTagReport(self):
		return self.tagType, self.wispID

	def updateEntry(self):
		self.entry = (self.time, self.wispID, self.tagType, self.tmp, self.sensorData, self.snr, self.rssi)
		self.data.append(self.entry)
		self.entryCount += 1
		return self.data, self.idEntry, self.newRow, self.entryCount
