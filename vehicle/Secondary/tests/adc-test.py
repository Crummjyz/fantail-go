# Prints voltages from the Analog -> Digital Converter
from time import sleep

import board
import busio
i2c = busio.I2C(board.SCL, board.SDA)

import adafruit_ads1x15.ads1015 as ADS

from adafruit_ads1x15.analog_in import AnalogIn

ads = ADS.ADS1015(i2c)

while True:
    chan = AnalogIn(ads, ADS.P0)
    print(chan.value, chan.voltage)
    sleep(1)
