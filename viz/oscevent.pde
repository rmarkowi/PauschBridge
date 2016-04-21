void oscEvent(OscMessage message){
  int pitch = message.get(0).intValue();
  int instrument = message.get(1).intValue();
  float duration = message.get(2).floatValue();
  float startTime = message.get(3).floatValue();
  int velocity = message.get(4).intValue();
  if(debug){
    println("OSC Message Received from " + message.addrPattern());
    println("The message was pitch: " + pitch + ", instrument: " + instrument + ", duration: " + duration + 
      ", start time: " + startTime + ", velocity: " + velocity);
  }
  if(songStartTime < 0){
    songStartTime = millis();
  }
  int toPanel = int(map(pitch, minPitch, maxPitch, 1, numPanels));
  int cVal = int(map(instrument, 0, 20, 0, 360));
  panels[toPanel].col = color(cVal, 255, 255, 255);
  panels[toPanel].startTime = millis();
  panels[toPanel].endTime = panels[toPanel].startTime + (duration * 1000);
}