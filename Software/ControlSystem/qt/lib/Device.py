import json
import time
from .Channel import Channel

class Device:
    def __init__(self, name, arduino_id, label="",
                 channels=None, debug=False, driver='arduino'):

        self.debug = debug

        self._name = name
        self._label = label
        self._poll_count = 0
        self._poll_start_time = 0.0

        self._channels = {}  # This is a dictionary of channels with their names as keys.
        if channels is not None:
            self._channels = channels

        self._arduino_id = arduino_id
        self._driver = driver

        # Parent will be set during add_channel in control system
        self._parent = None
        self._locked = False

    @property
    def arduino_id(self):
        return self._arduino_id

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

    def add_one_to_poll_count(self):
        self._poll_count += 1

    def reset_poll_count(self):
        self._poll_count = 0

    @property
    def poll_count(self):
        return self._poll_count

    def poll_start_time(self):
        return self._poll_start_time

    def reset_poll_start_time(self):
        self._poll_start_time = time.time()

    @property
    def name(self):
        return self._name

    @property
    def label(self):
        return self._label

    @property
    def channels(self):
        return self._channels

    def get_channel_by_name(self, channel_name):
        return self._channels[channel_name]

    def add_channel(self, channel):
        """
        Adds a channel to the current device. Since the _channels property of the Device class is a
        dictionary with channel names as its keys, this takes Channel.name() as the key for the channel being added.
        """
        channel.arduino_id = self._arduino_id
        channel.parent_device = self
        self._channels[channel.name] = channel

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
        properties = {"name": self._name,
                      "label": self._label,
                      "arduino_id": self._arduino_id,
                      "on_overview_page": self._on_overview_page,
                      "channels": {}
                      }

        for channel_name, channel in self._channels.items():
            properties['channels'][channel_name] = channel.get_json()

        return json.dumps(properties)

    def write_json(self, filename):
        myjson = self.get_json()

        with open(filename, "wb") as f:
            f.write(myjson)

    @staticmethod
    def load_from_json(filename):
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
