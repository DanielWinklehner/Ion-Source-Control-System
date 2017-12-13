import serial
import time

import numpy as np

from devices.serial_com import fast_read

class Pico():
    def __init__(self, port):

        self._terminate = False

        self._init_prgm = [
                '*RST', 'FORM:ELEM READ', 'NPLC .01', # 'TRIG:COUN 10', 'TRAC:POIN 10', 
                #'TRAC:FEED SENS', 'TRAC:FEED:CONT NEXT', 'NPLC .01', 
                'SYST:ZCH OFF'
        ]
        
        self._run_prgm = [
        'READ?', 'r'
        #'TRAC:FEED:CONT NEXT', 'STAT:MEAS:ENAB 512', '*SRE 1', #'*OPC?', 'r', 
        #'TRAC:CLE', 'INIT', 'CALC3:FORM MEAN', 'CALC3:DATA?', 'r'
        ]

        self._s = serial.Serial(port, 57600)

        self._s.reset_input_buffer()
        self._s.reset_output_buffer()

        self.current_value = -1.

    def run(self):

        for cmd in self._init_prgm:
            #print cmd
            self._s.write(cmd + '\r')

        while not self._terminate:
            for cmd in self._run_prgm:
                #print cmd
                if cmd != 'r':
                    self._s.write(cmd + '\r')
                else:
                    resp = fast_read(self._s)#.split(',')
                    #print resp
                    self.current_value = float(resp)

    def terminate(self):
        self._terminate = True
