from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from math import sin, sqrt
from time import time

MAX_ZOOM = 1000000

class Camera:

    def __init__(self, windowWidth, windowHeight):
        self.x = 29.5
        self.y = 1
        self.z = 6.7
        self.aspectRatio = float(windowWidth) / windowHeight
        self.dragging = False
        self.dragStartPos = (0, 0)
        self.dragDispX = 0
        self.dragDispY = 0

    def updateDimensions(self, w, h):
        self.aspectRatio = float(w) / h

    def setProjection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, self.aspectRatio, 0.1, MAX_ZOOM  * 2)

    def setView(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(self.x + self.dragDispX, self.y + self.dragDispY, self.z,
                  self.x + self.dragDispX, self.y + self.dragDispY, 0,
                  0, 1, 0)

    def screenToCanvas(self, x, y):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(self.x, self.y, -self.z,
                  self.x, self.y, 0,
                  0, -1, 0)
        nearCoords = gluUnProject(x, y, 0)
        farCoords = gluUnProject(x, y, 1)

        diffVec = map(lambda i: farCoords[i] - nearCoords[i], range(len(nearCoords)))

        amount = nearCoords[2] / diffVec[2]
        nearCoords = map(lambda i: nearCoords[i] - amount * diffVec[i], range(len(nearCoords)))

        return (nearCoords[0], nearCoords[1])


    def processMouse(self, button, state, x, y):
        if button == 3 or button == 4:
            if state == GLUT_UP:
                return
            elif button == 3:
                self.zoomIn()
            elif button == 4:
                self.zoomOut()
        elif button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                self.dragging = True
                canvasCoords = self.screenToCanvas(x, y)
                self.dragStartPos = canvasCoords

            elif state == GLUT_UP:
                self.dragging = False
                self.x += self.dragDispX
                self.dragDispX = 0
                self.y += self.dragDispY
                self.dragDispY = 0

    def processMotion(self, x, y):
        if self.dragging:
            canvasCoords = self.screenToCanvas(x, y)
            self.dragDispX = -(canvasCoords[0] - self.dragStartPos[0])
            self.dragDispY = -(canvasCoords[1] - self.dragStartPos[1])
    
    def zoomIn(self):
        self.z = max(1, self.z * 0.9)

    def zoomOut(self):
        self.z = min(MAX_ZOOM, self.z * 1.1)

    def idle(self):
        self.zoomOut()
        if self.z > MAX_ZOOM / 2:
            self.z = 1100