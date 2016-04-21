import smf
import sys
import signal
from threading import Thread
from bridgemidi import Note
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

def writeNotes(noteList, filename):
  with open(filename, 'w') as out:
    for note in notes:
      noteString = "%d %d %f %f %d\n" % (note.pitch, note.channelNumber, note.duration, note.startTime, note.velocity)
      out.write(noteString)

# Look here for example usage.
if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "usage: python bridgemidi.py <midi file>"
    exit()

  filename = sys.argv[1]

  # In order to use this stuff, first create a MidiStreamer
  # using the filename of the midi you want to use
  notes = getNotes(filename)

  outFile = "%s.notelist" % filename
  writeNotes(notes, outFile)