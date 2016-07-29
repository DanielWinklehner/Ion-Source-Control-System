from __future__ import division
import time
from client import *

# Create a client object and connect to the server.
some_client = Client()
some_client.connect()

# Ask to connect to a given Arduino.
arduino_id = "2cc580d6-fa29-44a7-9fec-035acd72340e"
response = some_client.ask_server_to_connect_arduino(arduino_id)

print "Got a response back from the server", response

if response == arduino_id:
	# Server succesfully connected to the given arduino.

	print some_client.query_channels(arduino_id=arduino_id, channel_names=['f0', 'f1', 'f2', 'f3'], precisions=[3, 4, 1, 3])

	some_client.close_connection()

else:
	print "Connection to the given arduino failed."







# Old Test.
'''
some_client = Client()

some_client.connect()

some_client.send_message("connect_arduino:2cc580d6-fa29-44a7-9fec-035acd72340e")

response = some_client.receive_message()

arduino_key = response.split(":")[1]

# Create a list of channels to query.
channel_names = ['f0', 'f1', 'f2', 'f3']
precisions = [3, 4, 1, 3]

query_message = messages.build_query_message(arduino_key, channel_names, precisions)

some_client.send_message(query_message)
response = some_client.receive_message()

print "Got the following message back: {}".format(messages.parse_arduino_output_message(response))

some_client.close_connection()
'''



### Communication messages protocol design.

# Query Message:
# q{2f}{2s}{1f}.format(number_of_channels, channel_name, precision)
# e.g., q01f18
#
#
# Output Message:
# o{2f}{2s}{1f}{+/-}{1f}{pf}{1f}{+/-}.format(number_of_channels, channel_name, precision, +/-, digit_before_decimal, digit_after_decimal_upto_p_precision, index(power), sign_of_index(+/-) )



# Messages begin with arduino id and a number of lines thing. That tells the server to pass the next N lines to that arduino.

# Or a better option would be to have a connect and disconnect message.
# Maybe have connect:<arduino id> and then the server will keep passing all messages to that arduino  until it receives a disconnect:<arduino id> message.

# Maybe have the server assign an integer, which it will tell back to the GUI, that links it to the correct arduino id?
# This way we'll always know which arduino a particular message is intended for. 
# This is important since multiple arduino messages must probably be done in parallel (kind of parallel, more like arduino 1, arduino 1, arduino 2, arduino 1, arduino 1, arduino 2, arduino 2, arduino 1)