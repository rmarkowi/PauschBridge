import sys
import signal
from threading import Thread
import time
import OSC
import math

NUM_PANELS = 59
LOWEST_NOTE = 30
FALLOFF_RATE = 3

def handler(addr, tags, data, client_address):
  txt = "OSCMessage '%s' from %s: " % (addr, client_address)
  txt += str(data)
  print(txt)

class LightArray:

  def __init__(self):
    self.panelColors = []
    for i in xrange(NUM_PANELS):
      self.panelColors.append([0, 0, 0])
    self.lastTime = time.time()

  def updateLights(self):
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


def handle_stuff(server):
    # clear timed_out flag
    server.timed_out = False
    # handle all pending requests then return
    while not server.timed_out:
        server.handle_request()

if __name__ == "__main__":
  lights = LightArray()

  s = OSC.OSCServer(('127.0.0.1', 9001))  # listen on localhost, port 57120
  s.addMsgHandler('/1', handler)     # call handler() for OSC messages received with the /startup address

  print "Started server"

  s.serve_forever()

  while True:
    time.sleep(0.01)
    handle_stuff(s)
    lights.updateLights()
