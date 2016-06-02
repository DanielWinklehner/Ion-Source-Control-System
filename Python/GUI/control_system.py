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

		# --- SHow the GUI --- #
		self._main_window.maximize()
		self._main_window.show_all()

		# Initialize an empty dictionary to hold all devices. key = device_name, value = Device Object.
		self._devices = dict()

	def emergency_stop(self, widget):
		"""
		Callback for STOP button, but may also be called if interlock is broken or
		in any other unforseen sircumstance that warrants shutting down all power supplies.
		:param widget:
		:return:
		"""

		self._status_bar.push(1, "Emergency stop button was pushed!")

		return 0

	def get_connections(self):
		"""
		This just returns a dictionary of connections
		:return:
		"""
		con = {"main_quit": self.main_quit,
		"stop_button_clicked_cb": self.emergency_stop,
		"on_main_statusbar_text_pushed" : self.statusbar_changed_callback
		}

		return con

	def main_quit(self, widget):
		"""
		Shuts down the program (and threads) gracefully.
		:return:
		"""

		self._main_window.destroy()
		Gtk.main_quit()

		return 0

	def statusbar_changed_callback(self, statusbar, context_id, text):
		"""
		Callback that handles what happens when a message is pushed in the
		statusbar
		"""

		timestr = time.strftime("%d %b, %Y, %H:%M:%S: ", time.localtime())

		self._log_textbuffer.insert(self.log_textbuffer.get_end_iter(), timestr + text + "\n")

		return 0

	def add_device(self, device):
		"""Adds a Device unit to the list of devices the GUI handles. 
		
		Args:
		    device (Device): A Device object.
		
		Returns:
		    None
		"""
		self._devices[device.name()] = device



	def devices(self):
		"""This method is for testing purpose only. This will go away soon.

		WARNING: DO NOT USE THIS METHOD FOR PRODUCTION.
		
		Returns:
		    list(Device): a list of Device objects the GUI handles.
		"""
		return self._devices

if __name__ == "__main__":

	arduino_device_ids = dict(interlock_box='2cc580d6-fa29-44a7-9fec-035acd72340e')
	


	control_system = MIST1ControlSystem()


	

	# Get a dictionary of devices connected along with their respective port names. key = device_name, value = serial_port_name.
	devices_port_names = control_system_serial.identify_device_ports(arduino_device_ids)


	if "interlock_box" in devices_port_names.keys():

		interlock_box = Device("interlock_box")

		interlock_box_serial_com = SerialCOM(arduino_id=arduino_device_ids['interlock_box'], arduino_port=devices_port_names['interlock_box'])

		micro_switch_channel = Channel(name="micro_switch_1", serial_com=interlock_box_serial_com, message_header="micro_switch_1", upper_limit=1, lower_limit=0, data_type="bool", mode="read")
		interlock_box.add_channel( micro_switch_channel )

		control_system.add_device(interlock_box)

	# Gtk.main()

