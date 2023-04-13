
import logging


import serial_connection


logging.basicConfig(level=logging.DEBUG)



sc = serial_connection.serialConnection(port='COM1', baud_rate=19200)


print('flushing...')
for i in range(5):
    print(sc.serial.readline())


sc.send_string('c001')
