#!/usr/bin/env python
"""
 Created on Thursday July, 10, 2014
 @author Zerina Kapetanovic
"""
import sys, threading, time
import pkg_resources

### GUI ###
from PyQt4 import QtGui, Qt, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

### GRAPHING ###
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

### MODULES ###
from GUI_Setup import GUI_Setup
from inventory import Reader
from updateTagReport import UpdateTagReport
from saturn import SaturnDemo

#GIT Demonstration 

class RFID_Reader_App:
	def __init__(self, xcorr = 0.87, ycorr = 0.886, zcorr = 1.034):

		#saturn demo config
		self.xcorr = xcorr		
		self.zcorr = zcorr
		self.ycorr = ycorr
		self.saturnThread = SaturnDemo()

		#inventory config
		self.tagReport = UpdateTagReport(self.saturnThread, wispApp)
		self.impinjThread = Reader(self.tagReport, wispApp)
		self.usrpStart = False
		self.impinjStart = False
		self.runStarted = 0
		self.pause = 0

		#connect all widgets
		wispApp.startButton.clicked.connect(self.start)
		wispApp.connectButton.clicked.connect(self.readerSelect)
		wispApp.saturnButton.clicked.connect(self.initSaturn)
		#wispApp.captureButton.clicked.connect(self.captureImage)
		wispApp.pauseButton.clicked.connect(self.pauseRun)
		wispApp.clearButton.clicked.connect(self.clearImage)
		wispApp.caliButton.clicked.connect(self.calibrate)

	#Select a reader
	def readerSelect(self):
		if wispApp.readerSelect.currentText() == "Impinj":
			self.impinjStart = True
			host, modulation, tari = self.getReaderConfig()
			print str("Reader: ") + str("Impinj, ") + str("Host: ") + str(host)
			print str("Modulation: ") + str(modulation) + (" Tari: ") + str(tari)
		elif wispApp.readerSelect.currentText() == "USRP":
			self.usrpStart = True
			print str("Reader: ") + str("USRP, ") + str("Host: ") + str("N/A")

	#Get reader settings from user
	def getReaderConfig(self):
		host = str("%s" % wispApp.ipAddress.currentText())
		settings = str("%s" % wispApp.modSelect.currentText())
		settings = settings.split(" : ")
		return host, settings[0], settings[1]

	#Start inventory
	def start(self):
		if self.runStarted == 0:
			self.runStarted = 1
			self.timer = QtCore.QTimer()
			self.timer.timeout.connect(self.updateGUI)
			self.timer.timeout.connect(self.captureImage)
			self.timer.timeout.connect(self.updateTemp)
			self.timer.timeout.connect(self.updateAccel)
			self.timer.timeout.connect(self.updateProgressBar)
			self.timer.start(50)
			self.initReader()

		else:
			self.impinjThread.factory.resumeInventory()
			self.pause = 0

	#Stop inventory, terminate reactor
	def stop(self):
		self.impinjThread.impinj.stop()
		self.timer.stop()

	#Pause inventory
	def pauseRun(self):
		self.impinjThread.factory.pauseInventory()
		self.pause = 1		

	#Calibrate saturn
	def calibrate(self):
		accelX, accelY, accelZ = self.tagReport.updateAccel()
		self.xcorr = 50.0 / (accelX / self.xcorr)
		self.ycorr = 50.0 / (accelY / self.ycorr)
		self.zcorr = 41.0 / (accelZ / self.zcorr)
		
		self.tagReport.quickAccelCorrection(self.xcorr, self.ycorr, self.zcorr)

	#Start reader
	def initReader(self):
		if self.impinjStart == True:
			self.impinjThread.daemon = True
			self.impinjThread.start()
		elif self.usrpStart == True:
			global usrp_tb
			self.usrp_tb = my_top_block()
			self.usrp_tb.start()

	#Start saturn demo
	def initSaturn(self):
		self.saturnThread.daemon = True
		self.saturnThread.start()


	#Update table
	def updateGUI(self):
		data, idEntry, newRow, entryCount = self.tagReport.updateEntry()
		tagType, wispID = self.tagReport.updateTagReport()
		lastRow = wispApp.mainTable.rowCount()
		wispApp.statusLabel.setText("<b>Status</b>: Charging")
		if wispID != None:
			wispApp.mainTable.setRowCount(newRow)
			wispApp.mainTable.resizeColumnsToContents()
			wispApp.mainTable.horizontalHeader().setStretchLastSection(True)
			
			if tagType != "CA": 
				wispApp.statusLabel.setText("<b>Status</b>: Charging")

			for fieldPos in range(7):
				currentValue = idEntry.get(wispID)
				values = idEntry.values()

				if currentValue in values:
					item = QtGui.QTableWidgetItem(str(data[entryCount - 1][fieldPos]))
					wispApp.mainTable.setItem(currentValue, fieldPos, item)
					
	def updateProgressBar(self):
		percentage = self.tagReport.getCamProgress()
		wispApp.progress.setValue(percentage)
		wispApp.chargePercentage.setText(str(percentage) + "%")

	#Update temperature data
	def updateTemp(self):
		tagType, plotData = self.tagReport.updateTemp()	#get tag type and wisp id

		#if tag type is correct, update the temperature graph
		if tagType == "0F" or tagType == "0E":
			plt.clf()
			plt.grid(True)
			axes = wispApp.figure.add_subplot(111)
			axes.plot(plotData, color = 'red')
			plt.title('Temperature', fontsize = 12)
			plt.ylim(-300, 100)
			wispApp.canvas.draw()

	#Update accelerometer data
	def updateAccel(self):
		tagType, wispID = self.tagReport.updateTagReport()			#get tag type and wisp id
		accelX, accelY, accelZ = self.tagReport.updateAccel()		#get accel data
		
		#if the tag type is correct, update the sliders
		if tagType == "0B" or tagType == "0D":						
			wispApp.xAccel.setText(" X '%' Tilt: " + "\n" + '%6.2f%%' % accelX)
			wispApp.yAccel.setText(" Y '%' Tilt: " + "\n" + '%6.2f%%' % accelY)
			wispApp.zAccel.setText(" Z '%' Tilt: " + "\n" + '%6.2f%%' % accelZ)

			wispApp.sliderY.setValue(accelY)
			wispApp.sliderX.setValue(accelX)
			wispApp.sliderZ.setValue(accelZ)

	#Display new image
	def captureImage(self):
		tagType, wispID = self.tagReport.updateTagReport()
		
		if tagType == "CA":
			currImage, imageReady, index = self.tagReport.updateImage()
			if imageReady == True:
				plt.cla()	#clear plot
				plt.clf()	#clear plot
				plt.gray()	#set to grayscale
					
				image = wispApp.image.add_subplot(111) 	#create plot
				image.clear()							#clear image
				ax = wispApp.image.gca()				#remove axis
				ax.set_axis_off()						#remove axis
				image.imshow(currImage)					#show image
				wispApp.imageCanvas.draw()				#update gui
				

	#Clear current image
	def clearImage(self):
		self.tagReport.imageArray = [128 for x in range(25200)]
		plt.cla()
		plt.clf()


def main():
	app = QtGui.QApplication(sys.argv)
	global wispApp 
	wispApp = GUI_Setup()
	demo = RFID_Reader_App()
	wispApp.setWindowTitle("WISP Demo")
	sys.exit(app.exec_())

if __name__ == '__main__': main()
		
