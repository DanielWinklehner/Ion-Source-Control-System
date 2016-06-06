from __future__ import division

import time
import serial
import sys
import glob
import widgets


class Device:

	def __init__(self, name, channels=dict()):
		self._name = name
		self._channels = channels 					# This is a dictionary of channels with their names as keys.
		self._initialized = False

		self._front_page_widgets = {}	# This is a dictionary of FrontPageDisplay widgets. key = channel_name, value = FrontPageDisplay.

	def name(self):
		return self._name

	def channels(self):
		return self._channels

	def get_channel_by_name(self, channel_name):
		return self._channels[channel_name]

	def add_channel(self, channel):
		"""Adds a channel to the current device. Since the _channels property of the Device class is a dictionary with channel names as its keys, this takes Channel.name() as the key for the channel being added.
		
		Args:
		    channel (Channel): Channel object to add. 
		
		Returns:
		    None
		"""
		self._channels[channel.name()] = channel
	
	def initialized(self):
		return self._initialized

	def initialize(self):
		"""Initializes the current device.
			This means, this method goes through all the channels associated with this device and creates widgets for all of them. 
			
		Returns:
		    TYPE: Description
		"""

		for channel_name, channel in self._channels.items():
			front_page_widget = widgets.FrontPageDisplayValue(name=channel.pretty_name())
			self._front_page_widgets[channel_name] = front_page_widget
		
		self._initialized = True
		
	def front_page_widgets(self):
		return self._front_page_widgets

class Channel:

	def __init__(self, name, pretty_name, serial_com, message_header, upper_limit, lower_limit, data_type, unit="", scaling=1., mode="both"):
		
		self._name = name
		self._pretty_name = pretty_name
		self._serial_com = serial_com
		self._message_header = message_header

		self._upper_limit = upper_limit
		self._lower_limit = lower_limit
		
		self._data_type = data_type
		self._unit = unit
		self._scaling = scaling

		self._value = -1

		self._mode = mode


	def pretty_name(self):
		return self._pretty_name

	def name(self):
		return self._name

	def serial_com(self):
		return self._serial_com

	def message_header(self):
		return self._message_header

	def upper_limit(self):
		return self._upper_limit

	def lower_limit(self):
		return self._lower_limit

	def data_type(self):
		return self._data_type

	def unit(self):
		return self._unit

	def scaling(self):
		return self._scaling

	def mode(self):
		return self._mode

	def read_arduino_message(self):

		start = time.time()

		response = self._serial_com.read_message()

		end = time.time()

		print "Reading arduino response took {} seconds.".format(end - start)

		try:

			response_parts =  response.split(':')
			result_parts = response_parts[1].split('=')

			keyword = response_parts[0]
			header = result_parts[0]
			value  = result_parts[1]

			return keyword, header, value
		except: 
			return "", "", ""

	def read_value(self):

		print "Reading value!"
		
		if self._mode == "write":
			raise ValueError("ERROR: You are trying to read in values from a write-only channel!")
			return
		
		# Build a query message.
		message = "query:{}={}".format(self._message_header, '?')

		# Send the query message.
		self._serial_com.send_message(message)

		# Read the Arduino's response.
		keyword, header, value = self.read_arduino_message()

		

		

		# Ideally, we should have all we need. But in case the first message sent by the Arduino was dropped, keep querying until we get some response.
		while not ( keyword == "output" and header == self._message_header ):			# THOUGHT: Maybe have a timeout?

			print "Trying again!"

			self._serial_com.send_message(message)

			# print "Message sent: ", message
			keyword, header, value = self.read_arduino_message()

			# print keyword, header, self._message_header, header == self._message_header

		# We have what we need.

		self._value = value

		return self._value


	def set_value(self, value):

		if self._mode == "read":
			raise ValueError("ERROR: You are trying to write values to a read-only channel!")
			return

		# Build a set message to send to the Arduino.
		message = "set:{}={}".format(self._message_header, value)

		# Send the set message.
		self._serial_com.send_message(message)

		# We're probably set. But just listen for an "assigned" message to make sure the value was set properly.

		# Read the Arduino's response.
		keyword, header, value = self.read_arduino_message()

		# Repeat the set message until we get the "assigned" message back from Arduino.
		while not ( (keyword == "assigned") and (header == self._message_header) ):				# THOUGHT: Maybe have a timeout?
			self._serial_com.send_message(message)

		# THOUGHT: Do we even need to "store" the value here as a class attribute?
		self._value = value


class SerialCOM:

	def __init__(self, arduino_id, arduino_port):
		self._arduino_id = arduino_id
		self._arduino_port = arduino_port

		self._ser = serial.Serial(self._arduino_port, baudrate=115200, timeout=2)

	def arduino_id(self):
		return self._arduino_id

	def arduino_port(self):
		return self._arduino_port

	def send_message(self, message):
		
		self._ser.flushInput()
		self._ser.flushOutput()

		self._ser.write(message)

	def read_message(self):

		# start = time.time()
		self._ser.flushInput()
		# end = time.time()
        #
		# print "Flushing input took {} seconds.".format(end - start)
        #
		# start = time.time()
        #
		self._ser.flushOutput()
        #
		# end = time.time()
        #
		# print "Flushing output took {} seconds.".format(end - start)

		start = time.time()

		# bytesToRead = self._ser.in_waiting
        #
		# print bytesToRead
        #
		# message = self._ser.read(bytesToRead)
        #
		# print message.decode()

		message = self._ser.readline()
		print message

		end = time.time()

		print "Actual time for reading the message is {} seconds.".format(end - start)
		return message
