from ArduinoDriver import *
from MFCDriver import *

"""
The driver mapping contains the information needed for the DeviceDriver class and the RasPiServer to
use the respective translation functions from GUI to Device and back and the correct baud rate
"""
driver_mapping = {'Arduino': {'driver': ArduinoDriver,
                              'baud_rate': 115200
                              },
                  'RS485': {'driver': MFCDriver,
                            'baud_rate': 9600
                            }
                  }
