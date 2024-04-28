#!/bin/sh

# This enables circular scrolling for the touchpad of my old laptop.
# So old that it didn't support multi-finger scrolling.

# See also: man synaptics
# Looks like... x = 1350..5600 ; y = 1216..4722
synclient \
  CircularScrolling=1 \
  CircScrollDelta=0.524 \
  CircScrollTrigger=2 \
  VertEdgeScroll=0 \
  HorizEdgeScroll=0 \
  EdgeMotionMaxZ=85 \
  LeftEdge=1750 \
  RightEdge=5100 \
  TopEdge=1900 \
  BottomEdge=4100 \
  RTCornerButton=0 \
  RBCornerButton=0 \
  LTCornerButton=0 \
  LBCornerButton=0 \
  TapButton1=1 \
  TapButton2=2 \
  TapButton3=3 \
  ClickFinger1=0 \
  ClickFinger2=0 \
  ClickFinger3=0 \
  EmulateTwoFingerMinW=8 \
  EmulateTwoFingerMinZ=50 \
  VertTwoFingerScroll=1 \
  HorizTwoFingerScroll=1
# Other settings:
#   LockedDrags=1
#   CircScrollDelta: Move angle (radians) of finger to generate a scroll event.
#   CircScrollTrigger: 2 = Top Right
# Other default settings:
#   MaxTapMove=220
#   MaxTapTime=180
#   MaxDoubleTapTime=180
#   FingerPress=255
#   TapButton1=1
#   TapButton2=3
#   TapButton3=2
