#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Dialog for creating/editing procedures

import operator

from PyQt5.QtWidgets import QDialog, QFrame, QLabel, QPushButton, QVBoxLayout, \
                            QHBoxLayout

from .ui_ProcedureDialog import Ui_ProcedureDialog
from lib.Procedure import Procedure

class ProcedureDialog(QDialog):

    def __init__(self, devices, proc=None):
        super().__init__()
        self.ui = Ui_ProcedureDialog()
        self.ui.setupUi(self)
        self.ui.btnDone.clicked.connect(self.on_done_click)
        self.ui.cbRuleDevice.currentIndexChanged.connect(self.on_rule_device_cb_changed)
        self.ui.cbActionDevice.currentIndexChanged.connect(self.on_action_device_cb_changed)
        self.ui.btnAddAction.clicked.connect(self.on_add_action_click)

        self._vboxActions = QVBoxLayout()
        self._vboxActions.addStretch()
        self.ui.fmActions.setLayout(self._vboxActions)

        self._devdict = devices

        # maintain order of the list of devices
        self._devlist = [x for name, x in self._devdict.items()]


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

        fm = QFrame()
        
        vbox = QVBoxLayout()
        lblDevCh = QLabel(self.ui.cbActionDevice.currentText() + '.' + \
                          self.ui.cbActionChannel.currentText())
        lblSetVal = QLabel('Set value: ' + self.ui.txtActionVal.text())
        vbox.addWidget(lblDevCh)
        vbox.addWidget(lblSetVal)

        btnDel = QPushButton('Delete')

        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addStretch()
        hbox.addWidget(btnDel)

        fm.setLayout(hbox)

        self._vboxActions.insertWidget(0, fm)

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

    def on_done_click(self):

        self._accepted = True
        self.accept()

    def exec_(self):
        super(ProcedureDialog, self).exec_()
        return(self._accepted, self._newproc)
