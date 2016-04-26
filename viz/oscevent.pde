void oscEvent(OscMessage message){
  int panel = message.get(0).intValue();
  int r = message.get(1).intValue();
  int g = message.get(2).intValue();
  int b = message.get(3).intValue();
  if(debug){
    println("OSC Message Received from " + message.addrPattern());
    println("The message was panel: " + panel + ", r: " + r + ", g: " + g + 
      ", b: " + b);
  }
  panels[panel].r = r;
  panels[panel].g = g;
  panels[panel].b = b;
}