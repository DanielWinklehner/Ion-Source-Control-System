#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Thomas Wester <twester@mit.edu>
#
# Device representation class

import json
import datetime
from collections import deque

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, \
        QLabel, QRadioButton, QLineEdit, QPushButton, QDial
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from gui.widgets.DateTimePlotWidget import DateTimePlotWidget
from gui.widgets.EntryForm import EntryForm

class Channel(QWidget):
    # emits itself and the new value
    _set_signal = pyqtSignal(object, object)

    # emits device and channel
    _pin_signal = pyqtSignal(object, object)

    _settings_signal = pyqtSignal(object)

    _sig_entry_form_ok = pyqtSignal(object, dict)
    _sig_delete = pyqtSignal(object)

    def __init__(self, name='', label='', upper_limit=0.0, lower_limit=0.0, 
                 data_type=float, unit="", scaling=1.0, scaling_read=None, 
                 mode="both", display_order=0, display_mode="f", precision=2, 
                 default_value=0.0, plot_settings = None, stored_values=500,
                 write_mode='text'):

        super().__init__()

        # basic properties
        self._name = name
        self._label = label
        self._upper_limit = upper_limit
        self._lower_limit = lower_limit
        self._data_type = data_type
        self._unit = unit
        self._scaling = scaling
        self._scaling_read = scaling_read
        self._value = default_value
        self._mode = mode
        self._precision = precision
        self._display_mode = display_mode
        self._write_mode = write_mode
        self._display_order = display_order

        # derived properties
        self._displayformat = ".{}{}".format(precision, display_mode)

        # properties that will be set during run time
        self._parent_device = None  
        self._locked = False
        if plot_settings is None:
            self._plot_settings = {
                    'x': {'mode': 'auto', 'min': 0, 'max': 0, 'log': False,
                          'label': '', 'grid': False},
                    'y': {'mode': 'auto', 'min': 0, 'max': 0, 'log': False,
                          'label': '', 'grid': False},
                    'widget': {'color': '#FF0000'}
                    }
        else:
            self._plot_settings = plot_settings

        self._retain_last_n_values = stored_values
        self._x_values = deque(maxlen=self._retain_last_n_values)
        self._y_values = deque(maxlen=self._retain_last_n_values)

        # entry form representation (settings page in GUI)
        self._entry_form = EntryForm(self.label, '',
                                     self.user_edit_properties(), self)
        self._entry_form.sig_save.connect(self.save_changes)
        self._entry_form.sig_delete.connect(self.delete)

        self._initialized = False

    @property
    def initialized(self):
        return self._initialized

    def initialize(self):
        """ Create widgets for this channel """
        self._initialized = True

        self._entry_form.add_delete_button()

        # overview widget
        gb = QGroupBox(self._label)
        self._overview_widget = gb
        self._unit_labels = []
        self._write_widget = None
        self._dial_widget = None
        self._read_widget = None

        if self._data_type == bool:
            hbox_radio = QHBoxLayout()
            self._overview_widget.setLayout(hbox_radio)
            rbOn = QRadioButton('On')
            self._write_widget = rbOn
            rbOn.toggled.connect(self.set_value_callback)
            rbOff = QRadioButton('Off')
            rbOff.toggle()
            hbox_radio.addWidget(rbOn)
            hbox_radio.addWidget(rbOff)

        else:
            vbox_readwrite = QVBoxLayout()
            self._overview_widget.setLayout(vbox_readwrite)
            if self._mode in ['write', 'both']:
                # add first row
                hbox_write = QHBoxLayout()
                if self._write_mode == 'text':
                    lblUnit = QLabel(self._unit)
                    self._unit_labels.append(lblUnit)
                    txtWrite = QLineEdit(str(self._lower_limit))
                    txtWrite.returnPressed.connect(self.set_value_callback)
                    self._write_widget = txtWrite
                    hbox_write.addWidget(self._write_widget)
                    hbox_write.addWidget(lblUnit)
                elif self._write_mode == 'dial':
                    dial = QDial()
                    dial.setMaximum(10**self._precision)
                    self._dial_widget = dial
                    self._dial_widget.valueChanged.connect(self.set_value_callback_dial)
                    hbox_write.addWidget(self._dial_widget)
                vbox_readwrite.addLayout(hbox_write)

            if self._mode in ['read', 'both']:
                # add readonly second row
                hbox_read = QHBoxLayout()
                lblUnit = QLabel(self._unit)
                self._unit_labels.append(lblUnit)
                txtRead = QLineEdit()
                txtRead.setDisabled(True)
                self._read_widget = txtRead

                hbox_read.addWidget(self._read_widget)
                hbox_read.addWidget(lblUnit)
                vbox_readwrite.addLayout(hbox_read)

        # plot widget
        gb_plot = QGroupBox()
        gb_plot.setMinimumSize(350, 300)
        
        self._plot_item = DateTimePlotWidget(settings=self._plot_settings)
        self._plot_curve = self._plot_item.curve

        vbox = QVBoxLayout()
        gb_plot.setLayout(vbox)
        hbox = QHBoxLayout()
        btnPin = QPushButton('Pin')
        btnSettings = QPushButton('Settings')
        btnPin.clicked.connect(self.set_pin_callback)
        btnSettings.clicked.connect(self.settings_callback)
        hbox.addWidget(btnSettings)
        hbox.addStretch()
        hbox.addWidget(btnPin)
        vbox.addWidget(self._plot_item)
        vbox.addLayout(hbox)
        self._plot_widget = gb_plot


    # ---- Entry form ----

    def reset_entry_form(self):
        self._entry_form.properties = self.user_edit_properties()
        self._entry_form.reset()

    @property
    def entry_form(self):
        return self._entry_form.widget

    @pyqtSlot(dict)
    def save_changes(self, newvals):
        """ Validates the user data entered into the channel's Entry Form. 
            Returns a dictionary of values to update if there are no errors. """
        data_type_map = {'Float': float, 'Int': int, 'Bool': bool}
        display_mode_map = {'Float': 'f', 'Scientific': 'e'}
        data_type = data_type_map[newvals['data_type']]

        validvals = {}
        for prop_name, val in newvals.items(): 
            if prop_name in ['lower_limit', 'upper_limit']:
                try:
                    value = data_type(val)
                except:
                    print('bad value entered for limits')
                    return
            elif prop_name == 'scaling':
                try:
                    value = float(val)
                except:
                    print('bad value entered for scaling')
            elif prop_name in ['stored_values', 'precision', 'display_order']:
                try:
                    value = int(val)
                except:
                    print('{} must be int.'.format(prop_name))
                    return
            elif prop_name == 'display_mode':
                value = display_mode_map[val]
            elif prop_name == 'mode':
                value = val.lower()
            elif prop_name == 'write_mode':
                value = val.lower()
            elif prop_name == 'data_type':
                value = data_type
            elif prop_name == 'unit':
                value = val
            else:
                if val != '':
                    value = val
                else:
                    print('No value entered for {}.'.format(prop_name))
                    return

            validvals[prop_name] = value

        self._sig_entry_form_ok.emit(self, validvals)

    @property
    def sig_entry_form_ok(self):
        return self._sig_entry_form_ok

    @property
    def sig_delete(self):
        return self._sig_delete

    def user_edit_properties(self):
        
        return {
                'name': {
                    'display_name': 'Name', 
                    'entry_type': 'text',
                    'value': self._name,
                    'display_order': 1
                    },
                'label': {
                    'display_name': 'Label', 
                    'entry_type': 'text',
                    'value': self._label,
                    'display_order': 2
                    },
                'unit': {
                    'display_name': 'Unit', 
                    'entry_type': 'text',
                    'value': self._unit,
                    'display_order': 3
                    },
                'scaling': {
                    'display_name': 'Scaling', 
                    'entry_type': 'text',
                    'value': self._scaling,
                    'display_order': 4
                    },
                'precision': {
                    'display_name': 'Precision', 
                    'entry_type': 'text',
                    'value': self._precision,
                    'display_order': 5
                    },
                'display_mode': {
                    'display_name': 'Display Mode', 
                    'entry_type': 'combo',
                    'value': 'Scientific' if self._display_mode == 'e' else 'Float',
                    'defaults': ['Float', 'Scientific'],
                    'display_order': 6
                    },
                'write_mode': {
                    'display_name': 'Write Mode', 
                    'entry_type': 'combo',
                    'value': 'Dial' if self._write_mode == 'dial' else 'Text',
                    'defaults': ['Text', 'Dial'],
                    'display_order': 7
                    },
                'lower_limit': {
                    'display_name': 'Lower Limit', 
                    'entry_type': 'text',
                    'value': self._lower_limit,
                    'display_order': 8
                    },
                'upper_limit': {
                    'display_name': 'Upper Limit', 
                    'entry_type': 'text',
                    'value': self._upper_limit,
                    'display_order': 9
                    },
                'data_type': {
                    'display_name': 'Data Type', 
                    'entry_type': 'combo',
                    'value': str(self._data_type).split("'")[1].title(),
                    'defaults': ['Float', 'Int', 'Bool'],
                    'display_order': 10
                    },
                'mode': {
                    'display_name': 'Mode', 
                    'entry_type': 'combo',
                    'value': self._mode.title(),
                    'defaults': ['Read', 'Write', 'Both'],
                    'display_order': 11
                    },
                'display_order': {
                    'display_name': 'Display Order', 
                    'entry_type': 'text',
                    'value': self._display_order,
                    'display_order': 12
                    },
                'stored_values': {
                    'display_name': '# Stored Values', 
                    'entry_type': 'text',
                    'value': self._retain_last_n_values,
                    'display_order': 13
                    },
                }

    def delete(self):
        self._sig_delete.emit(self)
        
    # ---- GUI interaction ----

    def update(self):
        """ Update the GUI representation of this channel """
        self._overview_widget.setTitle(self._label)
        for lbl in self._unit_labels:
            lbl.setText(self._unit)

        self._plot_widget.layout().itemAt(0).widget().setLabel('left', '{} [{}]'.format(self._label, self._unit))
        if self._parent_device is not None:
            if self._parent_device.error_message == '':
                self._plot_widget.setTitle('{}/{}'.format(
                    self._parent_device.label, self._label))
            else:
                self._plot_widget.setTitle('(Error) {}/{}'.format(
                    self._parent_device.label, self._label))

    @pyqtSlot()
    def set_value_callback(self):
        """ Function called when user enters a value into this channel's write widget """
        if self._data_type != bool:
            try:
                val = self._data_type(self._write_widget.text())
            except:
                print('bad value entered')
                return

            if val > self._upper_limit or val < self._lower_limit:
                print('value exceeds limits')
                return

            self._write_widget.setText(str(self._data_type(val)))
            self._set_signal.emit(self, val)
        else:
            self._set_signal.emit(self, self._write_widget.isChecked())

    @pyqtSlot()
    def set_value_callback_dial(self):
        """ Function called when user scrolls/moves the dial """
        value = self._dial_widget.value() / float(self._dial_widget.maximum())

        val = self._upper_limit * value

        try:
            val = self._data_type(val)
        except:
            print('bad value entered')
            return

        if val > self._upper_limit or val < self._lower_limit:
            print('value exceeds limits')
            return

        self._set_signal.emit(self, val)

    @pyqtSlot()
    def set_pin_callback(self):
        """ Called when user presses the channel's pin button """
        self._pin_signal.emit(self.parent_device, self)

    @pyqtSlot()
    def settings_callback(self):
        self._settings_signal.emit(self)

    @property
    def plot_settings(self):
        return self._plot_settings

    @plot_settings.setter
    def plot_settings(self, newsettings):
        self._plot_settings = newsettings
        self._plot_item.settings = self._plot_settings

    @property
    def x_values(self):
        return self._x_values

    @property
    def y_values(self):
        return self._y_values

    @property
    def stored_values(self):
        return self._retain_last_n_values

    @stored_values.setter
    def stored_values(self, value):
        n = len(self._x_values)

        if value < n:
            # take last n values of current deque
            x_vals = [self._x_values[i] for i in range(n - value, n)]
            y_vals = [self._y_values[i] for i in range(n - value, n)]
        else:
            x_vals = self._x_values
            y_vals = self._y_values

        self._retain_last_n_values = value
        self._x_values = deque(maxlen=self._retain_last_n_values)
        self._x_values.extend(x_vals)
        self._y_values = deque(maxlen=self._retain_last_n_values)
        self._y_values.extend(y_vals)

    def append_data(self, x, y):
        self._x_values.append(x)
        self._y_values.append(y)

    def clear_data(self):
        self._x_values.clear()
        self._y_values.clear()
        self._plot_item.setData(0,0)

    # ---- Properties ----

    @property
    def precision(self):
        return self._precision

    @precision.setter
    def precision(self, precision):
        self._precision = precision
        self._displayformat = '.{}{}'.format(self._precision, self._display_mode)

    @property
    def write_mode(self):
        return self._write_mode

    @write_mode.setter
    def write_mode(self, val):
        self._write_mode = val

    @property
    def display_mode(self):
        return self._display_mode

    @display_mode.setter
    def display_mode(self, value):
        self._display_mode = value
        self._displayformat = '.{}{}'.format(self._precision, self._display_mode)

    @property
    def displayformat(self):
        # should not be edited directly. Changed when precision is changed
        return self._displayformat

    def lock(self):
        if not self._locked:
            if not self._overview_page_display.locked():
                self._overview_page_display.lock()
                self._locked = True

    def unlock(self):
        if self._locked:
            if self._overview_page_display.locked():
                self._overview_page_display.unlock()
                self._locked = False

    @property
    def locked(self):
        return self._locked

    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def device_id(self, device_id):
        self._device_id = device_id

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value_to_set):
        if not self._locked:
            self._value = value_to_set

    def read_value(self):
        if not self._locked:
            return self._value

    @property
    def display_order(self):
        return self._display_order

    @display_order.setter
    def display_order(self, value):
        self._display_order = value

    @property
    def parent_device(self):
        return self._parent_device

    @parent_device.setter
    def parent_device(self, device):
        self._parent_device = device
        if self._initialized:
            self.update()

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value
        if self._initialized:
            if self._overview_widget.title() != self._label:
                self._overview_widget.setTitle(self._label)
                self.update()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def upper_limit(self):
        return self._upper_limit

    @upper_limit.setter
    def upper_limit(self, value):
        self._upper_limit = value

    @property
    def lower_limit(self):
        return self._lower_limit

    @lower_limit.setter
    def lower_limit(self, value):
        self._lower_limit = value

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, value):
        if value not in [bool, int, float]:
            return
        self._data_type = value

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        if len(str(value)) > 5:
            return
        self._unit = str(value)

    @property
    def scaling(self):
        return self._scaling

    @scaling.setter
    def scaling(self, value):
        self._scaling = value

    def scaling_read(self):
        return self._scaling_read

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value not in ['read', 'write', 'both']:
            return
        self._mode = value

    def get_json(self):

        properties = {'name': self._name,
            'label': self._label,
            'upper_limit': self._upper_limit,
            'lower_limit': self._lower_limit,
            'data_type': str(self._data_type),
            'unit': self._unit,
            'scaling': self._scaling,
            'scaling_read': self._scaling_read,
            'mode': self._mode,
            'precision': self._precision,
            'display_mode': self._display_mode,
            'display_order': self._display_order,
            'plot_settings': self._plot_settings,
            'stored_values': self._retain_last_n_values,
            'write_mode': self._write_mode,
            }

        return properties #json.dumps(properties)

    @staticmethod
    def load_from_json(channel_json):

       properties = json.loads(channel_json)

       data_type_str = properties['data_type']

       properties['data_type'] = eval(data_type_str.split("'")[1])

       return Channel(**properties)

