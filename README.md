# PauschBridge
BRIDGE

Ultimately, the software should map the following:
1) "Track Number" should correspond to Hue. I think we will look at the Midi file, grab all the track numbers, map them between 0 and 360. We should get distinct colors.

2) "Velocity" should be brightness. That being said, the default value for any panel should be (50, 50, 50) or something like that. The goal is that the panels glow white and pop to a color when a note is played. The brightness should map so that it ranges between the RGB color value specified by the track. Ie, if the track is (255, 127, 0), then the velocity should map (0 - 255) as (50 -> 255, 50 -> 127, 50 -> 50).

3) "Duration" is saturation. As the note sustains, the values should return to (50, 50, 50) all at the same time. So, if the Track indicated a note of (255, 127, 0) with a duration of 2 seconds, then over those two second the RGB values should slowly return to (50, 50, 50).
