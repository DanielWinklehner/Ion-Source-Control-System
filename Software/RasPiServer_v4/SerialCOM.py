from __future__ import division

import time
import serial
import ftd2xx

class COM(object):
    def __init__(self, id, port, timeout, baud_rate):
        self._id = id
        self._port = port
        self._timeout = timeout
        self._baud_rate = baud_rate

class FTDICOM(COM):
    def __init__(self, serial_number, port, timeout=1.0, baud_rate=9600):
        COM.__init__(self, serial_number, port, timeout, baudrate)
        self._dev = ftd2xx.open(self._port)

    @property
    def serial_number(self):
        # if this fails, the device has been unplugged!
        return self._dev.eeRead().SerialNumber

    def send_message(self, message):
        pass

class SerialCOM(COM):
    def __init__(self, arduino_id, port_name, timeout=1.0, baud_rate=115200):
        """Summary

        Args:
            arduino_id (TYPE): Description
        """
        COM.__init__(self, arduino_id, port_name, timeout, baud_rate)
        self._ser = serial.Serial(self._port, baudrate=self._baud_rate, timeout=self._timeout)

        time.sleep(1.0)

    def get_arduino_id(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self._id

    def get_port(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self._port

    def send_message(self, message):
        """Summary

        Args:
            message (TYPE): Description

        Returns:
            TYPE: Description
        """

        try:

            self._ser.reset_input_buffer()
            self._ser.reset_output_buffer()

            self._ser.write(message[0])

            # Our own 'readline()' function
            response = b''

	    if message[1]:

                start_time = time.time()
                while not (time.time() - start_time) > self._timeout:
                    resp = self._ser.read(1)
                    if resp:
                        response += bytes(resp)
                        if resp in [b'\n', b'\r']:
                            break
                        elif resp == b';':
                            # Handle MFC Readout (read in two more bytes for checksum and break)
                            response += bytes(self._ser.read(2))
                            break
                else: # thanks, python
                    response += b'TIMEOUT'

            else:
                response += b"Didn't wait :P"

            if len(response) != 0:
                return response

        except Exception as e:
            raise Exception("Something's wrong! Exception in SerialCOM: {}".format(e))

        return ""


if __name__ == "__main__":

    pass
