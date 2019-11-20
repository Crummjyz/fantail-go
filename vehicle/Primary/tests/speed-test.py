from time import time
from math import pi

import board
import digitalio

breakBeam = digitalio.DigitalInOut(board.D22)
breakBeam.direction = digitalio.Direction.INPUT
breakBeam.pull = digitalio.Pull.UP

wheelDiameter = 500 #mm
wheelCircumference = pi * wheelDiameter

while True:
  """ # Nanosecond Logic
  start = perf_counter_ns
  end = start + 250000000
  currentBeamState = 0
  ticks = 0
  while perf_counter_ns < end:
    if breakBeam.value != currentBeamState:
      currentBeamState = breakBeam.value
      if currentBeamState == 1:
        ticks += 1
  rotations = ticks / 5
  distance = rotations * wheelCircumference
  mmS = distance * 4
  mS = mmS * 0.001
  speed = mS * 3.6
  print(speed)
  """
  start = time()
  end = start + 1 #0.25
  currentBeamState = 0
  ticks = 0
  while time() < end:
    if breakBeam.value != currentBeamState:
      currentBeamState = breakBeam.value
      if currentBeamState == 1:
        ticks += 1
  rotations = ticks / 5
  distance = rotations * wheelCircumference
  mmS = distance #* 4
  mS = mmS * 0.001
  speed = mS * 3.6
  print(speed)
