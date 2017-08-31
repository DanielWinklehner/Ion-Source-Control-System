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
import copy
from multiprocessing import Process, Pipe
from collections import deque

from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QFileDialog

import pyqtgraph as pg
import numpy as np

from gui import MainWindow
from gui.dialogs.PlotChooseDialog import PlotChooseDialog
from gui.dialogs.PlotSettingsDialog import PlotSettingsDialog
from gui.dialogs.ProcedureDialog import ProcedureDialog
from gui.dialogs.ErrorDialog import ErrorDialog
from lib.Device import Device
from lib.Channel import Channel
from lib.Procedure import Procedure

def query_server(com_pipe, server_url, debug=False):
    """ Sends info from RasPi server to listener pipe """
    _keep_communicating = True
    _com_period = 5.0
    _device_dict_list = None
    poll_count = 0
    poll_time = timeit.default_timer()
    _paused = False

    while _keep_communicating:
        # Do the timing of this process:
        _thread_start_time = timeit.default_timer()
        if com_pipe.poll():
            _in_message = com_pipe.recv()
            if _in_message[0] == "com_period":
                _com_period = _in_message[1]
            elif _in_message[0] == "device_or_channel_changed":
                _device_dict_list = _in_message[1]
            elif _in_message[0] == "pause_query":
                _paused = not _paused 

        if _device_dict_list is not None and _device_dict_list and not _paused:
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
    """ Gets info from server pipe & passes it to main thread, 
        so that GUI updates are thread-safe """
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
        self._keep_communicating = True

    @property
    def isRunning(self):
        return self._keep_communicating

    @isRunning.setter
    def isRunning(self, val):
        self._keep_communicating = val

    @pyqtSlot()
    def listen(self):
        self.sig_status.emit('Listener started')

        while True:
            # wrap this in a "while True" because self._keep_communicating 
            # will change. Want to resume if it becomes true again.
            while self._keep_communicating:
                if self._listen_pipe.poll():
                    gui_message = self._listen_pipe.recv()
                    if gui_message[0] == "polling_rate":
                        self.sig_poll_rate.emit(gui_message[1])
                    elif gui_message[0] == "query_response":
                        self.sig_device_info.emit(gui_message[1])

                app.processEvents()
                if self._terminate:
                    break

            if self._terminate:
                self.sig_status.emit('Listener terminating...')
                break


        self.sig_done.emit('Listener stopped')

    def terminate(self):
        self.sig_status.emit('Listener received terminate signal')
        self._terminate = True

class ControlSystem():
    def __init__(self, server_ip='127.0.0.1', server_port=80, debug=False):
        ## Set up Qt UI and connect UI signals
        self._window = MainWindow.MainWindow()
        
        self._window.ui.btnSave.triggered.connect(self.on_save_button)
        self._window.ui.btnLoad.triggered.connect(self.on_load_button)
        self._window._btnquit.triggered.connect(self.on_quit_button)

        self._window.ui.btnStartPause.clicked.connect(self.on_start_pause_click)
        self._window.ui.btnStop_2.clicked.connect(self.on_stop_click)
        self._window.ui.btnStop_2.setEnabled(False)

        self._window.ui.btnSetupDevicePlots.clicked.connect(self.show_PlotChooseDialog)
        self._window.ui.btnAddProcedure.clicked.connect(self.show_ProcedureDialog)
        self._window.sig_device_channel_changed.connect(self.on_device_channel_changed)

        ## Plotting timer
        self._plot_timer = QTimer()
        self._plot_timer.timeout.connect(self.update_value_displays)
        self._plot_timer.start(20)

        ##  Initialize RasPi server
        self.debug = debug
        self._server_url = 'http://{}:{}/'.format(server_ip, server_port)

                
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
            for device_id, device_info in devices.items():
                self._window.status_message('Found {} with ID {} on port {}.'.format(
                    device_info['identifyer'], device_id, device_info['port']))
        else:
            print('[Error getting devices] {}: {}'.format(r.status_code, r.text))
        

        ## Set up communication pipes.
        self._keep_communicating = False
        self._polling_rate = 15.0
        self._com_period = 1.0 / self._polling_rate

        ## Set up data dictionaries
        self._devices = {}
        self._device_name_id_map = {}
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

    def update_gui_devices(self):
        for name, device in self._devices.items():
            device.update()
        self._window.update_overview(self._devices)
        self._window.update_device_settings(self._devices)
        self._window.update_plots(self._devices, self._plotted_channels)
        self._window.update_procedures(self._procedures)

    def on_start_pause_click(self):
        btn = self._window.ui.btnStartPause
        if btn.text() == 'Start':
            self.setup_communication_threads()
            btn.setText('Pause')
            self._window.ui.btnStop_2.setEnabled(True)
        elif btn.text() == 'Pause':
            self._pipe_gui.send(('pause_query',))
            self._keep_communicating = False
            self._listener.isRunning = False
            btn.setText('Resume')
        else:
            self._pipe_gui.send(('pause_query',))
            self._keep_communicating = True
            self._listener.isRunning = True
            btn.setText('Pause')

    def on_stop_click(self):
        self.shutdown_communication_threads()
        self._window.ui.btnStartPause.setText('Start')
        self._window.ui.btnStop_2.setEnabled(False)

        try:
            # if server has not been started, _listener won't exist
            self._listener.terminate()
        except AttributeError:
            pass

        try:
            # deques might not exist. If not, then don't do anything.
            for xs, ys in zip(self._x_values.items(), self._y_values.items()):
                xs[1].clear()
                ys[1].clear()
        except:
            pass
        
        for device_name, device in self._devices.items():
            device.error_message = ''
            for channel_name, channel in device.channels.items():
                channel._plot_widget.layout().itemAt(0).widget().setData(0,0)
        #self._plotted_channels = {}
        #self.update_gui_devices()

    def setup_communication_threads(self):
        """ Create gui/server pipe pair, start listener """
        self._pipe_gui, pipe_server = Pipe()

        self._com_process = Process(target=query_server, args=(pipe_server,
                                                            self._server_url,
                                                            False,))

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
        self._listener = Listener(self._pipe_gui)
        query_thread = QThread()
        query_thread.setObjectName('listener_thread')
        self._threads.append((query_thread, self._listener))
        self._listener.moveToThread(query_thread)

        self._listener.sig_status.connect(self.on_listener_status)
        self._listener.sig_poll_rate.connect(self.on_listener_poll_rate)
        self._listener.sig_device_info.connect(self.on_listener_device_info)
        query_thread.started.connect(self._listener.listen)

        query_thread.start()

    def shutdown_communication_threads(self):
        self._keep_communicating = False
        try:
            self._com_process.terminate()
            self._com_process.join()
        except:
            pass
        if self._threads:
            for thread, listener in self._threads:
                thread.quit()

    @pyqtSlot(str)
    def on_listener_status(self, data: str):
        """ update status bar with thread message """
        self._window.status_message(data)

    @pyqtSlot(float)
    def on_listener_poll_rate(self, data: float):
        """ update polling rate in GUI """
        self._window.set_polling_rate('%.2f' % (data))

    @pyqtSlot(dict)
    def on_listener_device_info(self, data: dict):
        """ update device info in GUI """
        parsed_response = data
        #print(parsed_response)
        timestamp = parsed_response["timestamp"]

        for device_name, device in self._devices.items():
            device_id = device.device_id
            if not device.locked and device_id in parsed_response.keys():
                if "ERROR" not in parsed_response[device_id]:
                    if device.error_message != '':
                        device.error_message = ''
                    for channel_name, value in parsed_response[device_id].items():
                        channel = device.get_channel_by_name(channel_name)
                        if channel is None:
                            device.error_message = 'Could not find channel with name {}.'.format(channel_name)
                            continue

                        # Scale value back to channel
                        channel.value = value / channel.scaling
                        self.update_stored_values(device_name, channel_name, timestamp)

                        try:
                            self.log_data(channel, timestamp)
                        except Exception as e:
                            if self.debug:
                                print("Exception '{}' caught while trying to log data.".format(e))
                else:
                    if device.error_message != parsed_response[device_id]:
                        device.error_message = parsed_response[device_id]

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
            for name, device in self._devices.items():
                for chname, channel in device.channels.items():
                    if channel._read_widget is None:
                        continue

                    if channel.data_type in [int, float]:
                        fmt = '{:' + channel.displayformat + '}'
                        val = str(fmt.format(channel.value))
                        channel._read_widget.setText(val)

        # update the pinned plot
        if self._pinned_plot_name != ():
            self._pinned_curve.setData(self._x_values[self._pinned_plot_name],
                                       self._y_values[self._pinned_plot_name],
                                       clear=True, _callsync='off')

        # if we are on the plotting tab, update the plots there too
        if self._window.current_tab == 'plots':
            for device_name, device in self._devices.items():
                for channel_name, channel in device.channels.items():
                    channel._plot_curve.setData(
                            self._x_values[(channel.parent_device.name, channel_name)],
                            self._y_values[(channel.parent_device.name, channel_name)],
                            clear=True, _callsync='off')
        app.processEvents()

    @pyqtSlot(object, dict)
    def on_device_channel_changed(self, obj, vals):
        """ Called when user presses Save Changes button on the settings page """

        if vals == {}:
            # We are adding a device/channel
            if isinstance(obj, Device):
                self.add_device(obj)
            elif isinstance(obj, Channel):
                obj.parent_device.add_channel(obj)
                self.add_channel_to_gui(obj)
        else:
            # We are editing a device/channel
            for procedure_name, procedure in self._procedures.items():
                used_devices, used_channels = procedure.devices_channels_used()
                if obj.name in used_devices + used_channels:
                    self.show_ErrorDialog('Object is part of a procedure. Delete the procedure before editing this object.')
                    return
            for attr, val in vals.items():
                # attempt to set attributes. Need to make sure we only have
                # unique channel/device names, and arduino ids
                if attr == 'name' and val != obj.name:
                    if isinstance(obj, Channel):
                        if val in obj.parent_device.channels.keys():
                            self.show_ErrorDialog('Channel name is already used by another channel on this device. Choose a unique name for this channel.')
                            continue

                        # channel name is unique, so we update it in the device object
                        obj.parent_device.channels[val] = obj.parent_device.channels.pop(obj.name)
                        self._x_values[(obj.parent_device.name, val)] = \
                                self._x_values.pop((obj.parent_device.name, obj.name))
                        self._y_values[(obj.parent_device.name, val)] = \
                                self._y_values.pop((obj.parent_device.name, obj.name))

                    elif isinstance(obj, Device):
                        if val in self._devices.keys():
                            self.show_ErrorDialog('Device name is already used by another device. Choose a unique name for this device.')
                            continue

                        # device name is unique, so update it in the Control System
                        self._devices[val] = self._devices.pop(obj.name)
                        if obj.name in self._pinned_plot_name:
                            self._pinned_plot_name = (val, self._pinned_plot_name[1])
                        for channel_name, channel in self._devices[val].channels.items():
                            self._x_values[(val, channel_name)] = \
                                    self._x_values.pop((obj.name, channel_name))
                            self._y_values[(val, channel_name)] = \
                                    self._y_values.pop((obj.name, channel_name))

                elif isinstance(obj, Device) and attr == 'device_id' and val != obj.device_id:
                    if val in [x.device_id for name, x in self._devices.items()]:
                        self.show_ErrorDialog('Device ID has already been assigned to another device. Choose a unique device ID for this device')
                        continue
                    
                # use setattr to set obj properties by 'attr' which is a string
                setattr(obj, attr, val)

        self.device_or_channel_changed()
        self.update_gui_devices()

    @pyqtSlot(str, str)
    def set_pinned_plot_callback(self, device, channel):
        # click button emits (device, channel)
        key = (device.name, channel.name)
        self._pinned_plot_name = key 
        
        # update plot settings
        x = self._window._gbpinnedplot.layout().itemAt(0).widget()
        x.setLabel('left', '{} [{}]'.format(channel.label, channel.unit))
        Channel.update_plot_settings(x, self._pinned_curve, channel.plotsettings) 
        self._window._gbpinnedplot.setTitle('{}.{}'.format(device.label, channel.label))

    @pyqtSlot(Channel)
    def set_plot_settings_callback(self, ch):
        rng = ch._plotitem.viewRange()
        ch._plot_settings['x']['min'] = rng[0][0]
        ch._plot_settings['x']['max'] = rng[0][1]
        ch._plot_settings['y']['min'] = rng[1][0]
        ch._plot_settings['y']['max'] = rng[1][1]

        _plotsettingsdialog = PlotSettingsDialog(ch)
        _plotsettingsdialog.exec_()

    @pyqtSlot()
    def on_quit_button(self):
        # shut down communication threads
        self.shutdown_communication_threads()
        self._window.close()

    def device_or_channel_changed(self):
        """ Sends a device changed request to the pipe """
        device_dict_list = [{
            'device_driver': device.driver,
            'device_id': device.device_id,
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

        try:
            self._pipe_gui.send(pipe_message)
        except AttributeError:
            # _pipe_gui will not exist if the server has not been started
            # at least once. If it hasn't, no need to send this message
            pass

    def add_channel_to_gui(self, channel):
        if channel.parent_device is None:
            print('Attempt to add channel with no parent device to gui')
            return

        key = (channel.parent_device.name, channel.name)
        channel._set_signal.connect(self.set_value_callback)
        channel._pin_signal.connect(self.set_pinned_plot_callback)
        channel._settings_signal.connect(self.set_plot_settings_callback)
        self._x_values[key] = deque(np.linspace(time.time() - 5.0, time.time(),
                                                self._retain_last_n_values),
                                                maxlen=self._retain_last_n_values)
        self._y_values[key] = deque(np.zeros(self._retain_last_n_values),
                                             maxlen=self._retain_last_n_values)
        channel.parent_device.update()


    def add_device(self, device):
        """ Adds a device to the control system """
        if device.name in self._devices.keys():
            self.show_ErrorDialog('Device with the same name already loaded.')
            return False

        device.parent = self

        # Add device to the list of devices in the control system
        self._devices[device.name] = device
        self._device_name_id_map[device.device_id] = device.name

        for chname, ch in device.channels.items():
            self.add_channel_to_gui(ch)

        return True

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

    @pyqtSlot(Channel, object)
    def set_value_callback(self, channel, val):
        """ Gets updated channel info from GUI, creates a message to send to server """
        values = None
        if channel.data_type == float:
            values = val * channel.scaling
        else:
            values = float(val)
        if self.debug:
            print('Set value callback was called with widget {}, '
                  'type {}, and scaled value {}.'.format(channel, 
                                                         channel.data_type, 
                                                         channel.value))

        _data = {'device_driver': channel.parent_device.driver,
                 'device_id': channel.parent_device.device_id,
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

    # ---- dialogs ----
    def on_save_button(self):
        fileName, _ = QFileDialog.getSaveFileName(self._window,
                            "Save Devices as JSON","","Text Files (*.txt)")
        
        if fileName == '':
            return
        
        if fileName[-4:] != '.txt':
            fileName += '.txt'

        with open(fileName, 'w') as f:
            output = {}
            for device_name, device in self._devices.items():
                output[device_name] = device.get_json()

            json.dump(output, f, sort_keys=True, indent=4, separators=(', ', ': '))

    def on_load_button(self):
        successes = 0
        fileName, _ = QFileDialog.getOpenFileName(self._window,
                            "Load devices from JSON","","Text Files (*.txt)")

        if fileName == '':
            return

        with open(fileName, 'r') as f:
            try:
                data = json.loads(f.read())
            except:
                self.show_ErrorDialog('Unable to read JSON file')
                return

        for device_name, device_data in data.items():
            filtered_params = {}
            for key, value in device_data.items():
                if not key == "channels":
                    filtered_params[key] = value

            device = Device(**filtered_params)

            for channel_name, channel_data in device_data['channels'].items():
                data_type_str = channel_data['data_type']
                channel_data['data_type'] = eval(data_type_str.split("'")[1])

                ch = Channel(**channel_data)
                device.add_channel(ch)

            if self.add_device(device):
                successes += 1

        if successes > 0:
            self.update_gui_devices()
            self._window.status_message('Loaded {} devices from JSON.'.format(successes))

    @pyqtSlot()
    def show_PlotChooseDialog(self):
        _plotchoosedialog = PlotChooseDialog(self._devices, self._plotted_channels)
        accept, chs = _plotchoosedialog.exec_()
        self._plotted_channels = chs
        self.update_gui_devices()

    def add_procedure(self, procedure):
        self._procedures[procedure.name] = procedure
        procedure._edit_sig.connect(self.edit_procedure)
        procedure._delete_sig.connect(self.delete_procedure)

    def edit_procedure(self, proc):
        self.show_ProcedureDialog(False, proc = proc)

    def delete_procedure(self, proc):
        del self._procedures[proc.name]
        self._window.update_procedures(self._procedures)

    @pyqtSlot()
    @pyqtSlot(Procedure)
    def show_ProcedureDialog(self, btnbool, proc=None):
        _proceduredialog = ProcedureDialog(self._devices, self._procedures.keys(), proc)
        accept, rproc = _proceduredialog.exec_()

        if rproc is not None:
            if proc is not None:
                # if we edited a procedure delete the old version before adding the new one
                self.delete_procedure(proc)

            self.add_procedure(rproc)
            self._window.update_procedures(self._procedures)

    @pyqtSlot()
    def show_ErrorDialog(self, error_message='Error'):
        _errordialog = ErrorDialog(error_message)
        _errordialog.exec_()
        self.update_gui_devices()

    def run(self):
        #self.setup_communication_threads()
        self.update_gui_devices()
        self._window.show()

# ---- End control system class ----

def dummy_device(n, ard_id):
    # --- Set up the Dummy PS Controller 1 --- #
    ps_controller1 = Device("ps_controller" + str(n),
                            device_id=ard_id,
                            label="Dummy HV Power Supplies",
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

    #cs.add_device(dummy_device(1, "95432313837351706152"))
    #cs.add_device(dummy_device(2, "95433343933351B012C2"))

    cs.run()
    sys.exit(app.exec_())
