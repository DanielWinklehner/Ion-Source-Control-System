import json
import datetime
from scipy.interpolate import interp1d

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, \
    QRadioButton, QLineEdit, QPushButton
from PyQt5.QtCore import pyqtSignal, pyqtSlot

import pyqtgraph as pg

class DateTimeAxis(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        strings = []
        for v in values:
            val = datetime.datetime.fromtimestamp(v).strftime('%H:%M:%S')
            strings.append(val)
        return strings

class Channel(QWidget):
    # emits itself and the new value
    _set_signal = pyqtSignal(object, object)

    # emits device and channel
    _pin_signal = pyqtSignal(object, object)

    def __init__(self, name='', label='', upper_limit=0.0, lower_limit=0.0, data_type=float, unit="",
        scaling=1.0, scaling_read=None, mode="both", display_order=0, 
        display_mode="f", precision=2, default_value=0.0):

        super().__init__()
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
        self._display_order = display_order

        # The device this channel belongs to will be set during add_channel().
        self._parent_device = None  
        self._displayformat = ".{}{}".format(precision, display_mode)
        self._precision = precision
        self._display_mode = display_mode

        self._locked = False

        self._pages = ['overview']

        # overview widget
        gb = QGroupBox(self._label)
        self._overview_widget = gb
        self._unit_labels = []
        self._write_widget = None
        self._read_widget = None

        # plot widget
        gb_plot = QGroupBox()
        gb_plot.setMinimumSize(350, 300)
        
        dateaxis = DateTimeAxis(orientation='bottom')
        plotwidget = pg.PlotWidget(axisItems={'bottom': dateaxis})

        vbox = QVBoxLayout()
        gb_plot.setLayout(vbox)
        hbox = QHBoxLayout()
        hbox.addStretch()
        btnPin = QPushButton('Pin')
        btnPin.clicked.connect(self.set_pin_callback)
        hbox.addWidget(btnPin)
        hbox.addStretch()
        vbox.addWidget(plotwidget)
        vbox.addLayout(hbox)
        self._plot_widget = gb_plot

        self._plot_curve = plotwidget.plot(pen='r', axisItems={'bottom': dateaxis})

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
                lblUnit = QLabel(self._unit)
                self._unit_labels.append(lblUnit)
                txtWrite = QLineEdit(str(self._lower_limit))
                txtWrite.returnPressed.connect(self.set_value_callback)
                self._write_widget = txtWrite

                hbox_write.addWidget(txtWrite)
                hbox_write.addWidget(lblUnit)
                vbox_readwrite.addLayout(hbox_write)

            if self._mode in ['read', 'both']:
                # add readonly second row
                hbox_read = QHBoxLayout()
                lblUnit = QLabel(self._unit)
                self._unit_labels.append(lblUnit)
                txtRead = QLineEdit()
                txtRead.setDisabled(True)
                self._read_widget = txtRead

                hbox_read.addWidget(txtRead)
                hbox_read.addWidget(lblUnit)
                vbox_readwrite.addLayout(hbox_read)

    @staticmethod
    def user_edit_properties():
    # this function tells the gui which properties can be edited
    # during run time. Any key in this list needs to have a getter 
    # and setter method, and must be decorated with 
    # @property and @<name>.setter

        return {
            'name':          {'display_name': 'Name', 
                'display_order': 1, 'type': str},
            'label':         {'display_name': 'Label', 
                'display_order': 2, 'type': str},
            'unit':          {'display_name': 'Unit', 
                'display_order': 3, 'type': str},
            'scaling':       {'display_name': 'Scaling', 
                'display_order': 4, 'type': float},
            'precision':     {'display_name': 'Precision', 
                'display_order': 5, 'type': int},
            'display_mode':  {'display_name': 'Display Mode', 
                'display_order': 6, 'type': str},
            'lower_limit':   {'display_name': 'Lower Limit', 
                'display_order': 7, 'type': None},
            'upper_limit':   {'display_name': 'Upper Limit', 
                'display_order': 8, 'type': None},
            'data_type':     {'display_name': 'Data Type', 
                'display_order': 9, 'type': type},
            'mode':          {'display_name': 'Mode', 
                'display_order': 10, 'type': str},
            'display_order': {'display_name': 'Display Order', 
                'display_order': 11, 'type': int},
            }

    def update(self):
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
        if self._data_type != bool:
            try:
                val = self._data_type(self._write_widget.text())
            except:
                print('bad value entered')
            return

            self._write_widget.setText(str(self._data_type(val)))
            self._set_signal.emit(self, val)
        else:
            self._set_signal.emit(self, self._write_widget.isChecked())

    @pyqtSlot()
    def set_pin_callback(self):
        self._pin_signal.emit(self.parent_device, self)

    @property
    def precision(self):
        return self._precision

    @precision.setter
    def precision(self, precision):
        self._precision = precision
        self._displayformat = '.{}{}'.format(self._precision, self._display_mode)

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
        self.update()

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value
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
            'display_order': self._display_order
            }

        return properties #json.dumps(properties)

    @staticmethod
    def load_from_json(channel_json):

       properties = json.loads(channel_json)

       data_type_str = properties['data_type']

       properties['data_type'] = eval(data_type_str.split("'")[1])

       return Channel(**properties)

