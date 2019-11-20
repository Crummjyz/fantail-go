# Control position of steering servo with an Xbox controller connected via USB.

from inputs import get_gamepad

from gpiozero import Servo
servo = Servo(18)

def setSteering(value):
  if value > 1:
    value = 1
  if value < -1
    value = -1
  servo.value = value

leftStickCenter = None
while leftStickCenter == None:
  events = get_gamepad()
  for event in events:
    if event.code == "ABS_X":
      leftStickCenter = event.state

while True:
  events = get_gamepad()
  for event in events:
    if event.code == "ABS_X":
      steeringInput = event.state - leftStickCenter
      steeringNormalized = steeringInput / 16384
      setSteering(steeringNormalized)
