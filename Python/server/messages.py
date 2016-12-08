from __future__ import division
import time
import re


def parse_arduino_output_message(output_message):
	parsed_message = ""

	# Everybody stand back. I know regular expressions.
	pattern = "([a-zA-Z][0-9])([\+\-])([0-9])([0-9]+)([0-9])([\+\-])"

	matches = re.findall(pattern, output_message[3:], flags=0)
	
	result = {}	
	for match in matches:
		channel_name = match[0]

		value = float("{}.{}".format(match[2], match[3]))

		if match[5] == "+":
			value *= 10**(int(match[4]))
		elif match[5] == "-":
			value *= 10**( - int(match[4]))

		if match[1] == "-":
			value = 0 - value

		result[channel_name] = value
		
	return result

def build_query_message(channel_names, precisions):
	
	msg = "q"
	msg += "{0:0>2}".format(len(channel_names))
	
	for channel_name, precision in zip(channel_names, precisions):
		msg += "{}{}".format(channel_name, precision)

	return msg

def build_set_message(channel_names, values_to_set):

	# Supports 1 message at at time only at the moment.
	
	if values_to_set[0] == "True":
		values_to_set[0] = "1"
	elif values_to_set[0] == "False":
		values_to_set[0] = "0"

	msg = "s"
	msg += str(channel_names[0])
	msg += str(values_to_set[0])

	return str(msg)

def decode_channel_names(message):
	all_channels = []
	channel_names = message.split(",")

	for channel_name in channel_names:
		name = channel_name[0].strip(" \r\n")
		total_number = int(channel_name[1].strip(" \r\n"))

		for i in range(total_number):
			all_channels.append( "{}{}".format(name, i) )

	return all_channels

# print parse_arduino_output_message("o04f0+60231+f1+000000+f2+000+f3+00000+")
