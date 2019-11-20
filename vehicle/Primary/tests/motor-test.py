import board
import busio
import adafruit_mcp4725
i2c = busio.I2C(board.SCL, board.SDA)
dac = adafruit_mcp4725.MCP4725(i2c)

while True:
  value = float(input("Enter motor signal [0 to 1]:"))
  dac.normalized_value = value
