import numpy as np
import cv2
import time
import serial
'''
	test serial communication
	
'''
def saturate(value, valueMin, valueMax, warningOn=False):
	if value < valueMin:
		if warningOn:
			print('Under Saturated in saturate().')
		return valueMin
	elif valueMax < value:
		if warningOn:
			print('Over Saturated in saturate().')
		return valueMax
	else:
		return value


def arduinoInit(port='COM5', baudrate=115200):
	print(f'Opening serial port.')
	arduino = serial.Serial(port, baudrate, timeout=.1)
	time.sleep(2)
	print('Port opened.')
	return arduino



def arduinoSend(command, values, arduino):
	''' Send values to arduino.
	'''

	# if command == 'moveJ':
	# 	commandStr = '!MJ'
	# elif command == 'moveS':
	# 	commandStr = '!MS'
	# elif command == 'moveSBuffer':
	# 	commandStr = '!MSB'
	# elif command == 'printAll':
	# 	commandStr = '!PA'
	# 	values = [values]
	# elif command == 'moveSSetSpeed':
	# 	commandStr = '!MSss'
	# 	values = [values]
	# else:
	# 	print('Unsupported command in function arduinoSend.')
	# 	return -1
	commandStr = command



	values = np.array(values)
	for i in range(len(values)):
		values[i] = saturate(values[i], -9999, 99999, warningOn=True)
	values = values.astype(int)

	stringToSend = commandStr + ' '
	for value in values[:-1]:
		stringToSend += str(value) + ' '
	stringToSend += str(values[-1]) + '\r'
	
	# Debug prints
	# print('I will send this string to arduino:')
	# print(stringToSend)
	print(str.encode(stringToSend))
	arduino.write(str.encode(stringToSend))








# ### - improved readline: ----------------------------------------------------------

class ReadLine:
	def __init__(self, s):
		self.buf = bytearray()
		self.s = s
	
	def readline(self):
		print('ReadLine.readline() call.')
		i = self.buf.find(b"\n")
		print('i =', i)
		if i >= 0:
			r = self.buf[:i+1]
			self.buf = self.buf[i+1:]
			return r
		while True:
			i = max(1, min(2048, self.s.in_waiting))
			print('-- reading data ---', end='')

			data = self.s.read(i)
			if len(data) <= 0:
				return ''
			# print(' ---> read finished ----------  data:')
			# print(len(data), data)
			
			i = data.find(b"\n")
			if i >= 0:
				r = self.buf + data[:i+1]
				self.buf[0:] = data[i+1:]
				return r
			else:
				self.buf.extend(data)
	# def readline(self):
	# 	i = self.buf.find(b"\n")
	# 	if i >= 0:
	# 		r = self.buf[:i+1]
	# 		self.buf = self.buf[i+1:]
	# 		return r
	# 	while True:
	# 		i = max(1, min(2048, self.s.in_waiting))
	# 		data = self.s.read(i)
	# 		i = data.find(b"\n")
	# 		if i >= 0:
	# 			r = self.buf + data[:i+1]
	# 			self.buf[0:] = data[i+1:]
	# 			return r
	# 		else:
	# 			self.buf.extend(data)






# ser = serial.Serial('COM5', 125000)


# Initialize
arduino = arduinoInit(port='COM5')
print('Setup Done!')








rl = ReadLine(arduino)

N = 10

for i in range(N):

	print('------------------------i:', i)

	if i < 2 :
		values = [5000*(0.5*np.sin(2*np.pi*i/50) + 0.5 )]
		arduinoSend('!VO', values, arduino) 

	time.sleep(0.1)


	print(rl.readline())
