import serial
import time
import numpy as np



def serialSend(command, values, ser):
    ''' Send values to serial.
    '''

    commandStr = command

    stringToSend = commandStr

    if len(values) > 0:
        values = np.array(values)
        values = values.astype(int)

        stringToSend += ' '
        for value in values[:-1]:
            stringToSend += str(value) + ' '
        stringToSend += str(values[-1])

    stringToSend += '\r'

    # Debug prints
    print('I will send this string to serial:')
    # print(stringToSend)
    print(str.encode(stringToSend))
    ser.write(str.encode(stringToSend))





port = 'COM1'
baudrate = 19200

# Open serial port:
injectMan = serial.Serial(port, baudrate, timeout=.1)
time.sleep(2)

print('port opened.')




serialSend('C014 2', [], injectMan)
serialSend('C004', [], injectMan)
serialSend('C003', [], injectMan)


# #############


while True:
    data = injectMan.readline()
    while data:
        print('---->', data)
        # print(data)
        data = injectMan.readline()

    # inputString = input('Write motors steps seperated with spaces\n')
    inputString = input('Write command string (q to quit):\n')
    if inputString == 'q':
        break
    else:

        # array = inputString.split(' ')
        # angleSteps = [int(c) for c in array]

        # print('Motors steps:', angleSteps)
        serialSend(inputString, [], injectMan)
        # print('Steps set.')



serialSend('C005', [], injectMan)
print('Ending the script.')


