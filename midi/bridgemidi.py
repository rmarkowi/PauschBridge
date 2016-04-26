import sys
import signal
from threading import Thread
import time
import OSC

client = OSC.OSCClient()
client.connect(('127.0.0.1', 9001))

def signalHandler(signal, frame):
  print "Ctrl-C received, exiting."
  sys.exit(0)

signal.signal(signal.SIGINT, signalHandler)

class Note:
  def __init__(self, pitch, chanNum, velocity, lengthSeconds, startTime, trackNum):
    # MIDI pitch, an integer from 0 to 127
    self.pitch = pitch
    # MIDI channel number, integer from 0 to 15
    self.channelNumber = chanNum
    # Duration of this note in seconds
    self.duration = lengthSeconds
    # Start time of this note in seconds, relative to the start of the song
    self.startTime = startTime
    # MIDI "velocity" (pretty much means volume)
    self.velocity = velocity
    self.trackNumber = trackNum
    self.density = 0

  def __str__(self):
    return "Channel %d, note %d, velocity %d, length %f, start time %f" \
    % (self.channelNumber, self.pitch, self.velocity, self.duration, self.startTime, self.trackNumber)

def computeNoteDensity(noteList):
  for i in xrange(len(noteList)):
    currentNote = noteList[i]
    density = 0
    for j in reversed(xrange(i)):
      otherNote = noteList[j]
      timeDiff = currentNote.startTime - otherNote.startTime
      if timeDiff > 1:
        break
      factor = 1 - timeDiff
      density += factor
    for j in xrange(i, len(noteList)):
      otherNote = noteList[j]
      timeDiff = otherNote.startTime - currentNote.startTime
      if timeDiff > 1:
        break
      factor = 1 - timeDiff
      density += factor
    currentNote.density = density

class StreamerThread(Thread):

  def __init__(self, noteList, callbackFn):
    super(StreamerThread, self).__init__()
    self.noteList = noteList
    self.startTime = time.time()
    self.callbackFn = callbackFn
    self.done = False

  def elapsedTime(self):
      currentTime = time.time()
      elapsed = currentTime - self.startTime
      return elapsed

  def run(self):
    i = 0
    while i < len(self.noteList):
      elapsed = self.elapsedTime()
      nextNote = self.noteList[i]
      while elapsed < nextNote.startTime:
        elapsed = self.elapsedTime()
        time.sleep(0.001)
        # spin here because lazy
        pass
      self.callbackFn(nextNote)
      i += 1
    self.done = True

def readNoteList(filename):
  notes = []
  with open(filename, 'r') as inFile:
    for line in inFile:
      numbers = map(lambda x: x.strip(), line.split(' '))
      pitch = int(numbers[0])
      chanNum = int(numbers[1])
      duration = float(numbers[2])
      startTime = float(numbers[3])
      velocity = int(numbers[4])
      trackNum = int(numbers[5])
      notes.append(Note(pitch, chanNum, velocity, duration, startTime, trackNum))
  return notes

def hsvToRgb(h, s, v):
  c = v * s
  h_prime = h / 60
  x = c * (1 - abs((h_prime % 2 - 1)))
  if 0 <= h_prime and h_prime < 1:
    (r1, g1, b1) = (c, x, 0)
  elif 1 <= h_prime and h_prime < 2:
    (r1, g1, b1) = (x, c, 0)
  elif 2 <= h_prime and h_prime < 3:
    (r1, g1, b1) = (0, c, x)
  elif 3 <= h_prime and h_prime < 4:
    (r1, g1, b1) = (0, x, c)
  elif 4 <= h_prime and h_prime < 5:
    (r1, g1, b1) = (x, 0, c)
  elif 5 <= h_prime and h_prime < 6:
    (r1, g1, b1) = (c, 0, x)
  else:
    (r1, g1, b1) = (0, 0, 0)

  m = v - c
  (r, g, b) = (r1 + m, g1 + m, b1 + m)
  return (r, g, b)

def midiToOsc(note):
  msg = OSC.OSCMessage()
  print "send"
  msg.setAddress("/1")

  msg.append(note.pitch)
  msg.append(note.channelNumber)
  msg.append(note.duration)
  msg.append(note.startTime)
  msg.append(note.velocity)
  msg.append(note.trackNumber)
  client.send(msg)

class MidiStreamer:
  """
  A class that will "play back" the notes of a MIDI file in real time,
  so that they can be used to e.g. change the panels of the bridge in sync
  with the notes.
  """
  def __init__(self, filename):
    self.notes = readNoteList(filename)
    self.time = 0
    self.streamingThread = None
    computeNoteDensity(self.notes)

  # Begins a thread that will call the supplied function callbackFn
  # with the next notes in the MIDI file at each note's start time,
  # in real time.
  def streamNotesRealTime(self, callbackFn):
    if self.streamingThread is None:
      self.streamingThread = StreamerThread(self.notes, callbackFn)
      # Set this so we can kill it with ctrl-C in case of emergency
      self.streamingThread.daemon = True
      self.streamingThread.start()

  def waitToFinish(self):
    # Do it this way because join causes the main thread to block
    while not self.streamingThread.done:
      time.sleep(0.1)

# Look here for example usage.
if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "usage: python bridgemidi.py <midi file>"
    exit()

  filename = sys.argv[1]

  # In order to use this stuff, first create a MidiStreamer
  # using the filename of the midi notelist you want to use
  streamer = MidiStreamer(filename)

  """# Define a callback function -- this is a function that the streamer
  # will call each time it gets a new note. The argument to this function
  # needs to be an object of the Note class I've defined above.
  # For the bridge, this function probably does something like changing
  # the color of a panel based on what note it gets.
  def printNote(note):
    print note

  # Call streamNotesRealTime with the argument as the function you just defined.
  streamer.streamNotesRealTime(printNote)
  # This is here just in case the main program doesn't have anything else to do,
  # since if the main thread terminates, then the entire thing will end.
  # No need to use this if the main thread goes on to execute a different loop.
  streamer.waitToFinish()"""
  streamer.streamNotesRealTime(midiToOsc)
  streamer.waitToFinish()
