import sys
from multiprocessing import Process, Pipe
import threading
import json
import queue
import time
from datetime import datetime, timedelta
from collections import deque

from flask import Flask, request
import numpy as np

from MIST1DeviceDriver import MIST1DeviceDriver, driver_mapping
from SerialCOM import *
from HtmlPage import *
from DeviceFinder import *


class DeviceManager(object):
    """ Handles sending/receiving messages for each device """
    def __init__(self, serial_number, driver, com):
        self._serial_number = serial_number
        self._driver = driver
        self._com = com

        # the generic query message which is sent every time the user queries the device
        self._query_message = None
        self._query_device_data = None # some devices need this to translate the response back

        # device's current values (response to query command)
        self._current_values = {}

        # polling rate for this device
        self._polling_rate = 0
        self._com_times = deque(maxlen=20)
        self._polling_rate_max = 1. # Hz

        self._set_command_queue = queue.Queue()
        self._terminate = False

    @property
    def port(self):
        return self._com.port

    @property
    def current_values(self):
        return self._current_values

    @property
    def serial_number(self):
        return self._serial_number

    @property
    def query_message(self):
        return self._query_message

    @query_message.setter
    def query_message(self, device_data):
        self._query_device_data = device_data
        self._query_message = self._driver.translate_gui_to_device(device_data)

    def add_command_to_queue(self, cmd):
        self._set_command_queue.put(cmd)

    def run(self):
        while not self._terminate:
            t1 = datetime.now()

            self._waiting_for_resp = True
            if not self._set_command_queue.empty():
                # try to send the command to the device
                cmd = self._set_command_queue.get_nowait()

                msgs = self._driver.translate_gui_to_device(cmd)

                for msg in msgs:
                    # this takes some time
                    device_response = self._com.send_message(msg)

                print('Device response was {}'.format(device_response))
                #self._current_values = self._driver.translate_device_to_gui(device_response)

            else:
                # update the device's current value
                # this could take some time
                if self._query_message is not None:
                    #com_resp_list = [self._com.send_message(msg) \
                    #                    for msg in self._query_message]
                    com_resp_list = []
                    for msg in self._query_message:
                        com_resp = self._com.send_message(msg)
                        com_resp_list.append(com_resp)

                    try:
                        resp = self._driver.translate_device_to_gui(
                            com_resp_list, self._query_device_data
                        )
                    except:
                        continue

                    # add additional info to be shown in the GUI
                    resp['timestamp'] = time.time()
                    resp['polling_rate'] = self._polling_rate

                    self._current_values = resp

            t2 = datetime.now()
            delta = (t2 - t1).total_seconds()

            if 1.0 / delta > self._polling_rate_max:
                time.sleep(1.0 / self._polling_rate_max - delta)

            self._com_times.append((datetime.now() - t1).total_seconds())
            self.update_polling_rate()


    def update_polling_rate(self):
        self._polling_rate = 1.0 / np.mean(self._com_times)

    def terminate(self):
        self._terminate = True


def serial_watchdog(com_pipe, debug, port_identifiers):
    """
    Function to be called as a process. Watches the serial ports and looks for devices plugged in
    or removed.
    Underscore at beginning prevents flask_classy from making it a route in the Flask server.
    """
    _keep_communicating2 = True
    _com_freq = 2.0  # (Hz)
    _com_period = 1.0 / _com_freq  # (s)
    _debug = debug
    _port_identifiers = port_identifiers

    serial_finder = SerialDeviceFinder(port_identifiers)
    ftdi_finder = FTDIDeviceFinder(port_identifiers)
    finder_list = [serial_finder, ftdi_finder]

    while _keep_communicating2:

        # Do the timing of this process:
        _thread_start_time = time.time()

        if com_pipe.poll():
            _in_message = com_pipe.recv()

            if _in_message[0] == "com_period":
                _com_period = _in_message[1]
            elif _in_message[0] == "shutdown":
                break
            elif _in_message[0] == "port_identifiers":
                _port_identifiers = _in_message[1]
                # update each finder's identifier list
                for finder in finder_list:
                    finder.identifiers = _port_identifiers
            elif _in_message[0] == "debug":
                _debug = _in_message[1]


        _device_added = False
        _device_removed = False
        _finder_info = {}
        for finder in finder_list:
            _finder_info[finder.name] = finder.find_devices()
            if _finder_info[finder.name]['added'] != {}:
                _device_added = True

            if _finder_info[finder.name]['obsolete']:
                _device_removed = True

        if _device_added or _device_removed:
            # If something has changed:
            if _debug:
                pass # need to update this block
                #print("Updated List:")
                #for _key, item in _current_ports_by_ids.items():
                #    print ("{} #{} at port {}".format(item["identifier"], _key, item["port"]))

            pipe_message = ["updated_list", _finder_info]
            com_pipe.send(pipe_message)

        # Do the timing of this process:
        _sleepy_time = _com_period - time.time() + _thread_start_time

        if _sleepy_time > 0.0:
            if _debug:
                print("Watchdog alive, sleeping for {} s.".format(_sleepy_time))

            time.sleep(_sleepy_time)

# /===============================\
# |                               |
# |         Flask server          |
# |                               |
# \===============================/

app = Flask(__name__)

_mydebug = False
_pipe_server, pipe_serial_watcher = Pipe()
_ports_by_ids = {}
_ids_by_ports = {}
_watch_proc = Process(target=serial_watchdog,
                      args=(pipe_serial_watcher, _mydebug, driver_mapping))

_watch_proc.daemon = True
_keep_communicating = False
_initialized = False
_devices = {}
_threads = {}
_current_responses = {}

@app.route("/initialize/")
def initialize():

    global _initialized
    global _keep_communicating

    if _initialized:
        return "Server has already been initialized"
    else:
        _keep_communicating = True
        threading.Timer(0.1, listen_to_pipe).start()
        time.sleep(0.2)  # Need to wait a little for the thread to be ready to receive initial info of watchdog
        _initialized = True

        if not _watch_proc.is_alive():
            _watch_proc.start()
            return "Initializing Control System RasPi server services...Started the watchdog process."
        else:
            return "Initializing Control System RasPi server services...There was already a watchdog process running!"

@app.route("/device/set", methods=['GET', 'POST'])
def set_value_on_device():

    # Load the data stream
    set_cmd = json.loads(request.form['data'])
    set_cmd["set"] = True

    # For reference: This is the message from the GUI:
    # device_data = {'device_driver': device_driver_name,
    #                'device_id': device_id,
    #                'locked_by_server': False,
    #                'channel_ids': [channel_ids],
    #                'precisions': [precisions],
    #                'values': [values],
    #                'data_types': [types]}

    old_device_id = set_cmd['device_id']
    device_id_parts = old_device_id.split("_")
    port_id = device_id_parts[0]
    device_id = device_id_parts[0]

    if len(device_id_parts) > 1:
        device_id = device_id_parts[1]

    set_cmd['device_id'] = device_id

    _devices[device_id].add_command_to_queue(set_cmd)

    set_cmd['device_id'] = old_device_id

    if _mydebug:
        print("The message to the device is: {}".format(msg))

    '''
    try:
        print(msg)
        for cmd in msg:
            device_response = _comms[port_id].send_message(cmd)

    except Exception as e:
        device_response = "Error, exception happened: {}".format(e)

    return json.dumps(device_response)
    '''
    return 'Command sent to device'

@app.route("/device/query", methods=['GET', 'POST'])
def query_device():
    # Load the data stream
    data = json.loads(request.form['data'])
    devices_responses = {}
    for i, device_data in enumerate(data):
        device_id = device_data['device_id']
        device_data['set'] = False

        try:
            _devices[device_id].query_message = device_data
            devices_responses[device_id] = _devices[device_id].current_values
        except KeyError:
            # device not found on server
            devices_responses[device_id] = "ERROR: Device not found on server"

        '''
        old_device_id = device_data['device_id']
        device_id_parts = old_device_id.split("_")
        port_id = device_id_parts[0]
        device_id = device_id_parts[0]

        if len(device_id_parts) > 1:
            device_id = device_id_parts[1]

        device_data['device_id'] = device_id

        device_data['device_id'] = old_device_id
        '''
    global _current_responses
    _current_responses = json.dumps(devices_responses)
    return _current_responses

@app.route("/device/active/")
def all_devices():

    global _devices
    ports = {}
    for id, dm in _devices.items():
        ports[id] = dm.port
    return json.dumps(ports)

def listen_to_pipe():

    global _ports_by_ids
    global _ids_by_ports

    if _pipe_server.poll():

        gui_message = _pipe_server.recv()

        if gui_message[0] == "updated_list":

            temp_ports_by_ids = {}
            temp_ids_by_ports = {}

            if _mydebug:
                print("Updating ports/ids in main server")

            message_info = gui_message[1]
            for name, finder_result in message_info.items():
                if name == 'serial':
                    for key, val in finder_result['current'].items():
                        temp_ports_by_ids[key] = val
                        temp_ids_by_ports[val['port']] = key
                    _obsolete = finder_result['obsolete']
                    _added = finder_result['added']

                    for _key in _obsolete.keys():
                        # gracefully remove devices/threads
                        _devices[_key].terminate()
                        _threads[_key].join()
                        if not _threads[key].is_alive():
                            del _devices[_key]
                            del _threads[_key]

                    for _key, _port_info in _added.items():
                        # add devices/threads
                        _baud_rate = driver_mapping[_port_info["identifier"]]["baud_rate"]
                        com = SerialCOM(arduino_id=_key,
                                        port_name=_port_info["port"],
                                        baud_rate=_baud_rate,
                                        timeout=1.0)
                        drv = driver_mapping[_port_info["identifier"]]['driver']
                        _devices[_key] = DeviceManager(_key, drv, com)
                        _threads[_key] = threading.Thread(target=_devices[_key].run())
                        _threads[_key].start()
                '''
                elif name == 'ftdi':
                    for key, val in finder_result['current'].items():
                        if key in _ids_by_ports.keys():
                            # don't overwrite anything that is already present
                            # because we want to keep the serial number that was
                            # created when the device was added the first time
                            continue
                        temp_ports_by_ids[key] = val
                        temp_ids_by_ports[val['port']] = key
                    _obsolete = finder_result['obsolete']
                    _added = finder_result['added']

                    for key in _obsolete.keys():
                        del _comms[key]
                    for key, info in _added.items():
                        _baud_rate = driver_mapping[info['identifier']]['baud_rate']
                        _comms[key] = manager().FTDICOM(vend_prod_id=info['vend_prod'],
                                                        port_name=0,
                                                        baud_rate=_baud_rate,
                                                        timeout=1.0)
                        # we can only get the serial number after creating the com
                        # object, but we still want to use it as the key for everything
                        # since the user will put it in the gui
                        sn = _comms[key].serial_number()
                        _comms[sn] = _comms.pop(key)
                        temp_ports_by_ids[sn] = temp_ports_by_ids.pop(key)
                        temp_ids_by_ports[info['port']] = sn

                        com = SerialCOM(arduino_id=_key,
                                        port_name=_port_info["port"],
                                        baud_rate=_baud_rate,
                                        timeout=1.0)
                        devices[_key] = DeviceManager(_key, driver_mapping[_port_info["identifier"]], com)
                        threads[_key] = threading.Thread(target = dm.run())
                        threads[_key].start()
                '''
            # update the server's dictionaries all at once
            _ports_by_ids = temp_ports_by_ids
            _ids_by_ports = temp_ids_by_ports

    if _keep_communicating:
        threading.Timer(0.5, listen_to_pipe).start()


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5000)
