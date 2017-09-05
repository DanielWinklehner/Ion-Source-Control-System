from ArduinoDriver import *
from MFCDriver import *
from TDKDriver import *

"""
The driver mapping contains the information needed for the DeviceDriver class and the RasPiServer to
use the respective translation functions from GUI to Device and back and the correct baud rate
"""
driver_mapping = {'Arduino': {'driver': ArduinoDriver,
                              'baud_rate': 115200
                             },
                  'RS485': {'driver': MFCDriver,
                            'baud_rate': 9600
                           },
                  'Teensy': {'driver': ArduinoDriver,
                             'baud_rate': 115200
                            },
                  'FT232R': {'driver': TDKDriver,
                             'baud_rate': 19200
                            },
                  'Prolific': {'driver': REKDriver,
                               'baud_rate': 9600
                            },
                 }
