import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

import control_system_serial
import serial
import time

# ser = serial.Serial('/dev/ttyACM0', 9600)

class Handler:

	

	def __init__(self):
		
		self.devices = {}	 # key = COM Address; value = Device ID


		self.builder = Gtk.Builder()
		self.builder.add_from_file("arduino_gui.glade")
		self.builder.connect_signals(self)

		self.window = self.builder.get_object("main_window")

		self.window.connect("destroy", Gtk.main_quit)

		self.port_names = control_system_serial.get_all_serial_ports()

		self.identify_devices()

		self.write_all_serial_port_names()

		button = self.builder.get_object("send_message_button")
		button.connect("clicked", self.send_message)
    

	def send_message(self, button):
		print "Button clicked"
		device_selected = self.builder.get_object('devices_combobox').get_active_text()
		
		message_to_send = self.builder.get_object('message_to_send_textbox').get_text()

		port_name_index = device_selected.find("(")
		port_name = device_selected[:port_name_index].strip()

		ser = serial.Serial(port_name, 9600)

		ser.write(message_to_send)
		

	def onDeleteWindow(self, *args):
		Gtk.main_quit(*args)

	def write_all_serial_port_names(self):

		print "Mapping ports to their IDs!"

		for port_name in self.port_names:
			self.builder.get_object('devices_combobox').append_text(port_name + " ({})".format(self.devices[port_name][:6]))

		print "Mapping complete!"
		print

	def identify_devices(self):
		
		print
		print "Identifying devices connected!"

		for port_name in self.port_names:
			ser = serial.Serial(port_name, 9600)
			

			time.sleep(1)

			line = ser.readline().strip()

			print line

			self.devices[port_name] = line[3:] 
			ser.write("identified")
			
			print "Identified: " + line[3:] + " conncted on " + port_name

		print "Devices successfully identified!"
		print


if __name__ == "__main__":
	
	hand = Handler()

	hand.window.show_all()
	hand.window.maximize()
	

	Gtk.main()

