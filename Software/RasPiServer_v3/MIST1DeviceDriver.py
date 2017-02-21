# import pkgutil
# import os
# import glob
# import imp
# import sys
# from traceback import print_tb
# import importlib
from Drivers import *


class MIST1DeviceDriver:
    def __init__(self,
                 driver_name=None):

        self._module_extensions = ('.py', '.pyc', '.pyo')

        self._driver_name = driver_name
        self._driver = None

        self.load_driver()

    def load_driver(self):
        self._driver = driver_mapping[self._driver_name]()

    def get_driver_name(self):
        return self._driver_name

    def translate_gui_to_device(self, data):
        return self._driver.translate_gui_to_device(data)

    def translate_device_to_gui(self, data, original_message):
        return self._driver.translate_device_to_gui(data, original_message)
