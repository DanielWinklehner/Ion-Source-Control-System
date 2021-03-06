#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Procedure base class

import operator

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
                            QGroupBox, QWidget, QTextEdit, QLineEdit
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from PyQt5.QtGui import QSizePolicy, QPixmap, QIcon

from .Pid import Pid
from .Timer import Timer

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

    @property
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

    @property
    def json(self):
        return {'name': self._name}

class BasicProcedure(Procedure):

    _sig_trigger = pyqtSignal(object)

    def __init__(self, name, rules, actions, critical=False, triggertype='', email='', sms=''):
        super(BasicProcedure, self).__init__(name)

        self._rules = rules
        self._actions = actions
        self._critical = critical
        
        if  triggertype not in ('startpoll', 'stoppoll', 'emstop', ''):
            print('invalid trigger type, setting manual mode...')
            self._triggertype = ''
        else:
            self._triggertype = triggertype

        #if self._rules is None:

        # these should trigger sending email/sms if not blank
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

        totaldelay = 0
        for idx, action in self._actions.items():
            totaldelay += action['delay']
            actionvalstr = val_to_str(action['channel'].data_type, action['value'])
            rval += '  {}. Set {}.{} to {} {} after {} seconds\n'.format(str(idx + 1), action['device'].label, 
                                                   action['channel'].label, actionvalstr, 
                                                   action['channel'].unit,
                                                   totaldelay)


        if self._email != '':
            rval += '  Send an email to {}\n'.format(self._email)

        if self._sms != '':
            rval += '  Send a text to {}\n'.format(self._sms)

        return rval

class TimerProcedure(Procedure):

    def __init__(self, name, start_channel=None, start_value=0.0, start_comp=operator.gt, 
                             stop_channel=None, stop_value=0.0, stop_comp=operator.gt,
                             min_time=0.0, continuous=False):

        super(TimerProcedure, self).__init__(name)
        self._title = '(Timer) {}'.format(self._name)

        self._timer = Timer(start_channel, start_value, start_comp,
                            stop_channel, stop_value, stop_comp, 
                            min_time, continuous)

        self._timer.start_signal.connect(self.on_timer_start)
        self._timer.stop_signal.connect(self.on_timer_stop)

        self._timer_thread = QThread()
        self._timer.moveToThread(self._timer_thread)
        self._timer_thread.started.connect(self._timer.run)

    def initialize(self):
        gb = QGroupBox(self._title)
        vbox = QVBoxLayout()
        gb.setLayout(vbox)
        hbox = QHBoxLayout()
        vbox_info = QVBoxLayout()
        self._lblInfo = QLabel(self.info)
        self._txtLog = QTextEdit()
        self._txtLog.setReadOnly(True)
        self._txtLog.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._txtLog.setMaximumHeight(100)
        self._txtLog.setMaximumWidth(700)
        hbox.addWidget(self._lblInfo)
        hbox.addWidget(self._txtLog)
 
        vbox.addLayout(hbox)
        vbox.addLayout(self.control_button_layout())

        self._widget = gb 

    def control_button_layout(self):
        hbox = QHBoxLayout()
        self._btnStart = QPushButton('Start')
        self._btnStop = QPushButton('Stop')
        self._btnReset = QPushButton('Reset')
        self._btnStart.clicked.connect(self.on_start_click)
        self._btnStop.clicked.connect(self.on_stop_click)
        self._btnStop.setEnabled(False)
        hbox.addWidget(self._btnStart)
        hbox.addWidget(self._btnStop)
        hbox.addWidget(self._btnReset)
        hbox.addStretch()
        self._btnEdit = QPushButton('Edit')
        self._btnDelete = QPushButton('Delete')
        self._btnEdit.clicked.connect(lambda: self._sig_edit.emit(self))
        self._btnDelete.clicked.connect(lambda: self._sig_delete.emit(self))
        hbox.addWidget(self._btnEdit)
        hbox.addWidget(self._btnDelete)

        return hbox

    @pyqtSlot(str)
    def on_timer_start(self, time):
        self._txtLog.append('Timer started at {}'.format(time))

    @pyqtSlot(str, float)
    def on_timer_stop(self, time, value):
        self._txtLog.append('Timer stopped at {}, total time elapsed={} s'.format(time, str(value)))
        if not self._timer.continuous:
            self.on_stop_click()

    @pyqtSlot()
    def on_start_click(self):
        self._btnStart.setEnabled(False)
        self._btnEdit.setEnabled(False)
        self._btnDelete.setEnabled(False)
        self._btnStop.setEnabled(True)
        self._timer_thread.start()

    @pyqtSlot()
    def on_stop_click(self):
        self._timer.terminate()
        self._timer_thread.quit()
        self._btnStart.setEnabled(True)
        self._btnEdit.setEnabled(True)
        self._btnDelete.setEnabled(True)
        self._btnStop.setEnabled(False)


    @property
    def info(self):
        rval = ''
        if self._timer.continuous:
            rval += 'Continuous\n'
        
        rval += 'Start timing when {}.{} is {} than {} {}\n'.format(
                self._timer.start_channel.parent_device.label,
                self._timer.start_channel.label,
                self._timer.start_comp_str,
                self._timer.start_value,
                self._timer.start_channel.unit)
        rval += 'Stop timing when {}.{} is {} than {} {}'.format(
                self._timer.stop_channel.parent_device.label,
                self._timer.stop_channel.label,
                self._timer.stop_comp_str,
                self._timer.stop_value,
                self._timer.stop_channel.unit)
        if self._timer.min_time != 0.0:
            rval += '\nMinimum time: {} s'.format(self._timer.min_time)
        
        return rval

    def devices_channels_used(self):
        devices = set()
        channels = set()
        devices.add(self._timer.start_channel.parent_device)
        devices.add(self._timer.stop_channel.parent_device)
        channels.add(self._timer.start_channel)
        channels.add(self._timer.stop_channel)

        return (devices, channels)

    @property
    def json(self):
        return {
                'name': self._name,
                'type': 'timer',
                'start-device': self._timer.start_channel.parent_device.name,
                'start-channel': self._timer.start_channel.name,
                'stop-device': self._timer.stop_channel.parent_device.name,
                'stop-channel': self._timer.stop_channel.name,
                'start_value': self._timer.start_value,
                'start_comp': self._timer.start_comp_str,
                'stop_value': self._timer.stop_value,
                'stop_comp': self._timer.stop_comp_str,
                'min_time': self._timer.min_time,
                'continuous': self._timer.continuous,
                }

class PidProcedure(Procedure):

    _sig_set = pyqtSignal(object, float)

    def __init__(self, name, read_channel, write_channel,
                 target=0.0, coeffs=[1.0, 1.0, 1.0], dt=0.5,
                 ma=1, warmup=0, offset=0.0):

        super(PidProcedure, self).__init__(name)
        self._title = '(PID) {}'.format(self._name)
        self._pid = Pid(read_channel, target, coeffs, dt, ma, warmup, offset)
        self._pid.set_signal.connect(self.on_pid_set_signal)
        self._pid.skip_signal.connect(self.on_pid_skip_signal)
        self._pid.ma_signal.connect(self.on_pid_ma_signal)
        self._write_channel = write_channel
        self._pid_thread = None
        
        self._pid_thread = QThread()
        self._pid.moveToThread(self._pid_thread)
        self._pid_thread.started.connect(self._pid.run)
        self._pid_thread.finished.connect(self.on_pid_thread_finished)

        self._readfmt = '{' + '0:.{}{}'.format(read_channel.precision, read_channel.display_mode) + '}'
        self._writefmt = '{' + '0:.{}{}'.format(write_channel.precision, write_channel.display_mode) + '}'

    def initialize(self):
        gb = QGroupBox(self._title)
        vbox = QVBoxLayout()
        gb.setLayout(vbox)
        hbox = QHBoxLayout()
        vbox_info = QVBoxLayout()
        hbox_target = QHBoxLayout()
        self._lblInfo = QLabel(self.info)
        self._txtLog = QTextEdit()
        self._txtLog.setReadOnly(True)
        self._txtTarget = QLineEdit()
        self._txtTarget.returnPressed.connect(self.on_target_return_pressed)
        self._txtLog.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._txtLog.setMaximumHeight(100)
        self._txtLog.setMaximumWidth(700)
        vbox_info.addWidget(self._lblInfo)
        lbl = QLabel('Set target:')
        lbl2 = QLabel(self._pid.channel.unit)
        hbox_target.addWidget(lbl)
        hbox_target.addWidget(self._txtTarget)
        hbox_target.addWidget(lbl2)
        hbox_target.addStretch()
        vbox_info.addLayout(hbox_target)
        hbox.addLayout(vbox_info)
        hbox.addWidget(self._txtLog)
 
        vbox.addLayout(hbox)
        vbox.addLayout(self.control_button_layout())

        self._widget = gb 

    def control_button_layout(self):
        hbox = QHBoxLayout()
        self._btnStart = QPushButton('Start')
        self._btnStop = QPushButton('Stop')
        self._btnStart.setIcon(QIcon(QPixmap('gui/images/icons/media-playback-start.png')))
        self._btnStart.clicked.connect(self.on_start_click)
        self._btnStop.clicked.connect(self.on_stop_click)
        self._btnStop.setEnabled(False)
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

    @pyqtSlot(float)
    def on_pid_set_signal(self, val):
        val = max(self._write_channel.lower_limit, min(val, self._write_channel.upper_limit))
        self._txtLog.append('Send SET command to {}.{}. Value={} {}'.format(
                self._write_channel.parent_device.label, self._write_channel.label,
                self._writefmt.format(val), self._write_channel.unit))
        self._sig_set.emit(self._write_channel, val)

    @pyqtSlot(float)
    def on_pid_skip_signal(self, val):
        self._txtLog.append('SKIPPING set to {}.{} with value={} {}'.format(
                self._write_channel.parent_device.label, self._write_channel.label,
                self._writefmt.format(val), self._write_channel.unit))

    @pyqtSlot(float)
    def on_pid_ma_signal(self, val):
        self._txtLog.append('Averaging values: current value={} {}'.format(
                self._readfmt.format(val), self._pid.channel.unit))

    @pyqtSlot()
    def on_target_return_pressed(self):
        try:
            val = float(self._txtTarget.text())
        except:
            print('bad value entered')
            return

        self._txtLog.append('Changing target to {} {}'.format(
            self._readfmt.format(val), self._pid.channel.unit))

        self._pid.target = val
        self._lblInfo.setText(self.info)
        self._txtTarget.setText(str(val))

    @pyqtSlot()
    def on_start_click(self):
        if self._btnStart.text() == 'Start':
            self._txtLog.setText('')
            #self._btnStart.setEnabled(False)
            self._btnStart.setText('Pause')
            self._btnStart.setIcon(QIcon(QPixmap('gui/images/icons/media-playback-pause.png')))
            self._btnEdit.setEnabled(False)
            self._btnDelete.setEnabled(False)
            self._btnStop.setEnabled(True)
            self._pid_thread.start()
        elif self._btnStart.text() == 'Pause':
            self._pid.pause()
            self._btnStart.setText('Resume')
            self._btnStart.setIcon(QIcon(QPixmap('gui/images/icons/media-playback-start.png')))
        elif self._btnStart.text() == 'Resume':
            self._pid.unpause()
            self._btnStart.setText('Pause')
            self._btnStart.setIcon(QIcon(QPixmap('gui/images/icons/media-playback-pause.png')))

    @pyqtSlot()
    def on_stop_click(self):
        self._pid.terminate()
        self._pid_thread.quit()
        #self._btnStart.setEnabled(True)
        self._btnStart.setText('Start')
        self._btnStart.setIcon(QIcon(QPixmap('gui/images/icons/media-playback-start.png')))
        self._btnEdit.setEnabled(True)
        self._btnDelete.setEnabled(True)
        self._btnStop.setEnabled(False)

    @pyqtSlot()
    def on_pid_thread_finished(self):
        print('PID procedure {} stopped.'.format(self._name))

    @property
    def set_signal(self):
        return self._sig_set

    @property
    def info(self):
        rval = ''
        rval += 'Reading channel {}.{}\n'.format(self._pid.channel.parent_device.label,
                                                self._pid.channel.label)
        rval += 'Writing to channel {}.{}\n'.format(self._write_channel.parent_device.label,
                                                    self._write_channel.label)
        rval += 'Target value: {} {}\n'.format(self._pid.target, self._pid.channel.unit)
        rval += 'Parameters: P={}, I={}, D={}, dt={}s\n'.format(*self._pid.coeffs, self._pid.dt)
        rval += 'Extra Options: Average={} samples, Warmup={} samples, Offset={} {}'.format(
                self._pid.ma, self._pid.warmup, self._pid.offset, self._write_channel.unit)

        return rval

    def devices_channels_used(self):
        devices = set()
        channels = set()
        devices.add(self._pid.channel.parent_device)
        devices.add(self._write_channel.parent_device)
        channels.add(self._pid.channel)
        channels.add(self._write_channel)

        return (devices, channels)

    @property
    def json(self):
        return {
                'name': self._name,
                'type': 'pid',
                'read-device': self._pid.channel.parent_device.name,
                'read-channel': self._pid.channel.name,
                'write-device': self._write_channel.parent_device.name,
                'write-channel': self._write_channel.name,
                'target': self._pid.target,
                'coeffs': self._pid.coeffs,
                'dt': self._pid.dt,
                'ma': self._pid.ma,
                'warmup': self._pid.warmup,
                'offset': self._pid.offset,
                }
