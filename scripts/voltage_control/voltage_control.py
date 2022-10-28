"""
	Module for voltage control 
	utilizing the serial connection and providing python interface to the micro 
	controller (Arduino) commands.

	By Erik Plesko 28.10.22

_______________________________________________________________________
### A copy of the arduino code for which voltage_control is written
	void setup() {
		Serial.begin(19200);

		scmd.addCommand("!V", cmd_set_voltage);            // _ #tip_number [] #voltageIn [mV]   // Set voltage In for a specific tip (it goes out, but the signal goes to V-in on the current generator)
		scmd.addCommand("?V", cmd_get_voltage);            // _ #tip_number []                  // Read the voltage of a specific pin (connected to V-sense)

		scmd.addCommand("!TT", cmd_set_auto_timeout_time);  // _ #autoTimeoutTime
		scmd.addCommand("!TO", cmd_set_auto_timeout_on);    // _ #autoTimeoutOn (0 or 1)
		scmd.addCommand("!VM", cmd_set_voltage_max);        // _ #Vmax (in range 0 to 3000)

		// General:
		scmd.addCommand("!PA", cmd_setPrintAll);            // _ #printAll (0 or 1)
		scmd.addCommand("Test", cmd_test);                  // _ (#a #b #c #d ...)
		scmd.addDefaultHandler(unrecognized);


		// I/O
		pinMode(LED_BUILTIN, OUTPUT);   // Builtin LED

		Serial.println(F("Setup done."));
		Serial.println(F("File: V01_voltageControl.2"));

	}
_______________________________________________________________________


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
			self.serial_connection = serial_connection.serialConnection(port=self.port, baud_rate=self.baud_rate, string_terminator='\r')

		logging.info(f'VoltageControl init done. is_simulated = {self.is_simulated}')

	def close_serial(self):
		self.serial_connection.serial.close()

	# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
	def set_voltage(tip_number, voltage_in):
		pass

	def get_voltage(tip_number):
		pass

	def set_parameters(auto_timeout_time=None, 
					   auto_timeout_on=None,
					   voltage_max=None, 
					   print_all=None):
		pass
	
	# --------------------------------------------------------------------
	# Helpers:

	def call_command_code(self, command_name, *parameters: int):
		"""
		Call a command by its code with parameters using integers 

		Args:
			command_name (str):nd parameters
				added if present.
				Examples: 
					4 -> 'C004'
					4, 10, 123 -> 'C004 10, 123'
					'C001 5 70' -> 'C001 5 70'
					'C001 5 70', 123, 400 -> 'C001 5 70'
			*parameters (int): integers to be added to the string message (separated with spaces)
		"""

		
		# Deal with the parameters:
		parameters = [str(int(x)) for x in parameters]
		
		# Make string of parameters - it is empty if there are no parameters.
		parameters_str = " " if len(parameters) > 0 else ""
		parameters_str += " ".join(parameters)
		
		logging.debug(f'call_command_code(): code: {command_name} parameters_str: {parameters_str}')
		
		# Put it all together
		command_string = f'{command_name}{parameters_str}'
	
		result = self.send_command_serial(command_string)
		logging.debug(f'in call_command_code:\n\tcommand: {command_string}\n\t answer: {result}')
		return result

	def send_command_serial(self, command_str, wait_for_answer=True):
		""" send command to serial (all other calls use this to send )

		if the object is simulated, call the simulate response function.
		"""
		result = None
		if self.is_simulated:
			logging.debug(f'in send_command_serial(): sending "{command_str}" to simulated.')
			result = self.simulate_serial_response(command_str)
		else:
			logging.debug(f'in send_command_serial(): sending "{command_str}" to serial on port {self.port}.')
			
			# TODO: think about wait_for_answer usage. are there cases where it would need to be managed differently?
			result = self.serial_connection.send_string(command_str, wait_for_answer=wait_for_answer)
			
		return result

	def simulate_serial_response(self, command_str):
		"""Simulate serial response for debugging purposes.
		
		Function is not simulating Arduino behavior, just echoes the exact command.
		"""
		return command_str


	# --------------------------------------------------------------------
	# ### High level functions:
	def set_voltage(voltage_1, voltage_2=None, wait_for_completion=True):
		pass
















