from __future__ import division
import Device

import h5py
import numpy as np
import time
import os


class DataLogging:
    def __init__(self, log_filename):
        self._log_filename = log_filename
        self._file_object = None
        self._data_set = {}

    def initialize(self):
        if not os.path.exists("log"):
                os.makedirs("log")
        self._file_object = h5py.File(self._log_filename, "w")
        self._main_group = self._file_object.create_group("mist1_control_system")

    def add_device(self, device):
        self._main_group.create_group(device.name())

    def add_channel(self, channel):

        device_name = channel.get_parent_device().name()
        channel_name = channel.name()
        # data_type = np.dtype( [ ('timestamp', np.float64), ('value', np.int32) ] )
        data_type = np.dtype(np.float64)

        if device_name not in self._main_group.keys():
            self._main_group.create_group(device_name)

        if channel_name not in self._main_group[device_name].keys():
            dset = self._main_group[device_name].create_dataset(channel_name, (1, 2), maxshape=(None, 2),
                                                                dtype=data_type, compression="gzip")
            self._data_set[dset.name] = dset

    def log_value(self, channel, timestamp):

        device_name = channel.get_parent_device().name()
        channel_name = channel.name()
        value = channel.get_value()

        if value is not None:
            dataset_name = "{}/{}/{}".format(self._main_group.name, device_name, channel_name)
            dset = self._data_set[dataset_name]

            dset.resize((len(dset) + 1, 2))

            a = (timestamp, value)
            dset[len(dset) - 1] = a

            self._file_object.flush()
