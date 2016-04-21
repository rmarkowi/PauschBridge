import smf
import sys
import signal
from threading import Thread
import time

def signalHandler(signal, frame):
	print "Ctrl-C received, exiting."
	sys.exit(0)

signal.signal(signal.SIGINT, signalHandler)

def checkNoteOff(event):
  midiCode = event.midi_buffer[0]
  if midiCode < 128:
    return (False, -1)
  if midiCode > 143:
    return (False, -1)
  channelNum = midiCode - 128
  return (True, channelNum)

def checkNoteOn(event):
  midiCode = event.midi_buffer[0]
  if midiCode < 144:
    return (False, -1)
  if midiCode > 159:
    return (False, -1)
  channelNum = midiCode - 144
  return (True, channelNum)

def findNoteOff(eventList, chanNum, pitch, startIndex):
  # Search forward through the eventList starting at index startIndex,
  # and look for a Note Off event that matches chanNum and pitch.
  for i in xrange(startIndex, len(eventList)):
    event = eventList[i]
    (isNoteOff, noteOffChanNum) = checkNoteOff(event)
    if isNoteOff:
      noteOffPitch = event.midi_buffer[1]
      if noteOffChanNum == chanNum and noteOffPitch == pitch:
        return event
  raise Exception("Paired NOTE-OFF signal not found")

class Note:
  def __init__(self, pitch, chanNum, velocity, lengthSeconds, startTime):
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

  def __str__(self):
    return "Channel %d, note %d, velocity %d, length %f, start time %f" \
    % (self.channelNumber, self.pitch, self.velocity, self.duration, self.startTime)

def getNotes(filename):

  print("opening file '%s'..." % filename)
  f = smf.SMF(filename)

  print("file is in format %d" % f.format)
  print("pulses per quarter note is %d" % f.ppqn)
  print("number of tracks is %d" % f.number_of_tracks)

  notes = []

  for track in f.tracks:
    # for every track, we want to get all of the note ons
    for i in xrange(len(track.events)):
      event = track.events[i]
      # check if each event is a note on
      (isNoteOn, chanNum) = checkNoteOn(event)
      if isNoteOn:
        pitch = event.midi_buffer[1]
        velocity = event.midi_buffer[2]
        eventTime = event.time_seconds
        #print "Note on, pitch %d, velocity %d, at time %f" \
        #  % (pitch, velocity, eventTime)
        noteOffEvent = findNoteOff(track.events, chanNum, pitch, i)
        #print "Corresponding note off: pitch %d at time %f" \
        #  % (noteOffEvent.midi_buffer[1], noteOffEvent.time_seconds)

        duration = noteOffEvent.time_seconds - event.time_seconds

        note = Note(pitch, chanNum, velocity, duration, eventTime)

        notes.append(note)

  notes.sort(key=lambda n: n.startTime)

  return notes

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

class MidiStreamer:
	"""
	A class that will "play back" the notes of a MIDI file in real time,
	so that they can be used to e.g. change the panels of the bridge in sync
	with the notes.
	"""
	def __init__(self, filename):
		self.notes = getNotes(filename)
		self.time = 0
		self.streamingThread = None

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
  # using the filename of the midi you want to use
  streamer = MidiStreamer(filename)

  # Define a callback function -- this is a function that the streamer
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
  streamer.waitToFinish()
