from __future__ import division
from mfc_driver import build_message, parse_message





def get_information(device_address="254", what="status"):
	message_to_sent = build_message("query", device_address=device_address, category="info", for_what=what)

	return message_to_sent

def get_flow_sensor_info(device_address="254", what="indicated_flow_rate_percent"):
	message_to_sent = build_message("query", device_address=device_address, category="flow_sensor", for_what=what)
	

	response = "@@@000ACK90.00;FF"

	return message_to_sent, parse_message(response)

if __name__ == '__main__':
	# print get_status(device_address="254")
	print get_information(device_address="254", what="status")
	print get_information(device_address="254", what="internal_temperature")
	print get_information(device_address="254", what="standard_temperature")
	print get_information(device_address="254", what="standard_pressure")
	print get_information(device_address="254", what="valve_power_off_state")

	print

	print get_flow_sensor_info(device_address="254", what="indicated_flow_rate_percent")
	print get_flow_sensor_info(device_address="254", what="indicated_flow_rate_units")