import serial
import time

import numpy as np

from devices.serial_com import fast_read



class Pico():
    def __init__(self, port):
        self._init_prgm = [
                '*RST', 'FORM:ELEM READ', 'TRIG:COUN 100', 'TRAC:POIN 100', 
                'TRAC:FEED SENS', 'TRAC:FEED:CONT NEXT', 'SYST:ZCH OFF'
        ]
        
        self._run_prgm = [
        #'TRAC:FEED:CONT NEXT', 'STAT:MEAS:ENAB 512', '*SRE 1', #'*OPC?', 'r', 
        'TRAC:CLE', 'INIT','CALC3:FORM MEAN', 'CALC3:DATA?', 'r'
        ]

        self._s = serial.Serial(port, 57600)

        self._s.reset_input_buffer()
        self._s.reset_output_buffer()

        self.current_value = -1.

    def run(self):

        for cmd in self._init_prgm:
            #print cmd
            self._s.write(cmd + '\r')

        while True:
            for cmd in self._run_prgm:
                print cmd
                if cmd != 'r':
                    self._s.write(cmd + '\r')
                else:
                    resp = fast_read(self._s)#.split(',')
                    print resp
                    #data = [float(msg[:-1]) for msg in resp if msg[-1] == 'A']
                    #if len(data) > 0:
                    #    self.current_value = np.mean(data)

