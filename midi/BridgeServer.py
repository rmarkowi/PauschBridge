import sys
import signal
from threading import Thread
import time
import OSC
import math

from ServerBase import FalloffColor, LightArray
from ServerBase import NUM_PANELS, LOWEST_NOTE, FALLOFF_RATE

import lumiversepython as L

lights = None

def sendLightsToBridge(lightarray, panels):
  for i in xrange(len(panels)):
    # send the color
    color = lightarray.panelColors[i]
    r = color.r / 255.0
    g = color.g / 255.0
    b = color.b / 255.0
    panels[i].setRGBRaw(r, g, b)

def handle_stuff(server):
  # clear timed_out flag
  server.timed_out = False
  # handle all pending requests then return
  while not server.timed_out:
    server.handle_request()

class RequestThread(Thread):

  def run(self):
    while True:
      time.sleep(0.01)
      handle_stuff(s)

if __name__ == "__main__":

  lights = LightArray()

  s = OSC.OSCServer(('pbridge.adm.cs.cmu.edu', 5724))
  s.addMsgHandler('/1', lights.handler)

  print "Started server"

  rig = L.Rig("/home/teacher/Lumiverse/PBridge.rig.json")

  rig.init()
  rig.run()

  queryResults = []

  for i in xrange(NUM_PANELS):
    queryStr = "$panel=%d" % i
    queryResults.append(rig.select(queryStr))

  reqT = RequestThread()
  reqT.daemon = True
  reqT.start()

  while True:
    time.sleep(0.01)
    lights.updateLights()
    sendLightsToBridge(lights, queryResults)

