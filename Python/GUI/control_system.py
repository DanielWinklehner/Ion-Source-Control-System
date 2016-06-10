import gi

gi.require_version('Gtk', '3.0')

import time
import random
import threading
import datetime
import uuid


import control_system_serial
import serial

from gi.repository import Gtk, GLib, GObject, Gdk

from serial import SerialException
from device import Device, Channel
from MIST1_Control_System_GUI_Widgets import *

import data_logging



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

		self._emergency_stop_button = self._builder.get_object("stop_button")
		self._emergency_stop_button.set_name("stop_button")

		# --- Paint the stop button red! --- #
		style_provider = Gtk.CssProvider()

		css = """
		GtkButton#stop_button {
		    color: #000000;
		    font-size: 18pt;
		    background-image: url('bg.png');
		}
		"""

		style_provider.load_from_data(css)

		Gtk.StyleContext.add_provider_for_screen(
			Gdk.Screen.get_default(),
			style_provider,
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)

		# --- The main device dict --- #
		self._devices = {}

		# --- The serialCOM dict --- #
		self._serial_comms = {}

		self._initialized = False

		self._keep_communicating = False
		self._communication_threads = {}

		# key = device_name, value = 'read' / 'write' i.e. which direction the communication is
		# supposed to happen. It's from POV of the GUI i.e. the direction is GUI -> Arduino.
		self._communication_threads_mode = {}
		self._communication_threads_poll_count = {}
		self._communication_threads_start_time = {}
		self._arduino_status_bars = {}

		self._set_value_for_widget = None	

		# HDF5 logging.
		self._data_logger = None

		self._last_checked_for_devices_alive = time.time()
		self._alive_device_names = set()
		self._check_for_alive_interval = 5	# In seconds.



	def register_data_logging_file(self, filename):
		self._data_logger = data_logging.DataLogging(log_filename=filename)
		self._data_logger.initialize()

	
	def log_data(self, channel):
		self._data_logger.log_value(channel=channel)
	

	def about_program_callback(self, menu_item):
		"""
		:param menu_item:
		:return:
		"""
		dialog = self._builder.get_object("about_dialogbox")
		dialog.run()
		dialog.destroy()

		return 0

	def set_widget_connections(self):
		for device_name, device in self._devices.items():
			for channel_name, channel in device.channels().items():

				if channel.mode() == "both" or channel.mode() == "write":	# TODO: Find a better way to do this.

					widget = channel.get_overview_page_display()
					
					try:	# According to http://stackoverflow.com/questions/1549801/differences-between-isinstance-and-type-in-python, better to use try-except than check type / instanceof.
						widget.get_radio_buttons()[0].connect("toggled", self.set_value_callback, widget)
					except Exception as e:
						pass



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


		# Add corresponding channels to the hdf5 log.
		for channel_name, channel in device.channels().items():
			if channel.mode() == "read" or channel.mode() == "both":
				self._data_logger.add_channel(channel)

		return 0

	def add_serial_com(self, serial_com):
		self._serial_comms[serial_com.arduino_id()] = serial_com


	def set_value_callback(self, button, widget):
		
		# print "Set callback called by {}".format(widget.get_name())

		parent_channel = widget.get_parent_channel()

		self._set_value_for_widget = widget
		self._communication_threads_mode[parent_channel.get_arduino_id()] = "write"

	def listen_for_reconnected_devices(self, devices):
		for device in devices:
			if device.name() in self._devices.keys() and device.name() not in self._alive_device_names:
				print "Reinitalizing device ", device.name()
				device.reinitialize()


	def check_for_alive_devices(self, devices):
		# Check which Arduinos are still alive.

		for device in devices:
			if device.get_serial_com().is_alive():
				
				self._alive_device_names.add(device.name())

				if device.locked():
					device.unlock()
			else:
				print "Device not alive."
				print "Locking device", device.name()
				device.lock()
				self._alive_device_names.discard(device.name())

		self._last_checked_for_devices_alive =  time.time()

		print "The set of all alive devices = ", self._alive_device_names

	def communicate(self, devices):
		"""
		:param devices:
		:return:
		"""

		while self._keep_communicating:
			
			if (time.time() - self._last_checked_for_devices_alive) > self._check_for_alive_interval:
				self.check_for_alive_devices(devices)
				self.listen_for_reconnected_devices(devices)

			GLib.idle_add(self.dummy_update)

			for device in devices:

				# For each device that belonds to the same arduino (i.e same thread) we do this
				# Find out whether we're supposed to read in values or write values at this time.

				# THOUGHT: Maybe implement a device.locked thing and don't operate on a given device unless that lock is released?
				# Ideally, even all the methods in the Device class would respect that lock. 
				
				if device.name() in self._alive_device_names:


					arduino_id = device.get_arduino_id()

					# print "Trying to communicate with device {} @ arduino {}".format(device.name(), arduino_id)

					if self._communication_threads_mode[arduino_id] == "read":

						# Find all the channels, see if they are in 'read' or 'both' mode,
						# then update the widgets with those values.

						for channel_name, channel in device.channels().items():

							if channel.mode() == "read" or channel.mode() == "both":

								try:
									channel.read_value()
									# Log data.
									self.log_data(channel)

									self._communication_threads_poll_count[arduino_id] += 1

									GLib.idle_add(self.update_gui, channel)
								except Exception as e:
									"Got an exception", e

					elif self._communication_threads_mode[arduino_id] == "write" and self._set_value_for_widget is not None:
						
						print "Setting value."

						widget_to_set_value_for = self._set_value_for_widget
						channel_to_set_value_for = self._set_value_for_widget.get_parent_channel()

						print "Communicating updated value for widget {}".format( widget_to_set_value_for.get_name() )

						# Check if the channel is actually a writable channel (channel.mode() ?= "write" or "both").
						
						if channel_to_set_value_for.mode() == "write" or channel_to_set_value_for.mode() == "both":
		
							try:
								value_to_update = widget_to_set_value_for.get_value()
							except ValueError:
								value_to_update = -1

							
							print "Setting value = {}".format(value_to_update)

							try:
								channel_to_set_value_for.set_value(value_to_update)
							except Exception, e:
								# Setting value failed. There was some exception.
								# Write the error message to the status bar.
								self._status_bar.push(2, str(e))


						self._communication_threads_mode[arduino_id] = "read"
						self._set_value_for_widget = None

		print "Closing communication thread."

		return 0

	def emergency_stop(self, widget):
		"""
		Callback for STOP button, but may also be called if interlock is broken or
		in any other unforseen sircumstance that warrants shutting down all power supplies.
		:param widget:
		:return:
		"""

		self._status_bar.push(1, "Emergency stop button was pushed!")
		self.shut_down_communication_threads()

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

		# Setup connections for widgets (for radio buttons for example).
		self.set_widget_connections()

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


	def dummy_update(self):
		pass

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

	# Setup data logging.
	current_time = time.strftime('%a-%d-%b-%Y_%H %M %S-EST', time.localtime())
	control_system.register_data_logging_file(filename="log/{}.hdf5".format(current_time))

	# Generate a device.
	# Each device is connected to a single arduino, several devices can be connected to the
	# same Arduino, but never several arduinos to a single device!

	# Aashish => 2cc580d6-fa29-44a7-9fec-035acd72340e
	# Daniel => 49ffb802-50c5-4194-879d-20a87bcfc6ef
	interlock_box_device = Device("interlock_box", arduino_id="2cc580d6-fa29-44a7-9fec-035acd72340e", label="Interlock Box")
	interlock_box_device.set_overview_page_presence(True)

	
	# Add channels to the interlock box device.

	# Flow meters. x5.
	for i in range(5):
		ch = Channel(name="flow_meter#{}".format(i + 1), label="Flow Meter {}".format(i + 1),
					 message_header="flow_meter#" + str(i + 1),
					 upper_limit=1,
					 lower_limit=0,
					 data_type=int,
					 mode="read",
					 unit="Hz",
					 display_order=(11 - i))

		interlock_box_device.add_channel(ch)

	# Microswitches. x2.
	for i in range(2):
		ch = Channel(name="micro_switch#{}".format(i + 1), label="Micro Switch {}".format(i + 1),
					message_header="micro_switch#{}".format(i + 1),
					upper_limit=1,
					lower_limit=0,
					data_type=bool,
					mode="read",
					display_order=(11 - 5 - i))

		interlock_box_device.add_channel(ch)
	
	# Solenoid valves. x2.
	for i in range(2):	
		ch = Channel(name="solenoid_valve#{}".format(i + 1), label="Solenoid Valve {}".format(i + 1),
					message_header="solenoid_valve#{}".format(i + 1),
					upper_limit=1,
					lower_limit=0,
					data_type=bool,
					mode="write",
					display_order=(11 - 5 - 2 - i))

		interlock_box_device.add_channel(ch)

	# Vacuum Valves. x2.
	for i in range(2):
		ch = Channel(name="vacuum_valve#{}".format(i + 1), label="Vacuum Valve {}".format(i + 1),
					message_header="vacuum_valve#{}".format(i + 1),
					upper_limit=1,
					lower_limit=0,
					data_type=bool,
					mode="read",
					display_order=(11 - 5 - 2 - 2 - i))

		interlock_box_device.add_channel(ch)

	# Add all our devices to the control system.
	
	control_system.add_device(interlock_box_device)

	'''
	ion_gauge = Device("ion_gauge", arduino_id="cf436e6b-ba3d-479a-b221-bc387c37b858", label="Ion Gauge")
	ion_gauge.set_overview_page_presence(True)

	for i in range(2):
		ch = Channel(name="gauge_state#{}".format(i + 1), label="Gauge State {}".format(i + 1),
					 message_header="gauge_state#" + str(i + 1),
					 upper_limit=1,
					 lower_limit=0,
					 data_type=bool,
					 mode="read",
					 display_order=(4 - i))

		ion_gauge.add_channel(ch)

	for i in range(2):
		ch = Channel(name="gauge_pressure#{}".format(i + 1), label="Gauge Pressure {}".format(i + 1),
					 message_header="gauge_pressure#" + str(i + 1),
					 upper_limit=1000,
					 lower_limit=0,
					 data_type=float,
					 mode="read",
					 unit="Torr",
					 display_order=(4 - i),
					 displayformat=".2e")

		ion_gauge.add_channel(ch)

	control_system.add_device(ion_gauge)
	'''

	# Run the control system, this has to be last as it does all the initializations and adding to the GUI.
	control_system.run()
