"""
	Module for voltage control 
	utilizing the serial connection and providing python interface to the micro 
	controller (Arduino) commands.

	By Erik Plesko 28.10.22

	V0 - Basic functionality


"""


import logging
import time


import serial_connection


class VoltageControl:
	def __init__(self,
				 port='COM1',
				 baud_rate=19200,
				 is_simulated=False
				 ) -> None:
		self.port = port
		self.baud_rate = baud_rate
		self.is_simulated = is_simulated	# the Arduino is simulated. no connection will be made and the object can be used for testing.

		
		if not is_simulated:
			self.serial_connection = serial_connection.serialConnection(port=self.port, baud_rate=self.baud_rate)

		logging.info(f'VoltageControl init done. is_simulated = {self.is_simulated}')


	def close_serial(self):
		self.serial_connection.serial.close()