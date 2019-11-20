# Prints temperatures read from all sensors connected when the code was started.
"""
# Adafruit CircuitPython Code (Not working)

# Simple demo of printing the temperature from the first found DS18x20 sensor every second.
# Author: Tony DiCola
import time

import board

from adafruit_onewire.bus import OneWireBus
from adafruit_ds18x20 import DS18X20


# Initialize one-wire bus on board pin D5.
ow_bus = OneWireBus(board.D5)

# Scan for sensors and grab the first one found.
ds18 = DS18X20(ow_bus, ow_bus.scan()[0])

# Main loop to print the temperature every second.
while True:
    print('Temperature: {0:0.3f}C'.format(ds18.temperature))
    time.sleep(1.0)
"""

import glob
import time

base_dir = '/sys/bus/w1/devices/'
device_folders = []
globs = glob.glob(base_dir + '28*')
for i in range(len(globs)):
    device_folders.append(globs[i])

device_files = []
for i in range(len(device_folders)):
    device_files.append(device_folders[i] + '/w1_slave')

def read_temp_raw(sensor):
    f = open(device_files[sensor], 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(sensor):
    lines = read_temp_raw(sensor)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(sensor)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        #temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c #, temp_f

while True:
    temps = []
    for i in range(len(device_files)):
        temps.append(read_temp(i))
    print(temps)
    time.sleep(1)

