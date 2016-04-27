
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import sys
import signal
from threading import Thread
import time
import OSC
import math

from viewer import Viewer

NUM_PANELS = 59
LOWEST_NOTE = 30
FALLOFF_RATE = 3

view = None
lights = None

def handler(addr, tags, data, client_address):

  r = data[0]
  g = data[1]
  b = data[2]
  duration = data[3]
  pitch = data[4]

  """
  pitch = data[0]
  channelNumber = data[1]
  duration = data[2]
  startTime = data[3]
  velocity = data[4]
  trackNumber = data[5]
  """

  panelNum = pitch - LOWEST_NOTE

  if panelNum < 0 or panelNum >= NUM_PANELS:
    return

  lights.panelColors[panelNum].r = r
  lights.panelColors[panelNum].g = g
  lights.panelColors[panelNum].b = b
  lights.panelColors[panelNum].falloffRate = 1 / (20 * duration)

class FalloffColor:

  def __init__(self):
    self.r = 0
    self.g = 0
    self.b = 0
    self.falloffRate = 1

  def falloff(self, elapsed):
    factor = 1 / math.pow(2, self.falloffRate * elapsed)
    self.r *= factor
    self.g *= factor
    self.b *= factor

def laplaceDiff(tup1, tup2, center):
  return (tup1[0] + tup2[0] - 2 * center[0],
    tup1[1] + tup2[1] - 2 * center[1],
    tup1[2] + tup2[2] - 2 * center[2],
    tup1[3] + tup2[3] - 2 * center[3])

def scaleAddToColor(color, t, tup2):
  color.r += t * tup2[0]
  color.g += t * tup2[1]
  color.b += t * tup2[2]
  color.falloffRate += t * tup2[3]

class LightArray:

  def __init__(self):
    self.panelColors = []
    for i in xrange(NUM_PANELS):
      self.panelColors.append(FalloffColor())
    self.lastTime = time.time()

  def advectLights(self, delta):
    diffs = []
    for i in xrange(len(self.panelColors)):
      center = self.panelColors[i]
      centerColor = (center.r, center.g, center.b, center.falloffRate)
      if i == 0:
        leftColor = (0, 0, 0, 1)
      else:
        left = self.panelColors[i-1]
        leftColor = (left.r, left.g, left.b, left.falloffRate)
      if i == NUM_PANELS - 1:
        rightColor = (0, 0, 0, 1)
      else:
        right = self.panelColors[i+1]
        rightColor = (right.r, right.g, right.b, right.falloffRate)
      diffs.append(laplaceDiff(leftColor, rightColor, centerColor))
    for i in xrange(len(diffs)):
      scaleAddToColor(self.panelColors[i], delta, diffs[i])

  def updateLights(self):
    currentTime = time.time()
    elapsed = currentTime - self.lastTime

    self.advectLights(elapsed)

    for fColor in self.panelColors:
      fColor.falloff(elapsed)

    self.lastTime = currentTime

def sendLightsToViewer(lightarray, view):
  for i in xrange(len(lightarray.panelColors)):
    fColor = lightarray.panelColors[i]
    view.setPanelColor(i, fColor.r, fColor.g, fColor.b)

def handle_stuff(server):
  # clear timed_out flag
  server.timed_out = False
  # handle all pending requests then return
  while not server.timed_out:
    server.handle_request()

class GlutThread(Thread):

  def run(self):
    global view
    view = Viewer(1800, 400)
    glutMainLoop()

class RequestThread(Thread):

  def run(self):
    while True:
      time.sleep(0.01)
      handle_stuff(s)

if __name__ == "__main__":

  lights = LightArray()

  glutT = GlutThread()
  glutT.daemon = True
  glutT.start()

  while view is None:
    pass

  s = OSC.OSCServer(('127.0.0.1', 9001))  # listen on localhost, port 57120
  s.addMsgHandler('/1', handler)     # call handler() for OSC messages received with the /startup address

  print "Started server"

  reqT = RequestThread()
  reqT.daemon = True
  reqT.start()

  while True:
    time.sleep(0.01)
    lights.updateLights()
    sendLightsToViewer(lights, view)

