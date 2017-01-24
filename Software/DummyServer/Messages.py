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



arduino_error_messages_dict = {'ERR0': "Undefined error (does not fall into any of the other 9 categories).", 'ERR1': "Asking a precision that's too high (> 6).", 'ERR2': "Asking for something that would return more than 128 bytes.", 'ERR3': "Invalid number of channels.", 'ERR4': "Querying for one or more non-existing channel/s."}

def parse_arduino_output_message(output_messages):


	result = {}	
	for output_message in output_messages:
		
		if "ERR" in output_message:
			error_key = output_message.split("\r\n")[0]
			raise Exception(error_key, arduino_error_messages_dict[error_key])
		else:

			parsed_message = ""

			# Everybody stand back. I know regular expressions.
			pattern = "([a-zA-Z][0-9])([\+\-])([0-9])([0-9]+)([0-9])([\+\-])"

			matches = re.findall(pattern, output_message, flags=0)
			

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




def output_message_per_channel_length(precision):

	sign = 1
 	channel_name = 2
 	mentissa = 1
 	exponent = 1
 	exponent_sign = 1
 	per_channel_length = channel_name + sign + mentissa + int(precision) + exponent + exponent_sign 

 	return per_channel_length


def calculate_expected_output_message_length(precisions):
	message_identifier = 1	# The "o" at the beginning.
 	number_of_channels = 2	# 2 because if it is < 10, then it gets padded with a precedding zero.

 	total_length = message_identifier + number_of_channels + sum([output_message_per_channel_length(precision) for precision in precisions])

 	return total_length


def split_query_message(channel_names, precisions):


	message_identifier = 1	# The "o" at the beginning.
 	number_of_channels = 2	# 2 because if it is < 10, then it gets padded with a precedding zero.

 	message_length = message_identifier + number_of_channels

 	# Keep adding channels to query until you reach message_length == 127.

 	indices_to_split_after = [] 	
 	for i in range(len(channel_names)):
 		# Length that current channel would give.
 		current_channel_msg_length = output_message_per_channel_length(precisions[i])

 		message_length += current_channel_msg_length

 		# print "message length is", message_length, "vs.", 127

 		if message_length > 127:
 			# print "I think I'm gonna split."
 			indices_to_split_after.append(i)

 			message_length = message_identifier + current_channel_msg_length


 	split_channels = []
 	split_precisions = []

 	split_from = 0
 	for index_to_split_after in indices_to_split_after:
 		split_channels.append(channel_names[ split_from  : index_to_split_after])
 		split_precisions.append(precisions[ split_from : index_to_split_after])

 		split_from = index_to_split_after

 	# Finally, add the remainder.
 	split_channels.append(channel_names[split_from : ])
 	split_precisions.append(precisions[split_from : ])

 	
 	# print split_channels, len(split_channels)
 	# print split_precisions, len(split_precisions)

 	all_messages_less_than_128_bytes = [1 if calculate_expected_output_message_length(precisions) else 0 for precisions in split_precisions]

 	
 	if len(all_messages_less_than_128_bytes) != len(split_channels):
 		raise Exception("ERROR: One or more of the split message is going to be > 128 bytes long. Please fix the bug.")
 	else:
 		return split_channels, split_precisions


 	


def build_query_message(channel_names, precisions, safe_messages=[]):


	if len(channel_names) != len(precisions):
		raise Exception("Number of channel names to query does not match the number of precisions requested.", len(channel_names), len(precisions))

	# Here, make sure that we don't send a message that gives us an output that's more than 128 characters long.
	# If the message seems to be that way, split it into smaller messages.

 	# First, calculate the expected length of the output message.
	total_length = calculate_expected_output_message_length(precisions) 	

 	if total_length > 127:
 		# We need to split our message into smaller chunks.

 		split_channels, split_precisions = split_query_message(channel_names, precisions)

 		all_messages = []
 		for split_channel, split_precision in zip(split_channels, split_precisions):
 			# return build_query_message(split_channel, split_precision, safe_messages=[])
 			all_messages.append(build_query_message(split_channel, split_precision))
 		
 		return [msg[0] for msg in all_messages]

 	else:
		msg = "q"
		msg += "{0:0>2}".format(len(channel_names))
		
		for channel_name, precision in zip(channel_names, precisions):
			msg += "{}{}".format(channel_name, precision)

		return [msg]




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

	# print message
	
	for channel_name in channel_names:
		name = channel_name[0].strip(" \r\n")
		total_number = int(channel_name[1].strip(" \r\n"))

		for i in range(total_number):
			all_channels.append( "{}{}".format(name, i) )

	return all_channels

# print parse_arduino_output_message("o04f0+60231+f1+000000+f2+000+f3+00000+")
