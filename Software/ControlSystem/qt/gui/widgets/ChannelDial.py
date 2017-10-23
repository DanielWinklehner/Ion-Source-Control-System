#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Custom dial class for setting channel values

from PyQt5.QtWidgets import QDial
from PyQt5.QtCore import pyqtSignal, pyqtSlot

class ChannelDial(QDial):

    def __init__(self):
        super().__init__()

    # dial should be scroll wheel only, override all mouse events
    def mousePressEvent(self, event):
        event.ignore()

    def mouseMoveEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()
