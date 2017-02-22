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

            self._ser.write(message)
            response = self._ser.readline()

            if len(response) != 0:
                return response

        except serial.SerialException as e:
            raise Exception("Something's wrong! I cannot send any messages!" + str(e))
        except IOError as e2:
            raise Exception("Something's wrong! I cannot send any messages!" + str(e2))
        except Exception as e3:
            raise Exception("Something's wrong! I cannot send any messages!" + str(e3))

        return ""


if __name__ == "__main__":

    pass
