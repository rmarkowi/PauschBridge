class Panel{
  int panelNum;
  int r = 0;
  int g = 0;
  int b = 0;
  color c;
  Panel(int a){
    panelNum = a;
  }
  void update(){
    pushStyle();
      stroke(255, 255, 255);
      strokeWeight(1);
      c = color(r, g, b);
      fill(c);
      int startX;
      int startY;
      int endX;
      int endY;
      if(panelNum <= numPanels){
        startX = (panelNum *(width / numPanels)) - (width / numPanels);
        startY = (height / panelHeight);
        endX = (panelNum * (width / numPanels));
        endY = height;
      }
      else{
        startX = ((panelNum % numPanels) * (width / numVocals)) - (width / numVocals);
        startY = 0;
        endX = ((panelNum % numPanels) * (width / numVocals));
        endY = (height / panelHeight);
      }
      rect(startX, startY, endX, endY);
    popStyle();
  }
}