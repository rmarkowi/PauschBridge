# Test of a simple visualizer for the M-Blocks
# Uses PyOpenGL, (and GLUT)
# TODO: FORNOW: TODO: Uses pygame for 
# NOTE: Hacked together from one of my graphics assignments.
# Originally James Bern 6/26/2014
# Edited Chris Yu 9/06/2015

from __future__ import division

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from camera import Camera
import math
from time import time, clock
from SendMidi import *
import sys
from random import randint

NUM_PANELS = 59
LOWEST_NOTE = 30
FALLOFF_RATE = 3

class Viewer:

    def __init__(self, w, h):

        self.lastTime = time.time()

        self.windowWidth = w
        self.windowHeight = h

        self.initGLUT() # Initialize GLUT first!  Depth test depends on window.
        self.initGL()

        self.camera = Camera(w, h)

        self.camera.setProjection()
        self.camera.setView()

        self.buttonState = None
        self.lastPosition = None

        # Set up callbacks
        glutDisplayFunc(self.redraw)
        glutReshapeFunc(self.resize)
        glutKeyboardFunc(self.keyfunc)
        glutMouseFunc(self.mousefunc)
        glutMotionFunc(self.motionfunc)
        glutIdleFunc(self.idlefunc)

        self.panelColors = []

        for i in xrange(NUM_PANELS):
            self.panelColors.append([0, 0, 0])

    def keyfunc(self, key, x, y):
        # global drawing_mode
        glutPostRedisplay()
        if key == 'a':
            self.camera.x -= 1
        if key == 'd':
            self.camera.x += 1
        if key == 'w':
            self.camera.zoomIn()
        if key == 's':
            self.camera.zoomOut()
        if key == chr(27) or key == 'q' or key == 'Q':
            exit(0)

    def mousefunc(self, button, state, x, y):
        #self.camera.processMouse(button, state, x, y)
        glutPostRedisplay()

    def motionfunc(self, x, y):
        #self.camera.processMotion(x, y)
        glutPostRedisplay()

    def idlefunc(self):
        """
        currentTime = time.time()
        elapsed = currentTime - self.lastTime
        factor = 1 / math.pow(2, FALLOFF_RATE * elapsed)

        def falloff(color):
            color[0] *= factor
            color[1] *= factor
            color[2] *= factor
            return color

        map(lambda c: falloff(c), self.panelColors)
        self.lastTime = currentTime
        """
        glutPostRedisplay()

    def redraw(self, clearColor=(0.2, 0.2, 0.2, 0), fill=False):
        glClearColor(clearColor[0], clearColor[1], clearColor[2], clearColor[3])
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.camera.setView()

        for i in xrange(NUM_PANELS):
            startX = i
            points = [[startX, 0, 0], [startX + 1, 0, 0], [startX + 1, 3, 0], [startX, 3, 0]]
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(3, GL_FLOAT, 0, points)
            glColor3f(*self.panelColors[i])
            glDrawArrays(GL_QUADS, 0, len(points))
            glColor3f(0, 0.7, 0.7)
            glDrawArrays(GL_LINE_LOOP, 0, len(points))
            glDisableClientState(GL_VERTEX_ARRAY)

        glutSwapBuffers()

    def resize(self, w, h):
        self.windowWidth = w
        self.windowHeight = h

        glViewport(0, 0, self.windowWidth, self.windowHeight)

        self.camera.updateDimensions(w, h)
        self.camera.setProjection()

        glutPostRedisplay()

    def initGL(self):
        glShadeModel(GL_SMOOTH)
        #glEnable(GL_CULL_FACE)
        #glCullFace(GL_BACK)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glLineWidth(3)
        glPointSize(12)

        glDisable(GL_BLEND)

        #glEnable(GL_BLEND)
        #glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ONE)

        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

    def initGLUT(self):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(self.windowWidth, self.windowHeight)
        glutInitWindowPosition(200, 200)
        glutCreateWindow("Something")

    def setPanelColor(self, num, r, g, b):
        self.panelColors[num] = [r / 255, g / 255, b / 255]

    def setPanelFromNote(self, note):
        noteNum = note.pitch - LOWEST_NOTE
        if noteNum < 0 or noteNum >= NUM_PANELS:
            return

        density = min(10, note.density)

        if density > 5:
            factor = 1 / math.exp(0.4 * (density - 5))
            self.panelColors[noteNum] = [1, factor, factor]
        else:
            factor = 1 / math.exp(0.4 * (5 - density))
            self.panelColors[noteNum] = [factor, factor, 1]

def main(filename = None):
    if filename is None:
        view = Viewer(1800, 400)
        glutMainLoop()
    else:
        view = Viewer(1800, 400)
        streamer = MidiStreamer(filename)
        streamer.streamNotesRealTime(view.setPanelFromNote)
        glutMainLoop()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        main()
    filename = sys.argv[1]
    main(filename)

