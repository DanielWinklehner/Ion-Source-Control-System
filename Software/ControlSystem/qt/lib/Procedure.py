#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Procedure class

import operator

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
                            QGroupBox, QWidget
from PyQt5.QtCore import pyqtSignal

class Procedure(QWidget):

    _edit_sig = pyqtSignal(object)
    _delete_sig = pyqtSignal(object)

    def __init__(self, name, rules, actions, critical=False, email='', sms=''):

        super().__init__()
        # Rules dict:
        # key = arduino_id, device, channel, comparison, value

        # Action dict:
        # key = arduino_id, device, channel, value to set

        self._name = name
        self._rules = rules
        self._actions = actions
        self._critical = critical
        
        # these will trigger sending email/sms if not blank
        self._email = email
        self._sms = sms
        
        title = ''
        if self._critical:
            title = '(Critical) {}'.format(self._name)
        else:
            title = self._name
        gb = QGroupBox(title)
        vbox = QVBoxLayout()
        gb.setLayout(vbox)
        self._lblInfo = QLabel(self.info)
        vbox.addWidget(self._lblInfo)
        hbox = QHBoxLayout()
        hbox.addStretch()
        self._btnEdit = QPushButton('Edit', self)
        self._btnDelete = QPushButton('Delete', self)
        self._btnEdit.clicked.connect(self.on_edit_clicked)
        self._btnDelete.clicked.connect(self.on_delete_clicked)
        hbox.addWidget(self._btnEdit)
        hbox.addWidget(self._btnDelete)
        vbox.addLayout(hbox)

        self._widget = gb 

    def on_edit_clicked(self):
        self._edit_sig.emit(self)

    def on_delete_clicked(self):
        self._delete_sig.emit(self)

    def devices_channels_used(self):
        devices = []
        channels = []
        for idx, rule in self._rules.items():
            devices.append(rule['device'].name)
            channels.append(rule['channel'].name)

        for idx, action in self._actions.items():
            devices.append(action['device'].name)
            channels.append(action['channel'].name)

        return (devices, channels)

    @property
    def name(self):
        return self._name

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


    def __repr__(self):
        rval = ''

        if self._critical:
            rval += 'Critical procedure {}\n'.format(self._name)
        else:
            rval += 'Procedure {}\n'.format(self._name)

        rval += self.info
        return rval 
