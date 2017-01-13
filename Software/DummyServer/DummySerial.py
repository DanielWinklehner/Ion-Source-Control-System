from __future__ import division

import time
import serial
import sys
import glob
import subprocess
import math
import os

import Messages



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
		self._last_message = message

	def read(self):

		# Return sin of current time.
		return "o04f0+60231+f1+000000+f2+000+f3+00000+"

	def readline(self):


		# Take the query message (stored in self._last_message) and decode it to get everything we need.

		if self._last_message[0] == "q":
			# This is a query message.
			result = Messages.decode_query_message(self._last_message)

			output_message = Messages.build_output_message(result, [math.sin(time.localtime().tm_sec)] * len(result.keys()))

			return output_message

		elif self._last_message == "c":
			self._last_message = ""
			return "f0"



