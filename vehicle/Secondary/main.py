#!/usr/bin/python3

### Setup ###
#region

## Parallelism ##
#region
import multiprocessing
manager = multiprocessing.Manager()
log = manager.dict()
log['exceptions'] = []
#endregion

## Config ##
#region
def setupConfig(config):
  # Set up other config values here.
  return config

import json
config = manager.dict()
with open('/home/pi/Vehicle/Secondary/config.json') as data:
  loadedData = json.load(data)
  for i in loadedData: # Trust me, there's a reason for this madness.
    config[i] = loadedData[i]
  config = setupConfig(config)
#endregion

## Adafruit Circuitpython ##
#region
import board
import busio
#endregion

#endregion



### Units ###
#region

## Temperature Unit ##
#region
class TemperatureUnit:

  def readRawData(self, sensor):
    f = open(sensor, 'r')
    lines = f.readlines()
    f.close()
    return lines

  def start(self, log, local):
    temperatureUnitProcess = multiprocessing.Process(target = self.main, args = (log, local))
    temperatureUnitProcess.start()

  def main(self, log, local):
    import glob
    from time import sleep

    directories = glob.glob("/sys/bus/w1/devices/28*")
    temperatureSensors = []
    local.temperatures = []
    for directory in directories:
      temperatureSensors.append(directory + "/w1_slave")

    while True:
      try:
        while True:
          temperatures = []
          for sensor in temperatureSensors:
            lines = self.readRawData(sensor)
            while lines[0].strip()[-3:] != 'YES':
              sleep(0.2)
              lines = self.readRawData(sensor)
            equalsPosition = lines[1].find('t=')
            if equalsPosition != -1:
              temperatureString = lines[1][equalsPosition+2:]
              temperature = float(temperatureString) / 1000
              temperatures.append(temperature)
          local.temperatures = temperatures
      except Exception as exception:
        log["exceptions"].append(str(exception))

  def getTemperature(self, config, local, sensor="ALL"):
    if sensor == "ALL":
      temperatures = {
        "motor": local.temperatures[config["temperatureSensors"]["motor"]],
        "speedController": local.temperatures[config["temperatureSensors"]["speedController"]],
        "battery1": local.temperatures[config["temperatureSensors"]["battery1"]],
        "battery2": local.temperatures[config["temperatureSensors"]["battery2"]],
        "battery3": local.temperatures[config["temperatureSensors"]["battery3"]],
        "battery4": local.temperatures[config["temperatureSensors"]["battery4"]]
      }
      return temperatures

    return local.temperatures[config["temperatureSensors"][sensor]]

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
            "beat":"fantail-secondary"
          }

          logOutput["config"] = config.copy()
          logOutput.update(log.copy()) # Add all the current inline log values to the output.
          try:
            logOutput["temperatureUnit.temperatures"] = temperatureUnit.getTemperature(config, temperatureUnitLocal)
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
    import websockets

    while True:
      try:
        asyncio.get_event_loop().run_until_complete(websockets.serve(self.server, config['hostAddress'], config['dataPort']))
        asyncio.get_event_loop().run_forever()

      except Exception as exception:
        log["exceptions"].append(str(exception))

  async def server(self, websocket, path):
    while True:
      receivedData = await websocket.recv()
      receivedData = json.loads(receivedData)
      dataUnitLocal.dash = receivedData['dash']

#endregion

## Dashboard Unit ##
#region
# Packages data to be sent to the dashboard.
class DashboardUnit:

  def start(self, config, log, local):
    dashboardUnitProcess = multiprocessing.Process(target = self.main, args = (config, log, local))
    dashboardUnitProcess.start()

  def main(self, config, log, local):
    import websockets

    while True:
      try:
        asyncio.get_event_loop().run_until_complete(websockets.serve(self.server, config['hostAddress'], config['dashCommunicationPort']))
        asyncio.get_event_loop().run_forever()

      except Exception as exception:
        log["exceptions"].append(str(exception))

  async def server(self, websocket, path):
    while True:
      packet = json.loads(dataUnitLocal.dash)
      packet['infoItems'] = []
      try:
        packet['primaryBattery'] = log['batteryUnit.batteryVoltage'] / 5
      except Exception:
        pass
      try:
        packet['secondaryBattery'] = log['batteryUnit.subBatteryVoltage'] / 5
      except Exception:
        pass
      packet = json.dumps(packet)
      await websocket.send(packet)

#endregion

## Battery Unit ##
#region
# Monitors the status of the batteries and high voltage equipment.
class BatteryUnit:

  def start(self, log, local):
    batteryUnitProcess = multiprocessing.Process(target = self.main, args = (log, local))
    batteryUnitProcess.start()

  def main(self, log, local):
    import adafruit_ads1x15.ads1015 as adafruit_ads1015
    from adafruit_ads1x15.analog_in import AnalogIn
    i2c = busio.I2C(board.SCL, board.SDA)
    batteryMonitor = adafruit_ads1015.ADS1015(i2c, address=0x49)

    batteryVoltage = AnalogIn(batteryMonitor, adafruit_ads1015.P0)
    subBatteryVoltage = AnalogIn(batteryMonitor, adafruit_ads1015.P1)

    while True:
      try:
        while True:
          log['batteryUnit.batteryVoltage'] = batteryVoltage.voltage
          log['batteryUnit.subBatteryVoltage'] = subBatteryVoltage.voltage

      except Exception as exception:
        log["exceptions"].append(str(exception))

#endregion

#endregion



### Control Code ###
#region

## Temperature Unit ##
#region
temperatureUnitLocal = manager.Namespace()
temperatureUnit = TemperatureUnit()
temperatureUnit.start(log, temperatureUnitLocal)
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
dashboardUnit.start(config, log, dashboardUnitLocal)
#endregion

## Battery Unit ##
#region
batteryUnitLocal = manager.Namespace()
batteryUnit = BatteryUnit()
batteryUnit.start(log, batteryUnitLocal)
#endregion

# Keep the main thread alive.
while True:
  pass

#endregion