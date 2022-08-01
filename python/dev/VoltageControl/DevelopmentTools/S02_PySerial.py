from click import command
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
	print('I will send this string to arduino:')
	# print(stringToSend)
	print(str.encode(stringToSend))
	arduino.write(str.encode(stringToSend))

# Initialize
arduino = arduinoInit(port='COM5')
print('Setup Done!')


arduinoSend('Test', [0, 0], arduino) 


while True:
	data = arduino.readline()
	while data:
		print('A ---->', data)
		# print(data)
		data = arduino.readline()


	inputString = input('Write motors steps seperated with spaces\n')
	if inputString == 'q':
		break
	else:

		array = inputString.split(' ')
		angleSteps = [int(c) for c in array]

		# print('Motors steps:', angleSteps)
		arduinoSend('!VO', angleSteps, arduino) 
		# print('Steps set.')


	



arduinoSend('moveJ', [0, 0], arduino) 


