import netP5.*;
import oscP5.*;

boolean debug = true;

int numPanels = 50;
int numVocals = 4;
int panelHeight = 5;
Panel[] panels = new Panel[54];

int port = 9001;
OscP5 osc;
NetAddress address;

int minPitch = 30;
int maxPitch = 90;

int songStartTime = -1;

void setup(){
  fullScreen();
  colorMode(HSB, 360, 255, 255, 255);
  background(0, 0, 0);
  
  osc = new OscP5(this, port);
  address = new NetAddress("127.0.0.1", port);
  
  for(int i = (width / numVocals); i < width; i+=(width/numVocals)){
    line(i, 0, i, (height / panelHeight));
  }
  for(int panel = 1; panel <= (numPanels + numVocals); panel++){
    panels[panel - 1] = new Panel(panel, color(0,0,0,0));
  }
}

void draw(){
  background(0, 0, 0);
  for(Panel panel:panels){
    panel.update();
  }
}