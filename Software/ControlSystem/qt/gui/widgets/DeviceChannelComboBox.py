#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Combo boxes for selecting devices and channels

from PyQt5.QtWidgets import QFrame, QHBoxLayout, QComboBox, QLabel, QWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QSizePolicy

class DeviceChannelComboBox(QWidget):

    _sig_device_changed = pyqtSignal(object)
    _sig_channel_changed = pyqtSignal(object)

    def __init__(self, devices, device_params={}, channel_params={}):
        super().__init__()

        self._device_params = device_params
        self._channel_params = channel_params

        self._devlist = []
        for device_name, device in devices.items():
            valid = True
            for attr, validvals in self._device_params.items():
                if getattr(device, attr) not in validvals:
                    valid = False
                    break
            if valid:
                self._devlist.append(device)

        self._selected_device = None
        self._selected_channel = None

        self._layout = QHBoxLayout()
        self.setLayout(self._layout)

        self._cbDevices = QComboBox(self)
        self._cbDevices.addItems(
                ['- Choose a device -'] + [x.label for x in self._devlist])
        self._cbDevices.currentIndexChanged.connect(self.on_device_cb_changed)
        self._cbChannels = QComboBox(self)
        self._cbChannels.addItems(['- Choose a device -'])
        
        lblSep = QLabel('.', self)
        lblSep.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self._layout.addWidget(self._cbDevices)
        self._layout.addWidget(lblSep)
        self._layout.addWidget(self._cbChannels)

    def channel_list(self, device):
        chlist = []
        for channel_name, channel in device.channels.items():
            valid = True
            for attr, validvals in self._channel_params.items():
                if getattr(channel, attr) not in validvals:
                    valid = False
                    break

            if valid:
                chlist.append(channel)

        return chlist

    @pyqtSlot(int)
    def on_device_cb_changed(self, idx):
        if idx > 0:
            self._selected_device = self._devlist[idx - 1]
            self._cbChannels.clear()
            chlist = self.channel_list(self._devlist[idx - 1])
            self._cbChannels.addItems(
                    ['- Choose a channel -'] + [x.label for x in chlist])
        else:
            self._selected_device = None
            self._cbChannels.clear()
            self._cbChannels.addItems(['- Choose a device -'])

        self._sig_device_changed.emit(self._selected_device)

    @pyqtSlot(int)
    def on_channel_cb_changed(self, idx):
        if idx > 0:
            chlist = self.channel_list(self._devlist.index(self._selected_device))
            self._selected_channel = chlist[idx - 1]
        else:
            self._selected_channels = None

        self._sig_channel_changed.emit(self._selected_channel)

    @property
    def selected_device(self):
        return self._selected_device

    @property
    def selected_channel(self):
        return self._selected_channel
