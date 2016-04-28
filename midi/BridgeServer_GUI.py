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

from BridgeServer import FalloffColor, LightArray
from BridgeServer import NUM_PANELS, LOWEST_NOTE, FALLOFF_RATE

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
  lights.panelColors[panelNum].falloffRate = 1 / (10 * duration)
  print "received %s" % str(data)

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

  s = OSC.OSCServer(('127.0.0.1', 5724))
  s.addMsgHandler('/1', handler)

  print "Started server"

  reqT = RequestThread()
  reqT.daemon = True
  reqT.start()

  while True:
    time.sleep(0.01)
    lights.updateLights()
    sendLightsToViewer(lights, view)

