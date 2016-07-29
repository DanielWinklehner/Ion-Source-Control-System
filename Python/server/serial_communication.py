from __future__ import division

import time
import serial
import sys
import glob
import json


# 

class SerialCOM:

	def __init__(self, arduino_id):
		"""Summary
		
		Args:
		    arduino_id (TYPE): Description
		"""
		self._arduino_id = arduino_id
		self._arduino_port = self.find_port(arduino_id)

		if self._arduino_port is None:

			# TODO: Handle these cases such that all other devices are still connecting!
			print "arduino port was None"
			raise SystemExit

		self._baudrate = 115200
		self._timeout = 5.
		self._ser = serial.Serial(self._arduino_port, baudrate=self._baudrate, timeout=self._timeout)

		self._alive_timeout = 10.	# In seconds. Make sure this is float.

	def arduino_id(self):
		"""Summary
		
		Returns:
		    TYPE: Description
		"""
		return self._arduino_id

	def arduino_port(self):
		"""Summary
		
		Returns:
		    TYPE: Description
		"""
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
			raise EnvironmentError('Unsupported platform.')

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

			ser = serial.Serial(serial_port_name, baudrate=115200, timeout=1.)

			input_message = "i"

			timeout = 3.  # in seconds.

			first_attempt_time = time.time()

			# while (time.time() - first_attempt_time) < timeout:
			for i in range(int(timeout)):
				

				try:

					ser.write(input_message)
					
					response = ser.readline().strip()

					
					if "device_id" in response and "=" in response:

						# This is probably an Arduino designed for this Control System.
						# Get the device id.
						print response
						if arduino_id == response.split("=")[1]:

							print "Found the Arduino corresponding to UUID %s at port %s" % (arduino_id, serial_port_name)

							return serial_port_name
				except:
					print "got an exception"
					continue

				time.sleep(0.5)

				

		# If we cannot find the corresponding port, return None
		print "Could not find Arduino corresponding to UUID %s" % arduino_id

		# return None
		raise Exception("Couldn't find an Arduino with the given device id.")

	def is_alive(self):
		"""Summary
		
		Returns:
		    TYPE: Description
		"""
		try: 
			self.send_message("i")
			response = self.read_message()
			first_message_time = time.time()

			while (response.strip() != "device_id=" + self._arduino_id) and ((time.time() - first_message_time) < float(self._alive_timeout)):
				self.send_message("i")
				response = self.read_message()

			return (response.strip() == "device_id=" + self._arduino_id)

		except:
			print "There seems to be some problem with the port. It's not responding."
			return False
			

	def send_message(self, message):
		"""Summary
		
		Args:
		    message (TYPE): Description
		
		Returns:
		    TYPE: Description
		"""
		try:
			self._ser.flushInput()
			self._ser.flushOutput()

			self._ser.write(message)
		except:
			raise Exception("Something's wrong! I cannot send any messages!")

	def read_message(self):
		"""Summary
		
		Returns:
		    TYPE: Description
		"""
		try:
			self._ser.flushInput()
			self._ser.flushOutput()

			message = self._ser.readline()
			return message
		# except serial.SerialException as e:
		# except IOError as e:
		except:
			raise Exception("Something's not right! I cannot read my messages!")

