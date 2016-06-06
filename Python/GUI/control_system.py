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
from device import Device, Channel, SerialCOM

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

		self._main_window.connect("destroy", Gtk.main_quit)

		# --- Get some widgets from the builder --- #
		self._status_bar = self._builder.get_object("main_statusbar")
		self._log_textbuffer = self._builder.get_object("log_texbuffer")
		self._overview_page = self._builder.get_object("overview_alignment")

		# Initialize an empty dictionary to hold all devices. key = device_name, value = Device Object.
		self._devices = dict()

		self._keep_communicating = False
		self._communication_threads = dict()
		self._communication_threads_mode = dict() 	# key = device_name, value = 'read' / 'write' i.e. which direction the communication is supposed to happen. It's from POV of the GUI -> Arduino.


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

	def get_connections(self):
		"""
		This just returns a dictionary of connections
		:return:
		"""
		con = {"main_quit": self.main_quit,
		"stop_button_clicked_cb": self.emergency_stop,
		"on_main_statusbar_text_pushed" : self.statusbar_changed_callback,
		"about_program_menu_item_activated": self.about_program,
		}

		return con

	def main_quit(self, widget):
		"""
		Shuts down the program (and threads) gracefully.
		:return:
		"""

		self._main_window.destroy()
		Gtk.main_quit()

		self.shut_down_communication_threads()

		return 0

	def run(self):
		"""
		:return:
		"""
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
	
	def about_program(self, menu_item):
		dialog = self._builder.get_object("about_dialogbox")
		dialog.run()
		dialog.destroy()


	def add_device(self, device):
		"""Adds a Device unit to the list of devices the GUI handles. 
		
		Args:
		    device (Device): A Device object.
		
		Returns:
		    None
		"""
		self._devices[device.name()] = device

	def add_front_page_widgets(self):

		for device_name, device in self._devices.items():

			if device.initialized():

				# Read in the widgets and add them to the GUI.
				front_page_widgets = device.front_page_widgets()

				vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=len(front_page_widgets.keys()))
				self._overview_page.add(vbox)

				for channel_name, widget in front_page_widgets.items():
					vbox.pack_start(widget, True, True, 0)

	def shut_down_communication_threads(self):
		self._keep_communicating = False

	def communicate(self, device_name):
		
		i = 0

		while self._keep_communicating:
			
			print "Communication thread running", i
			i += 1

			for device_name, device in self._devices.items():
				
				# Each device has its own thread. 
				# Find out whether we're supposed to read in values or write values at this time. 

				if self._communication_threads_mode[device_name] == "read":

					# Find all the channels, see if they are in 'read' or 'both' mode, then update the widgets with those values.

					for channel_name, channel in device.channels().items():

						if channel.mode() == "read" or channel.mode() == "both":

							start = time.time()

							value = channel.read_value()

							end = time.time()

							print "Reading value took {} seconds!".format(end - start)
							
							value = float(value)

							# Take this value and assign it to the corresponding FrontPageDisplayValue widget.
							device.front_page_widgets()[channel_name].set_value(value)

					# time.sleep(0.1)	# Time to sleep in seconds.



	def initialize_communication_threads(self):
		
		# For each device, we create a thread to communicate with the corresponding Arduino.
		
		for device_name, device in self._devices.items():

			communication_thread = threading.Thread(target=self.communicate, name=device_name, kwargs=dict(device_name=device_name))
			
			self._communication_threads[device_name] = communication_thread
			self._communication_threads_mode[device_name] = 'read'

			self._keep_communicating = True

			self._communication_threads[device_name].start()



	def initialize_devices(self, forced=False):

		for device_name in self._devices.keys():
			
			device = self._devices[device_name]

			if (not device.initialized()) or forced:
				device.initialize() # This creates all the necessary FrontPageDisplayValue objects.

		# Next, add all the front page widgets to the GUI.
		self.add_front_page_widgets()

		# Create communication threads.
		self.initialize_communication_threads()


if __name__ == "__main__":

	# arduino_device_ids = dict(interlock_box='2cc580d6-fa29-44a7-9fec-035acd72340e')
	arduino_device_ids = dict(interlock_box="9de3d90f-cdf7-4ef8-9604-548243401df6")

	control_system = MIST1ControlSystem()

	# Get a dictionary of devices connected along with their respective port names. key = device_name, value = serial_port_name.
	devices_port_names = control_system_serial.identify_device_ports(arduino_device_ids)

	if "interlock_box" in devices_port_names.keys():

		interlock_box = Device("interlock_box")

		interlock_box_serial_com = SerialCOM(arduino_id=arduino_device_ids['interlock_box'], arduino_port=devices_port_names['interlock_box'])

		micro_switch_channel = Channel(name="micro_switch_1", pretty_name="Micro Switch 1", serial_com=interlock_box_serial_com, message_header="micro_switch_1", upper_limit=1, lower_limit=0, data_type="bool", mode="read")
		flow_meter_channel = Channel(name="flow_meter_1", pretty_name="Flow Meter 1", serial_com=interlock_box_serial_com, message_header="flow_meter_1", upper_limit=1, lower_limit=0, data_type="bool", mode="read")
		
		interlock_box.add_channel(micro_switch_channel)
		interlock_box.add_channel(flow_meter_channel)

		control_system.add_device(interlock_box)

	control_system.initialize_devices()

	control_system.run()
