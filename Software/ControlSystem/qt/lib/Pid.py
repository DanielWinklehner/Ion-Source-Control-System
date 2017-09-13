import time

import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class Pid(QObject):

    _sig_set_value = pyqtSignal(float)
    _sig_skip_value = pyqtSignal(float)

    def __init__(self, channel, target=0.0, coeffs=[1.0, 1.0, 1.0], dt=0.5,
                 ma=1, warmup=0, offset=0.0,):
        super().__init__()
        self._target = target
        self._channel = channel
        self._coeffs = coeffs
        self._dt = dt
        self._ma = ma
        self._warmup = warmup
        self._offset = offset

    @pyqtSlot()
    def run(self):
        self._terminate = False
        prev_err = 0.
        integral = 0.
        ma_count = 0
        warmup_count = 0
        ma_sum_values = 0.0
        while not self._terminate:

            err = self._target - self._channel.value
            integral += err * self._dt
            deriv = (err - prev_err) / self._dt

            resp = sum(np.multiply([err, integral, deriv], self._coeffs)) + self._offset

            if ma_count < self._ma:
                ma_count += 1
                ma_sum_values += resp
            
            if ma_count < self._ma:
                self._sig_skip_value.emit(resp)
            else:
                ma_count = 0
                output = ma_sum_values / self._ma
                ma_sum_values = 0.0
                if warmup_count < self._warmup:
                    warmup_count += 1
                    self._sig_skip_value.emit(output)
                else:
                    self._sig_set_value.emit(output)
            prev_err = err

            time.sleep(self._dt)

    @pyqtSlot()
    def terminate(self):
        self._terminate = True

    @property
    def set_signal(self):
        return self._sig_set_value

    @property
    def skip_signal(self):
        return self._sig_skip_value

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, ch):
        self._channel = ch

    @property
    def target(self):
        return self._target

    @property
    def coeffs(self):
        return self._coeffs

    @property
    def dt(self):
        return self._dt

    @property
    def ma(self):
        return self._ma

    @ma.setter
    def ma(self, value):
        if value < 1:
            print('bad value for ma')
            return

        self._ma = value

    @property
    def warmup(self):
        return self._warmup

    @property
    def offset(self):
        return self._offset
