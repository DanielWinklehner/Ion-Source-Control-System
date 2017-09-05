from __future__ import division


class REKDriver:
    def __init__(self):
        self.command_dict = {'VGET': 'VGET', 'VSET': 'VSET',
                             'IGET': 'IGET', 'ISET': 'ISET',
                             'SW': 'SW'}
                
        '''
                "identification": 'IDN', "software_revision": 'REV', "serial_number": 'SN',
                             "output_voltage": 'PV', "output_current": 'PC', "read_output_voltage": 'MV',
                             "read_output_current": 'MC', "output": 'OUT', "output_state": 'OUT?',
                             "PV": "PV", "PC": "PC", "OUT": "OUT", "MV": "MV", "MC":"MC"}
        '''

    @staticmethod
    def get_error(error_code):
        error_dict = {'01': "Checksum error", '10': "Syntax error", '11': "Data length error", '12': "Invalid data",
                      '13': "Invalid operating mode", '14': "Invalid action", '15': "Invalid gas",
                      '16': "Invalid control mode", '17': "Invalid command", '24': "Calibration error",
                      '25': "Flow too large", '27': "Too many gases in gas table",
                      '28': "Flow cal error; valve not open",
                      '98': "Internal device error", '99': "Internal device error"}
        return error_dict[str(error_code)]

    def tests(self):
        assert self.calculate_checksum("@001UT!TEST;") == "16"

    @staticmethod
    def calculate_checksum(message):

        checksum = sum(map(ord, [message_part for message_part in message]))

        return hex(checksum)[-2:].upper()

    def parse_message(self, _message):
        message = _message.strip().split('=')[1]

        if message != '':
            return {'acknowledged': True, 'value': float(message)}
        else:
            return {'acknowledged': False, 'value': False}

    def build_message(self, msg_type, for_what="OUT", value=None, data_type=None):

        msg = '#1 '
        msg += self.command_dict[for_what]

        if value is not None:
            # Handle the numerical values
            if self.command_dict[for_what] == 'SW':
                if value == 1.0:
                    msg += '1'
                else:
                    msg += '0'
            elif 'float' in data_type:
                msg += " {}".format(str(value))
            else:
                pass

        msg += ' \r'

        return msg

    @staticmethod
    def get_driver_name():
        return "rek"

    def translate_gui_to_device(self, server_to_driver):

        # --- For reference: --- #
        # device_data = {'device_driver': device_driver_name,
        #                'device_id': device_id,
        #                'locked_by_server': False,
        #                'channel_ids': [channel_ids],
        #                'precisions': [precisions],
        #                'values': [values],
        #                'data_types': [types]}

        num_of_mesg = len(server_to_driver['channel_ids'])
        assert num_of_mesg == len(server_to_driver['precisions'])
        assert server_to_driver['device_driver'] == "Prolific"

        drivers_response_to_server = ['#1 REN \r']

        for i in range(num_of_mesg):

            drivers_response_to_server.append(
                self.build_message(msg_type=server_to_driver['set'],
                                   for_what=server_to_driver['channel_ids'][i],
                                   value=server_to_driver['values'][i],
                                   data_type=server_to_driver['data_types'][i]))

        return drivers_response_to_server

    def translate_device_to_gui(self, responses, device_data):
        drivers_response_to_server = {}

        for response, channel_id in zip(responses[1:], device_data['channel_ids']):    
            parsed_message = self.parse_message(response)
            if parsed_message['acknowledged']:
                drivers_response_to_server[channel_id] = float(parsed_message['value'])
            else:
                drivers_response_to_server[channel_id] = "Error: " + self.get_error(parsed_message['value'])

        return drivers_response_to_server


if __name__ == '__main__':
    message_to_driver = {"channel_ids": ["PV", "PC", "OUT"], "device_driver": "tdk", "set": False,
                         "precisions": [1, 2, 3], "device_id": "254"}

    response_from_driver = ["OK", "OK", "OK"]

    x = REKDriver()
    x.tests()
    print(x.translate_gui_to_device(message_to_driver))
    print(x.translate_device_to_gui(response_from_driver, message_to_driver))
