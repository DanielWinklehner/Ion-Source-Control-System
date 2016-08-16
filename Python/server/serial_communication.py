from __future__ import division

import time
import serial
import sys
import glob





class SerialCOM(object):

	def __init__(self, arduino_id, port_name, timeout=1.):
		"""Summary
		
		Args:
		    arduino_id (TYPE): Description
		"""
		self._arduino_id = arduino_id
		self._port_name = port_name

		self._baudrate = 115200
		self._timeout = timeout
		self._ser = serial.Serial(port_name, baudrate=self._baudrate, timeout=self._timeout)
		# self._ser = serial.Serial(port_name, baudrate=self._baudrate)

		

		
	def get_arduino_id(self):
		"""Summary
		
		Returns:
		    TYPE: Description
		"""
		return self._arduino_id

	def get_port(self):
		"""Summary
		
		Returns:
		    TYPE: Description
		"""
		return self._port_name

	
	
	

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

			for i in range(2):
				self._ser.write(message)

				response = self._ser.readline()

				# print "I sent a message", message, "and received", response

				if len(response) != 0:
					return response

		except serial.SerialException as e:
			raise Exception("Something's wrong! I cannot send any messages!" + str(e))
		except IOError as e2:
			raise Exception("Something's wrong! I cannot send any messages!" + str(e2))
		except Exception as e3:
			raise Exception("Something's wrong! I cannot send any messages!" + str(e3))

		return ""

	def read_message(self):
		"""Summary
		
		Returns:
		    TYPE: Description
		"""
		raise Exception("You're not supposed to use this SerialCOM method.")
		

		try:	
			#print "SerialCOM reading a message."

			self._ser.flushInput()
			self._ser.flushOutput()

			message = self._ser.readline()
			
			#print "SerialCOM read a message", message

			return message

		except serial.SerialException as e:
			raise Exception("Something's wrong! I cannot read my messages!" + str(e))
		except IOError as e2:
			raise Exception("Something's wrong! I cannot read my messages!" + str(e2))
		except Exception as e3:
			raise Exception("Something's wrong! I cannot read my messages!" + str(e3))


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
			if "ttyACM" in port:	
				s = serial.Serial(port, timeout=1)
				s.close()
				result.append(port)
		except (OSError, serial.SerialException) as e:
			print e				
			pass
		except IOError as e2:
			print e2
			pass

	return result


def find_port(arduino_id):
	"""
	:return:
	"""

	all_serial_ports = get_all_serial_ports()
	

	for serial_port_name in all_serial_ports:

		#print "Connecting to", serial_port_name

		ser = serial.Serial(serial_port_name, baudrate=115200, timeout=1.)

		input_message = "i"

		timeout = 1.  # in seconds.

		first_attempt_time = time.time()

		# while (time.time() - first_attempt_time) < timeout:
		for i in range(int(timeout)):
			

			try:
				#print "trying to connect"
				ser.write(input_message)
				
				response = ser.readline().strip()

				
				if "device_id" in response and "=" in response:

					# This is probably an Arduino designed for this Control System.
					# Get the device id.
					
					# print response
					if arduino_id == response.split("=")[1]:

						print "Found the Arduino corresponding to UUID %s at port %s" % (arduino_id, serial_port_name)

						return serial_port_name
			except:
				print "got an exception"
				continue

			time.sleep(0.1)
	
			

	# If we cannot find the corresponding port, return None
	print "Could not find Arduino corresponding to UUID %s" % arduino_id

	return None
	# raise Exception("Couldn't find an Arduino with the given device id.")


def find_arudinos_connected():
	all_serial_ports = get_all_serial_ports()
	
	all_arduinos = []
	for serial_port_name in all_serial_ports:

		#print "Connecting to", serial_port_name

		ser = serial.Serial(serial_port_name, baudrate=115200, timeout=1.)

		input_message = "i"

		timeout = 2.  # in seconds.

		first_attempt_time = time.time()
		
		#print float(time.time() - first_attempt_time), timeout, float(time.time() - first_attempt_time) < timeout
		while float(time.time() - first_attempt_time) < timeout:

			try:
				print "trying to connect"
				ser.write(input_message)
				
				response = ser.readline().strip()

				
				if "device_id" in response and "=" in response:

					# This is probably an Arduino designed for this Control System.
					# Get the device id.
					
					# print response
					arduino_id = response.split("=")[1]

					print "Found the Arduino corresponding to UUID %s at port %s" % (arduino_id, serial_port_name)

					all_arduinos.append( (arduino_id, serial_port_name) )
					
					break

			except Exception as e:
				print "Got the following exception: ", e
				continue
				#break

			

	return all_arduinos
	

if __name__ == "__main__":
	s = SerialCOM("2cc580d6-fa29-44a7-9fec-035acd72340e", "/dev/ttyACM1")
	print s.send_message("i")
	# print s.send_message("q01t14")
	pass




