#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Procedure base class

import operator

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
                            QGroupBox, QWidget
from PyQt5.QtCore import QObject, pyqtSignal

from .Pid import Pid

class Procedure(QObject):

    _sig_edit = pyqtSignal(object)
    _sig_delete = pyqtSignal(object)

    def __init__(self, name):

        super().__init__()
        self._name = name
        self._title = self._name
        
    def initialize(self):
        gb = QGroupBox(self._title)
        vbox = QVBoxLayout()
        gb.setLayout(vbox)
        self._lblInfo = QLabel(self.info)
        vbox.addWidget(self._lblInfo)
 
        vbox.addLayout(self.control_button_layout())

        self._widget = gb 

    def control_button_layout(self):
        hbox = QHBoxLayout()
        hbox.addStretch()
        self._btnEdit = QPushButton('Edit')
        self._btnDelete = QPushButton('Delete')
        self._btnEdit.clicked.connect(lambda: self._sig_edit.emit(self))
        self._btnDelete.clicked.connect(lambda: self._sig_delete.emit(self))
        hbox.addWidget(self._btnEdit)
        hbox.addWidget(self._btnDelete)

        return hbox

    def info(self):
        return "Procedure base class"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def signal_edit(self):
        return self._sig_edit

    @property
    def signal_delete(self):
        return self._sig_delete

    @property
    def widget(self):
        return self._widget

class BasicProcedure(Procedure):

    _sig_trigger = pyqtSignal(object)

    def __init__(self, name, rules, actions, critical=False, email='', sms=''):
        super(BasicProcedure, self).__init__(name)

        self._rules = rules
        self._actions = actions
        self._critical = critical
        
        # these will trigger sending email/sms if not blank
        self._email = email
        self._sms = sms
        
        if self._critical:
            self._title = '(Critical) {}'.format(self._name)

    def control_button_layout(self):
        hbox = QHBoxLayout()
        self._btnTrigger = QPushButton('Trigger')
        self._btnTrigger.clicked.connect(lambda: self._sig_trigger.emit(self))
        hbox.addWidget(self._btnTrigger)
        hbox.addStretch()
        self._btnEdit = QPushButton('Edit')
        self._btnDelete = QPushButton('Delete')
        self._btnEdit.clicked.connect(lambda: self._sig_edit.emit(self))
        self._btnDelete.clicked.connect(lambda: self._sig_delete.emit(self))
        hbox.addWidget(self._btnEdit)
        hbox.addWidget(self._btnDelete)

        return hbox

    def devices_channels_used(self):
        devices = set()
        channels = set()
        for idx, rule in self._rules.items():
            devices.add(rule['device'])
            channels.add(rule['channel'])

        for idx, action in self._actions.items():
            devices.add(action['device'])
            channels.add(action['channel'])

        return (devices, channels)


    @property
    def rules(self):
        return self._rules

    @property
    def actions(self):
        return self._actions

    @property
    def critical(self):
        return self._critical

    @property
    def email(self):
        return self._email

    @property
    def sms(self):
        return self._sms
    
    def should_perform_procedure(self):
        condition_satisfied = True
        for arduino_id, rule in self._rules.items():
            if not rule['comparison'](channel.value, rule['value']):
                condition_satisfied = False
                break

        return condition_satisfied
    
    def do_actions(self):
        for arduino_id, action in self._actions.items():
            print('setting value of {}.{} to {}'.format(action['device'].name,
                                                        action['channel'].name,
                                                        action['value'].name))

        if self._email != '':
            # send email
            pass

        if self._sms != '':
            # send text
            pass
    
    @property
    def info(self):
        rval = ''

        for idx, rule in self._rules.items():
            if rule['comp'] == operator.eq:
                comptext = 'equal to'
            elif rule['comp'] == operator.lt:
                comptext = 'less than'
            elif rule['comp'] == operator.gt:
                comptext = 'greater than'
            elif rule['comp'] == operator.ge:
                comptext = 'greater than or equal to'
            elif rule['comp'] == operator.le:
                comptext = 'less than or equal to'

            def val_to_str(data_type, val):
                if data_type != bool:
                    return str(val)
                else:
                    if val:
                        return 'On'
                    else:
                        return 'Off'

            rulevalstr = val_to_str(rule['channel'].data_type, rule['value'])

            rval += 'If {}.{} is {} {} {}:\n'.format(rule['device'].label, rule['channel'].label,
                                                comptext, rulevalstr, rule['channel'].unit)

        for idx, action in self._actions.items():
            actionvalstr = val_to_str(action['channel'].data_type, action['value'])
            rval += '  {}) Set {}.{} to {} {}\n'.format(str(idx + 1), action['device'].label, 
                                                   action['channel'].label, actionvalstr, 
                                                   action['channel'].unit)


        if self._email != '':
            rval += '  Send an email to {}\n'.format(self._email)

        if self._sms != '':
            rval += '  Send a text to {}\n'.format(self._sms)

        return rval

class PidProcedure(Procedure):

    _sig_start = pyqtSignal(object)
    _sig_stop = pyqtSignal(object)

    def __init__(self, name, read_channel, write_channel,
                 target=0.0, coeffs=[1.0, 1.0, 1.0], dt=0.5):

        super(PidProcedure, self).__init__(name)
        self._title = '(PID) {}'.format(self._name)
        self._pid = Pid(read_channel, target, coeffs, dt)
        self._write_channel = write_channel

    def control_button_layout(self):
        hbox = QHBoxLayout()
        self._btnStart = QPushButton('Start')
        self._btnStop = QPushButton('Stop')
        self._btnStart.clicked.connect(lambda: self._sig_start.emit(self))
        self._btnStop.clicked.connect(lambda: self._sig_stop.emit(self))
        hbox.addWidget(self._btnStart)
        hbox.addWidget(self._btnStop)
        hbox.addStretch()
        self._btnEdit = QPushButton('Edit')
        self._btnDelete = QPushButton('Delete')
        self._btnEdit.clicked.connect(lambda: self._sig_edit.emit(self))
        self._btnDelete.clicked.connect(lambda: self._sig_delete.emit(self))
        hbox.addWidget(self._btnEdit)
        hbox.addWidget(self._btnDelete)

        return hbox

    @property
    def info(self):
        return 'PID Procedure'

    def devices_channels_used(self):
        return (self._pid.channel.parent_device, self._pid.channel)

