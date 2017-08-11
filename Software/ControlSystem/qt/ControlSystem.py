#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>

import sys
from PyQt5.QtWidgets import QApplication

import gui.MainWindow

class ControlSystem():
    def __init__(self):
        self._app = QApplication(sys.argv)
        self._MainWindow = gui.MainWindow.MainWindow()

    def run(self):
        self._MainWindow.show()
        sys.exit(self._app.exec_())


if __name__ == '__main__':
    cs = ControlSystem()
    cs.run()
