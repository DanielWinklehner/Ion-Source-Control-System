from __future__ import division

import time
import serial
import sys
import glob
import MIST1_Control_System_GUI_Widgets

class Device:
	def __init__(self, name, arduino_id, label="", channels=None, on_overview_page=False):

		self._name = name
		self._label = label

		self._channels = {}  # This is a dictionary of channels with their names as keys.
		if channels is not None:
			self._channels = channels

		self._arduino_id = arduino_id
		# self._front_page_widgets = {}  # This is a dictionary
		# of FrontPageDisplay widgets. key = channel_name, value = FrontPageDisplay.
		self._on_overview_page = on_overview_page

		# Parent will be set during add_channel in control system
		self._parent = None

		self._initialized = False
		self._overview_frame = None
		self._serial_com = None

	def get_arduino_id(self):
		return self._arduino_id

	def get_overview_frame(self):
		return self._overview_frame

	def get_serial_com(self):
		return self._serial_com

	def set_parent(self, parent):
		self._parent = parent

	def name(self):
		return self._name

	def label(self):
		return self._label

	def channels(self):
		return self._channels

	def get_channel_by_name(self, channel_name):
		return self._channels[channel_name]

	def add_channel(self, channel):
		"""
		Adds a channel to the current device. Since the _channels property of the Device class is a
		dictionary with channel names as its keys, this takes Channel.name() as the key for the channel being added.

		Args:
			channel (Channel): Channel object to add.

		Returns:
			None
		"""
		channel.set_arduino_id(self._arduino_id)
		channel.set_parent_device(self)
		self._channels[channel.name()] = channel

	def add_device_to_gui(self):
		"""
		Adds a device to the GUI
		:return:
		"""

		# Add device to GUI overview page if desired
		if self._on_overview_page:
			# Create a frame
			self._overview_frame = MIST1_Control_System_GUI_Widgets.FrontPageDeviceFrame(label=self._label)

			# Add the frame to the layout
			self._parent.get_overview_grid().add(self._overview_frame)

		# TODO: Adding the device to its main page and to the settings page

		return 0

	def initialized(self):
		return self._initialized

	def initialize(self):
		"""
		Initializes the current device. This means, this method goes through all the channels associated
		with this device and creates widgets for all of them.

		Returns:
			TYPE: Description
		"""

		# First, we check if there already is a SerialCOM object associated with the unique
		# Arduino ID, if not we create one.
		all_serial_comms = self._parent.get_serial_comms()

		if self._arduino_id not in all_serial_comms.keys():

			print "No SerialCOM for Arduino with UUID %s yet...Creating..." % self._arduino_id
			self._serial_com = SerialCOM(self._arduino_id)
			self._parent.add_serial_com(self._serial_com)

			# Add infobar to the arduino_vbox on the side of the GUI
			vbox = self._parent.get_arduino_vbox()
			infobar = MIST1_Control_System_GUI_Widgets.FrontPageDisplayValue(name="Arduino at Port: %s. Polling rate =" %
														 self._serial_com.arduino_port(),
													displayformat=".1f", unit="Hz")

			vbox.pack_start(infobar, False, False, 4)
			self._parent.add_arduino_status_bar(self._arduino_id, infobar)

		else:

			print "Found SerialCOM for Arduino with UUID %s ...using existing..." % self._arduino_id
			self._serial_com = all_serial_comms[self._arduino_id]

		# Have to add device first so that there is a frame to add to
		self.add_device_to_gui()

		# Create a list of tuples (display_order, channel).
		all_channels = []
		for channel_name, channel in self._channels.items():
			all_channels.append( (channel.get_display_order(), channel) )

		all_channels.sort(key=lambda tup: tup[0], reverse=True)


		for display_order, channel in all_channels:
			channel.initialize()

		self._initialized = True

	def is_on_overview_page(self):
		return self._on_overview_page

	def set_overview_page_presence(self, value):
		self._on_overview_page = value

	# def front_page_widgets(self):
	#     return self._front_page_widgets


class Channel:
	def __init__(self, name, label, message_header, upper_limit, lower_limit, data_type, unit="",
				 scaling=1., mode="both", display_order=0):

		self._name = name
		self._label = label
		self._serial_com = None
		self._message_header = message_header
		self._upper_limit = upper_limit
		self._lower_limit = lower_limit
		self._data_type = data_type
		self._unit = unit
		self._scaling = scaling
		self._value = -1
		self._mode = mode
		self._arduino_id = None
		self._parent_device = None  # The device this channel belongs to will be set during add_channel().
		self._initialized = False
		self._overview_page_display = None

		self._timeout = 2	# In seconds.

		self._display_order = display_order # Higher number on the top.

	def add_channel_to_gui(self):
		"""
		Adds a device to the GUI
		:return:
		"""
		parent_device = self._parent_device

		set_flag = True
		if self._mode == "read":
			set_flag = False

		# Add channels to the devices GUI overview page frame if desired
		if parent_device.is_on_overview_page():
			# Create a display

			if self._data_type == bool:

				self._overview_page_display = MIST1_Control_System_GUI_Widgets.FrontPageDisplayBool(name=self._label,
																		   set_flag=set_flag,
																		   parent_channel=self)

			else:

				# Create a display
				self._overview_page_display = MIST1_Control_System_GUI_Widgets.FrontPageDisplayValue(name=self._label,
																			unit=self._unit,
																			displayformat=".2f",
																			set_flag=set_flag,
																			parent_channel=self)


			parent_device.get_overview_frame().pack_start(self._overview_page_display, False, False, 4)

		# TODO: Adding the device to its main page and to the settings page

		return 0

	def get_arduino_id(self):
		return self._arduino_id

	def get_overview_page_display(self):
		return self._overview_page_display

	def get_value(self):
		return self._value

	def get_display_order(self):
		return self._display_order

	def initialize(self):
		"""
		Initializes the channel
		:return:
		"""
		self.add_channel_to_gui()

		# Set the SerialCOM object according to parent
		self._serial_com = self._parent_device.get_serial_com()

		self._initialized = True

		return 0

	def get_parent_device(self):
		return self._parent_device

	def set_parent_device(self, device):
		self._parent_device = device

	def set_arduino_id(self, arduino_id):
		self._arduino_id = arduino_id

	def label(self):
		return self._label

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

		response = self._serial_com.read_message()

		try:
			response_parts = response.split(':')
			result_parts = response_parts[1].split('=')

			keyword = response_parts[0]
			header = result_parts[0]
			value = result_parts[1]

			return keyword, header, value
		except:
			return "", "", ""

	def read_value(self):

		# print "Reading value!"

		if self._mode == "write":
			raise ValueError("ERROR: You are trying to read in values from a write-only channel!")

		# Build a query message.
		message = "query:{}={}".format(self._message_header, '?')

		# Send the query message.
		self._serial_com.send_message(message)

		# Read the Arduino's response.
		keyword, header, value = self.read_arduino_message()

		# Ideally, we should have all we need. But in case the first message sent
		# by the Arduino was dropped, keep querying until we get some response.

		start_time = time.time()
		while ( not (keyword == "output" and header == self._message_header) ) and (time.time() - start_time) <= self._timeout:  # THOUGHT: Maybe have a timeout?

			print "Trying again!"

			self._serial_com.send_message(message)

			# print "Message sent: ", message
			keyword, header, value = self.read_arduino_message()

		# print keyword, header, self._message_header, header == self._message_header

		# We have what we need.

		self._value = self._data_type(float(value))

		return self._value

	def set_value(self, value_to_set):

		if self._mode == "read":
			raise ValueError("ERROR: You are trying to write values to a read-only channel!")

		if type(value_to_set) == bool:
			value_to_set = int(value_to_set)

		# Build a set message to send to the Arduino.
		message = "set:{}={}".format(self._message_header, value_to_set)

		# Send the set message.
		self._serial_com.send_message(message)

		# We're probably set. But just listen for an "assigned" message to make sure the value was set properly.

		# Read the Arduino's response.
		keyword, header, value = self.read_arduino_message()

		# Repeat the set message until we get the "assigned" message back from Arduino.

		start_time = time.time()
		while ( not ((keyword == "assigned") and (header == self._message_header)) ) and (time.time() - start_time) <= self._timeout:  # THOUGHT: Maybe have a timeout?

			print "Didn't work out the first time so trying again!"

			self._serial_com.send_message(message)
			keyword, header, value = self.read_arduino_message()

		if len(value) == 0:
			# This means there was a timeout.
			print "Timeout!"
			raise Exception("ERROR: Could not set value = {} for channel = {} because of a timeout!".format(value_to_set, self._name))

		# THOUGHT: Do we even need to "store" the value here as a class attribute?
		self._value = value


class SerialCOM:

	def __init__(self, arduino_id):
		self._arduino_id = arduino_id
		self._arduino_port = self.find_port(arduino_id)

		if self._arduino_port is None:

			# TODO: Handle these cases such that all other devices are still connecting!
			raise SystemExit

		self._ser = serial.Serial(self._arduino_port, baudrate=115200, timeout=2)

	def arduino_id(self):
		return self._arduino_id

	def arduino_port(self):
		return self._arduino_port

	@staticmethod
	def get_all_serial_ports():
		""" Lists serial port names

			:raises EnvironmentError:
				On unsupported or unknown platforms
			:returns:
				A list of the serial ports available on the system

			Code From: http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
		"""

		if sys.platform.startswith('win'):

			ports = ['COM%s' % (i + 1) for i in range(256)]

		elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):

			# this excludes your current terminal "/dev/tty"
			ports = glob.glob('/dev/tty[A-Za-z]*')

		elif sys.platform.startswith('darwin'):

			ports = glob.glob('/dev/tty.*')

		else:

			raise EnvironmentError('Unsupported platform')

		result = []

		for port in ports:

			try:

				s = serial.Serial(port)
				s.close()
				result.append(port)

			except (OSError, serial.SerialException):

				pass

		return result

	def find_port(self, arduino_id):
		"""
		:return:
		"""

		all_serial_ports = self.get_all_serial_ports()

		for serial_port_name in all_serial_ports:

			print "Connecting to", serial_port_name

			ser = serial.Serial(serial_port_name, baudrate=115200, timeout=1)

			input_message = "query:identification=?"

			print input_message

			timeout = 2  # in seconds.

			for i in range(timeout):

				ser.write(input_message)
				response = ser.readline().strip()

				if "output" in response and "device_id" in response and "=" in response:

					# This is probably an Arduino designed for this Control System.
					# Get the device id.
					if arduino_id == response.split("=")[1]:

						print "Found the Arduino corresponding to UUID %s at port %s" % (arduino_id, serial_port_name)

						return serial_port_name

				time.sleep(1)  # Sleep for 1 second and send a query message again.

		# If we can't find the corresponding port, return None
		print "Couldn't find Arduino corresponding to UUID %s" % arduino_id

		return None

	def send_message(self, message):
		
		self._ser.flushInput()
		self._ser.flushOutput()

		self._ser.write(message)

	def read_message(self):

		self._ser.flushInput()
		self._ser.flushOutput()

		message = self._ser.readline()
		
		return message
