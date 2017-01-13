from __future__ import division
import time
import re



# void mist1::Communication::convert_scientific_notation_to_mist1(char * source, char * target, unsigned precision) {
def convert_scientific_notation_to_mist1(number, precision): 

	# print 'the number is', number

	formating_string = "{:." + str(precision) + "e}"
	number = formating_string.format(number)
	number = str(number)
	target = [None] * 100
	
	# print "new nunmber is ", number

	index = 0
	
	if (number[0] == '-'):
		target[0] = '-'
		index += 1          # For negative numbers, there's a '-' character in the front so we need to offset by 1.
	else:
		target[0] = '+'
	
	# Next, we want the first digit.
	target[1] = number[index];

	# The next character is a decimal point. We don't want that.
	
	if (precision == 0):

		# If precision is 0, we want to go to int (instead of float) i.e. we do not want any digits after the decimal. 
		
		# Next, we want the exponent. Assumes that the exponent is always going to be single-digit.
		# There's a space, an 'E' and then the sign of the exponent before the actual exponent.
	
		target[2 + precision] = number[index + 2 + 0 + 2]

		# // Finally, the sign of the exponent.
		target[2 + precision + 1] = number[index + 2 + 0 + 1]
	else:

		# // Next, we want the digits after the decimal.


		for i in range(precision):
			target[2 + i] = number[index + 2 + i]


		target[2 + precision] = number[index + 1 + precision + 3 + 1]

		# // Finally, the sign of the exponent.
		target[2 + precision + 1] = number[index + 1 + precision + 2]

	final_target = ''.join(map(str, [t for t in target if t != None]))


	return final_target



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

def decode_query_message(message):
	# The next two letters should give the number of channels queried.
	number_of_channels = int(message[1:3])

	# Next, use regex to decode individual channel names and their precisions.

	# Everybody stand back, I know regular expressions.
	pattern = "([a-zA-Z][0-9])([0-9])"

	matches = re.findall(pattern, message[3:], flags=0)
	

	result = {}	
	for match in matches:
		channel_name = match[0]
		precision = match[1]

		result[channel_name] = precision

	return result

def round_off_mist1_notation(number, precision):


	rounded_off_number = ""


	# First byte is the sign of the number.
	# Second byte is the mentissa unless the number is -1 < 0 < 1.
	# To find out whether or not that is the case, look for the exponent.
	# Last byte is sign of the exponent.
	# Second to last byte is the exponent.

	if (number[-1] == '-') and (number[-2] == '1'):
		# This means the number is -1 < 0 < 1.
		
		# The mentissa really is just 0. So,

		if precision == 1:
			rounded_off_number = number[0] + number[1] + '0' + number[2:precision + 1]	# + 1 for sign of number. Another + 1 would be for the mentissa but since it's going to be 0 which is not written here, we exclude it. So, it becomes just a single +1.
		else:
			rounded_off_number = number[:precision + 1 + 1 - 1]	# + 1 for sign of number. Another + 1 for the mentissa.
	else:
		# Second bye is the mentissa.
		# Chop off the number after "precision" bytes.
		rounded_off_number = number[:precision + 1 + 1 - 1]	# + 1 for sign of number. Another + 1 for the mentissa.

		# TODO: This is almost right except we need to implement proper rounding off. But since accuracy does not matter for dummy server, leave it for now.



	# Need to add the last two bytes:
	rounded_off_number += number[-2:]


	return rounded_off_number

def build_output_message(channels_and_precisions, values):

	output_message = "o" + "%02d" % (len(values),)

	for (i, (channel_name, precision)) in enumerate(channels_and_precisions.items()):
		number_to_return = float(values[i])
		output_message += str(channel_name) + str(round_off_mist1_notation( str(convert_scientific_notation_to_mist1(float(values[i]), int(precision))), int(precision)))

	return output_message

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
