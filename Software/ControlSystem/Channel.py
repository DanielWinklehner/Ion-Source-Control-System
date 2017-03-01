from __future__ import division

# import time
# import sys
# import glob
import json
import GUIWidgets
from scipy.interpolate import interp1d


class Channel:
    def __init__(self, name, label, upper_limit, lower_limit, data_type, unit="",
                 scaling=1.0, mode="both", display_order=0, displayformat="f",
                 precision=2, default_value=0.0):

        """Summary
        
        Args:
            name (TYPE): Description
            label (TYPE): Description
            upper_limit (TYPE): Description
            lower_limit (TYPE): Description
            data_type (TYPE): Description
            unit (str, optional): Description
            scaling (float, optional): Scaling is applied when the channel communicates with the server.
            mode (str, optional): Description
            display_order (int, optional): Description
            # displayformat (str, optional): Description
        
        Deleted Parameters:
            message_header (TYPE): Description
        """
        self._name = name
        self._label = label
        self._upper_limit = upper_limit
        self._lower_limit = lower_limit
        self._data_type = data_type
        self._unit = unit
        self._scaling = scaling
        self._value = default_value
        self._mode = mode
        self._arduino_id = None
        self._parent_device = None  # The device this channel belongs to will be set during add_channel().
        self._initialized = False
        self._overview_page_display = None
        self._displayformat = ".{}{}".format(precision, displayformat)
        self._precision = precision

        self._timeout = 1.0  # (s)

        self._display_order = display_order  # Higher number on the top.

        self._locked = False

    def add_channel_to_gui(self):
        """
        Adds a device to the GUI
        :return:
        """

        parent_device = self._parent_device

        # Add channels to the devices GUI overview page frame if desired
        if parent_device.is_on_overview_page():
            # Create a display

            if self._data_type == bool:

                self._overview_page_display = GUIWidgets.FrontPageDisplayBool(name=self._label,
                                                                              set_flag=(self._mode == "write"),
                                                                              parent_channel=self)

            else:

                # Create a display
                self._overview_page_display = GUIWidgets.FrontPageDisplayValue(name=self._label,
                                                                               unit=self._unit,
                                                                               displayformat=self._displayformat,
                                                                               mode=self._mode,
                                                                               parent_channel=self)

            parent_device.get_overview_frame().pack_start(self._overview_page_display, False, False, 4)

        return 0

    def get_precision(self):
        return self._precision

    def set_precision(self, precision):
        self._precision = precision

    def lock(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        if not self._locked:
            if not self._overview_page_display.locked():
                self._overview_page_display.lock()
            self._locked = True

    def unlock(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        if self._locked:
            if self._overview_page_display.locked():
                self._overview_page_display.unlock()
            self._locked = False

    def locked(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._locked

    def get_arduino_id(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._arduino_id

    def get_overview_page_display(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._overview_page_display

    def get_value(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._value

    def get_display_order(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._display_order

    def initialized(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._initialized

    def initialize(self):
        """
        Initializes the channel
        :return:set_parent
        """

        self.add_channel_to_gui()

        self._initialized = True

        return 0

    @staticmethod
    def reinitialize(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        pass

    def get_parent_device(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._parent_device

    def set_parent_device(self, device):
        """Summary
        
        Args:
            device (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        self._parent_device = device

    def set_arduino_id(self, arduino_id):
        """Summary
        
        Args:
            arduino_id (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        self._arduino_id = arduino_id

    def label(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._label

    def name(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._name

    def upper_limit(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._upper_limit

    def lower_limit(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._lower_limit

    def data_type(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._data_type

    def unit(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._unit

    def scaling(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._scaling

    def mode(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        return self._mode

    def get_json(self):

        properties = {'name': self._name,
                      'label': self._label,
                      'upper_limit': self._upper_limit,
                      'lower_limit': self._lower_limit,
                      'data_type': str(self._data_type),
                      'unit': self._unit,
                      'scaling': self._scaling,
                      'mode': self._mode,
                      'displayformat': self._displayformat,
                      'display_order': self._display_order
                      }

        return json.dumps(properties)
    
    @staticmethod
    def load_from_json(channel_json):

        properties = json.loads(channel_json)

        data_type_str = properties['data_type']

        properties['data_type'] = eval(data_type_str.split("'")[1])

        return Channel(**properties)

    def read_value(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        # print "Reading value!"

        if self._locked:
            return None

        '''
        if self._mode == "write":
            raise ValueError("ERROR: You are trying to read in values from a write-only channel!")
        '''
        
        return self._value

    def set_value(self, value_to_set):
        """Summary
        
        Args:
            value_to_set (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        if self._locked:
            return None

        self._value = value_to_set
