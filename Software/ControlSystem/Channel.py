from __future__ import division

# import time
# import sys
# import glob
import json
import GUIWidgets


class Channel:
    def __init__(self, name, label, upper_limit, lower_limit, data_type, unit="",
                 scaling=1., mode="both", display_order=0, displayformat=".2f",
                 precision=2, default_value=0.0):

        """Summary
        
        Args:
            name (TYPE): Description
            label (TYPE): Description
            upper_limit (TYPE): Description
            lower_limit (TYPE): Description
            data_type (TYPE): Description
            unit (str, optional): Description
            scaling (float, optional): Description
            mode (str, optional): Description
            display_order (int, optional): Description
            displayformat (str, optional): Description
        
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
        self._displayformat = displayformat
        self._precision = precision

        self._timeout = 2   # In seconds.

        self._display_order = display_order  # Higher number on the top.

        self._locked = False

    def add_channel_to_gui(self):
        """
        Adds a device to the GUI
        :return:
        """

        parent_device = self._parent_device

        set_flag = True
        if self._mode == "read":
            set_flag = False

        # Add channels to the devices GUI overview page frame if desired
        if parent_device.is_on_overview_page():
            # Create a display

            if self._data_type == bool:

                self._overview_page_display = GUIWidgets.FrontPageDisplayBool(name=self._label,
                                                                              set_flag=set_flag,
                                                                              parent_channel=self)

            else:

                # Create a display
                self._overview_page_display = GUIWidgets.FrontPageDisplayValue(name=self._label,
                                                                               unit=self._unit,
                                                                               displayformat=self._displayformat,
                                                                               set_flag=set_flag,
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
        properties = {}

        properties['name'] = self._name
        properties['label'] = self._label
        properties['upper_limit'] = self._upper_limit
        properties['lower_limit'] = self._lower_limit
        properties['data_type'] = str(self._data_type)
        properties['unit'] = self._unit
        properties['scaling'] = self._scaling
        properties['mode'] = self._mode
        properties['displayformat'] = self._displayformat
        properties['display_order'] = self._display_order

        return json.dumps(properties)
    
    @staticmethod
    def load_from_json(channel_json):

        properties = json.loads(channel_json)

        data_type_str = properties['data_type']

        properties['data_type'] = eval( data_type_str.split("'")[1] )

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

        '''
        # Build a query message.
        message = "query:{}={}".format(self._message_header, '?')


        try:
            # Send the query message.
            self._serial_com.send_message(message)

            # Read the Arduino's response.
            keyword, header, value = self.read_arduino_message()

            # Ideally, we should have all we need. But in case the first message sent
            # by the Arduino was dropped, keep querying until we get some response.

            start_time = time.time()
            while ( not (keyword == "output" and header == self._message_header) ) and (time.time() - start_time) <= self._timeout:  # THOUGHT: Maybe have a timeout?

                print "Trying again!"

                self._serial_com.send_message(message)

                # print "Message sent: ", message
                keyword, header, value = self.read_arduino_message()

            # print keyword, header, self._message_header, header == self._message_header

            # We have what we need.

            
            if len(str(value)) != 0:
                self._value = self._data_type(float(value)) # TODO: This is hacky. Fix this.
            else:
                self._value = None


        except Exception as e:
            self._value = None
            raise Exception(str(e))
            
        finally:
            return self._value
        '''

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

        # if self._mode == "read":
        #   raise ValueError("ERROR: You are trying to write values to a read-only channel!")

        # if type(value_to_set) == bool:
        #   value_to_set = int(value_to_set)



        '''
        # Build a set message to send to the Arduino.
        message = "set:{}={}".format(self._message_header, value_to_set)

        # Send the set message.
        self._serial_com.send_message(message)

        # We're probably set. But just listen for an "assigned" message to make sure the value was set properly.

        # Read the Arduino's response.
        keyword, header, value = self.read_arduino_message()

        # Repeat the set message until we get the "assigned" message back from Arduino.

        start_time = time.time()
        while ( not ((keyword == "assigned") and (header == self._message_header)) ) and (time.time() - start_time) <= self._timeout:  # THOUGHT: Maybe have a timeout?

            print "Did not work out the first time so trying again!"

            self._serial_com.send_message(message)
            keyword, header, value = self.read_arduino_message()

        if len(value) == 0:
            # This means there was a timeout.
            print "Timeout!"
            raise Exception("ERROR: Could not set value = {} for channel = {} because of a timeout!".format(value_to_set, self._name))

        # THOUGHT: Do we even need to "store" the value here as a class attribute?
        self._value = value
        '''

