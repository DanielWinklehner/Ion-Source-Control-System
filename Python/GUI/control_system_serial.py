from __future__ import division

import time
import serial
import sys
import glob


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



def get_device_name(arduino_device_ids, device_id):
	"""Searches the dictionary arduino_devices_ids for the value device_id and returns the corresponding key. 
	
	Args:
	    arduino_device_ids (dict): dictionary of device_ids. key = device_name, value = device_id.
	    device_id (string): device_id to search for.
	
	Returns:
	    string: device_name that corresponds to the device id given by device_id.
	"""

	for assigned_device_name, assigned_device_id in arduino_device_ids.items():
		if device_id == assigned_device_id:
			return assigned_device_name

	return ""

def identify_device_ports(arduino_device_ids):
	"""Finds all the serial devices connected, goes through them, identifies whether or not they are related to the Control System and returns a map of device_names and port_names.
	
	Args:
	    arduino_device_ids (dict): dictionary of device id's for arduinos. Should have key = device_name, value = device_id.
	
	Returns:
	    dict: Dictionary of device names and the serial ports they're connected to. key = device_name, value = serial_port_name.
	"""


	# First, get all the open serial ports.
	all_serial_ports = get_all_serial_ports()

	# Next, for each of the open ports, connect to them and ask for a device id. 
	# If they respond and give a valid id (marked by a presence in arduino_device_ids), add them to a map with key = device_name, value = port_name. 
	# Else just ignore them.

	devices_port_names = {}	# This is a dictionary with key = device_name, value = port_name.

	for serial_port_name in all_serial_ports:
		
		print "Connecting on", serial_port_name
		
		ser = serial.Serial(serial_port_name, baudrate=9600, timeout=3)

		# Send a message, querying for a device id. 
		input_message = "query:identification=?"

		timeout = 10	# in seconds.

		for i in range(timeout):
			ser.write(input_message)
			response = ser.readline().strip()

			if "output" in response and "device_id" in response and "=" in response:
				
				# This is probably an Arduino designed for this Control System.
				# Get the device id.
				
				device_id = response.split("=")[1]
				
				device_name = get_device_name(arduino_device_ids, device_id)

				if len(device_name) != 0:
					devices_port_names[device_name] = serial_port_name
					break

			time.sleep(1)	# Sleep for 1 second and send a query message again.

		return devices_port_names


