#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Code adapted from MIST1ControlSystem.py (Python 2/gtk3+ version)

import sys
import requests
import json
import timeit
import time
import threading
from multiprocessing import Process, Pipe
from collections import deque

from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication

import pyqtgraph as pg
import numpy as np

from gui import MainWindow
from lib.Device import Device
from lib.Channel import Channel #, Procedure

def query_server(com_pipe, server_url, debug=False):
    """ Sends info from RasPi server to listener pipe """
    _keep_communicating = True
    _com_period = 5.0
    _device_dict_list = None
    poll_count = 0
    poll_time = timeit.default_timer()

    while _keep_communicating:
        # Do the timing of this process:
        _thread_start_time = timeit.default_timer()
        if com_pipe.poll():
            _in_message = com_pipe.recv()
            if _in_message[0] == "com_period":
                _com_period = _in_message[1]
            elif _in_message[0] == "device_or_channel_changed":
                _device_dict_list = _in_message[1]

        if _device_dict_list is not None and len(_device_dict_list) > 0:
            poll_count += 1
            _url = server_url + "device/query"
            _data = {'data': json.dumps(_device_dict_list)}

            try:
                _r = requests.post(_url, data=_data)
                timestamp = time.time()
                _response_code = _r.status_code
            except Exception as e:
                if debug:
                    print("Exception '{}' caught while communicating with RasPi server.".format(e))
                continue

            if _response_code == 200:
                _response = _r.text
                if debug:
                    print("The response was: {}".format(json.loads(_response)))
            else:
                if debug:
                    print("Response code was not 200: {}".format(_response_code))
                continue

            #if _response.strip() != r"{}" and "error" not in str(_response).lower():
            if _response.strip() != r"{}":
                parsed_response = json.loads(_response)
                parsed_response["timestamp"] = timestamp
                pipe_message = ["query_response", parsed_response]

                com_pipe.send(pipe_message)

        if poll_count == 20:
            duration = timeit.default_timer() - poll_time
            poll_time = timeit.default_timer()
            poll_count = 0
            polling_rate = 20.0 / duration

            pipe_message = ["polling_rate", polling_rate]
            com_pipe.send(pipe_message)

            if debug:
                print("Polling rate = {}".format(polling_rate))

        # Do the timing of this process:
        _sleepy_time = _com_period - timeit.default_timer() + _thread_start_time

        #if debug:
            #print("Sleeping for {} s".format(_sleepy_time))

        if _sleepy_time > 0.0:
            time.sleep(_sleepy_time)

class Listener(QObject):
    """ Gets info from server pipe & passes it to main thread, so that GUI updates are thread-safe """
    # status message and ending signals
    sig_status = pyqtSignal(str)
    sig_done = pyqtSignal(str)

    # gui update signals
    sig_poll_rate = pyqtSignal(float)
    sig_device_info = pyqtSignal(dict)

    def __init__(self, listen_pipe):
        super().__init__()
        self._terminate = False # flag to stop listening process
        self._listen_pipe = listen_pipe

    @pyqtSlot()
    def listen(self):
        self.sig_status.emit('Listener started')
        
        while True:
            
            if self._listen_pipe.poll():
                gui_message = self._listen_pipe.recv()
                if gui_message[0] == "polling_rate":
                    self.sig_poll_rate.emit(gui_message[1])
                elif gui_message[0] == "query_response":
                    self.sig_device_info.emit(gui_message[1])
            
            app.processEvents()
            if self._terminate:
                self.sig_status.emit('Listener terminating...')
                break
        
        self.sig_done.emit('Listener done')
     
    def terminate(self):
        self.sig_status.emit('Listener received terminate signal')
        self._terminate = True

class ControlSystem():
    def __init__(self, server_ip='127.0.0.1', server_port=80, debug=False):
        ## Set up Qt UI and connect UI signals
        self._window = MainWindow.MainWindow()
        self._window._btnquit.triggered.connect(self.on_quit_button)
        self._window.sig_plots_changed.connect(self.on_plots_changed)

        ## Plotting timer
        self._plot_timer = QTimer()
        self._plot_timer.timeout.connect(self.update_value_displays)
        self._plot_timer.start(20)
                
        ##  Initialize RasPi server
        self.debug = debug
        self._server_url = 'http://{}:{}/'.format(server_ip, server_port)
        """         
        try:
            r = requests.get(self._server_url + 'initialize/')
            if r.status_code == 200:
                self._window.status_message(r.text)
            else:
                print('[Error initializing server] {}: {}'.format(r.status_code, r.text))
        except Exception as e:
            print('Exception was: {}'.format(e))
            exit()
        
        ## Get devices connected to server
        r = requests.get(self._server_url + 'device/active')
        if r.status_code == 200:
            devices = json.loads(r.text)
            print(devices.items())
            for device_id, device_info in devices.items():
                self._window.status_message('Found {} with ID {} on port {}.'.format(
                    device_info['identifyer'], device_id, device_info['port']))
        else:
            print('[Error getting devices] {}: {}'.format(r.status_code, r.text))
        """
        ## Set up communication pipes.
        self._keep_communicating = False 
        self._polling_rate = 15.0
        self._com_period = 1.0 / self._polling_rate
        self._pipe_gui, pipe_server = Pipe()

        self._com_process = Process(target=query_server, args=(pipe_server,
                                                            self._server_url,
                                                            debug,))
        
        ## Set up data dictionaries
        self._devices = {}
        self._device_name_arduino_id_map = {}
        self._read_textboxes = {} # textboxes on overview page to update
        self._x_values = {}
        self._y_values = {}
        self._procedures = {}
        self._critical_procedures = {}
        self._plotted_channels = {}
        self._threads = None # holds listener thead
        self._retain_last_n_values = 500 # number of points to plot before removing

        self._pinned_curve = self._window._pinnedplot.plot(pen='r')
        self._pinned_plot_name = ()

        self._window.status_message('Initialization complete.')

    def setup_communication_threads(self):
        """ For each device, we create a thread to communicate with the corresponding Arduino. """
        self._threads = []
        self._keep_communicating = True

        # Tell the query process the current polling rate:
        pipe_message = ["com_period", self._com_period]
        self._pipe_gui.send(pipe_message)

        # Get initial device/channel list and send to query process:
        self.device_or_channel_changed()

        # Start the query process:
        self._com_process.start()

        # Create listener object, and start listener process
        # Also connect all Qt signals/slots
        listener = Listener(self._pipe_gui)
        query_thread = QThread()
        query_thread.setObjectName('listener_thread')
        self._threads.append((query_thread, listener))
        listener.moveToThread(query_thread)

        listener.sig_status.connect(self.on_listener_status)
        listener.sig_poll_rate.connect(self.on_listener_poll_rate)
        listener.sig_device_info.connect(self.on_listener_device_info)
        query_thread.started.connect(listener.listen)

        query_thread.start()

    @pyqtSlot(str)
    def on_listener_status(self, data: str):
        """ update status bar with thread message """
        self._window.status_message(data)
        print(data)

    @pyqtSlot(float)
    def on_listener_poll_rate(self, data: float):
        """ update polling rate in GUI """
        self._window.set_polling_rate('%.2f' % (data))

    @pyqtSlot(dict)
    def on_listener_device_info(self, data: dict):
        """ update device info in GUI """
        parsed_response = data
        timestamp = parsed_response["timestamp"]
        devices = self._devices

        for device_name, device in devices.items():
            arduino_id = device.arduino_id
            if not device.locked and arduino_id in parsed_response.keys():
                if "ERROR" not in parsed_response[arduino_id]:
                    self._window.on_device_working(arduino_id)
                    for channel_name, value in parsed_response[arduino_id].items():
                        channel = device.get_channel_by_name(channel_name)
                        # Scale value back to channel
                        channel.value = value / channel.scaling
                        self.update_stored_values(device_name, channel_name, timestamp)

                        try:
                            self.log_data(channel, timestamp)
                        except Exception as e:
                            if self.debug:
                                print("Exception '{}' caught while trying to log data.".format(e))
                else:
                    self._window.on_device_error(arduino_id, err_msg=parsed_response[arduino_id])

    def update_stored_values(self, device_name, channel_name, timestamp):
        # update the stored data dictionaries
        self._x_values[(device_name, channel_name)].append(timestamp)
        self._y_values[(device_name, channel_name)].append(
            self._devices[device_name].channels[channel_name].value)
        
    @pyqtSlot()
    def update_value_displays(self):
        """ This function is called by a QTimer to ensure the GUI has a chance
            to get input. Handles updating of 'read' values on the overview
            page, and redraws plots if applicable """

        # update read values on overview page
        if self._window.current_tab == 'main':
            for arduino_id, boxinfo in self._read_textboxes.items():
                for chname, data in boxinfo.items():
                    data['textbox'].setText(str(data['channel'].value))

        # update the pinned plot
        if self._pinned_plot_name != ():
            self._pinned_curve.setData(self._x_values[self._pinned_plot_name],
                                       self._y_values[self._pinned_plot_name],
                                       clear=True, _callsync='off')

        # if we are on the plotting tab, update the plots there too
        if self._window.current_tab == 'plots':
            if len(self._window._plotted_channels) > 0:
                for names, data in self._window._plotted_channels.items():
                    data['curve'].setData(self._x_values[names], 
                                          self._y_values[names], 
                                          clear=True, _callsync='off')


    @pyqtSlot(dict)
    def on_plots_changed(self, plottedchs):
        self._plotted_channels = plottedchs
        for names, data in self._plotted_channels.items():
            data['btnPin'].connect(self.on_pin_plot_button)

    @pyqtSlot(tuple)
    def on_pin_plot_button(self, data):
       # click button emits (device, channel)
       self._pinned_plot_name = (data[0].name, data[1].name)
       self._window._gbpinnedplot.setTitle(data[0].label + ' / ' + data[1].label)

    @pyqtSlot()
    def on_quit_button(self):
        # shut down communication threads
        self._keep_communicating = False
        self._com_process.terminate()
        self._com_process.join()
        for thread, listener in self._threads:
            thread.quit()

        # close window
        self._window.close()

    def device_or_channel_changed(self):
        """ Sends a device changed request to the pipe """
        device_dict_list = [{
            'device_driver': device.driver,
            'device_id': device.arduino_id,
            'locked_by_server': False,
            'channel_ids': [name for name, mych in device.channels.items() if
                         mych.mode in ['read', 'both']],
            'precisions': [mych.precision for name, mych in device.channels.items() if
                        mych.mode in ['read', 'both']],
            'values': [None for name, mych in device.channels.items() if
                    mych.mode in ['read', 'both']],
            'data_types': [str(mych.data_type) for name, mych in device.channels.items() if
                        mych.mode in ['read', 'both']]
            }

            for device_name, device in self._devices.items()
            if not (device.locked or
                    len([name for name, mych in device.channels.items() if
                         mych.mode in ['read', 'both']]) == 0)]

        pipe_message = ["device_or_channel_changed", device_dict_list]
        self._pipe_gui.send(pipe_message)

    def add_device(self, device):
        """ Adds a device to the control system """

        # Set the control system as the device parent
        device.parent = self

        # Add device to the list of devices in the control system
        self._devices[device.name] = device
        self._device_name_arduino_id_map[device.arduino_id] = device.name

        # connect form controls to main control system set value function
        readboxes, emitters = self._window.add_device_to_overview(device)
        for chname, emitter in emitters.items():
            #print(emitter)
            emitter.connect(self.set_value_callback)

        #for chname, readboxes in readboxes.items():
        self._read_textboxes[device.arduino_id] = readboxes

        """ 
        # Add corresponding channels to the hdf5 log.
        for channel_name, channel in device.channels().items():
            if channel.mode() == "read" or channel.mode() == "both":
                self._data_logger.add_channel(channel)
    

        # Add the device to the settings page tree.
        device_iter = self._settings_page_tree_store.insert(None, (len(self._settings_page_tree_store) - 1),
                                                            [device.label(), "Device", "edit_device", device.name(),
                                                             device.name()])
        """
        for channel_name, channel in device.channels.items():
            # Add to "values".
            # Initialize with current time and 0.0 this will eventually flush out of the deque
            self._x_values[(device.name, channel_name)] = deque(np.linspace(time.time() - 5.0,
                                                                              time.time(),
                                                                              self._retain_last_n_values),
                                                                  maxlen=self._retain_last_n_values)
            self._y_values[(device.name, channel_name)] = deque(np.zeros(self._retain_last_n_values),
                                                                  maxlen=self._retain_last_n_values)
            # TODO: Add device to settings page

    @pyqtSlot(dict)
    def set_value_callback(self, emitter_info):
        """ Gets updated channel info from GUI, creates a message to send to server """
        # TODO: Need an elegant way to do this...
        channel = emitter_info['channel']
        values = None
        if channel.data_type == float:
            values = emitter_info['value'] * channel.scaling
        else:
            values = emitter_info['value']
        if self.debug:
            print('Set value callback was called with widget {}, '
                  'type {}, and scaled value {}.'.format(channel, channel.data_type, channel.value))

        _data = {'device_driver': channel.parent_device.driver,
                 'device_id': channel.parent_device.arduino_id,
                 'locked_by_server': False,
                 'channel_ids': [channel.name],
                 'precisions': [None],
                 'values': [values],
                 'data_types': [str(channel.data_type)]}

        # Create a new thread that sends the set command to the server and
        # waits for an answer.
        new_set_thread = threading.Thread(target=self.update_device_on_server, args=(_data,))
        new_set_thread.start()

    def update_device_on_server(self, _data):
        """ Sends POST request to RasPi server with new device/channel info """
        _url = self._server_url + "device/set"
        try:
            _data = {'data': json.dumps(_data)}
            _r = requests.post(_url, data=_data)

            if _r.status_code == 200:
                print("Sending set command to server successful, response was: {}".format(_r.text))
            else:
                print("Sending set command to server unsuccessful, response-code was: {}".format(_r.status_code))
        except Exception as e:
            if self.debug:
                print("Exception '{}' caught while communicating with RasPi server.".format(e))

    def run(self):
        #self.setup_communication_threads()
        self._window.show()


def dummy_device(n, ard_id):
    # --- Set up the Dummy PS Controller 1 --- #
    ps_controller1 = Device("ps_controller" + str(n),
                            arduino_id=ard_id,
                            label="Dummy HV Power Supplies",
                            debug=mydebug,
                            driver='Arduino')
    
    ch = Channel(name="o2", label="Source HV On/Off",
                 upper_limit=1,
                 lower_limit=0,
                 data_type=bool,
                 display_order=10,
                 mode="write")
    
    ps_controller1.add_channel(ch)
    
    ch = Channel(name="v2", label="Source HV Voltage",
                 upper_limit=20.0,
                 lower_limit=0.0,
                 data_type=float,
                 precision=2,
                 scaling=10.0/20.0,
                 display_order=9,
                 unit="kV",
                 mode="both")
    
    ps_controller1.add_channel(ch)
    
    ch = Channel(name="i2", label="Source HV Current",
                 upper_limit=120.0,
                 lower_limit=0.0,
                 data_type=float,
                 precision=2,
                 scaling=10.0/120.0,
                 display_order=8,
                 unit="mA",
                 mode="both")
    
    ps_controller1.add_channel(ch)
    
    ch = Channel(name="o1", label="Einzel Lens On/Off",
                 upper_limit=1,
                 lower_limit=0,
                 data_type=bool,
                 display_order=6,
                 mode="write")
    
    ps_controller1.add_channel(ch)
    
    ch = Channel(name="v1", label="Einzel Lens Voltage",
                 upper_limit=30.0,
                 lower_limit=0.0,
                 data_type=float,
                 precision=2,
                 scaling=10.0/30.0,
                 display_order=5,
                 unit="kV",
                 mode="both")
    
    ps_controller1.add_channel(ch)
    
    ch = Channel(name="i1", label="Einzel Lens Current",
                 upper_limit=40.0,
                 lower_limit=0.0,
                 data_type=float,
                 precision=2,
                 scaling=10.0/40.0,
                 display_order=4,
                 unit="mA",
                 mode="both")
    
    ps_controller1.add_channel(ch)
    return ps_controller1
    

if __name__ == '__main__':
    app = QApplication([])
    cs = ControlSystem(server_ip='10.77.0.3', server_port=5000, debug=False)

    mydebug = False

    cs.add_device(dummy_device(1, "95432313837351706152"))
    cs.add_device(dummy_device(2, "95433343933351B012C2"))

    cs.run()
    sys.exit(app.exec_())
