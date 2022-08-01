import logging

import time


import serial_connection



class InjectMan:
	def __init__(self,
				 port='COM1',
				 baud_rate=19200,
				 is_simulated=False,
				 ) -> None:
		""" Documentation of the class missing"""
		# TODO: write the documentation.
		self.port = port
		self.baud_rate = baud_rate
		self.is_simulated = is_simulated	# the InjectMan is simulated. no connection will be made and the object can be used for testing.
		
		logging.info(f'InjectMan initialization...')
		
		if not is_simulated:
			self.serial_connection = serial_connection.serialConnection(port=self.port, baud_rate=self.baud_rate)

		logging.info(f'InjectMan init done. is_simulated = {self.is_simulated}')
	

	def close_serial(self):
		self.serial_connection.serial.close()

	# ----------------------------------------------------------------------------------------------------------------
	# Functions for commands of InjectMan. Their docstring include command description from the
	# Cell Technology PC Control manual:

	def query_program_version(self):
		"""
		Parameter: none
		Answer: A001 version number
		"""
		command_code = 1
		return self.call_command_code(command_code)

	def reset_motor_control(self):
		"""
		Motor control is reset to default. This
		means that all motor movement is
		stopped and the current coordinates are
		set to 0,0,0. Each drive can have an
		offset of up to 10 μm.
		This command can be carried out at any
		time.

		Parameter: none
		"""
		command_code = 3
		return self.call_command_code(command_code)

	def switch_to_remote_control(self):
		"""
		All current movements are stopped and
		local operation via joystick and keypad is
		enabled. The feedback occurs as soon
		as all motors have stopped and the
		positioning via joystick can be carried
		out.
		This command can be carried out at any
		time.
		
		Parameter: none
		"""
		command_code = 4
		return self.call_command_code(command_code)

	def switch_to_manual_control(self):
		"""
		All current movements are stopped and
		local operation via joystick and keypad is
		enabled. The feedback occurs as soon
		as all motors have come stopped and
		the positioning via joystick can be
		carried out.
		This command can be carried out at any
		time.
		
		Parameter: none
		"""
		command_code = 5
		return self.call_command_code(command_code)

	def GOTO_position_in_micrometers(self, px, py, pz, vx, vy, vz):
		"""
		The manipulator moves to the preset
		position at the preset speed on all 3
		axes. If no movement shall take place
		on one axix, the speed value 0 is
		transmitted. The feedback occurs as
		soon as all motors have stopped and the
		final position is reached or the limit
		switch has responded. The answer will
		include the position of the limit switches.
		If positioning was successful, the value
		will be 0. All values are given in
		micrometers.
		This command can only be carried out if
		remote control is active.

		Parameter: px py pz vx vy vz
		Meaning of the answer: All motors have stopped.
		"""
		command_code = 7
		# TODO: implement default velocity values ----> THink about a high level move functions with the blocking/non blocking parameter, handling the defaults as well.
		# and leaving this just as a python wrapper.
		# TODO: implement checking the valid range of parameters - make a special function to do that and can be used across the class.
		# TODO: implement passing of the parameters 
		raise NotImplementedError('passing of the parameters not yet implemented.')
		return self.call_command_code(command_code)

	def STOP(self):
		"""The current movement will be stopped.
		The feedback occurs as soon as all
		motors are at a standstill.
		This command can only be carried out if
		remote control is active.
		"""
		command_code = 8
		return self.call_command_code(command_code)

	def position_query_in_micrometers(self):
		"""Regardless of the ongoing movement,
		the current position on all three axes as
		well as the position of the 6 limit
		switches will be reported in
		micrometers. An ongoing movement will
		not be stopped.
		This command can be carried out at any
		time.

		Meaning of the answer: Position reply in micrometers with
		limit switches
		
		Additional comment about limit switches: It looks like the data is provided as a byte, where every bit
		holds the info about it's limit switch pressed. The dec values you get if you move the tip to the limits:
		left / right -> 1 / 2
		back / front -> 4 / 8
		up / down -> 16 / 32
		"""
		command_code = 10
		answer_string = self.call_command_code(command_code)
		position, limit_switches = self._parse_position_query(answer_string)
		return position, limit_switches



	def GOTO_position_in_micrometers_NB(self, px, py, pz, vx, vy, vz):
		"""Non Blocking (NB)
		GOTO position in micrometers
		without "complete" message

		The manipulator moves to the preset
		position at the preset speed o all 3 axes.
		If no movement shall take place on one
		axis, the speed value 0 is transmitted.
		The feedback occurs as soon as the
		command has been evaluated
		completely and the next one is ready to
		be sent out. The final position, however,
		has not been reached yet. All values in
		micrometers.
		This command can only be carried out if
		remote control is active.

		Parameter: px py pz vx vy vz
		Meaning of the answer: Ready for next command.
		"""

		command_code = 12
		# TODO: implement default velocity values
		# TODO: implement checking the valid range of parameters - make a special function to do that and can be used across the class.
		# TODO: implement passing of the parameters 
		raise NotImplementedError('passing of the parameters not yet implemented.')

	def trigger_short_acoustic_signals(self, n):
		"""The number of short (100 ms) acoustic
		signals specified in the parameter is
		issued.
		
		Parameter: Number of acoustic signals
		"""
		command_code = 14
		# TODO: implement passing of the parameters
		raise NotImplementedError('passing of the parameters not yet implemented.')
		return self.call_command_code(command_code)

	def trigger_long_acoustic_signals(self, n):
		"""The number of long (1 second) acoustic
		signals specified in the parameter is
		issued.
		
		Parameter: Number of acoustic signals
		"""
		command_code = 15
		# TODO: implement passing of the parameters
		raise NotImplementedError('passing of the parameters not yet implemented.')
		return self.call_command_code(command_code)


		


	# ---------------------------------------------------------


	# Helpers:
	def _parse_position_query(self, answer_string):
		"""
		Parse position query answer to 2 lists.

		"""
		raw_list = answer_string.split(' ')
		answer_code = raw_list.pop(0)
		
		if not answer_code[0] in 'aA':
			raise Exception(f"""Expecting the first character of the answer_string to be 'a' or 'A'. 
							\rOtherwise this is not a complete answer string. answer_string I got: '{answer_string}'""")

		# We expect only numeric parameters in the list
		raw_list = [int(x) for x in raw_list]
		position = raw_list[:3]
		limit_switches = raw_list[3:]

		return position, limit_switches

	def _validate_parameters_range(self, parameters_list, lim_min, lim_max):
		"""
		Validate parameters to be in the valid range. 
		
		Limit is the last valid value. The first parameter that is outside the limits raises ValueError.

		Returns:
			parameters_list - if all the parameters are within the specified range.
		"""
		for p in parameters_list:
			if lim_min <= p <= lim_max:
				pass
			else:
				raise ValueError(f"""Parameter {p} is outside of valid range [{lim_min}, {lim_max}].
								 \r Parameter was in the list of {parameters_list}.""")
		return parameters_list

	def _movement_parameters_to_string(self, px, py, pz, vx, vy, vz):
		"""
		Write movement parameters to a string seperated with spaces.
		"""
		# TODO:

	



	# ---------------------------------------------------------


		
	# custom command - with just string C001 (or int number: 1)
	def call_command_code(self, command_name):
		"""
		Call a command by its code using int or str.

		Args:
			command_name (int or str): When of type int the message with that number is used.
				When type str the exact string will be used as a command. 
				Examples: 
					4 -> 'C004'
					'C001 5 70' -> 'C001 5 70'
		"""
		if type(command_name) == str:
			pass
		elif type(command_name) == int:
			if 0 < command_name < 1000:
				command_name = f'C{command_name:03}'
			else:
				logging.warning(f'Value {command_name} out of bounds for (0, 1000).')

		result = self.send_command_serial(command_name)
		logging.debug(f'in call_command_code:\n\tcommand: {command_name}\n\t anwser: {result}')
		return result

	# send command to serial (all other calls use this to send )
		# if the object is simulated, call the simulate response function.
	def send_command_serial(self, command_str, wait_for_answer=True):
		result = None
		if self.is_simulated:
			logging.debug(f'in send_command_serial(): sending "{command_str}" to simulated.')
			result = self.simulate_serial_response(command_str)
		else:
			# raise NotImplementedError('Currently only simulated usage is supported.')
			logging.debug(f'in send_command_serial(): sending "{command_str}" to serial on port {self.port}.')
			
			# TODO: think about wait_for_answer usage. are there cases where it would need to be managed differently?
			result = self.serial_connection.send_string(command_str, wait_for_answer=wait_for_answer)
			
		return result
		
	def simulate_serial_response(self, command_str):
		"""Simulate serial response for debugging purposes.
		
		Function is not simulating InjectMan behavior, just echoes the command.
		"""
		if command_str[0] in 'cC':
			if command_str[1:] == '010':
				# Used to test parsing of the answer - first three values are x,y,z the last one is the limit switches state.
				return 'A010 595 0 778 0'
			else:
				return f'A{command_str[1:]}'
		else:
			return f'ERR:{command_str}'

	

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	
	im = InjectMan(is_simulated=True)
	
	im.call_command_code(5)
	im.call_command_code('C005')
	im.call_command_code('4C005')
	
	a = im.position_query_in_micrometers()
	print(a)
	
	# --------------------------------------------------
	print(30*'-')
	
	p, ls = im.position_query_in_micrometers()
	print(p, ls)
	
	
	
	# --------------------------------------------------
	print(30*'-')
	
	p = im._validate_parameters_range([1, 2, 30], -5, 5)
	print('validated parameters:', p)
