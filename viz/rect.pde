class Panel{
  int panelNum;
  color col;
  float startTime = 0;
  float endTime = 0;
  Panel(int a, color b){
    panelNum = a;
    col = b;
  }
  void update(){
    int currentTime = millis();
    if(currentTime < endTime){
      int newAlpha = int(map(currentTime, startTime, endTime, 255, 0));  
      col = color(hue(col), saturation(col), brightness(col), newAlpha);
    }
    pushStyle();
      stroke(0, 0, 255, 255);
      strokeWeight(1);
      fill(col);
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