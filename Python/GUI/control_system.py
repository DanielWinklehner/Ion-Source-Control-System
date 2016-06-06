import gi

gi.require_version('Gtk', '3.0')

import time
import random
import threading
import datetime
import uuid

import control_system_serial
import serial

from gi.repository import Gtk, GLib, GObject

from serial import SerialException
from device import Device, Channel
from MIST1_Control_System_GUI_Widgets import *



__author__ = "Aashish Tripathee and Daniel Winklehner"
__doc__ = """GUI without actual functionality"""

class MIST1ControlSystem:
	"""
	Main class that runs the GUI for the MIST-1 control system
	"""

	def __init__(self):
		"""
		Initialize the control system GUI
		"""
		# --- Load the GUI from XML file and initialize connections --- #
		self._builder = Gtk.Builder()
		self._builder.add_from_file("mist_control_system_main_gui.glade")
		self._builder.connect_signals(self.get_connections())

		self._main_window = self._builder.get_object("main_window")
		self._arduino_vbox = self._builder.get_object("arduino_vbox")

		# --- Get some widgets from the builder --- #
		self._status_bar = self._builder.get_object("main_statusbar")
		self._log_textbuffer = self._builder.get_object("log_texbuffer")
		self._overview_grid = self._builder.get_object("overview_grid")

		# --- The main device dict --- #
		self._devices = {}

		# --- The serialCOM dict --- #
		self._serial_comms = {}

		self._initialized = False

		self._keep_communicating = False
		self._communication_threads = {}

		# key = device_name, value = 'read' / 'write' i.e. which direction the communication is
		# supposed to happen. It's from POV of the GUI -> Arduino.
		self._communication_threads_mode = {}
		self._communication_threads_poll_count = {}
		self._communication_threads_start_time = {}
		self._arduino_status_bars = {}

		

	def about_program_callback(self, menu_item):
		"""
		:param menu_item:
		:return:
		"""
		dialog = self._builder.get_object("about_dialogbox")
		dialog.run()
		dialog.destroy()

		return 0

	def add_arduino_status_bar(self, arduino_id, status_bar):
		self._arduino_status_bars[arduino_id] = status_bar

	def add_device(self, device):
		"""
		Adds a device to the control system
		:return:
		"""
		# Set the control system as the device parent
		device.set_parent(self)

		# Add device to the list of devices in the control system
		self._devices[device.name()] = device

		return 0

	def add_serial_com(self, serial_com):
		self._serial_comms[serial_com.arduino_id()] = serial_com

	def communicate(self, devices):
		"""
		:param devices:
		:return:
		"""

		j = 0

		while self._keep_communicating:
			# print "Communication thread running", j
			# j += 1
			for device in devices:

				# For each device that belonds to the same arduino (i.e same thread) we do this
				# Find out whether we're supposed to read in values or write values at this time.

				arduino_id = device.get_arduino_id()

				if self._communication_threads_mode[arduino_id] == "read":

					# Find all the channels, see if they are in 'read' or 'both' mode,
					# then update the widgets with those values.

					for channel_name, channel in device.channels().items():

						if channel.mode() == "read" or channel.mode() == "both":

							channel.read_value()

							self._communication_threads_poll_count[arduino_id] += 1

							GLib.idle_add(self.update_gui, channel)

		return 0

	def emergency_stop(self, widget):
		"""
		Callback for STOP button, but may also be called if interlock is broken or
		in any other unforseen sircumstance that warrants shutting down all power supplies.
		:param widget:
		:return:
		"""

		self._status_bar.push(1, "Emergency stop button was pushed!")

		return 0

	def initialize_communication_threads(self):
		"""
		For each device, we create a thread to communicate with the corresponding Arduino.
		:return:
		"""
		for arduino_id, serial_com in self._serial_comms.items():

			my_devices = [dev for devname, dev in self._devices.items() if arduino_id == dev.get_arduino_id()]

			communication_thread = threading.Thread(target=self.communicate,
													kwargs=dict(devices=my_devices))

			self._communication_threads[arduino_id] = communication_thread
			self._communication_threads_mode[arduino_id] = 'read'
			self._communication_threads_poll_count[arduino_id] = 0
			self._communication_threads_start_time[arduino_id] = time.time()

			self._keep_communicating = True

			self._communication_threads[arduino_id].start()

		return 0

	def get_arduino_vbox(self):
		return self._arduino_vbox

	def get_connections(self):
		"""
		This just returns a dictionary of connections
		:return:
		"""
		con = {"main_quit": self.main_quit,
			   "stop_button_clicked_cb": self.emergency_stop,
			   "on_main_statusbar_text_pushed": self.statusbar_changed_callback,
			   "about_program_menu_item_activated": self.about_program_callback,
			   }

		return con

	def get_overview_grid(self):
		return self._overview_grid

	def get_serial_comms(self):
		return self._serial_comms

	def initialize(self):
		"""
		:return:
		"""
		# Initialize the ankered devices first
		for device_name, device in self._devices.items():

			device.initialize()

		# Any and all remaining initializations go here
		self.initialize_communication_threads()

		self._initialized = True

		return 0

	def main_quit(self, widget):
		"""
		Shuts down the program (and threads) gracefully.
		:return:
		"""

		self._main_window.destroy()
		self.shut_down_communication_threads()
		Gtk.main_quit()

		return 0

	def shut_down_communication_threads(self):
		"""
		:return:
		"""
		self._keep_communicating = False

		return 0

	def run(self):
		"""
		:return:
		"""
		self.initialize()

		# --- Show the GUI --- #
		self._main_window.maximize()
		self._main_window.show_all()

		Gtk.main()

		return 0

	def statusbar_changed_callback(self, statusbar, context_id, text):
		"""
		Callback that handles what happens when a message is pushed in the
		statusbar
		"""

		timestr = time.strftime("%d %b, %Y, %H:%M:%S: ", time.localtime())

		self._log_textbuffer.insert(self._log_textbuffer.get_end_iter(), timestr + text + "\n")

		return 0

	def update_gui(self, channel):
		"""
		Updates the GUI. This is called from the communication threads through idle_add()
		:return:
		"""
		# Update the polling rate (frequency) for this arduino:
		arduino_id = channel.get_arduino_id()
		count = self._communication_threads_poll_count[arduino_id]

		if count >= 10:

			elapsed = time.time() - self._communication_threads_start_time[arduino_id]
			frequency = self._communication_threads_poll_count[arduino_id] / elapsed

			self._communication_threads_start_time[arduino_id] = time.time()
			self._communication_threads_poll_count[arduino_id] = 0

			self._arduino_status_bars[arduino_id].set_value(frequency)

		# If display on overview page is desired, update:
		if channel.get_parent_device().is_on_overview_page():

			channel.get_overview_page_display().set_value(channel.get_value())

		return 0


if __name__ == "__main__":

	control_system = MIST1ControlSystem()

	# Generate a test device
	# Each device is connected to a single arduino, several devices can be connected to the
	# same Arduino, but never several arduinos to a single device!
	test_device1 = Device("interlock_box", arduino_id="2cc580d6-fa29-44a7-9fec-035acd72340e",
						  label="Interlock Box")
	test_device1.set_overview_page_presence(True)

	# Generate a test channel as part of the test device
	test_channel1 = Channel(name="micro_switch_1", label="Micro Switch 1",
							message_header="micro_switch_1",
							upper_limit=1,
							lower_limit=0,
							data_type=int,
							mode="read")

	test_channel1a = Channel(name="flow_meter_1", label="Flow Meter 1",
							 message_header="flow_meter_1",
							 upper_limit=1,
							 lower_limit=0,
							 data_type=int,
							 mode="read")

	# Add the channel to the device and the device to the control system
	test_device1.add_channel(test_channel1)
	test_device1.add_channel(test_channel1a)
	control_system.add_device(test_device1)

	'''
	# Another test device
	test_device2 = Device("vacuum_box", arduino_id="bd0f5a84-a2eb-4ff3-9ff2-597bf3b2c20a",
						  label="Vacuum Box")
	test_device2.set_overview_page_presence(True)

	# Generate a test channel as part of the test device
	test_channel2 = Channel(name="flow_meter_1", label="Flow Meter 1",
							message_header="flow_meter_1",
							upper_limit=1,
							lower_limit=0,
							data_type=int,
							mode="read")

	# Add the channel to the device
	test_device2.add_channel(test_channel2)
	control_system.add_device(test_device2)

	# Another test device
	test_device3 = Device("dummy_device", arduino_id="bd0f5a84-a2eb-4ff3-9ff2-597bf3b2c20a",
						  label="Dummy Device")
	test_device3.set_overview_page_presence(True)

	# Generate a test channel as part of the test device
	test_channel3 = Channel(name="micro_switch_1", label="Micro Switch 1",
							message_header="micro_switch_1",
							upper_limit=1,
							lower_limit=0,
							data_type=int,
							mode="read")

	# Add the channel to the device
	test_device3.add_channel(test_channel3)
	control_system.add_device(test_device3)
	'''
	
	# Run the control system, this has to be last as it does all the initializations and adding to the gui
	control_system.run()
