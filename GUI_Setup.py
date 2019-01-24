#!/usr/bin/env python
"""
 Created on Thursday July, 10, 2014
 @author Zerina Kapetanovic
"""

from PyQt4 import QtGui, Qt, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class GUI_Setup(QtGui.QMainWindow):
	def __init__(self):
		super(GUI_Setup, self).__init__()
		self.initUI()
		self.resize(1190, 560)

	def initUI(self):

		#### Main Table ####
		self.main_frame = QWidget()
		self.mainTable = QtGui.QTableWidget(0, 7, self)
		self.mainTable.setFont(QFont('Courier New', 8))
		self.mainTable.setHorizontalHeaderLabels(('TIME', 'WISP ID', 'TAG TYPE', 'EPC', 'SENSOR DATA', 'SNR', 'RSSI'))
		self.mainTable.horizontalHeader().setStretchLastSection(True)
		self.mainTable.setGeometry(10, 160, 700, 330)

		#### Buttons ####
		self.startButton = QtGui.QPushButton('Start', self)
		self.startButton.setFlat(False)
		self.startButton.setObjectName("Start")
		self.startButton.setGeometry(30, 500, 100, 30)

		self.pauseButton = QtGui.QPushButton('Pause', self)
		self.pauseButton.setObjectName("Stop")
		self.pauseButton.setGeometry(140, 500, 100, 30)

		self.clearButton = QtGui.QPushButton('Clear Image', self)
		self.clearButton.setObjectName("Clear")
		self.clearButton.setGeometry(250, 500, 100, 30)

		#### Accelerometer ####
		self.xAccel = QtGui.QLabel("X Tilt %",self)
		self.yAccel = QtGui.QLabel("Y Tilt %",self)
		self.zAccel = QtGui.QLabel("Z Tilt %",self)
		
		self.sliderY = QtGui.QSlider(QtCore.Qt.Vertical, self)
		self.sliderX = QtGui.QSlider(QtCore.Qt.Horizontal, self)
		self.sliderZ = QtGui.QSlider(QtCore.Qt.Vertical, self)


		########## Image Capture ##########
		#self.xVal = QtGui.QTextEdit(self)
		#self.xVal.setFixedWidth(100)
		#self.xVal.setFixedHeight(25)
		#self.xVal.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		
		#self.yVal = QtGui.QTextEdit(self)
		#self.yVal.setFixedWidth(100)
		#self.yVal.setFixedHeight(25)
		#self.yVal.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		
		#self.xLabel = QtGui.QLabel("    <b>X-Value</b> (0 - 255):       ")
		#self.yLabel = QtGui.QLabel("    <b>Y-Value</b> (0 - 255):       ")
		self.statusLabel = QtGui.QLabel("<b>Charge Status</b>:")
		self.font = QtGui.QFont()
		self.font.setPointSize(15)
		self.statusLabel.setFont(self.font)

		self.chargePercentage = QtGui.QLabel("0%")
		self.font = QtGui.QFont()
		self.font.setPointSize(15)
		self.statusLabel.setFont(self.font)

		#self.captureButton = QtGui.QPushButton("Enter Values")
		#self.captureButton.setFixedHeight(30)
		#self.captureButton.setFixedWidth(100)

		self.image = Figure()
		self.imageCanvas = FigureCanvas(self.image)

		self.progress = QtGui.QProgressBar(self)
		self.progress.setRange(0, 100)
		self.progress.setValue(0)
		#self.progress.setFixedHeight(200)
		#self.progress

		############################### CONFIG TABS #############################

		########## Reader Config ##########	
		self.tabs2Frame = QtGui.QFrame(self)
		self.tabs2Frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
		self.tabs2Frame.setLineWidth(4)
		self.tabs2Frame.setGeometry(10, 35, 700, 120)

		tabs2 = QtGui.QTabWidget(self)
		tabs2.resize(650, 160)
		tabs2.move(10, 7)
		readerTab 	= QtGui.QWidget()
		readerTab.setFont(QFont('Arial', 12))

		tabs2.addTab(readerTab, "Configure Reader")

		## Select Reader ##
		self.readerSelectLabel = QtGui.QLabel("Select Reader:  ", self)
		self.readerSelectLabel.setFont(QFont('Arial', 10))
		self.readerSelect = QtGui.QComboBox(self)
		self.readerSelect.setEditable(False)
		self.readerSelect.setFixedHeight(25)
		self.readerSelect.setFixedWidth(80)
		self.readerSelect.setFont(QFont('Arial', 10))
		self.readerSelect.addItem('Impinj')
		self.readerSelect.addItem('USRP')
		self.readerSelect.setCurrentIndex(0);

		## Select Modulation and Tari ##
		self.modLabel = QtGui.QLabel("    Reader Settings:        ")
		self.modLabel.setFont(QFont('Arial', 10))
		self.modSelect = QtGui.QComboBox(self)
		self.modSelect.setEditable(False)
		self.modSelect.setFixedHeight(25)
		self.modSelect.setFixedWidth(130)
		self.modSelect.setFont(QFont('Arial', 10))
		self.modSelect.addItem('Modulation : Tari')
		self.modSelect.addItem('FM0 : 7140')
		self.modSelect.addItem('M4 : 25000')
		self.modSelect.addItem('WISP5pre : 12500')
		self.modSelect.addItem('WISP5 : 7140')
		self.modSelect.setCurrentIndex(1);

		## Select Host ##
		self.ipLabel = QtGui.QLabel("    Host IP:    ", self)
		self.ipLabel.setFont(QFont('Arial', 10))
		self.ipAddress = QtGui.QComboBox(self)
		self.ipAddress.setFixedHeight(20)
		self.ipAddress.setFixedWidth(150)
		self.ipAddress.setFont(QFont('Arial', 10))
		self.ipAddress.addItem('192.168.1.3')
		self.ipAddress.addItem('192.168.10.100')
		self.ipAddress.setCurrentIndex(0)
		
		## Connect to reader ##
		self.connectButton = QtGui.QPushButton("Connect", self)
		self.connectButton.setFixedHeight(25)
		self.connectButton.setFixedWidth(75)
		self.connectButton.setFont(QFont('Arial', 10))
		self.connectButton.setObjectName("readerSelect")

		readerLayout = QtGui.QGridLayout()
		readerLayout.setRowMinimumHeight(0, 20)
		readerLayout.setHorizontalSpacing(0)
		readerLayout.addWidget(self.readerSelectLabel, 0, 0)
		readerLayout.addWidget(self.readerSelect, 0, 1)
		readerLayout.addWidget(self.modLabel, 0, 2)
		readerLayout.addWidget(self.modSelect, 0, 3)
		readerLayout.addWidget(self.ipLabel, 0, 4)
		readerLayout.addWidget(self.ipAddress, 0, 5)
		readerLayout.addWidget(self.connectButton, 2, 0)
		readerTab.setLayout(readerLayout)

		######### Saturn Config #########
		saturnTab = QtGui.QWidget()
		saturnTab.setFont(QFont('Arial', 12))
		tabs2.addTab(saturnTab, "Configure Saturn")

		self.saturnButton = QtGui.QPushButton('Display Saturn', self)
		self.saturnButton.setObjectName("Saturn")
		self.saturnButton.setFixedHeight(25)
		self.saturnButton.setFixedWidth(95)
		self.saturnButton.setFont(QFont('Arial', 10))

		self.caliButton = QtGui.QPushButton('Calibrate', self)
		self.caliButton.setObjectName("Calibrate")
		self.caliButton.setGeometry(580, 500, 100, 30)
		self.caliButton.setFixedHeight(25)
		self.caliButton.setFixedWidth(75)
		self.caliButton.setFont(QFont('Arial', 10))

		self.xFlip = QtGui.QCheckBox("Flip X", self)
		self.yFlip = QtGui.QCheckBox("Flip Y", self)
		self.xFlip.setFont(QFont('Arial', 10))
		self.yFlip.setFont(QFont('Arial', 10))
		self.xFlip.setChecked(False)
		self.yFlip.setChecked(False)

		saturnLayout = QtGui.QGridLayout()
		saturnLayout.setRowMinimumHeight(0, 20)
		saturnLayout.addWidget(self.caliButton, 1, 0)
		saturnLayout.addWidget(self.saturnButton, 2, 0)
		saturnLayout.addWidget(self.xFlip, 0, 0)
		saturnLayout.addWidget(self.yFlip, 0, 1)
		saturnTab.setLayout(saturnLayout)
		################################ Demo Tabs #############################

		######### Graph ##########		
		self.figure = plt.figure()
		self.canvas = FigureCanvas(self.figure)
		
		#Image Capture
		self.imageLayout = QtGui.QGridLayout()
		self.imageLayout.setHorizontalSpacing(30)
		#self.imageLayout.addWidget(self.xLabel, 1, 0)
		#self.imageLayout.addWidget(self.xVal, 1, 4)
		#self.imageLayout.addWidget(self.yLabel, 2, 0)
		#self.imageLayout.addWidget(self.yVal, 2, 4)
		self.imageLayout.addWidget(self.progress, 1,2)
		self.imageLayout.addWidget(self.statusLabel, 1, 0)
		self.imageLayout.addWidget(self.chargePercentage,1,3)
		#self.imageLayout.addWidget(self.captureButton, 3, 4)
		self.imageLayout.addWidget(self.imageCanvas, 5, 0, 5, 5)
		
		#Temperature
		self.tempLayout = QtGui.QGridLayout()
		self.tempLayout.addWidget(self.canvas, 0, 0)
		
		#Accelerometer
		accelLayout = QtGui.QGridLayout()
		accelLayout.setRowMinimumHeight(0, 20)
		accelLayout.addWidget(self.yAccel, 0, 0)
		accelLayout.addWidget(self.sliderY, 1, 0)
		accelLayout.addWidget(self.zAccel, 0, 5)
		accelLayout.addWidget(self.sliderZ, 1, 5)
		accelLayout.addWidget(self.xAccel, 5, 3, QtCore.Qt.AlignCenter)
		accelLayout.addWidget(self.sliderX, 6, 3)	

		#### TABS ####
		tabFrame = QtGui.QFrame(self)
		tabFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
		tabFrame.setLineWidth(4)
		tabFrame.setGeometry(720, 30, 450, 485)		
		
		tabs = QtGui.QTabWidget(self)
		tabs.resize(450, 500)
		tabs.move(720, 10)
			
		accelTab 	= QtGui.QWidget()
		tempTab 	= QtGui.QWidget()
		imageTab 	= QtGui.QWidget()

		tabs.addTab(imageTab, "Image Capture")
		tabs.addTab(accelTab, "Accelerometer")
		tabs.addTab(tempTab, "Temperature")
		
		accelTab.setLayout(accelLayout)
		tempTab.setLayout(self.tempLayout)
		imageTab.setLayout(self.imageLayout)

		########## Stylesheet ##########
		Stylesheet = """
		QPushButton {border: 1px solid black; border-radius: 6px;}
		QPushButton:pressed {
		background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                          stop: 0 #dadbde, stop: 1 #f6f7fa);
		}
		QPushButton#Stop {border: 1px solid red; border-radius: 6px;}
		QPushButton#Start {border: 1px solid #5BD463; border-radius: 6px;}
		QTabWidget:pane{border: 1px sp;od #C2C7CB;}
		QTabWidget:tab-bar{left: 0px; border: none;}
		QTabBar: tab {background: qlineargradient(x1: 0, y1: 0, x2:0, y2: 1,\
		stop: 0 #E1E1E1, stop: 0.4 #DDDDDD, stop 0.5 #D8D8D8, stop: 1.0 #D3D3D3);\
		border: 1px solid #C4C4C3; border-top-left-radius: 2px;\
		border-top-right-radius: 4px; min-width: 8px; padding: 2px;}
		QTabBar:tab:selected {border-color: #9B9B9B; border-bottom-color: #C2C7CB;}
		QTabBar:tab:!selected {margin-top: 2px;}
		QTableWidget {background-color: qlineargradient(x1; 0, y1: 0, x2: 0.5, y2: 0.5,\
		stop: 0 #FF92BB, stop: 1 white);}
		"""
		
		self.setStyleSheet(Stylesheet)	

		self.show()

