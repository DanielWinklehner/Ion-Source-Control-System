from __future__ import division
import device

import h5py
import numpy as np


class DataLogging:

	def __init__(self, log_filename):
		self._log_filename = log_filename

	def initialize(self):
		self._file_object = h5py.File(self._log_filename, "w")
