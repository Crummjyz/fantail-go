from inputs import get_gamepad
from gpiozero import Servo, DigitalOutputDevice

servo = Servo(18)
reverse = DigitalOutputDevice(24)

import board
import busio
import adafruit_mcp4725
i2c = busio.I2C(board.SCL, board.SDA)
dac = adafruit_mcp4725.MCP4725(i2c)

def setSteering(value):
  if value > 1:
    value = 1
  elif value < -1:
    value = -1
  servo.value = value

def setThrottle(value):
  if value > 0.4425: #0.4425: 1/4 Speed, 0.635: 1/2 Speed
    value = 0.4425 # Change this value as well!
  dac.normalized_value = value

try:
  leftStickCenter = None
  while leftStickCenter == None:
    events = get_gamepad()
    for event in events:
      if event.code == "ABS_X":
        leftStickCenter = event.state

  while True:
    events = get_gamepad()
    for event in events:
      if event.code == "BTN_WEST":
        reverse.value = event.state

      if event.code == "ABS_X":
        steeringInput = event.state - leftStickCenter
        steeringNormalized = steeringInput / 16384
        setSteering(steeringNormalized)
      elif event.code == "ABS_RZ":
        throttleInput = event.state
        throttleNormalized = throttleInput / 2047 # 1535 1/2 speed, 2047 1/4 speed, 1023 full speed (This adjusts the sensitivity)
        setThrottle(throttleNormalized)

except:
  dac.normalized_value = 0
  reverse.off()
  print("WARNING: AN EXCEPTION OCCURRED. MOTOR HAS BEEN SHUT OFF AND SCRIPT WILL EXIT.")
