import json
from scipy.interpolate import interp1d


class Channel:
    def __init__(self, name, label, upper_limit, lower_limit, data_type, unit="",
                 scaling=1.0, scaling_read=None, mode="both", display_order=0, displayformat="f",
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
        self._scaling_read = scaling_read
        self._value = default_value
        self._mode = mode
        self._display_order = display_order
        self._arduino_id = None
        self._parent_device = None  # The device this channel belongs to will be set during add_channel().
        self._displayformat = ".{}{}".format(precision, displayformat)
        self._precision = precision

        self._timeout = 1.0  # (s)
        self._locked = False

    def __repr__(self):
        return 'Channel {}, label={}, data_type={}, unit={}, mode={}'.format(self._name, self._label, self._data_type, self._unit, self._mode)

    @property
    def precision(self):
        return self._precision

    @precision.setter
    def precision(self, precision):
        self._precision = precision

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
    def arduino_id(self):
        return self._arduino_id

    @arduino_id.setter
    def arduino_id(self, arduino_id):
        self._arduino_id = arduino_id

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

    @property
    def parent_device(self):
        return self._parent_device

    @parent_device.setter
    def parent_device(self, device):
        self._parent_device = device

    @property
    def label(self):
        return self._label

    @property
    def name(self):
        return self._name

    @property
    def upper_limit(self):
        return self._upper_limit

    @property
    def lower_limit(self):
        return self._lower_limit

    @property
    def data_type(self):
        return self._data_type

    @property
    def unit(self):
        return self._unit

    @property
    def scaling(self):
        return self._scaling

    def scaling_read(self):
        return self._scaling_read

    @property
    def mode(self):
        return self._mode

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

