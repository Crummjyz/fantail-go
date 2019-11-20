#!/usr/bin/python3

### Setup ###
#region

## Parallelism ##
#region
import multiprocessing
manager = multiprocessing.Manager()
log = manager.dict()
log["exceptions"] = []
#endregion

## Config ##
#region
def setupConfig(config):
  from math import pi
  config['wheelCircumference'] = pi * config['wheelDiameter']
  return config

import json
config = manager.dict()
with open('/home/pi/Vehicle/Primary/config.json') as data:
  loadedData = json.load(data)
  for i in loadedData: # Trust me, there's a reason for this madness.
    config[i] = loadedData[i]
  config = setupConfig(config)
#endregion

## Adafruit Circuitpython ##
#region
import board
import busio
import pulseio
import digitalio
#endregion

#endregion



### Units ###
#region

## Drive Unit ##
#region
# Handles control of the vehicle, primarily through an Xbox controller.
class DriveUnit:

  def setMotor(self, config, log, motor, value):
    value = max(0, min(value, config['maxThrottle']))
    motor.normalized_value = value
    log["driveUnit.motorOutput"] = value

  def setSteering(self, log, steering, value):
    value = max(-1, min(value, 1))
    microseconds = 500 * (value + 3)
    steering.set_servo_pulsewidth(18, microseconds)
    log["driveUnit.steeringOutput"] = value

  def start(self, config, log, local):
    driveUnitProcess = multiprocessing.Process(target = self.main, args = (config, log, local))
    driveUnitProcess.start()

  def main(self, config, log, local):
    from inputs import get_gamepad, UnpluggedError, devices
    from time import sleep

    import adafruit_mcp4725
    i2c = busio.I2C(board.SCL, board.SDA)
    motor = adafruit_mcp4725.MCP4725(i2c)

    # PulseIO is not yet supported on Raspberry Pi
    # (f11384e0 is the last commit with Adafruit Servo code
    # should Pi's be supported in the future.)
    import pigpio
    steering = pigpio.pi()

    reverse = digitalio.DigitalInOut(board.D24)
    reverse.direction = digitalio.Direction.OUTPUT
    reverse.value = True

    boost = False

    currentSteeringSensetivity = 0
    log["driveUnit.reverse"] = False

    while True:
      try:
        leftStickCenter = None
        leftStickPosition = None
        while leftStickCenter == None:
          events = get_gamepad()
          for event in events:
            if event.code == "ABS_X":
              leftStickPosition = event.state
            if event.code == "BTN_SELECT":
              if leftStickPosition != None:
                leftStickCenter = leftStickPosition
                gamepad = devices.gamepads[0]


        while True:
          events = get_gamepad()
          log['driveUnit.controllerConnected'] = True
          for event in events:
            if event.code == "BTN_SELECT":
              leftStickCenter = leftStickPosition

            if event.code == "BTN_WEST":
              reverse.value = not event.state
              log["driveUnit.reverse"] = not reverse.value # The reverse pin/transistor is pulled the wrong way, so this double invert is needed.
            
            if event.code == "BTN_EAST":
              boost = event.state
              log["driveUnit.boost"] = boost

            if event.code == "ABS_X":
              leftStickPosition = event.state
              steeringInput = event.state - leftStickCenter
              log["driveUnit.steeringInput"] = steeringInput
              steeringNormalized = steeringInput / 16384
              speed = speedUnit.getSpeed(config, speedUnitLocal)
              if speed > 10 and config['speedSteeringSensitivity']: # Ajust steering sensetivity/range based on speed.
                if speed < currentSteeringSensetivity:
                  if -config['steeringDeadzone'] < steeringNormalized < config['steeringDeadzone']:
                    steeringNormalized = steeringNormalized / (speed / 10) # Adjust steering sensitivity based on speed.
                    currentSteeringSensetivity = speed
                else:
                  steeringNormalized = steeringNormalized / (speed / 10) # Adjust steering sensitivity based on speed.
                  currentSteeringSensetivity = speed
              steeringNormalized = steeringNormalized * config['steeringSensitivity']
              
              if -config['steeringDeadzone'] < steeringNormalized < config['steeringDeadzone']:
                steeringNormalized = 0
              elif steeringNormalized < 0:
                steeringNormalized += config['steeringDeadzone']
              elif steeringNormalized > 0:
                steeringNormalized -= config['steeringDeadzone']

              self.setSteering(log, steering, steeringNormalized)

            elif event.code == "ABS_RZ":
              throttleInput = event.state
              log["driveUnit.throttleInput"] = throttleInput
              throttleNormalized = ((throttleInput * (0.76 - 0.18)) / 1024) + 0.18 # Motor activates at ~0.24
              if throttleNormalized > 0.2 and boost:
                throttleNormalized = 1
              self.setMotor(config, log, motor, throttleNormalized)
      except Exception as exception:
        log["exceptions"].append(str(exception))
        if type(exception) == UnpluggedError:
          log['driveUnit.controllerConnected'] = False
        motor.normalized_value = 0
        reverse.value = 0

#endregion

## Speed Unit ##
#region
# Measures the speed of the vehicle.
class SpeedUnit:

  def start(self, config, log, local):
    speedUnitProcess = multiprocessing.Process(target = self.main, args = (config, log, local))
    speedUnitProcess.start()

  def main(self, config, log, local):
    from time import time

    breakBeam = digitalio.DigitalInOut(board.D22)
    breakBeam.direction = digitalio.Direction.INPUT
    breakBeam.pull = digitalio.Pull.UP

    local.ticks = 0
    local.recentTicks = []

    while True:
      try:
        while True:
          end = time() + config['speedMeasurementDuration']
          currentBeamState = 0
          ticks = 0

          while time() < end:
            if breakBeam.value != currentBeamState:
              currentBeamState = breakBeam.value
              if currentBeamState == 1:
                ticks += 1

          local.ticks = ticks

          recentTicks = local.recentTicks
          if len(recentTicks) >= config['speedAveragingHistory']:
            del recentTicks[-1]
          recentTicks.insert(0, ticks)
          local.recentTicks = recentTicks

      except Exception as exception:
        log["exceptions"].append(str(exception))

  def getSpeed(self, config, local, SI=False): # SI will return in metres/second.
    if len(local.recentTicks) < 1:
      return 0
    recentTicks = local.recentTicks.copy()
    for i, x in enumerate(recentTicks):
      recentTicks[i] = x * (1 / len(recentTicks)) * (len(recentTicks) - i)
    averageTicks = sum(recentTicks)/len(recentTicks)
    rotations = averageTicks / 5
    distance = rotations * config['wheelCircumference']
    mmS = distance * (1 / config['speedMeasurementDuration'])
    if mmS < 315:
      return 0
    if SI:
      return mmS * 0.001

    return mmS * 0.0036

#endregion

## Lidar Unit
#region
# Scans the environment with the Lidar.
class LidarUnit:

  def start(self, config, log, local):
    lidarUnitProcess = multiprocessing.Process(target = self.main, args = (config, log, local))
    lidarUnitProcess.start()

  def main(self, config, log, local):
    from adafruit_rplidar import RPLidar

    from math import cos, sin, radians

    while True:
      try:
        lidar = RPLidar(None, config['lidarPort'])
        lidar.set_pwm(config['lidarSpeed'])

        try: # Rear LIDAR failure will not impact main LIDAR
          import adafruit_tfmini
          import serial
          uart = serial.Serial("/dev/ttyS0", timeout=1)
          rearLidar = adafruit_tfmini.TFmini(uart)
          rearLidar.mode = adafruit_tfmini.MODE_SHORT
        except Exception as exception:
          log["exceptions"].append(str(exception))
        while True:
          for scan in lidar.iter_scans():
            local.scan = scan
            try:
              rearScan = (rearLidar.distance - config['rearLidarOverhang'], rearLidar.strength, rearLidar.mode)
              if rearScan[0] <= 0:
                rearScan = (None, rearScan.strength, rearScan.mode)
              local.rearScan = rearScan
            except Exception as exception:
              log["exceptions"].append(str(exception))
      except Exception as exception:
        log["exceptions"].append(str(exception))
        if type(exception) == KeyboardInterrupt: # This might not work because it runs it a separate process.
          lidar.stop()
          lidar.disconnect()

  def getLidar(self, config, local, flattened=False):
    if flattened:
      flattenedScan = []
      for (quality, angle, distance) in local.scan:
        flattenedDistance = distance * cos(radians(config['lidarAngle'] * cos(radians(angle))))
        flattenedScan.append((quality, angle, flattenedDistance))
      return flattenedScan

    return local.scan
  
  def getRearLidar(self, config, local):
    return lidarUnitLocal.rearScan

#endregion

## Log Unit ##
#region
# Records and transmits extensive log data back to the Fantail Go database/server.
class LogUnit:

  def start(self, config, log):
    logUnitProcess = multiprocessing.Process(target = self.main, args = (config, log))
    logUnitProcess.start()

  def main(self, config, log):
    import socket
    from datetime import datetime

    while True:
      try:
        while True:
          # Add config to log here.
          logOutput = {}
          logOutput["@timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
          logOutput["@metadata"] = {
            "beat":"fantail-primary"
          }

          logOutput["config"] = config.copy()
          logOutput.update(log.copy()) # Add all the current inline log values to the output.
          try:
            logOutput["speedUnit.speed"] = speedUnit.getSpeed(config, speedUnitLocal)
          except Exception:
            pass
          try:
            logOutput["lidarUnit.scan"] = lidarUnit.getLidar(config, lidarUnitLocal)
            logOutput["lidarUnit.rearScan"] = lidarUnit.getRearLidar(config, lidarUnitLocal)
          except Exception:
            pass
          try:
            logOutput["lidarUnit.rearScan"] = lidarUnit.getRearLidar(config, lidarUnitLocal)
          except Exception:
            pass

          tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          serverAddress = (config["logServer"], config["logPort"])
          tcpSocket.connect(serverAddress)
          message = json.dumps(logOutput) + "\n"
          tcpSocket.sendall(bytes(message, 'UTF-8'))
          tcpSocket.close()
      except Exception as exception:
        # Well... crap
        print(exception)

#endregion

## Data Unit ##
#region
# Manages data transfers between the onboard computers.
class DataUnit:

  def start(self, config, log, local, dataQueue):
    dataUnitProcess = multiprocessing.Process(target = self.main, args = (config, log, local, dataQueue))
    dataUnitProcess.start()

  def main(self, config, log, local, dataQueue):
    while True:
      try:
        asyncio.get_event_loop().run_until_complete(self.server(config, dataQueue))

      except Exception as exception:
        log["exceptions"].append(str(exception))

  async def server(self, config, dataQueue):
    import websockets
    async with websockets.connect("ws://{}:{}".format(config['secondaryComputerAddress'], config['dataPort'])) as websocket:
      while True:
        if len(dataQueue) > 0:
          await websocket.send(json.dumps(dataQueue.copy()))
          dataQueue.clear()
        #receivedData = await websocket.recv()
        # As there is currently no data send to this Pi, don't bother receiving any.

  def sendData(self, prefix, data, dataQueue):
    dataQueue[prefix] = json.dumps(data)

#endregion

## Dashboard Unit ##
#region
# Packages data to be sent to the dashboard.
class DashboardUnit:

  def start(self, config, log, local, dataQueue):
    dashboardUnitProcess = multiprocessing.Process(target = self.main, args = (config, log, local, dataQueue))
    dashboardUnitProcess.start()

  def main(self, config, log, local, dataQueue):
    while True:
      try:
        while True:
          data = {}
          data['infoItems'] = []

          try:
            data['speed'] = speedUnit.getSpeed(config, speedUnitLocal)
          except Exception:
            pass

          try:
            data['controller'] = log['driveUnit.controllerConnected']
          except Exception:
            pass

          try:
            if log['driveUnit.reverse']:
              data['mode'] = 2
            else:
              data['mode'] = 1
          except Exception:
            pass

          try:
            data['lidarScan'] = lidarUnit.getLidar(config, lidarUnitLocal, flattened=True)
          except Exception:
            pass
          
          try:
            data["rearLidarScan"] = lidarUnit.getRearLidar(config, lidarUnitLocal)
            if log['driveUnit.reverse']:
              data['infoItems'].append({
                "icon": "info",
                "title": "{}cm Reversing Space".format(data["rearLidarScan"])
              })
          except Exception:
            pass

          dataUnit.sendData("dash", data, dataQueue)

      except Exception as exception:
        log["exceptions"].append(str(exception))

#endregion

#endregion

### Control Code ###
#region

## Speed Unit ##
#region
speedUnitLocal = manager.Namespace()
speedUnit = SpeedUnit()
speedUnit.start(config, log, speedUnitLocal)
#endregion

## Drive Unit ##
#region
driveUnitLocal = manager.Namespace()
driveUnit = DriveUnit()
driveUnit.start(config, log, driveUnitLocal)
#endregion

## Lidar Unit ##
#region
lidarUnitLocal = manager.Namespace()
lidarUnit = LidarUnit()
lidarUnit.start(config, log, lidarUnitLocal)
#endregion

## Log Unit ##
#region
logUnit = LogUnit()
logUnit.start(config, log)
#endregion

## Data Unit ##
#region
import asyncio
dataUnitLocal = manager.Namespace()
dataUnitQueue = manager.dict()
dataUnit = DataUnit()
dataUnit.start(config, log, dataUnitLocal, dataUnitQueue)
#endregion

## Dashboard Unit ##
#region
dashboardUnitLocal = manager.Namespace()
dashboardUnit = DashboardUnit()
dashboardUnit.start(config, log, dashboardUnitLocal, dataUnitQueue)
#endregion

# Keep the main thread alive.
while True:
  pass

#endregion