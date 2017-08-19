#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Dialog for creating/editing procedures

import operator

from PyQt5.QtWidgets import QDialog, QFrame, QLabel, QPushButton, QVBoxLayout, \
                            QHBoxLayout
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from .ui_ProcedureDialog import Ui_ProcedureDialog
from lib.Procedure import Procedure

class ProcedureDialog(QDialog):

    def __init__(self, devices, proc=None):
        super().__init__()
        self.ui = Ui_ProcedureDialog()
        self.ui.setupUi(self)

        self.ui.cbActionBool.addItems(['On', 'Off'])
        self.ui.cbActionBool.hide()

        self.ui.btnDone.clicked.connect(self.on_done_click)
        self.ui.cbRuleDevice.currentIndexChanged.connect(self.on_rule_device_cb_changed)
        self.ui.cbActionDevice.currentIndexChanged.connect(self.on_action_device_cb_changed)
        self.ui.cbActionChannel.currentIndexChanged.connect(self.on_action_channel_cb_changed)
        self.ui.btnAddAction.clicked.connect(self.on_add_action_click)

        self._vboxActions = QVBoxLayout()
        self._vboxActions.addStretch()
        self.ui.fmActions.setLayout(self._vboxActions)

        self._devdict = devices

        # maintain order of the list of devices
        self._devlist = [x for name, x in self._devdict.items()]
        self._actions = {}
        self._actioncontrols = {}


        # if proc = None, assume this is for a new procedure
        # else, we are editing a procedure

        self._newproc = None
        self._accepted = False

        self.initialize()

    def initialize(self):

        # Fill comboboxes with devices/channels
        devnamelist = [x.label for x in self._devlist]
        self.ui.cbRuleDevice.addItems([' - Choose a device - '] + devnamelist)
        self.ui.cbActionDevice.addItems([' - Choose a device - '] + devnamelist)
        self.ui.cbRuleCompare.addItems(['<', '>', '=', '<=', '>='])

    def on_add_action_click(self):
        if self.ui.cbActionDevice.currentIndex() == 0 or self.ui.cbActionChannel.currentIndex() == 0:
            return

        device = self._devlist[self.ui.cbActionDevice.currentIndex() - 1]
        chs = device.channels
        chlist = [x for name, x in reversed(sorted(chs.items(), key=lambda t: t[1].display_order))]
        channel = chlist[self.ui.cbActionChannel.currentIndex() - 1]
        print(device, channel)
        if channel.data_type != bool:
            try:
                value = channel.data_type(self.ui.txtActionVal.text())
            except:
                print('bad input')
                return

            if value > channel.upper_limit or value < channel.lower_limit:
                print('exceeded channel limits')
                return
        else:
            if self.ui.cbActionBool.currentText() == 'On':
                value = True
            else:
                value = False
            
        index = len(self._actions)

        fm = QFrame()
        
        vbox = QVBoxLayout()
        lblDevCh = QLabel(self.ui.cbActionDevice.currentText() + '.' + \
                          self.ui.cbActionChannel.currentText())
        if channel.data_type != bool:
            lblSetVal = QLabel('Set value: ' + str(value))
        else:
            if value:
                lblSetVal = QLabel('Set value: On')
            else:
                lblSetVal = QLabel('Set value: Off')

        vbox.addWidget(lblDevCh)
        vbox.addWidget(lblSetVal)

        btnDel = QPushButtonX('Delete', index)
        btnDel.clickedX.connect(self.on_delete_action_click)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addStretch()
        hbox.addWidget(btnDel)

        fm.setLayout(hbox)

        self._vboxActions.insertWidget(0, fm)

        self.ui.txtActionVal.setText('')
        self.ui.cbActionDevice.setCurrentIndex(0)
        self.ui.cbActionBool.hide()
        self.ui.txtActionVal.show()

        self._actions[index] = {'device' : device, 'channel' : channel, 'value' : value}
        self._actioncontrols[index] = {'button' : btnDel, 'frame' : fm}

    def on_delete_action_click(self, index):
        print('deleting form at', index)
        print('len actions is now', len(self._actions) - 1)
        del self._actions[index]
        self._actioncontrols[index]['frame'].deleteLater()

    def on_rule_device_cb_changed(self, index):
        if index > 0:
            self.ui.cbRuleChannel.clear()
            chs = self._devlist[index - 1].channels
            chlist = [x.label for name, x in reversed(sorted(chs.items(), key=lambda t: t[1].display_order))]
            self.ui.cbRuleChannel.addItems(['- Choose a channel -'] + chlist)
        else:
            self.ui.cbRuleChannel.clear()
            self.ui.cbRuleChannel.addItems(['- Choose a device - '])

    def on_action_device_cb_changed(self, index):
        if index > 0:
            self.ui.cbActionChannel.clear()
            chs = self._devlist[index - 1].channels
            chlist = [x.label for name, x in reversed(sorted(chs.items(), key=lambda t: t[1].display_order))]
            self.ui.cbActionChannel.addItems(['- Choose a channel -'] + chlist)
        else:
            self.ui.cbActionChannel.clear()
            self.ui.cbActionChannel.addItems(['- Choose a device - '])

    def on_action_channel_cb_changed(self, index):
        if index > 0:
            chs = self._devlist[self.ui.cbActionDevice.currentIndex() - 1].channels
            chlist = [x for name, x in reversed(sorted(chs.items(), key=lambda t: t[1].display_order))]
            currentChannel = chlist[index - 1]
            if currentChannel.data_type == bool:
                # switch text field for combobox
                self.ui.cbActionBool.show()
                self.ui.txtActionVal.hide()
            else:
                # switch combobox for test field
                self.ui.cbActionBool.hide()
                self.ui.txtActionVal.show()

    def on_done_click(self):

        self._accepted = True
        self.accept()

    def exec_(self):
        super(ProcedureDialog, self).exec_()
        return(self._accepted, self._newproc)

class QPushButtonX(QPushButton):
    """ QPushButton which returns its index """
    clickedX = pyqtSignal(int)

    def __init__(self, text, index):
        super().__init__()
        self._index = index
        self.setText(text)
        self.clicked.connect(self.on_clicked)

    @pyqtSlot()
    def on_clicked(self):
        self.clickedX.emit(self._index)
