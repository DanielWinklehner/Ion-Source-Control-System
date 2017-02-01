from __future__ import division
import json
import time
import GUIWidgets
from Channel import Channel


class Device:
    def __init__(self, name, arduino_id, label="", channels=None, on_overview_page=False, debug=False):

        self.debug = debug

        self._name = name
        self._label = label
        self._poll_count = 0
        self._poll_start_time = 0.0

        self._channels = {}  # This is a dictionary of channels with their names as keys.
        if channels is not None:
            self._channels = channels

        self._arduino_id = arduino_id
        self._driver = 'arduino'
        # self._front_page_widgets = {}  # This is a dictionary
        # of FrontPageDisplay widgets. key = channel_name, value = FrontPageDisplay.
        self._on_overview_page = on_overview_page

        # Parent will be set during add_channel in control system
        self._parent = None

        self._initialized = False
        self._overview_frame = None

        self._locked = False

    def get_arduino_id(self):
        return self._arduino_id

    def get_driver(self):
        return self._driver

    def set_driver(self, driver):
        self._driver = driver

    def get_overview_frame(self):
        return self._overview_frame

    def set_parent(self, parent):
        self._parent = parent

    def add_one_to_poll_count(self):
        self._poll_count += 1

    def reset_poll_count(self):
        self._poll_count = 0

    @property
    def poll_count(self):
        return self._poll_count

    @property
    def poll_start_time(self):
        return self._poll_start_time

    def reset_poll_start_time(self):
        self._poll_start_time = time.time()

    def name(self):
        return self._name

    def label(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self._label

    def channels(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self._channels

    def get_channel_by_name(self, channel_name):
        """Summary

        Args:
            channel_name (TYPE): Description

        Returns:
            TYPE: Description
        """
        return self._channels[channel_name]

    def add_channel(self, channel):
        """
        Adds a channel to the current device. Since the _channels property of the Device class is a
        dictionary with channel names as its keys, this takes Channel.name() as the key for the channel being added.

        Args:
            channel (Channel): Channel object to add.

        Returns:
            None
        """
        channel.set_arduino_id(self._arduino_id)
        channel.set_parent_device(self)
        self._channels[channel.name()] = channel

    def add_device_to_gui(self):
        """
        Adds a device to the GUI
        :return:
        """

        # Add device to GUI overview page if desired
        if self._on_overview_page:

            if self.debug:
                print("Adding a device to the overview page.")

            # Create a frame
            self._overview_frame = GUIWidgets.FrontPageDeviceFrame(label=self._label)

            # Add the frame to the layout
            self._parent.get_overview_grid().add(self._overview_frame)

        # TODO: Adding the device to its main page and to the settings page

        return 0

    def initialized(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self._initialized

    def reinitialize_channels(self):

        for channel_name, channel in self._channels.items():

            if channel.initialized():

                if self.debug:

                    print("Reinitializing channel {}".format(channel.name()))

                channel.reinitialize()

            else:

                if self.debug:

                    print("Initializing channel {}".format(channel.name()))

                channel.initialize()

    def reinitialize(self):
        """Summary

        Returns:
            TYPE: Description
        """
        self._initialized = False

        try:

            # Also reinitialize all channels associated with this device.
            for channel_name, channel in self._channels.items():
                if channel.initialized():
                    channel.reinitialize()
                else:
                    channel.initialize()

            self._initialized = True

        except Exception as e:

            print(e)

        except SystemExit as e2:

            print("Exception: Got a system exit: {}".format(e2))

            return

    def initialize(self):
        """
        Initializes the current device. This means, this method goes through all the channels associated
        with this device and creates widgets for all of them.

        Returns:
            TYPE: Description
        """

        # First, we check if there already is a SerialCOM object associated with the unique
        # Arduino ID, if not we create one.

        # Add infobar to the arduino_vbox on the side of the GUI
        vbox = self._parent.get_arduino_vbox()

        infobar = GUIWidgets.FrontPageDisplayValue(name="{}. Polling rate =".format(self._label),
                                                   displayformat=".1f",
                                                   unit="Hz")

        vbox.pack_start(infobar, False, False, 4)
        self._parent.add_arduino_status_bar(self._arduino_id, infobar)

        # Have to add device first so that there is a frame to add to
        self.add_device_to_gui()

        # Create a list of tuples (display_order, channel).
        all_channels = []
        for channel_name, channel in self._channels.items():
            all_channels.append((channel.get_display_order(), channel))

        all_channels.sort(key=lambda tup: tup[0], reverse=True)

        for display_order, channel in all_channels:
            channel.initialize()

        # Initialize rest of the channels (i.e. channels without displayorder).
        for ch_name, ch in self._channels.items():
            if not ch.initialized():
                ch.initialize()

        self._initialized = True

    def lock(self):
        """Summary

        Returns:
            TYPE: Description
        """
        if not self._locked:

            for channel_name, channel in self._channels.items():

                channel.lock()

            self._locked = True

    def unlock(self):
        """Summary

        Returns:
            TYPE: Description
        """
        if self._locked:

            for channel_name, channel in self._channels.items():

                channel.unlock()

            self._locked = False

    def locked(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self._locked

    def is_on_overview_page(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self._on_overview_page

    def set_overview_page_presence(self, value):
        """Summary

        Args:
            value (TYPE): Description

        Returns:
            TYPE: Description
        """
        self._on_overview_page = value

    # def front_page_widgets(self):
    #     return self._front_page_widgets

    def get_json(self):
        """Summary

        Returns:
            TYPE: Description
        """
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
        """Summary

        Args:
            filename (TYPE): Description

        Returns:
            TYPE: Description
        """
        myjson = self.get_json()

        with open(filename, "wb") as f:

            f.write(myjson)

    @staticmethod
    def load_from_json(filename):
        """Summary

        Args:
            filename (TYPE): Description

        Returns:
            TYPE: Description
        """
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
