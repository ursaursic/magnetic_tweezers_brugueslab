import logging
import time
import serial


class serialConnection:
	def __init__(self, 
				 port,
				 baud_rate=9600,
				 string_terminator = '\n'
				) -> None:
		self.port = port
		self.baud_rate = baud_rate
		self.string_terminator = string_terminator 

		self.serial = serial.Serial(self.port, self.baud_rate, timeout=0.1)
		time.sleep(3)
		logging.info(f'Serial opened on port {self.port} with baud rate {self.baud_rate}')

		self.buf = bytearray()

	def send_string(self, string_to_send, wait_for_answer=False):

		string_to_send += self.string_terminator
		encoded_string = str.encode(string_to_send)

		logging.debug(f'In send_string(): Encoded string: {encoded_string}')

		self.serial.write(encoded_string)
		
		if not wait_for_answer:
			return None
		else:
			# time.sleep(1)
			# TODO: Add a check if the answer is not an empty string and thing about other possible edge cases
			# TODO: for example if the communication tries to happen to fast, and add a wait for the answer - so wait until a non-emply string is available (or some longer timeout)
			
			
			answer_recieved = False
			while not answer_recieved:
				if self.serial.in_waiting > 0:
					answer = self.readline()
					answer_recieved = True
				
			
			logging.debug(f'In send_string(): Raw answer: {answer} type: {type(answer)}')
			
			answer_decoded = answer.decode().strip()
			logging.debug(f'Answer is: {answer}')
			logging.debug(f'Answer decoded and stripped: "{answer_decoded}"')
			
			return answer_decoded

	def readline(self):
		# print('ReadLine.readline() call. self.buf:', self.buf, self.buf.decode())
		i = self.buf.find(b"\n")
		# print('i =', i)
		if i >= 0:
			r = self.buf[:i+1]
			self.buf = self.buf[i+1:]
			return r
		while True:
			i = max(1, min(2048, self.serial.in_waiting))

			data = self.serial.read(i)
			if len(data) <= 0:
				return ''
			
			i = data.find(b"\n")
			if i >= 0:
				r = self.buf + data[:i+1]
				self.buf[0:] = data[i+1:]
				return r
			else:
				self.buf.extend(data)
	
	def readline_normal(self):
		print('using the "normal" readline')
		return self.serial.readline()
		"""Left of: cista jajca. even the normal readline seem not to work. the problems seems the same.
		next steps: 2 things:
		- continue working with flushing the buffer - nasty temp workaround
		- go back to basics and try the simple examples of readline usage and try what happens if you give the same imput. (also maybe modify the arduino answers
		to see where the bahaviour comes from. my code or somehwere else.
		
		Tested in the lab on the injectman and no such problem could be found."""
	

	