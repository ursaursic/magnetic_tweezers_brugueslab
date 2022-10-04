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
time.sleep(1)

# #############

#
# while True:
#     data = injectMan.readline()
#     while data:
#         print('---->', data)
#         # print(data)
#         data = injectMan.readline()
#
#     # inputString = input('Write motors steps seperated with spaces\n')
#     inputString = input('Write command string (q to quit):\n')
#     if inputString == 'q':
#         break
#     else:
#
#         # array = inputString.split(' ')
#         # angleSteps = [int(c) for c in array]
#
#         # print('Motors steps:', angleSteps)
#         serialSend(inputString, [], injectMan)
#         # print('Steps set.')

N = 20
r = 5000
speed = 7000


# serialSend('C007', [0, 0, 3500, speed, speed, speed], injectMan)
# time.sleep(5)

for i in range(N+1):
    delta = i/N
    x = r*np.sin(2*np.pi*delta)
    y = r*np.cos(2*np.pi*delta) - r
    z = 4700

    serialSend('C010', [], injectMan)
    data = injectMan.readline()
    while data:
        print('---->', data)
        # print(data)
        data = injectMan.readline()


    serialSend('C007', [x, y, z, speed, speed, speed], injectMan)
    # serialSend('C012', [x, y, z, speed, speed, speed], injectMan)
    if i < 1:
        time.sleep(1)
    # else:
    #     time.sleep(0.05)

    data = injectMan.readline()
    while not data:
        print('---->', data)
        # print(data)
        data = injectMan.readline()

print('Ending the program...')
serialSend('C010', [], injectMan)

serialSend('C007', [0, 0, 0, speed, speed, speed], injectMan)

while data:
    print('---->', data)
    # print(data)
    data = injectMan.readline()

serialSend('C005', [], injectMan)
print('Ending the script.')


