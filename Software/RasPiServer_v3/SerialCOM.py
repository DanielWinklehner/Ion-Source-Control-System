from __future__ import division

import time
import serial


class SerialCOM(object):
    def __init__(self, arduino_id, port_name, timeout=1.0, baud_rate=115200):
        """Summary

        Args:
            arduino_id (TYPE): Description
        """
        self._arduino_id = arduino_id
        self._port_name = port_name

        self._baudrate = baud_rate
        self._timeout = timeout
        self._ser = serial.Serial(port_name, baudrate=self._baudrate, timeout=self._timeout)

        time.sleep(1.0)

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
