import time

import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class Pid(QObject):

    _sig_set_value = pyqtSignal(float)

    def __init__(self, channel, target=0.0, coeffs=[1.0, 1.0, 1.0], dt=0.5):
        super().__init__()
        self._target = target
        self._channel = channel
        self._coeffs = coeffs
        self._dt = dt

    @pyqtSlot()
    def run(self):
        prev_err = 0.
        integral = 0.
        while True:
            err = self._target - self._channel.value
            integral += err * self._dt
            deriv = (err - prev_err) / self._dt
            output = sum(np.multiply([err, integral, deriv], self._coeffs))
            self._sig_set_value.emit(output)
            prev_err = err
            time.sleep(self._dt)

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, ch):
        self._channel = ch
