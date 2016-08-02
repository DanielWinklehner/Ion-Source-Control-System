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

# print parse_arduino_output_message("o04f0+60231+f1+000000+f2+000+f3+00000+")