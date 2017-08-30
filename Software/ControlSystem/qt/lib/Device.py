import json
import time

from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QLabel, QFrame

from .Channel import Channel

class Device:
    def __init__(self, name, arduino_id, label="", channels=None, driver='Arduino'):

        self._name = name
        self._label = label

        self._channels = {}  # This is a dictionary of channels with their names as keys.
        if channels is not None:
            self._channels = channels

        self._arduino_id = arduino_id
        self._driver = driver

        self._parent = None
        self._locked = False

        self._pages = ['overview']

        # create gui representation
        fr = QFrame()
        vbox_main = QVBoxLayout()
        fr.setLayout(vbox_main)
        gb = QGroupBox(self._label)
        vbox_main.addWidget(gb)
        vbox_main.addStretch()

        vbox_gb = QVBoxLayout()
        gb.setLayout(vbox_gb)

        self._gblayout = vbox_gb
        self._overview_widget = fr
        self._error_message = ''
        self._hasError = False
    
    @staticmethod
    def user_edit_properties():
        """ Returns list of properties that should be user-editable 
            key name must match a propertyi of this class """
            
        return {'name':     {'display_name': 'Name', 'display_order': 1},
                'id':       {'display_name': 'Device ID', 'display_order': 2},
                'label':    {'display_name': 'Label', 'display_order': 3},
                'driver':   {'display_name': 'Driver', 'display_order': 4},
                }


    def update(self):
        chlist = [ch for chname, ch in reversed(sorted(self._channels.items(), 
                                                        key=lambda x: x[1].display_order))]
        for idx, ch in enumerate(chlist):
            if ch._overview_widget.parent() != self._gblayout.parent():
                self._gblayout.insertWidget(idx, ch._overview_widget)

    @property
    def error_message(self):
        return self._error_message

    @error_message.setter
    def error_message(self, value):
        self._error_message = value
       
        if self._error_message != '':
            if not self._hasError:
                self._hasError = True
                txtError = QLabel('<font color="red">{}</font>'.format(self._error_message))
                self._overview_widget.layout().insertWidget(0, txtError)
                self._gblayout.parent().setEnabled(False)
                for name, ch in self.channels.items():
                    ch.update()
        else:
            if self._hasError:
                self._hasError = False
                txtError = self._overview_widget.layout().takeAt(0).widget()
                txtError.deleteLater()
                self._gblayout.parent().setEnabled(True)
                for name, ch in self.channels.items():
                    ch.update()
      

    @property
    def arduino_id(self):
        return self._arduino_id

    @arduino_id.setter
    def arduino_id(self, value):
        self._arduino_id = value

    @property
    def driver(self):
        return self._driver
    
    @driver.setter
    def driver(self, value):
        self._driver = value

    @property
    def parent(self):
        return parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def label(self):
        return self._label
    
    @label.setter
    def label(self, value):
        self._label = value
        if self._gblayout.parent().title() != self._label:
            self._gblayout.parent().setTitle(self._label)
            for channel_name, channel in self.channels.items():
                channel.update()


    @property
    def pages(self):
        return self._pages

    def add_page(self, value):
        self._pages.append(value)

    @property
    def channels(self):
        return self._channels

    def get_channel_by_name(self, channel_name):
        try:
            return self._channels[channel_name]
        except:
            return None

    def add_channel(self, channel):
        channel.arduino_id = self._arduino_id
        channel.parent_device = self
        self._channels[channel.name] = channel
        self.update()

    def lock(self):
        if not self._locked:
            for channel_name, channel in self._channels.items():
                channel.lock()
            self._locked = True

    def unlock(self):
        if self._locked:
            for channel_name, channel in self._channels.items():
                channel.unlock()
            self._locked = False

    @property
    def locked(self):
        return self._locked

    def get_json(self):
        """ Gets a serializable representation of this device """
        properties = {'name': self._name,
                      'label': self._label,
                      'arduino_id': self._arduino_id,
                      'driver': self._driver,
                      'channels': {}
                      }

        for channel_name, channel in self._channels.items():
            properties['channels'][channel_name] = channel.get_json()

        return properties #json.dumps(properties)

    def write_json(self, filename):
        myjson = self.get_json()

        with open(filename, "wb") as f:
            f.write(myjson)

    @staticmethod
    def load_from_json(string):
        with open(filename, "rb") as f:
            data = json.load(f)

        filtered_params = {}
        for key, value in data.items():
            if not key == "channels":
                filtered_params[key] = value

        device = Device(**filtered_params)

        for channel_name in data['channels']:
            channel_json = data['channels'][channel_name]
            ch = Channel.load_from_json(channel_json)

            device.add_channel(ch)

        return device
