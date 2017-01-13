from __future__ import division

import time
import serial
import sys
import glob
import subprocess
import math
import os

import Messages

from DummySerial import DummySerial


class SerialCOM(object):

    def __init__(self, arduino_id, port_name, timeout=1.):
        """Summary
        
        Args:
            arduino_id (TYPE): Description
        """
        self._arduino_id = arduino_id
        self._port_name = port_name

        self._baudrate = 115200
        self._timeout = timeout
        # self._ser = serial.Serial(port_name, baudrate=self._baudrate, timeout=self._timeout)
        self._ser = DummySerial(port_name, baudrate=self._baudrate)
        

        
    def get_arduino_id(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._arduino_id

    def get_port(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._port_name

    
    
    

    def send_message(self, message):
        """Summary
        
        Args:
            message (TYPE): Description
        
        Returns:
            TYPE: Description
        """

        for i in range(2):
            self._ser.write(message)

            response = self._ser.readline()

            # print "I sent a message", message, "and received", response

            if len(response) != 0:
                # print "And now I am returning a response"
                return response

        return ""

    def read_message(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        raise Exception("You're not supposed to use this SerialCOM method.")
        
