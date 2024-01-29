'''
Ursa Ursic, updated: 29.1.2024

This scipt provides different useful functions for 'Run_VoltageControl.ipynb', mostly voltage profiles for tweezers. 
'''

import time
import sys
import glob
import serial
import numpy as np


t_signal_start = 2 #s

def box(t_on: int, voltage_ampl: int) -> list:
    pass


def multi_box(t_on: int, t_off: int, N_pulses: int, voltage_ampl: int, tip_idx: int, serial: object)-> list:
    sc = serial

    dT = 0.05 # Approximate time resolution (loop time)
    measurements = []
    recorded_time = []
    set_voltage = []

    period = t_on + t_off
    t_start = time.time()
    timer_loop_time = time.time()


    t_recording_stop = t_signal_start + N_pulses*period + 3
    while time.time() < t_start + t_recording_stop:
        t = time.time() - t_start
        recorded_time.append(t)
        if 0 <= t%period - t_signal_start <= t_on and t < t_signal_start + N_pulses*period:
            voltage = voltage_ampl
        else:
            voltage = 0

        set_voltage.append(voltage)

        # Send control voltage to Arduino - Vin
        a = sc.send_string(f"!SI {tip_idx} " + str(voltage), wait_for_answer=True)
        VI = int(a.split(' ')[2])
        
        # Read the voltage measurement - Vsense
        a = sc.send_string(f'?SS {tip_idx}', wait_for_answer=True)
        VS = int(a.split(' ')[1])
        t = time.time() - t_start

        measurements.append([t, VI, VS])
        while time.time() < timer_loop_time + dT:
            time.sleep(0.0001)
        timer_loop_time = time.time()

    print('Done')
    return recorded_time, set_voltage, measurements


def multi_box_ampl_variation(t_on: int, t_off: int, N_pulses: int, voltage_ampl: list[int], tip_idx: int, serial: object)-> list:
    sc = serial

    dT = 0.05 # Approximate time resolution (loop time)
    measurements = []
    recorded_time = []
    set_voltage = []

    period = t_on + t_off
    t_start = time.time()
    timer_loop_time = time.time()

    # if only V_min and V_max are given, linearly interpolate
    if len(voltage_ampl) == 2:
        voltage_ampl_sequence = [voltage_ampl[0] + i*(voltage_ampl[1]-voltage_ampl[0])//(N_pulses-1) for i in range(N_pulses)]
        voltage_ampl = voltage_ampl_sequence
        print(voltage_ampl_sequence)
    
    # if voltage is given as a lits, but too short, repeat pulses with the last voltage amplitude
    elif len(voltage_ampl) < N_pulses:
        for i in range(N_pulses- len(voltage_ampl)):
            voltage_ampl.append(voltage_ampl[-1])

    t_recording_stop = t_signal_start + N_pulses*period + 3
    while time.time() < t_start + t_recording_stop:
        t = time.time() - t_start
        recorded_time.append(t)
        if 0 <= t%period - t_signal_start <= t_on and t < t_signal_start + N_pulses*period:
            cycle = int((t-t_signal_start)//period)
            voltage = voltage_ampl[cycle]
        else:
            voltage = 0

        set_voltage.append(voltage)

        # Send control voltage to Arduino - Vin
        a = sc.send_string(f"!SI {tip_idx} " + str(voltage), wait_for_answer=True)
        VI = int(a.split(' ')[2])
        
        # Read the voltage measurement - Vsense
        a = sc.send_string(f'?SS {tip_idx}', wait_for_answer=True)
        VS = int(a.split(' ')[1])
        t = time.time() - t_start

        measurements.append([t, VI, VS])
        while time.time() < timer_loop_time + dT:
            time.sleep(0.0001)
        timer_loop_time = time.time()

    print('Done')
    return recorded_time, set_voltage, measurements


def multi_box_t_on_variation(t_on: list[int], t_off: int, N_pulses: int, voltage_ampl: int, tip_idx: int, serial: object)-> list:
    sc = serial

    dT = 0.05 # Approximate time resolution (loop time)
    measurements = []
    recorded_time = []
    set_voltage = []

    t_start = time.time()
    timer_loop_time = time.time()

    # if only V_min and V_max are given, linearly interpolate
    if len(t_on) == 2:
        t_on_sequence = [voltage_ampl[0] + i*(voltage_ampl[1]-voltage_ampl[0])//(N_pulses-1) for i in range(N_pulses)]
        t_on = t_on_sequence
    
    # if voltage is given as a lits, but too short, repeat pulses with the last voltage amplitude
    elif len(t_on) < N_pulses:
        for i in range(N_pulses- len(t_on)):
            t_on.append(t_on[-1])

    t_recording_stop = t_signal_start + sum(t_on) + N_pulses*t_off + 3
    while time.time() < t_start + t_recording_stop:
        t = time.time() - t_start
        recorded_time.append(t)

        for t in np.linspace(0, 10, 20):
            cycle = sum([t - t_signal_start > sum(t_on[:i]) + i*t_off for i in range(N_pulses)])-1
            if sum(t_on[:cycle]) + cycle*t_off < t - t_signal_start < sum(t_on[:cycle+1]) + cycle*t_off:
                voltage = voltage_ampl
            else: 
                voltage = 0

        set_voltage.append(voltage)

        # Send control voltage to Arduino - Vin
        a = sc.send_string(f"!SI {tip_idx} " + str(voltage), wait_for_answer=True)
        VI = int(a.split(' ')[2])
        
        # Read the voltage measurement - Vsense
        a = sc.send_string(f'?SS {tip_idx}', wait_for_answer=True)
        VS = int(a.split(' ')[1])
        t = time.time() - t_start

        measurements.append([t, VI, VS])
        while time.time() < timer_loop_time + dT:
            time.sleep(0.0001)
        timer_loop_time = time.time()

    print('Done')
    return recorded_time, set_voltage, measurements




def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
