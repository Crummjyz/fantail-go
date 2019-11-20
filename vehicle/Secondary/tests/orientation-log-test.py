# Records data from orientation sensors and writes to a CSV file.

import time

import board
import busio

import adafruit_fxos8700
import adafruit_fxas21002c

i2c = busio.I2C(board.SCL, board.SDA)
sensorA = adafruit_fxos8700.FXOS8700(i2c)
sensorB = adafruit_fxas21002c.FXAS21002C(i2c)


with open("orientation-data.csv", "a+") as file:
  while True:
    accel_x, accel_y, accel_z = sensorA.accelerometer
    mag_x, mag_y, mag_z = sensorA.magnetometer
    gyro_x, gyro_y, gyro_z = sensorB.gyroscope
    
    file.write("{}, {}, {}, {}, {}, {}, {}, {}, {}\n".format(accel_x, accel_y, accel_z, mag_x, mag_y, mag_z, gyro_x, gyro_y, gyro_z))
    time.sleep(0.5)
