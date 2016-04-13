import smf
import sys

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
  return None

class Note:
  def __init__(self, pitch, chanNum, velocity, lengthSeconds, startTime):
    self.pitch = pitch
    self.channelNumber = chanNum
    self.duration = lengthSeconds
    self.startTime = startTime
    self.velocity = velocity

  def __str__(self):
    return "Channel %d, note %d, velocity %d, length %f, start time %f" \
    % (self.channelNumber, self.pitch, self.velocity, self.duration, self.startTime)

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "usage: python bridgemidi.py <midi file>"
    exit()

  filename = sys.argv[1]

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

  for note in notes:
    print note

