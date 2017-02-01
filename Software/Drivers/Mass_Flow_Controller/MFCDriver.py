from __future__ import division
import binascii
import json

def calculate_checksum(message):
    checksum = sum(map(ord, [x for x in message]))
    return hex(checksum)[-2:].upper()


def get_error(error_code):
    error_dict = {'01': "Checksum error", '10': "Syntax error", '11': "Data length error", '12': "Invalid data",
                  '13': "Invalid operating mode", '14': "Invalid action", '15': "Invalid gas",
                  '16': "Invalid control mode", '17': "Invalid command", '24': "Calibration error",
                  '25': "Flow too large", '27': "Too many gases in gas table", '28': "Flow cal error; valve not open",
                  '98': "Internal device error", '99': "Internal device error"}
    return error_dict[str(error_code)]


#def get_command(category, for_what):
#    setup_dict = {"baud_rate": 'CC', "address": 'CA', "user_tag": 'UT', "operating_mode": 'OM',
#                  "programmed_gas_table_size": 'GTS', "programmed_gas_table_search": 'GL',
#                  "activate_programmed_gas": 'PG', "flow_units": 'U', "full_scale_range": 'FS', "wink": 'WK',
#                  "run_hours_meter": 'RH'}
#    flow_sensor_dict = {"auto_zero": "AZ", "high_trip_point": "H", "high_high_trip_point": "HH", "low_trip_point": "L",
#                        "low_low_trip_point": "LL", "indicated_flow_rate_percent": "F",
#                        "indicated_flow_rate_units": "FX", "flow_totalizer": "FT"}
#    informational_dict = {"status": "T", "status_reset": "SR", "gas_name_or_number_search": "GN",
#                          "gas_code_number": "SGN", "device_type": "DT", "valve_type": "VT",
#                          "valve_power_off_state": "VPO", "manafacturer": "MF", "model_designation": "MD",
#                          "serial_number": "SN", "internal_temperature": "TA", "standard_temperature": "ST",
#                          "standard_pressure": "SP"}
#    control_dict = {"control_mode": "CM", "set_point_percent": "S", "set_point_units": "SX", "freeze_mode": "FM",
#                    "softstart_rate": "SS", "valve_override": "VO", "valve_drive_level": "VD"}
#
#    if category == "info":
#        return informational_dict[for_what]
#    elif category == "flow_sensor":
#        return flow_sensor_dict[for_what]
#    elif category == "control":
#        return control_dict[for_what]
#    elif category == "setup":
#        return setup_dict[for_what]
#
    # return error_dict[for_what]
def get_command(what):
    command_dict = {"baud_rate": 'CC', "address": 'CA', "user_tag": 'UT', "operating_mode": 'OM',
                  "programmed_gas_table_size": 'GTS', "programmed_gas_table_search": 'GL',
                  "activate_programmed_gas": 'PG', "flow_units": 'U', "full_scale_range": 'FS', "wink": 'WK',
                  "run_hours_meter": 'RH', "auto_zero": "AZ", "high_trip_point": "H", "high_high_trip_point": "HH",
                  "low_trip_point": "L", "low_low_trip_point": "LL", "indicated_flow_rate_percent": "F", 
                  "indicated_flow_rate_units": "FX", "flow_totalizer": "FT", "status": "T", "status_reset": "SR", 
                  "gas_name_or_number_search": "GN","gas_code_number": "SGN", "device_type": "DT", "valve_type": "VT",
                   "valve_power_off_state": "VPO", "manafacturer": "MF", "model_designation": "MD",
                   "serial_number": "SN", "internal_temperature": "TA", "standard_temperature": "ST",
                    "standard_pressure": "SP", "control_mode": "CM", "set_point_percent": "S", "set_point_units": "SX", 
                    "freeze_mode": "FM", "softstart_rate": "SS", "valve_override": "VO", "valve_drive_level": "VD"}
    return command_dict[what]

def parse_message(message):
    assert message[0:3] == "@" * 3
    assert message[3:6] == "0" * 3
    assert message[-3] == ";"
    checksum = message[-2:]
    assert (checksum == calculate_checksum(message[2:-2])) or (checksum == "FF")

    response = message[6:9]

    if (response == "ACK"):
        response_value = message[9:-3]
        return {'acknowledged': True, 'value': response_value}
    elif (response == "NAK"):
        response_value = message[9:-3]
        return {'acknowledged': False, 'value': response_value}


def build_message(msg_type, device_address="254", for_what="wink", data_variable=None):
    """Summary

    Args:
        device_address (str, optional): Description
        type (TYPE): Should either be "query" or "set".

    Returns:
        TYPE: Description
    """
    start_msg = "@"
    msg = start_msg
    msg += str(device_address)

    assert (len(str(device_address)) == 3)

    msg += get_command(for_what)

    if msg_type == False:
        msg += "?"
    elif msg_type == True:
        msg += "!"
    else:
        raise Exception("Error: Unknown message type.")

    if data_variable is not None:
        msg += data_variable

    msg += ";"

    # print msg, calculate_checksum(msg)

    msg += calculate_checksum(msg)
    msg = "@@" + msg

    return msg


def tests():
    assert calculate_checksum("@001UT!TEST;") == "16"

class MFCDriver:

    def translate_gui_to_driver(self, server_to_driver):
    
        num_of_mesg = len(server_to_driver['channel_ids'])
        assert num_of_mesg == len(server_to_driver['precisions'])
        assert server_to_driver['device_driver']=="mfc"
        
        drivers_response_to_server=[]
    
        for i in range(0,num_of_mesg):
            drivers_response_to_server.append(build_message(msg_type=server_to_driver['set'], device_address=server_to_driver['device_id'], for_what=server_to_driver['channel_ids'][i]))
    
        return drivers_response_to_server
    
    def translate_driver_to_gui(self, response_string):
    
        drivers_response_to_server=[]
        response=response_string['response']
        precision=response_string['precision']
        num_of_mesg=len(response)
    
        for i in range(0,num_of_mesg):
            x = parse_message(response[i])  
            if x['acknowledged']==True:
                concat_value = '{0:.{1}f}'.format(float(x['value']
    ),precision[i])
                drivers_response_to_server.append(concat_value)
            if x['acknowledged']==False:
                drivers_response_to_server.append("Error"+x['value'])
            
        return drivers_response_to_server
    

message_to_driver={"channel_ids": ["wink", "wink", "wink","wink"], "device_driver": "mfc", "set": False, "precisions": [1, 2, 3, 4], "device_id": "254"}
response_from_driver = {'response': ["@@@000ACK90.00;FF", "@@@000ACK90.00;FF", "@@@000ACK90.00;FF", "@@@000NAK34;FF"], 'precision': [1,2,3,4]}
if __name__ == '__main__':
    tests()

#    message_to_driver_string='{"channel_ids": ["wink", "wink", "wink","wink"], "device_driver": "mfc", "set": false, "precisions": [1, 2, 3, 4], "device_id": "254"}'

#    message_to_driver=json.loads(message_to_driver_string)

    message_to_driver={"channel_ids": ["wink", "wink", "wink","wink"], "device_driver": "mfc", "set": False, "precisions": [1, 2, 3, 4], "device_id": "254"}
 

    response_from_driver = {'response': ["@@@000ACK90.00;FF", "@@@000ACK90.00;FF", "@@@000ACK90.00;FF", "@@@000NAK34;FF"], 'precision': [1,2,3,4]}
    
    x=MFCDriver()
    print x.translate_gui_to_driver(message_to_driver)
    print x.translate_driver_to_gui(response_from_driver)
    #print parse_message("@@@000ACKCR,H,HH;FF")
    # print parse_message(message="@@@000ACK9600;A9")
    # print parse_message(message="@@@000ACK10;FF")
    # print parse_message(message="@@@000ACKAr,4,500,SCCM;FF")
