#!/usr/bin/env python

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import threading
from PIL import Image
import sys
import os
import numpy as np

texture = [0 for x in range(2)]

class SaturnDemo(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.angle = 0						#calculateDisk()
		self.j =  0 						#drawDisk()

		self.diskVertexX = []
		self.diskVertexY = []

		#Initial rotation
		self.defViewAngleX = 90
		self.defViewAngleY = 0

		self.viewAngleX = self.defViewAngleX
		self.viewAngleY = self.defViewAngleY
		self.angleX = 0 - self.viewAngleX
		self.angleY = 0 - self.viewAngleY


	def run(self):
		self.drawInit()

	def drawInit(self):
		glutInit(())
		glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH | GLUT_DOUBLE)
		glutInitWindowSize(600, 600)
		glutCreateWindow("Saturn Demo")

		self.setLight()
		self.setMaterial()

		glClearColor(0, 0, 0, 0)
		glEnable(GL_TEXTURE_2D)
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

		#Planet
		glGenTextures(2, texture)
		glBindTexture(GL_TEXTURE_2D, texture[0])
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

		img = Image.open('saturn.jpg')

		try:
			ix, iy, image = img.size[0], img.size[1], img.tostring("raw", "RGBA", 0, -1)
		except SystemError:
			ix, iy, image = img.size[0], img.size[1], img.tostring("raw", "RGBX", 0, -1)

		glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)

		self.quadObj = gluNewQuadric()
		gluQuadricTexture(self.quadObj, GL_TRUE)


		#Rings
		'''
			glBindTexture(GL_TEXTURE_2D, texture[1])
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
			glBindTexture(GL_TEXTURE_2D, texture[2])
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
			glBindTexture(GL_TEXTURE_2D, texture[3])
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
			self.loadRings()
			self.calculateDisk()
		'''

		glutDisplayFunc(self.render)
		glMatrixMode(GL_PROJECTION)
		gluPerspective(30, 1, 1, 30)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		gluLookAt(0,0,10,
				  0,0,0,
				  0,1,0)

		glutMainLoop() 

	def loadRings(self):
		img2 = Image.open('saturnringcolor.jpg')

		try:
			x, y, image2 = img2.size[0], img2.size[1], img2.tostring("raw", "RGBA", 0, -1)
		except SystemError:
			x, y, image2 = img2.size[0], img2.size[1], img2.tostring("raw","RGBX", 0, -1)

		glTexImage2D(GL_TEXTURE_2D, 0, 3, x, y, 0, GL_RGBA, GL_UNSIGNED_BYTE, image2)


	def setAngles (self, x, y, z):
		#if x != self.angleX or y != self.angleY or self.angleZ != z:
			#self.angleX = x
			#self.angleY = y
			#self.angleZ = z

		xAccel = x - 50.
		yAccel = y - 50.
		zAccel = z - 50.

		if zAccel != 0.0:
			senseAngleX = float((180. / 3.14149) * np.arctan(xAccel / zAccel))
			senseAngleY = float(np.sign(zAccel) * (180. / 3.14149) * np.arctan(yAccel / zAccel))

		self.angleX = senseAngleX - self.viewAngleX
		self.angleY = senseAngleY - self.viewAngleY


	def render(self):
		glClearColor(0, 0, 0, 1)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		glPushMatrix()

		#Rotate
		glTranslatef(0.0, 0.0, 0.0)
		glRotatef(self.angleX, 1.0, 0.0 ,0.0)
		glTranslatef(0.0, 0.0, 0.0)
		glRotatef(self.angleY, 0.0, 1.0, 0.0)
		glTranslatef(0.0, 0.0, 0.0)

		#Draw planet
		glBindTexture(GL_TEXTURE_2D, texture[0])
		glColor3f(1,1,1)
		gluSphere(self.quadObj, 0.601, 40, 40)

		#Draw Rings
		glColor3ub(180, 255, 180)
		glutSolidTorus(0.03, 0.89, 3, 40) #1st
		glColor3ub(160, 160, 255)
		glutSolidTorus(0.03, 0.94, 3, 40) #2nd
		glColor3ub(255, 255, 255)
		glutSolidTorus(0.04, 1, 3, 40) #3rd
		glColor3ub(180, 255, 180)
		glutSolidTorus(0.05, 1.06, 3, 40) #4th
		glColor3ub(100, 100, 100)
		glutSolidTorus(0.02, 1.08, 3, 40) #5th
		glColor3ub(170, 170, 255)
		glutSolidTorus(0.03, 1.1, 3, 40) #6th
		glColor3ub(255, 255, 255)
		glutSolidTorus(0.02, 1.13, 3, 40) #7th

		glPopMatrix()

		glutSwapBuffers()
		glutPostRedisplay()
       

	def calculateDisk(self):
		rads = math.atan(1) / 45.
		radius1 = 0.744
		radius2 = 1.402

		while self.angle <= 360:
			self.angle += 8
			            
			#Calculate position of vertices for inner circle
			self.diskVertexX.append(radius1 * math.sin(rads * (self.angle - 90)))
			self.diskVertexY.append(radius1 * math.sin(rads * self.angle))

			#Calculate position of vertices for outer circle
			self.diskVertexX.append(radius2 * math.sin(rads * (self.angle - 90)))
			self.diskVertexY.append(radius2 * math.sin(rads * self.angle))

	def drawDisk(self):
		while self.j <= (len(self.diskVertexX) - 3) and self.j <= (len(self.diskVertexY) - 3):
			glBegin(GL_TRIANGLES)

			#1st triangle
			glTexCoord2f(0, 0)
			glVertex3f(self.diskVertexX[self.j], self.diskVertexY[self.j], 0)
			glTexCoord2f(1, 0)
			glVertex3f(self.diskVertexX[self.j + 1], self.diskVertexY[self.j + 1], 0)
			glTexCoord2f(0, 1)
			glVertex3f(self.diskVertexX[self.j + 2], self.diskVertexY[self.j + 2], 0)

			#2nd triangle
			glTexCoord2f(1, 1)
			glVertex3f(self.diskVertexX[self.j + 3], self.diskVertexY[self.j + 3], 0)
			glTexCoord2f(0, 1)
			glVertex3f(self.diskVertexX[self.j + 2], self.diskVertexY[self.j + 2], 0)
			glTexCoord2f(1, 0)
			glVertex3f(self.diskVertexX[self.j + 1], self.diskVertexY[self.j + 1], 0)

			self.j += 2

			glEnd()

	def setLight(self):
		ambientLight= [1, float(0.8), float(0.80), 1]
		diffuseLight = [1., float(0.8), float(0.8), 1]
		lightPos = [0, 0, 50, 0]
		spotDirection = [0, -2, -1, 1]

		glEnable(GL_LIGHT0)
		glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
		glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
		glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuseLight)
		glEnable(GL_LIGHTING)

                
	def setMaterial(self):
		mat_specular = [0, 0, 1, 1]
		mat_diffuse = [0, 0, float(0.7), 1]
		mat_ambient = [0, 0, 1, 1]
		mat_shininess = [5]

		glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
		glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)
		glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
		glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)

		glEnable(GL_COLOR_MATERIAL)