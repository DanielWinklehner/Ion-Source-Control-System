import time
import datetime as dt

import numpy as np

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class Timer(QObject):

    _sig_start = pyqtSignal()
    _sig_stop = pyqtSignal(float)

    def __init__(self, channel, start_val, start_comp, stop_val, stop_comp, mintime):
        super().__init__()
        self._channel = channel
        self._start_value = start_val
        self._start_comp = start_comp
        self._stop_value = stop_val
        self._stop_comp = stop_comp
        self._min_time = mintime
        self._dt = 0.05

    @pyqtSlot()
    def run(self):
        self._terminate = False
        started = False
        starttime = None
        stoptime = None

        while not self._terminate:
            value = self._channel.value

            if self._start_comp(value, self._start_value) and not started:
                started = True
                starttime = dt.now()
                _sig_start.emit

            if self._stop_comp(value, self._stop_value) and started:
                temptime = dt.now()
                if (temptime - starttime).total_seconds() > self._min_time:
                    stoptime = temptime
                    self._terminate = True

            time.sleep(self._dt)

        self._sig_stop.emit((stoptime - starttime).total_seconds())

    @pyqtSlot()
    def terminate(self):
        self._terminate = True

    @property
    def start_signal(self):
        return self._sig_start

    @property
    def stop_signal(self):
        return self._sig_stop

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, ch):
        self._channel = ch

