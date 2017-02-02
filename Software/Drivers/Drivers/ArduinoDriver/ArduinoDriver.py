from __future__ import division
import ArduinoMessages

class ArduinoDriver:
    def __init__(self):
        pass

    @staticmethod
    def get_driver_name():
        return "arduino"

    def translate_gui_to_device(self, data):
        
        if data['set']:
            return ArduinoMessages.build_set_message([data['channel_name']], [data['value']])
        else:
            # Query message.
            return ArduinoMessages.build_query_message(data['channel_ids'], data['precisions'])
            

        return [] 

    def translate_device_to_gui(self, data):
        return ArduinoMessages.parse_arduino_output_message(data)



