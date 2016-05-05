import sys
import signal
from threading import Thread
import time
import OSC
import math

NUM_PANELS = 59
LOWEST_NOTE = 30
FALLOFF_RATE = 3
BASE_COLOR = 50

lights = None

class FalloffColor:

  def __init__(self):
    self.r = 0
    self.g = 0
    self.b = 0
    self.falloffRate = 1

  def falloff(self, elapsed):
    factor = 1 / math.pow(2, self.falloffRate * elapsed)
    self.r = (self.r - BASE_COLOR) * factor + BASE_COLOR
    self.g = (self.g - BASE_COLOR) * factor + BASE_COLOR
    self.b = (self.b - BASE_COLOR) * factor + BASE_COLOR

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

  def handler(self, addr, tags, data, client_address):

    r = data[0]
    g = data[1]
    b = data[2]
    duration = data[3]
    pitch = data[4]

    panelNum = pitch - LOWEST_NOTE

    if panelNum < 0 or panelNum >= NUM_PANELS:
      return

    self.panelColors[panelNum].r = r
    self.panelColors[panelNum].g = g
    self.panelColors[panelNum].b = b
    self.panelColors[panelNum].falloffRate = 1 / (20 * duration)

  def advectLights_Heat(self, delta):
    diffs = []
    for i in xrange(len(self.panelColors)):
      center = self.panelColors[i]
      centerColor = (center.r, center.g, center.b, center.falloffRate)
      if i == 0:
        leftColor = (BASE_COLOR, 0, 0, 1)
      else:
        left = self.panelColors[i-1]
        leftColor = (left.r, left.g, left.b, left.falloffRate)
      if i == NUM_PANELS - 1:
        rightColor = (0, 0, 255, 1)
      else:
        right = self.panelColors[i+1]
        rightColor = (right.r, right.g, right.b, right.falloffRate)
      diffs.append(laplaceDiff(leftColor, rightColor, centerColor))
    for i in xrange(len(diffs)):
      scaleAddToColor(self.panelColors[i], delta, diffs[i])

  def updateLights(self):
    currentTime = time.time()
    elapsed = currentTime - self.lastTime

    self.advectLights_Heat(elapsed)

    for fColor in self.panelColors:
      fColor.falloff(elapsed)

    self.lastTime = currentTime

def sendLightsToBridge(lightarray, panels):
  for i in xrange(len(panels)):
    # send the color
    color = lightarray.panelColors[i]
    r = color.r / 255.0
    g = color.g / 255.0
    b = color.b / 255.0
    panels[i].setRGBRaw(r, g, b)
  # TODO: send things using lumiverse

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
