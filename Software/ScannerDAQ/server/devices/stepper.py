import serial
import time

from devices.serial_com import fast_read

class Stepper():
    def __init__(self, port, debug=False):

        self._terminate = False

        self._current_value = -1.

    @property
    def current_value(self):
        return self._current_value

    def run(self):
        while not self._terminate:
            pass

    def terminate(self):
        self._terminate = True
