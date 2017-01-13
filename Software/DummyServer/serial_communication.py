from __future__ import division

import time
import serial
import sys
import glob
import subprocess
import math
import os

import messages



class DummySerial():

	def __init__(self, port_name, baudrate, timeout=5.):
		self._port_name = port_name
		self._baudrate = baudrate
		self._timeout = timeout

		self._last_message = ""

	def flushInput(self):
		pass

	def flushOutput(self):
		pass

	def write(self, message):
		print "Writing the following"
		self._last_message = message

	def read(self):

		# Return sin of current time.
		print "Called read"


		return "o04f0+60231+f1+000000+f2+000+f3+00000+"

	def readline(self):

		print "Called readline", self._last_message, time.localtime().tm_sec

		# Take the query message (stored in self._last_message) and decode it to get everything we need.

		if self._last_message[0] == "q":
			# This is a query message.
			result = messages.decode_query_message(self._last_message)

			output_message = messages.build_output_message(result, [math.sin(time.localtime().tm_sec)] * len(result.keys()))

			return output_message

		elif self._last_message == "c":
			self._last_message = ""
			return "f0"

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
		# self._ser = serial.Serial(port_name, baudrate=self._baudrate, timeout=self._timeout)
		self._ser = DummySerial(port_name, baudrate=self._baudrate)
		

		
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

		for i in range(2):
			self._ser.write(message)

			response = self._ser.readline()

			# print "I sent a message", message, "and received", response

			if len(response) != 0:
				# print "And now I am returning a response"
				return response

		return ""

	def read_message(self):
		"""Summary
		
		Returns:
		    TYPE: Description
		"""
		raise Exception("You're not supposed to use this SerialCOM method.")
		



def find_arudinos_connected():
	return [("R2D2", "/dev/ttyACM0"), ("BB8", "/dev/ttyACM1"), ("C3PO", "/dev/ttyACM2")]
	


if __name__ == "__main__":

	print find_arudinos_connected()
	pass
	




