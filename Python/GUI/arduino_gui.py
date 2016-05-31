import gi

import random
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GLib, GObject

from serial import SerialException



# from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas

from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas


import matplotlib.animation as animation
from matplotlib import pyplot as plt


import matplotlib.dates as md


import control_system_serial
import serial

import time
import threading
import datetime


from device import Device, Channel, SerialCOM

import uuid


pressure_arduino_id = "9de3d90f-cdf7-4ef8-9604-548243401df6"

# ser = serial.Serial('/dev/ttyACM0', 9600)

class Handler:

	

	def __init__(self):
		
		GLib.threads_init()

		self._device_addresses = {}	 # key = COM Address; value = Device ID

		self._devices = {} # Contains actual Device objects, keyed by their names (maybe ids?)

		self._device_ids = {} # Key = common name, value = device id

		self._read_data = False


		self._builder = Gtk.Builder()
		self._builder.add_from_file("arduino_gui.glade")
		self._builder.connect_signals(self)

		self._window = self._builder.get_object("main_window")

		self._window.connect("destroy", Gtk.main_quit)

		button = self._builder.get_object("send_message_button")
		button.connect("clicked", self.send_message)

		start_gauge1_button = self._builder.get_object("start_gauge1_button")
		start_gauge1_button.connect("clicked", self.start_gauge1)

		read_pressure_button = self._builder.get_object("read_pressure_button")
		read_pressure_button.connect("clicked", self.start_reading_data)

		read_serial_ports_thread = threading.Thread(target=self.read_and_identify_devices)
		read_serial_ports_thread.start()


		self._data_reading_thread = threading.Thread(target=self.read_data)
		

		# These are for the pressure plot.

		self._plot_box = self._builder.get_object('plot_box')

		self._figure = plt.figure()
		self._axis = self._figure.add_subplot(1,1,1)
		self._canvas = False

		self._timestamps = []
		self._pressures = []

		# self._ani = None

	# Need another method to keep track of all threads, like when it says to stop reading data, that thread should stop.


	def start_gauge1(self, button):
		device = self._devices[self._device_ids['pressure']]
		channel = device.channels()['on_off']
		com = channel.serial_com()

		com.send_message("start_gauge_1")


	def create_plot(self):
		self._ani = animation.FuncAnimation(self._figure, self.update_plot, interval=1000, blit=True, frames=200)

	def update_plot(self, interval):

	  x =  md.date2num(self._timestamps)
	  y_1 =  [ a for (a, b) in self._pressures]
	  y_2 =  [ b for (a, b) in self._pressures]

	  self._axis.plot(x, y_1, color="red", lw=5, alpha=0.5)
	  self._axis.plot(x, y_2, color="blue", lw=5, alpha=0.5)

	  self._axis.set_yscale('log')

	  if not self._canvas:
	      self._canvas = FigureCanvas(self._figure)
	      self._plot_box.pack_start(self._canvas, True, True, 0)
	      self._canvas.show()
	  self._canvas.draw()
	  xfmt = md.DateFormatter('%H:%M:%S')
	  self._axis.xaxis.set_major_formatter(xfmt)
	  
	  # self._figure.autoscale(True)



	def update_stuff(self, value):
		# Update the value textbox.
		self._builder.get_object("current_pressure_reading").set_text(str(value))

		# Update the plot.
		if len(self._pressures) > 0:
			self.update_plot(1000)
		
		return False

	def read_data(self):

		list_size = 10

		while self._read_data:
			# Just pressure data for now.
			device = self._devices[self._device_ids['pressure']]

			timestamp = time.time()
			
			gauge_1_state_channel    = device.get_channel_by_name('gauge_1_state')
			gauge_1_pressure_channel = device.get_channel_by_name('gauge_1_pressure')
			gauge_2_state_channel    = device.get_channel_by_name('gauge_2_state')
			gauge_2_pressure_channel = device.get_channel_by_name('gauge_2_pressure')

			gauge_1_state, gauge_1_pressure = gauge_1_state_channel.read_value(), gauge_1_pressure_channel.read_value()
			gauge_2_state, gauge_2_pressure = gauge_2_state_channel.read_value(), gauge_2_pressure_channel.read_value()

			if len(values) == 4:
				self._builder.get_object("gauge1_state").set_text( gauge_1_state    )
				self._builder.get_object("gauge1_torr" ).set_text( gauge_1_pressure )
				self._builder.get_object("gauge2_state").set_text( gauge_2_state    )
				self._builder.get_object("gauge2_torr" ).set_text( gauge_2_pressure )

			pressure_1 = gauge_1_pressure
			pressure_2 = gauge_2_pressure

			try:
				
				float(pressure_1)
				float(pressure_2)

				if float(pressure_1) >= 0. and float(pressure_2) >= 0.:

					# if len(self._timestamps) > list_size:
					# 	self._timestamps = self._timestamps[1:]

					# if len(self._pressures) > list_size:
					# 	self._pressures = self._pressures[1:]

					# if len(self._timestamps) > list_size + 1:
						# print "List too big!"

					self._timestamps.append(   datetime.datetime.fromtimestamp(timestamp) )
					self._pressures.append( ( float(pressure_1), float(pressure_2)) )

				GLib.idle_add( self.update_stuff, value )   

			except ValueError:
				pass
		
			time.sleep(1)

	def start_reading_data(self, button):

		self.write_to_logger("Starting Reading data.")

		self._read_data = True

		self._data_reading_thread.start()	# This thread is associated with the "read_data()" method.

		self.create_plot()

	def read_and_identify_devices(self):
		self.port_names = control_system_serial.get_all_serial_ports()

		self.identify_devices()

		self.write_all_serial_port_names()

		for port_name in self._device_addresses:
			
			# Replace this with another hashmap of arduino IDs against what those units are.
			
			if self._device_addresses[port_name] == pressure_arduino_id:
				# This is our pressure unit.

				# Assign a new device id.
				device_id = uuid.uuid4()
				channel_id = uuid.uuid4()


				pressure_serial_com = SerialCOM(channel_id=channel_id, arduino_id=pressure_arduino_id, arduino_port=port_name)

				id_channel 				 = Channel(name="id",               serial_com=pressure_serial_com, message_header="id",               upper_limit=1,       lower_limit=0, uid=uuid.uuid4(), data_type="bool",   unit=None, scaling=1)
				gauge_1_state_channel    = Channel(name="gauge_1_status",   serial_com=pressure_serial_com, message_header="gauge_1_state",    upper_limit=1,       lower_limit=0, uid=uuid.uuid4(), data_type="string", unit=None, scaling=1)
				gauge_1_pressure_channel = Channel(name="gauge_1_pressure", serial_com=pressure_serial_com, message_header="gauge_1_pressure", upper_limit=1000000, lower_limit=0, uid=uuid.uuid4(), data_type="float",  unit=None, scaling=1)
				gauge_2_state_channel    = Channel(name="gauge_2_status",   serial_com=pressure_serial_com, message_header="gauge_2_state",    upper_limit=1000000, lower_limit=0, uid=uuid.uuid4(), data_type="float",  unit=None, scaling=1)
				gauge_2_pressure_channel = Channel(name="gauge_2_pressure", serial_com=pressure_serial_com, message_header="gauge_2_pressure", upper_limit=1000000, lower_limit=0, uid=uuid.uuid4(), data_type="float",  unit=None, scaling=1)

				pressure_channels = {'id': id_channel, 'gauge_1_state': gauge_1_state_channel, 'gauge_1_pressure': gauge_1_pressure_channel, 'gauge_2_state': gauge_2_state_channel, 'gauge_2_pressure': gauge_2_pressure_channel}

				pressure_unit = Device(name="Ion Gauge Controller", arduino_device_id=device_id, channels=pressure_channels)

				self._devices[device_id] = pressure_unit

				self._device_ids['pressure'] = device_id


	def write_to_logger(self, message):
		text_buffer = self._builder.get_object("footer_logger").get_buffer()
		iterator = text_buffer.get_end_iter()
		message = "[{:%Y-%b-%d %H:%M:%S}]: {}\n".format(datetime.datetime.now(), message)
		text_buffer.insert(iterator, message)


	def send_message(self, button):
		print "Button clicked"
		device_selected = self._builder.get_object('devices_combobox').get_active_text()
		
		message_to_send = self._builder.get_object('message_to_send_textbox').get_text()

		port_name_index = device_selected.find("(")
		port_name = device_selected[:port_name_index].strip()

		ser = serial.Serial(port_name, 9600)

		ser.write(message_to_send)
		

	def onDeleteWindow(self, *args):
		Gtk.main_quit(*args)

	def write_all_serial_port_names(self):

		print "Mapping ports to their IDs!"

		for port_name in self.port_names:
			self._builder.get_object('devices_combobox').append_text(port_name + " ({})".format(self._device_addresses[port_name][:8]))

		print "Mapping complete!"
		print

	def identify_devices(self):
		
		print "Identifying devices connected!"
		self.write_to_logger("Identifying devices connected!")

		for port_name in self.port_names:

			# print port_name

			try:
				ser = serial.Serial(port_name, timeout=3)
				ser.close()
				ser.open()
			except SerialException:
				print 'Port already open'
			
			
			output_msg = ser.readline().strip()
			input_message = "identify_yourself"

			while "device_id" not in output_msg:
				ser.write(input_message)
				time.sleep(0.01)

				output_msg = ser.readline()

				print output_msg

			# ser.write("identify_yourself")

			# time.sleep(0.5)

			print (ser.readline())

			while True:
				
				line1 = ser.readline().strip()
				line2 = ser.readline().strip()

				print "reading lines"

				if line1 == line2:
				# if True:
					self._device_addresses[port_name] = line2[10:]
					ser.write("identified")

					if line2[10:] == pressure_arduino_id:
						self._builder.get_object("pressure_port_name").set_text(port_name)
						self._builder.get_object("pressure_device_id").set_text("( {} )".format(line2[10:]))

					self.write_to_logger("Identified device id = {} on port {}.".format(line2[10:], port_name))

					ser.flushInput()
					ser.flushOutput()	
					ser.close()

					break

		self.write_to_logger("{} devices successfully identified!".format(len(self._device_addresses)))
		


if __name__ == "__main__":
	
	hand = Handler()

	hand._window.show_all()
	hand._window.maximize()
	

	Gtk.main()

