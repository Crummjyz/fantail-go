# Requirements (Main Raspberry Pi)
## Tasks
- Send log data to phone for transmission
- Recieve log data from Drive Pi
- Send info data to display
- Read temperatures from sensors
- Read accelerometer data
- Send configuration commands to Drive Pi
- Recieve configuration commands from phone
- Send bluetooth connection setup to tablet or phone
- Read battery voltage
- Read current draw/charge rate

## Connections
| Device                  | Method
| ----------------------- | ---------
| Drive Pi                | Ethernet
| Phone                   | USB UART/Bluetooth
| Temperature Sensors/ADC | I<sup>2</sup>C
| Display                 | USB UART/Bluetooth
| Accelerometer           | I<sup>2</sup>C
| Battery Voltage/ADC     | I<sup>2</sup>C
| Battery Current/ADC     | I<sup>2</sup>C