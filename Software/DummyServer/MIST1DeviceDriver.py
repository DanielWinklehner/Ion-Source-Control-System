class MIST1DeviceDriver:
    def __init__(self,
                 driver_name=None):

        self._driver_name = driver_name
        self._driver = None

        self.load_driver()

    def load_driver(self):
        self._driver = None

    def translate_gui_to_device(self, data):
        return self._driver.translate_gui_to_device(self, data)

    def translate_device_to_gui(self, data):
        return self._driver.translate_device_to_gui(self, data)
