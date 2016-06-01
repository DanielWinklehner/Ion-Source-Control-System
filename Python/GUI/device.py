from __future__ import division

import serial

class Device:

	def __init__(self, name, arduino_device_id, channels):
		self._name = name
		self._arduino_device_id = arduino_device_id
		self._channels = channels 					# This is a dictionary of channels with their names as keys.

	def get_name(self):
		return self._name

	def arduino_device_id(self):
		return self._arduino_device_id

	def channels(self):
		return self._channels

	def get_channel_by_name(self, channel_name):
		return self._channels[channel_name]

	def register_serial_com(self, serial_com):
		self._serial_com = serial_com

	def serial_com(self):
		return _self.serial_com

class Channel:

	def __init__(self, name, serial_com, message_header, upper_limit, lower_limit, uid, data_type, unit, scaling, mode="both"):
		
		self._name = name
		self._serial_com = serial_com
		self._message_header = message_header

		self._upper_limit = upper_limit
		self._lower_limit = lower_limit
		self._uid = uid
		self._data_type = data_type
		self._unit = unit
		self._scaling = scaling

		self._value = -1

		self._mode = mode

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

	def uid(self):
		return self._uid

	def data_type(self):
		return self._data_type

	def unit(self):
		return self._unit

	def scaling(self):
		return self._scaling

	def mode(self):
		return self._mode

	def read_arduino_message(self):
		response = self._serial_com.read_message()

		response_parts =  response.split(':')
		result_parts = response_parts[1].split('=')

		keyword = response_parts[0]
		header = result_parts[0]
		value  = result_parts[1]

		return keyword, header, value


	def read_value(self):
		
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
			self._serial_com.send_message(message)

			keyword, header, value = self.read_arduino_message()

			print keyword, header, self._message_header, header == self._message_header

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
		self._value = _value


class SerialCOM:

	def __init__(self, channel_id, arduino_id, arduino_port):
		self._channel_id = channel_id
		self._arduino_id = arduino_id
		self._arduino_port = arduino_port

		self._ser = serial.Serial(self._arduino_port, baudrate=9600, timeout=3)

	def channel_id(self):
		return self._channel_id

	def arduino_id(self):
		return self._arduino_id

	def arduino_port(self):
		return self._arduino_port

	def send_message(self, message):
		
		self._ser.flushInput()
		self._ser.flushOutput()	

		self._ser.write(message)

	def read_message(self):
		self._ser.flushInput()
		self._ser.flushOutput()	

		return self._ser.readline()
