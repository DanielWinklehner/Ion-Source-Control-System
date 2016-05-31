from __future__ import division

import serial

class Device:

	def __init__(self, name, device_id, channels, physical_quantity, unit):
		self._name = name
		self._device_id = device_id
		self._physical_quantity = physical_quantity
		self._unit = unit
		self._channels = channels
		self._value = -1
		self._state = "resting"

	def get_name(self):
		return self._name

	def device_id(self):
		return self._device_id

	def physical_quantity(self):
		return self._physical_quantity

	def value(self):
		if self._state != "sending_output":
			raise Exception("ERROR: Device not in correct state to get a value!")

		self._value = self._channels['on_off'].serial_com().read_message()
		
		return self._value

	def set_value(self, value):
		self._value = value

	def state(self):
		return self._state

	def set_state(self, state):
		self._state = state

	def channels(self):
		return self._channels

	def start_reading_data(self):
		self._channels['on_off'].serial_com().send_message("send_output")
		self._state = "sending_output"



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

class Channel:

	def __init__(self, name, serial_com, upper_limit, lower_limit, uid, data_type, unit, scaling, mode):
		
		self._name = name
		self._serial_com = serial_com

		self._upper_limit = upper_limit
		self._lower_limit = lower_limit
		self._uid = uid
		self._data_type = data_type
		self._unit = unit
		self._scaling = scaling
		self._mode = mode

		self._value = -1
		self._error_state = "OK"



	def name(self):
		return self._name

	def serial_com(self):
		return self._serial_com

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

	def read_value(self):
		return self._value

	def set_value(self, value):
		self._value = value

	def error_state(self):
		return self._error_state