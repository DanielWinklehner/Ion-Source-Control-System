from __future__ import division

import gi
gi.require_version('Gtk', '3.0')  # nopep8
gi.require_version('Gdk', '3.0')  # nopep8
from gi.repository import Gdk, GLib
# from gi.repository import Gtk, GLib, GObject, Gdk

import json
import time
import timeit
import threading
import requests
from collections import deque
from Device import Device
from Channel import Channel
from GUIWidgets import *
from DataLogging import DataLogging
import Dialogs as MIST1Dialogs
from MIST1Plot import MIST1Plot
import GUIWidgets
import numpy as np
from multiprocessing import Process, Pipe


__author__ = "Aashish Tripathee and Daniel Winklehner"
__doc__ = """GUI for a simple Ion Source Control System"""


def query_server(com_pipe, server_url, debug=False):
    """
    Process that handles communication with the RasPi server
    :return:
    """
    _keep_communicating = True
    _com_period = 5.0
    _device_dict_list = None
    _server_url = server_url
    _debug = debug
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

            _url = _server_url + "device/query"
            _data = {'data': json.dumps(_device_dict_list)}

            try:

                _r = requests.post(_url, data=_data)
                timestamp = time.time()
                _response_code = _r.status_code

            except Exception as e:

                if _debug:
                    print("Exception '{}' caught while communicating with RasPi server.".format(e))

                continue

            if _response_code == 200:

                _response = _r.text

                if _debug:
                    print("The response was: {}".format(json.loads(_response)))

            else:

                if _debug:
                    print("Response code was not 200: {}".format(_response_code))

                continue

            if _response.strip() != r"{}" and "error" not in str(_response).lower():

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

            if _debug:
                print("Polling rate = {}".format(polling_rate))

        # Do the timing of this process:
        _sleepy_time = _com_period - timeit.default_timer() + _thread_start_time

        if _debug:
            print("Sleeping for {} s".format(_sleepy_time))

        if _sleepy_time > 0.0:
            time.sleep(_sleepy_time)


class MIST1ControlSystem:
    """
    Main class that runs the GUI for the MIST-1 control system
    """

    def __init__(self, server_ip="127.0.0.1", server_port=80, debug=False):
        """
        Initialize the control system GUI
        """
        self.debug = debug

        # --- Load the GUI from XML file and initialize connections --- #
        self._builder = Gtk.Builder()
        self._builder.add_from_file("MIST1ControlSystem.glade")
        self._builder.connect_signals(self.get_connections())

        self._main_window = self._builder.get_object("main_window")
        self._arduino_vbox = self._builder.get_object("arduino_vbox")

        # --- Get some widgets from the builder --- #
        self._status_bar = self._builder.get_object("main_statusbar")
        self._log_textbuffer = self._builder.get_object("log_texbuffer")
        self._overview_grid = self._builder.get_object("overview_grid")

        self._emergency_stop_button = self._builder.get_object("stop_button")
        self._emergency_stop_button.set_name("stop_button")

        # --- Paint the stop button red! --- #
        style_provider = Gtk.CssProvider()

        css = """
        GtkButton#stop_button {
            color: #000000;
            font-size: 18pt;
            background-image: url('bg.png');
        }
        """

        style_provider.load_from_data(css)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # --- INitialize the server connection --- #
        self._server_ip = server_ip
        self._server_port = server_port
        self._server_url = "http://{}:{}/".format(server_ip, server_port)
        self._server_infobar = None

        try:
            # Send the initialize command to the server
            r = requests.get(self._server_url + "initialize/")

            if r.status_code != 200:

                print("Couldn't initialize server!")
                print("Response was {}: {}".format(r.status_code, r.text))
                exit()

            else:
                self._status_bar.push(0, r.text)

        except Exception as e:

            print("Could not connect to the server at {}. Shutting down.".format(self._server_url))
            print("Exception was: {}".format(e))

            exit()

        r = requests.get(self._server_url + "device/active/")

        if r.status_code == 200:

            devices = json.loads(r.text)

            for device_id, port in devices.items():

                self._status_bar.push(0, "Found device {} connected to port {} of the server.".format(device_id,
                                                                                                      port))

        else:

            if self.debug:
                print("{}: {}".format(r.status_code, r.text))
        # ---------------------------- #

        # --- The main device dict --- #
        self._devices = {}
        self._device_name_arduino_id_map = {}

        self._initialized = False

        self._keep_communicating = False

        # Two threads to communicate with the server:
        # Query thread just listens to the pipe coming from the query process.
        # Command thread doesn't need a process as commands are short and quick.
        self._query_thread = None

        # This will be used for the main GUI <--> Server polling rate
        self._communication_thread_poll_count = None
        self._communication_thread_start_time = timeit.default_timer()
        self._polling_rate = 15.0  # (Hz) # TODO: make this a user-adjustable parameter
        self._com_period = 1.0 / self._polling_rate  # Period between calls to the communicate function (s)

        # Dictionaries of last self._retain_last_n_values. These will be initialized with
        # a collections.deque for each channel later.
        self._x_values = {}
        self._y_values = {}

        self._pipe_gui, pipe_com_proc = Pipe()

        self._com_proc = Process(target=query_server, args=(pipe_com_proc,
                                                            self._server_url,
                                                            self.debug,))
        self._com_proc.daemon = True

        self._arduino_status_bars = {}

        self._set_value_for_widget = None

        # HDF5 logging.
        self._data_logger = None

        self._last_checked_for_devices_alive = timeit.default_timer()
        self._alive_device_names = set()
        self._check_for_alive_interval = 5  # In seconds.

        self._edit_frame = None

        # self._settings_tree_view = None
        # self._settings_page_tree_store = None

        self._settings_page_tree_store = Gtk.TreeStore(str, str, str, str, str)
        self._settings_tree_view = Gtk.TreeView(self._settings_page_tree_store)

        # self.setup_settings_page()

        self._keep_procedure_thread_running = False
        self._procedures = {}
        self._procedure_thread = None

        self._keep_critical_procedure_threads_running = False
        self._critical_procedures = {}  # These get their own threads.
        self._critical_procedure_threads = {}

        self._plot_page_channels_tree_store = Gtk.TreeStore(bool, str, str, str, str)

        self._plotting_page_grid = None
        self._plotting_frames = {}  # Dictionary of all plotting frames. Key = Tuple(device_name, channel_name).
        self._mist1_plots = {}  # Dictionary of all plotting frames. Key = Tuple(device_name, channel_name).
        self._we_are_on_plot_page = False

        # TODO: Make this adjustable by user during runtime (MIST1Plot should be set up for this already) -DW
        self._retain_last_n_values = 500

        self._status_bar.push(0, "Initialization Complete.")

    def register_data_logging_file(self, filename):
        self._data_logger = DataLogging(log_filename=filename)
        self._data_logger.initialize()

    def log_data(self, channel, timestamp):
        self._data_logger.log_value(channel=channel, timestamp=timestamp)

    def listen_to_pipe(self):

        while self._keep_communicating:

            if self._pipe_gui.poll():

                gui_message = self._pipe_gui.recv()

                if gui_message[0] == "polling_rate":
                    # To be thread safe, anything that changes the GUI display from within a thread
                    # should be added through GLib.idle_add().
                    GLib.idle_add(self._server_infobar.set_value, gui_message[1])

                elif gui_message[0] == "query_response":

                    parsed_response = gui_message[1]
                    timestamp = parsed_response["timestamp"]
                    devices = self._devices

                    for device_name, device in devices.items():

                        arduino_id = device.get_arduino_id()

                        if not device.locked() and arduino_id in parsed_response.keys():

                            if "ERR" in parsed_response[arduino_id]:
                                # self._status_bar.push(2, "Error: " + str(parsed_response[arduino_id]))
                                pass

                            else:

                                for channel_name, value in parsed_response[arduino_id].items():

                                    channel = device.get_channel_by_name(channel_name)

                                    # Scale value back to channel

                                    channel.set_value(value / channel.scaling())

                                    try:
                                        self.log_data(channel, timestamp)

                                    except Exception as e:
                                        if self.debug:
                                            print("Exception '{}' caught while trying to log data.".format(e))

                                    try:
                                        self.update_stored_values(device_name, channel_name, timestamp)

                                    except Exception as e:
                                        if self.debug:
                                            print("Exception '{}' caught while updating stored values.".format(e))

                                    try:
                                        # To be thread safe, anything that changes the GUI display from within a thread
                                        # should be added through GLib.idle_add().
                                        GLib.idle_add(self.update_gui, channel)

                                    except Exception as e:
                                        if self.debug:
                                            print("Exception '{}' caught while updating GUI.".format(e))

        return self._keep_communicating

    def about_program_callback(self, menu_item):
        """
        :param menu_item:
        :return:
        """
        if self.debug:
            print("About Dialog called by {}".format(menu_item))

        dialog = self._builder.get_object("about_dialogbox")
        dialog.run()
        dialog.destroy()

        return 0

    def add_device_callback(self, button):

        dialog = MIST1Dialogs.AddDevicesDialog(self._main_window)

        dialog.add_pre_existing_devices(self._devices)

        dialog.initialize()

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            # Reinitialize all devices.
            for device_name, device in self._devices.items():

                if not device.initialized():

                    del self._devices[device_name]

                    if self.debug:

                        print("{} clicked. Adding a new device.".format(button))

                    self.add_device(device)

            self.reinitialize()

        elif self.debug and response == Gtk.ResponseType.CANCEL:

                print("Cancel clicked ({}).".format(button))

        dialog.destroy()

    def edit_device_callback(self, button):

        dialog = MIST1Dialogs.EditDevicesDialog(self._main_window)

        dialog.add_pre_existing_devices(self._devices)

        dialog.initialize()

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            # Reinitialize all devices.
            if self.debug:

                print("Save Changes clicked ({}).".format(button))

            self.reinitialize()

            # for device_name, device in self._devices.items():

            #   # if not device.initialized():
            #   #   del self._devices[device_name]
            #   #   print "Adding a new device."
            #   #   self.add_device(device)

        elif self.debug and response == Gtk.ResponseType.CANCEL:

                print("Cancel clicked ({}).".format(button))

        dialog.destroy()

    def load_device_from_file_callback(self, button):

        dialog = Gtk.FileChooserDialog("Please choose a file.", self._main_window,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK),
                                       )

        filter_text = Gtk.FileFilter()
        filter_text.set_name("JSON files")
        filter_text.add_mime_type("application/json")
        dialog.add_filter(filter_text)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()

            if self.debug:

                print("Open clicked ({}).".format(button))
                print("File selected: " + filename)

            device = Device.load_from_json(filename)

            if device.name() not in self._devices.keys():
                self.add_device(device)

                self.initialize()

                self._devices[device.name()].get_overview_frame().show_all()

        elif self.debug and response == Gtk.ResponseType.CANCEL:

            print("Cancel clicked.")

        dialog.destroy()

        return 0

    def add_arduino_status_bar(self, arduino_id, status_bar):

        self._arduino_status_bars[arduino_id] = status_bar

    def add_channel(self, channel, device):

        if channel.name() not in device.channels().keys():

            # Add channel to device.
            device.add_channel(channel)

            channel.initialize()

            # Add channel to logger.
            self._data_logger.add_channel(channel)

            self._main_window.show_all()

            # Add channel to settings page tree.
            # First, find the position of device in the iterator.
            device_iter = None

            for j in range(len(self._settings_page_tree_store)):

                if device.name() == self._settings_page_tree_store[j][-1]:

                    # position = j
                    device_path = Gtk.TreePath.new_from_string("{}".format(j))
                    device_iter = self._settings_page_tree_store.get_iter(device_path)
                    break

            print("{}: {}".format(device_iter, self._settings_page_tree_store.get_value(device_iter, 0)))

            channel_iter = self._settings_page_tree_store.insert(device_iter, 0,
                                                                 [channel.label(),
                                                                  "Channel",
                                                                  "edit_channel",
                                                                  channel.name(),
                                                                  device.name()])

            print("{}: {}".format(channel_iter, self._settings_page_tree_store.get_value(channel_iter, 0)))

            self._settings_page_tree_store.append(device_iter,
                                                  ["<b>[ Add a New Channel ]</b>",
                                                   "",
                                                   "add_new_channel",
                                                   device.name(),
                                                   device.name()])

            self._settings_tree_view.show_all()

        return 0

    def add_procedure(self, procedure):
        # TODO: NOT IN USE RIGHT NOW.

        if procedure.get_priority() == -1:
            # Gets its own thread so is a "critical" procedure.
            self._critical_procedures[procedure.get_name()] = procedure
        else:
            self._procedures[procedure.get_name()] = procedure

    def register_device_with_server(self, device):
        # return self.send_message_to_server("register_device", [device.get_arduino_id()])
        pass

    def add_device(self, device):
        """
        Adds a device to the control system
        :return:
        """

        # Set the control system as the device parent
        device.set_parent(self)

        # Add device to the list of devices in the control system
        self._devices[device.name()] = device

        self._device_name_arduino_id_map[device.get_arduino_id()] = device.name()

        # Add corresponding channels to the hdf5 log.
        for channel_name, channel in device.channels().items():
            if channel.mode() == "read" or channel.mode() == "both":
                self._data_logger.add_channel(channel)

        # Add the device to the settings page tree.

        device_iter = self._settings_page_tree_store.insert(None, (len(self._settings_page_tree_store) - 1),
                                                            [device.label(), "Device", "edit_device", device.name(),
                                                             device.name()])

        for channel_name, channel in device.channels().items():
            self._settings_page_tree_store.append(device_iter,
                                                  [channel.label(), "Channel", "edit_channel",
                                                   channel.name(), device.name()])

            # Add to "values".
            # Initialize with current time and 0.0 this will eventually flush out of the deque
            self._x_values[(device.name(), channel_name)] = deque(np.linspace(time.time() - 5.0,
                                                                              time.time(),
                                                                              self._retain_last_n_values),
                                                                  maxlen=self._retain_last_n_values)
            self._y_values[(device.name(), channel_name)] = deque(np.zeros(self._retain_last_n_values),
                                                                  maxlen=self._retain_last_n_values)

        self._settings_page_tree_store.append(device_iter,
                                              ["<b>[ Add a New Channel ]</b>", "", "add_new_channel",
                                               device.name(), device.name()])

        self._settings_tree_view.show_all()

        return 0

    def listen_for_reconnected_devices(self, devices):

        for device in devices:

            if device.name() in self._devices.keys() and device.name() not in self._alive_device_names:

                if self.debug:

                    print("Reinitializing device {}".format(device.name()))

                device.reinitialize()

    def update_stored_values(self, device_name, channel_name, timestamp):

        self._x_values[(device_name, channel_name)].append(timestamp)
        self._y_values[(device_name, channel_name)].append(
            self._devices[device_name].channels()[channel_name].get_value())

        return False

    def device_or_channel_changed(self):
        """

        :return:
        """

        # device_data = {'device_driver': device_driver_name,
        #                'device_id': device_id,
        #                'locked_by_server': False,
        #                'channel_ids': [channel_ids],
        #                'precisions': [precisions],
        #                'values': [values],
        #                'data_types': [types]}

        device_dict_list = [{'device_driver': device.get_driver(),
                             'device_id': device.get_arduino_id(),
                             'locked_by_server': False,
                             'channel_ids': [name for name, mych in device.channels().items() if
                                             mych.mode() in ['read', 'both']],
                             'precisions': [mych.get_precision() for name, mych in device.channels().items() if
                                            mych.mode() in ['read', 'both']],
                             'values': [None for name, mych in device.channels().items() if
                                        mych.mode() in ['read', 'both']],
                             'data_types': [str(mych.data_type()) for name, mych in device.channels().items() if
                                            mych.mode() in ['read', 'both']]}

                            for device_name, device in self._devices.items()
                            if not (device.locked() or
                                    len([name for name, mych in device.channels().items() if
                                         mych.mode() in ['read', 'both']]) == 0)]

        pipe_message = ["device_or_channel_changed", device_dict_list]
        self._pipe_gui.send(pipe_message)

        return 0

    def send_command_to_server(self, _data):

        _url = self._server_url + "device/set"

        try:

            if self.debug:
                print(_url)
                print(_data)

            _data = {'data': json.dumps(_data)}
            _r = requests.post(_url, data=_data)

            if _r.status_code == 200:

                print("Sending set command to server successful, response was: {}".format(_r.text))

            else:

                print("Sending set command to server unsuccessful, response-code was: {}".format(_r.status_code))

        except Exception as e:
            if self.debug:
                print("Exception '{}' caught while communicating with RasPi server.".format(e))

        return False

    def emergency_stop(self, widget):
        """
        Callback for STOP button, but may also be called if interlock is broken or
        in any other unforseen sircumstance that warrants shutting down all power supplies.
        :param widget:
        :return:
        """

        if self.debug:
            print("Emergency stop was called from {}".format(widget))

        self._status_bar.push(1, "Emergency stop button was pushed!")

        return 0

    def monitor_procedures(self):
        # TODO: NOT IN USE RIGHT NOW.

        # This is the method that all non-critical procedure threads run.

        while self._keep_procedure_thread_running:

            # print "Monitoring all non-critical threads here."

            # TODO:
            # THOUGHT: Should this also have a while loop? I mean, so that we keep on
            # trying to do the procedure until it succeeds.

            for procedure_name, procedure in self._procedures.items():
                if procedure.should_perform_procedure():
                    procedure.act()

    def monitor_critical_procedure(self, critical_procedure):

        # TODO: NOT IN USE RIGHT NOW.
        # This is the method that all critical procedure threads run. Each of them run in a separate thread.

        while self._keep_critical_procedure_threads_running:

            # print("Critical thread running on its own thread.")

            # Technically, we don't have to check this here since it's checked in the Procedure
            # class before actually performing the procedure. But double-checking it probably
            # won't hurt (will have some non-zero cost associated with retrieving values and then
            # computing whether or not all the conditions are satisfied).
            # The second conditional is so that we can keep trying to perform the procedure until we succeed.
            # This is crucial for "critical" procedures.
            while critical_procedure.should_perform_procedure() and (not critical_procedure.act()):

                critical_procedure.act()

    def setup_procedure_threads(self):

        # TODO: NOT IN USE RIGHT NOW.
        # For N critical threads, there's going to be (N + 1) total threads. The N threads are one each
        # for the "crtical" (procedure.priority = -1) procedures. All remaining procedures are processed
        # with just 1 thread.

        # TODO: Need to implement proper thread waiting, especially for "critical" threads.
        # Because critical threads need to have higher priorities than "communication threads".
        # First, setup a general thread i.e. one thread for all non-critical procedures.

        # TODO: THOUGHT: We could pass a list / dictionary of all the procedures we want to monitor here as kwargs.
        # But, that way, the thread would only act only on those procedures that were created at the
        # very beginning. There wouldn't be a straightforward way for this thread to also handle the
        # procedures that were added later on.

        if self._procedure_thread is None:

            self._procedure_thread = threading.Thread(target=self.monitor_procedures)

            self._keep_procedure_thread_running = True

            self._procedure_thread.start()

        # Next, setup one thread each for each of the critical procedures we have.
        for critical_procedure_name, critical_procedure in self._critical_procedures.items():

            critical_procedure_thread = threading.Thread(target=self.monitor_critical_procedure)

            self._critical_procedure_threads[critical_procedure_name] = critical_procedure_thread

            self._keep_critical_procedure_threads_running = True

            self._critical_procedure_threads[critical_procedure_name].start()

        pass

    def setup_communication_threads(self):
        """
        For each device, we create a thread to communicate with the corresponding Arduino.
        :return:
        """
        # for arduino_id, serial_com in self._serial_comms.items():
        # self._communication_thread_mode = 'read'
        # self._communication_thread_poll_count = 0
        # self._communication_thread_start_time = time.time()
        #
        self._keep_communicating = True

        # Tell the query process the current polling rate:
        pipe_message = ["com_period", self._com_period]
        self._pipe_gui.send(pipe_message)

        # Get initial device/channel list and send to query process:
        self.device_or_channel_changed()

        # Start the query process:
        self._com_proc.start()

        # Start a thread that listens to the pipe connecting to the comm process,
        # and one that waits for commands to be sent to server
        self._query_thread = threading.Thread(target=self.listen_to_pipe)
        self._query_thread.start()

        return 0

    def get_arduino_vbox(self):
        return self._arduino_vbox

    def save_as_devices_callback(self, button):

        if self.debug:
            print("Called the save_as_devices callback from {}".format(button))

        def select_all_callback(widget, checkboxes):

            if self.debug:
                print("Called the select_all callback from {}".format(widget))

            for mydevice_name, mycheckbox in checkboxes.items():

                mycheckbox.set_active(True)

        def unselect_all_callback(widget, checkboxes):

            if self.debug:
                print("Called the unselect_all callback from {}".format(widget))

            for mydevice_name, mycheckbox in checkboxes.items():

                mycheckbox.set_active(False)

        dialog = Gtk.FileChooserDialog("Save Device", self._main_window,
                                       Gtk.FileChooserAction.SELECT_FOLDER,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        "_Save", Gtk.ResponseType.OK),
                                       )

        content_area = dialog.get_content_area()

        select_all_label = Gtk.Button("Select All")
        unselect_all_label = Gtk.Button("Unselect All")

        device_checkboxes = {}
        for device_name, device in self._devices.items():
            device_checkboxes[device.name()] = Gtk.CheckButton(device.label())

        info_frame = Gtk.Frame(label="Select Devices To Save", margin=4)
        info_frame.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        info_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, margin=4)
        info_frame.add(info_vbox)

        select_all_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1, margin=4)

        select_all_hbox.pack_start(select_all_label, expand=False, fill=False, padding=5)
        select_all_hbox.pack_start(unselect_all_label, expand=False, fill=False, padding=5)

        select_all_label.connect("clicked", select_all_callback, device_checkboxes)
        unselect_all_label.connect("clicked", unselect_all_callback, device_checkboxes)

        device_name_hboxes = []

        for device_name, checkbox in device_checkboxes.items():
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1, margin=4)

            hbox.pack_start(checkbox, expand=True, fill=True, padding=0)

            device_name_hboxes.append(hbox)

        info_vbox.pack_start(select_all_hbox, expand=True, fill=True, padding=0)

        for hbox in device_name_hboxes:
            info_vbox.pack_start(hbox, expand=True, fill=True, padding=0)

        content_area.add(info_frame)

        content_area.pack_start(info_vbox, expand=False, fill=False, padding=0)

        info_vbox.reorder_child(info_vbox, 0)

        dialog.show_all()

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            directory = dialog.get_filename()

            device_count = 0
            for device_name, device in self._devices.items():

                if device_checkboxes[device_name].get_active():
                    device.write_json(directory + "/" + device_name + ".json")
                    device_count += 1

            msg_dialog = Gtk.MessageDialog(dialog, 0, Gtk.MessageType.INFO,
                                           Gtk.ButtonsType.OK, "Device Save Successful")

            noun = "device"
            if device_count > 1:
                noun += "s"

            msg_dialog.format_secondary_text("Successfully saved {} {} to {}.".format(device_count, noun, directory))
            msg_dialog.run()

            msg_dialog.destroy()

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def settings_expand_all_callback(self, button):

        if self.debug:
            print("Called the settings_expand_all callback from {}".format(button))

        self._settings_tree_view.expand_all()

    def settings_collapse_all_callback(self, button):

        if self.debug:
            print("Called the settings_collapse_all callback from {}".format(button))

        self._settings_tree_view.collapse_all()

    def get_connections(self):
        """
        This just returns a dictionary of connections
        :return:
        """
        con = {"main_quit": self.main_quit,
               "stop_button_clicked_cb": self.emergency_stop,
               "on_main_statusbar_text_pushed": self.statusbar_changed_callback,
               "about_program_menu_item_activated": self.about_program_callback,
               "add_device_toolbutton_clicked_cb": self.add_device_callback,
               "edit_device_toolbutton_clicked_cb": self.edit_device_callback,
               "load_device_from_file_toolbutton_cb": self.load_device_from_file_callback,
               "save_as_devices_toolbutton_clicked_cb": self.save_as_devices_callback,
               "settings_expand_all_clicked_cb": self.settings_expand_all_callback,
               "settings_collapse_all_clicked_cb": self.settings_collapse_all_callback,
               "plotting_setup_channels_clicked_cb": self.plotting_setup_channels_callback,
               "notebook_page_changed": self.notebook_page_changed_callback,
               }

        return con

    def get_overview_grid(self):
        return self._overview_grid

    def set_value_callback(self, emitter, data_type, value):

        channel = emitter.get_parent_channel()

        if self.debug:
            print("Set value callback was called with widget {}, type {}, and scaled value {}.".format(channel,
                                                                                                       data_type,
                                                                                                       value))

        _data = {'device_driver': channel.get_parent_device().get_driver(),
                 'device_id': channel.get_parent_device().get_arduino_id(),
                 'locked_by_server': False,
                 'channel_ids': [channel.name()],
                 'precisions': [None],
                 'values': [value],
                 'data_types': [str(channel.data_type())]}

        # Create a new thread that sends the set command to the server and
        # waits for an answer.
        new_set_thread = threading.Thread(target=self.send_command_to_server, args=(_data,))
        new_set_thread.start()

        return 0

    def initialize(self):
        """
        :return:
        """
        # Initialize the status bar for server polling:
        vbox = self.get_arduino_vbox()

        self._server_infobar = GUIWidgets.FrontPageDisplayValue(name="Server polling rate =",
                                                                displayformat=".1f",
                                                                unit="Hz")

        vbox.pack_start(self._server_infobar, False, False, 4)

        # Initialize the ankered devices first
        for device_name, device in self._devices.items():
            device.initialize()

            for channel_name, channel in device.channels().items():

                if channel.mode() in ["write", "both"]:

                    channel.get_overview_page_display().connect_set_signal()
                    channel.get_overview_page_display().connect('set_signal', self.set_value_callback)

        # Setup connections for widgets (for radio buttons for example).
        # self.set_widget_connections()

        # Any and all remaining initializations go here
        self.setup_communication_threads()

        self.setup_settings_page()

        self.setup_plotting_page()

        # self.setup_procedure_threads()

        self._initialized = True

        return 0

    def settings_add_device_callback(self, button, params):

        if self.debug:
            print("Called the settings_add_device callback from {}".format(button))

        device_name = params['name'].get_text()
        device_label = params['label'].get_text()
        arduino_id = params['arduino_id'].get_text()
        overview_page_presence = params['overview_page_presence'].get_active()

        if self.debug:
            print("Got a new device!")

        new_device = Device(name=device_name, label=device_label, arduino_id=arduino_id)
        new_device.set_overview_page_presence(overview_page_presence)

        self.add_device(new_device)

        self.reinitialize()

    # if self._edit_frame != None:
    #   self._builder.get_object("settings_page_settings_box").remove(self._edit_frame)

    def settings_add_channel_callback(self, button, device_name, params):
        # Default values.

        if self.debug:
            print("Called the settings_add_channel callback from {}".format(button))

        data_type, mode = float, "both"

        data_type_iter = params['data_type'].get_active_iter()

        if data_type_iter is not None:

            model = params['data_type'].get_model()
            data_type, data_type_str = model[data_type_iter][:2]
            data_type = eval(data_type)

        mode_iter = params['mode'].get_active_iter()

        if mode_iter is not None:

            model = params['mode'].get_model()
            mode, mode_str = model[mode_iter][:2]

        # Create a new channel.
        mych = Channel(name=params['name'].get_text(),
                       label=params['label'].get_text(),
                       upper_limit=float(params['upper_limit'].get_text()),
                       lower_limit=float(params['lower_limit'].get_text()),
                       data_type=data_type,
                       mode=mode,
                       unit=params['unit'].get_text())

        # Add the newly created channel to the correct device.
        self.add_channel(mych, self._devices[device_name])

    # if self._edit_frame != None:
    #   self._builder.get_object("settings_page_settings_box").remove(self._edit_frame)

    def device_settings_tree_selection_callback(self, selection):

        if self._edit_frame is not None:

            self._builder.get_object("settings_page_settings_box").remove(self._edit_frame)

        model, treeiter = selection.get_selected()

        if treeiter is not None:

            label = model[treeiter][0]
            # object_type = model[treeiter][1]
            selection_type = model[treeiter][2]
            name = model[treeiter][3]
            device_name = model[treeiter][4]

            edit_device_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin=12)

            if selection_type == "edit_device":

                # Populate the right-side-box with fields to edit device information.
                device = self._devices[device_name]

                self._edit_frame = Gtk.Frame(label="Edit {}".format(label))
                self._edit_frame.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
                self._edit_frame.add(edit_device_vbox)

                grid = Gtk.Grid(column_spacing=20, row_spacing=15)
                edit_device_vbox.add(grid)

                labels = ["Name", "Label", "Arduino ID", "Overview Page Presence"]
                entries = [Gtk.Entry(), Gtk.Entry(), Gtk.Entry(), Gtk.CheckButton()]
                values = [device.name(), device.label(), device.get_arduino_id(), device.is_on_overview_page()]

                last_entry, last_label = None, None

                for label_text, entry, value in zip(labels, entries, values):

                    label = Gtk.Label(xalign=1)
                    label.set_markup("<span foreground='#888a85'>" + label_text + "</span>")

                    if label_text == "Name":

                        grid.add(label)
                        grid.attach_next_to(entry, label, Gtk.PositionType.RIGHT, width=20, height=1)

                    else:

                        grid.attach_next_to(label, last_label, Gtk.PositionType.BOTTOM, width=1, height=1)
                        grid.attach_next_to(entry, last_entry, Gtk.PositionType.BOTTOM, width=20, height=1)

                    entry_type = str(type(entry)).split("'")[1]

                    if entry_type == "gi.repository.Gtk.Entry":

                        entry.set_text(value)

                    elif entry_type == "gi.repository.Gtk.CheckButton":

                        entry.set_active(value)

                    last_entry, last_label = entry, label

                edit_device_save_button = Gtk.Button(label="Save Changes to Device")
                grid.attach_next_to(edit_device_save_button, last_entry, Gtk.PositionType.BOTTOM, width=20, height=1)

            elif selection_type == "add_new_device":

                self._edit_frame = Gtk.Frame(label="Add a New Device")
                self._edit_frame.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
                self._edit_frame.add(edit_device_vbox)

                grid = Gtk.Grid(column_spacing=20, row_spacing=15)
                edit_device_vbox.add(grid)

                labels = ["Name", "Label", "Arduino ID", "Overview Page Presence"]
                entries = [Gtk.Entry(), Gtk.Entry(), Gtk.Entry(), Gtk.CheckButton()]

                last_entry, last_label = None, None

                for label_text, entry in zip(labels, entries):

                    label = Gtk.Label(xalign=1)
                    label.set_markup("<span foreground='#888a85'>" + label_text + "</span>")

                    if label_text == "Name":

                        grid.add(label)
                        grid.attach_next_to(entry, label, Gtk.PositionType.RIGHT, width=20, height=1)

                    else:

                        grid.attach_next_to(label, last_label, Gtk.PositionType.BOTTOM, width=1, height=1)
                        grid.attach_next_to(entry, last_entry, Gtk.PositionType.BOTTOM, width=20, height=1)

                    last_entry, last_label = entry, label

                add_device_button = Gtk.Button(label="Add Device")
                add_device_button.connect("clicked", self.settings_add_device_callback,
                                          dict(name=entries[0], label=entries[1], arduino_id=entries[2],
                                               overview_page_presence=entries[3]))

                grid.attach_next_to(add_device_button, last_entry, Gtk.PositionType.BOTTOM, width=20, height=1)

            elif selection_type == "edit_channel":

                device = self._devices[device_name]
                channel = device.channels()[name]

                self._edit_frame = Gtk.Frame(label="Edit {}".format(label))
                self._edit_frame.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
                self._edit_frame.add(edit_device_vbox)

                grid = Gtk.Grid(column_spacing=20, row_spacing=15)
                edit_device_vbox.add(grid)

                labels = ["Name", "Label", "Lower Limit", "Upper Limit", "Unit"]
                entries = [Gtk.Entry(), Gtk.Entry(), Gtk.Entry(), Gtk.Entry(), Gtk.Entry()]
                values = [channel.name(), channel.label(), channel.lower_limit(),
                          channel.upper_limit(), channel.unit()]

                last_entry, last_label = None, None

                for label_text, entry, value in zip(labels, entries, values):

                    label = Gtk.Label(xalign=1)
                    label.set_markup("<span foreground='#888a85'>" + label_text + "</span>")

                    if label_text == "Name":
                        grid.add(label)
                        grid.attach_next_to(entry, label, Gtk.PositionType.RIGHT, width=20, height=1)
                    else:
                        grid.attach_next_to(label, last_label, Gtk.PositionType.BOTTOM, width=1, height=1)
                        grid.attach_next_to(entry, last_entry, Gtk.PositionType.BOTTOM, width=20, height=1)

                    entry.set_text(str(value))

                    last_entry, last_label = entry, label

                data_type_model_view = Gtk.ListStore(str, str)
                data_type_options = [["bool", "Boolean"], ["int", "Integer"], ["float", "Float"]]

                for option in data_type_options:
                    data_type_model_view.append(option)

                data_type_combo = Gtk.ComboBox.new_with_model_and_entry(data_type_model_view)
                data_type_combo.set_entry_text_column(1)
                data_type_combo.set_active(
                    [x for x, y in data_type_options].index(str(channel.data_type()).split("'")[1]))

                label = Gtk.Label(xalign=1)
                label.set_markup("<span foreground='#888a85'>Data Type</span>")

                grid.attach_next_to(label, last_label, Gtk.PositionType.BOTTOM, width=1, height=1)
                grid.attach_next_to(data_type_combo, last_entry, Gtk.PositionType.BOTTOM, width=20, height=1)

                last_entry = data_type_combo
                last_label = label

                mode_model_view = Gtk.ListStore(str, str)
                mode_options = [["read", "Read"], ["write", "Write"], ["both", "Both"]]

                for option in mode_options:
                    mode_model_view.append(option)

                mode_combo = Gtk.ComboBox.new_with_model_and_entry(mode_model_view)
                mode_combo.set_entry_text_column(1)
                mode_combo.set_active([x for x, y in mode_options].index(channel.mode()))

                label = Gtk.Label(xalign=1)
                label.set_markup("<span foreground='#888a85'>Mode</span>")

                grid.attach_next_to(label, last_label, Gtk.PositionType.BOTTOM, width=1, height=1)
                grid.attach_next_to(mode_combo, last_entry, Gtk.PositionType.BOTTOM, width=20, height=1)

                last_entry, last_label = mode_combo, label

                edit_channel_save_button = Gtk.Button(label="Save Changes to Channel")
                grid.attach_next_to(edit_channel_save_button, last_entry, Gtk.PositionType.BOTTOM, width=20, height=1)

            elif selection_type == "add_new_channel":

                device = self._devices[device_name]

                self._edit_frame = Gtk.Frame(label="Add a New Channel to {}".format(device.label()))
                self._edit_frame.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
                self._edit_frame.add(edit_device_vbox)

                grid = Gtk.Grid(column_spacing=20, row_spacing=15)
                edit_device_vbox.add(grid)

                labels = ["Name", "Label", "Lower Limit", "Upper Limit", "Unit"]
                entries = [Gtk.Entry(), Gtk.Entry(), Gtk.Entry(), Gtk.Entry(), Gtk.Entry(), Gtk.Entry()]

                last_entry, last_label = None, None

                for label_text, entry in zip(labels, entries):

                    label = Gtk.Label(xalign=1)
                    label.set_markup("<span foreground='#888a85'>" + label_text + "</span>")

                    if label_text == "Name":
                        grid.add(label)
                        grid.attach_next_to(entry, label, Gtk.PositionType.RIGHT, width=20, height=1)
                    else:
                        grid.attach_next_to(label, last_label, Gtk.PositionType.BOTTOM, width=1, height=1)
                        grid.attach_next_to(entry, last_entry, Gtk.PositionType.BOTTOM, width=20, height=1)

                    last_entry = entry
                    last_label = label

                data_type_model_view = Gtk.ListStore(str, str)
                data_type_options = [["bool", "Boolean"], ["int", "Integer"], ["float", "Float"]]

                for option in data_type_options:
                    data_type_model_view.append(option)

                data_type_combo = Gtk.ComboBox.new_with_model_and_entry(data_type_model_view)
                data_type_combo.set_entry_text_column(1)
                data_type_combo.set_active([x for x, y in data_type_options].index("float"))

                label = Gtk.Label(xalign=1)
                label.set_markup("<span foreground='#888a85'>Data Type</span>")

                grid.attach_next_to(label, last_label, Gtk.PositionType.BOTTOM, width=1, height=1)
                grid.attach_next_to(data_type_combo, last_entry, Gtk.PositionType.BOTTOM, width=20, height=1)

                last_entry = data_type_combo
                last_label = label

                mode_model_view = Gtk.ListStore(str, str)
                mode_options = [["read", "Read"], ["write", "Write"], ["both", "Both"]]

                for option in mode_options:
                    mode_model_view.append(option)

                mode_combo = Gtk.ComboBox.new_with_model_and_entry(mode_model_view)
                mode_combo.set_entry_text_column(1)
                mode_combo.set_active([x for x, y in mode_options].index("read"))

                label = Gtk.Label(xalign=1)
                label.set_markup("<span foreground='#888a85'>Mode</span>")

                grid.attach_next_to(label, last_label, Gtk.PositionType.BOTTOM, width=1, height=1)
                grid.attach_next_to(mode_combo, last_entry, Gtk.PositionType.BOTTOM, width=20, height=1)

                last_entry, last_label = mode_combo, label

                add_device_button = Gtk.Button(label="Add Channel")
                add_device_button.connect("clicked", self.settings_add_channel_callback, device_name,
                                          dict(name=entries[0], label=entries[1],
                                               lower_limit=entries[2], upper_limit=entries[3], unit=entries[4],
                                               data_type=data_type_combo, mode=mode_combo))
                grid.attach_next_to(add_device_button, last_entry, Gtk.PositionType.BOTTOM, width=20, height=1)

            self._builder.get_object("settings_page_settings_box").add(self._edit_frame)

        self._main_window.show_all()

    def remove_plotting_frame(self, device_name, channel_name):
        plotting_frame = self._plotting_frames[(device_name, channel_name)]

        # Need to readjust position of the plots on the grid.

        # First, find the position that this plotting frame used to take.

        window_width = self._main_window.get_size()[0]
        plot_frame_min_width = 500
        number_of_plots_per_row = int(window_width / plot_frame_min_width)

        total_number_of_plot_frames = len(self._plotting_frames.keys())
        n_rows = np.ceil(total_number_of_plot_frames / number_of_plots_per_row)

        for x in range(int(number_of_plots_per_row) - 1):
            for y in range(int(n_rows)):
                widget = self._plotting_page_grid.get_child_at(x, y)

                if widget == plotting_frame:
                    position = (x, y)
                    break

        self._plotting_page_grid.remove(plotting_frame)

        # Move all other frames so that the cell that we just removed the frame from does not remain empty.
        # max_y depends on whether or not the bottom-most row has just one plot. If it is, that row
        # will eventually be removed since all the plots move one step back.

        # if (total_number_of_plot_frames % number_of_plots_per_row) == 1:
        #   print "bingo! new max_y is",
        #   max_y = int(n_rows) - 1
        #   print max_y
        # else:
        #   max_y = int(n_rows)

        for y in range(int(n_rows)):

            if y < int(n_rows) - 1:

                max_x = int(number_of_plots_per_row)

            else:

                if self.debug:
                    print("bingo")

                max_x = total_number_of_plot_frames % number_of_plots_per_row

            if self.debug:

                print("max x is {}".format(max_x))

            if y < position[1]:
                # Elements before the row where the removal happened. These need not do anything.

                pass

            elif y == position[1]:
                # Elements in the row where the removal happened.
                # What happens to each frame depends on what column it occupied.

                for x in range(max_x):

                    if self.debug:
                        print("Current x, y = {}, {}".format(x, y))

                    widget = self._plotting_page_grid.get_child_at(x, y)

                    if x < position[0]:
                        # Elements before the column where the remove happened. These need not do anything either.
                        pass
                    elif x >= position[1]:
                        # Just shift it one step to the left.
                        if self.debug:
                            print("I need to move {} one step to the left.".format(widget.get_label()))

                        self._plotting_page_grid.remove(widget)
                        self._plotting_page_grid.attach(widget, x - 1, y, width=1, height=1)

            elif y > position[1]:

                for x in range(max_x):

                    if self.debug:
                        print("Current x, y = {}, {}".format(x, y))

                    widget = self._plotting_page_grid.get_child_at(x, y)

                    if x == 0:
                        # This needs to move to the previous row.
                        if self.debug:
                            print("I need to move {} to the previous row.".format(widget.get_label()))

                        self._plotting_page_grid.remove(widget)
                        self._plotting_page_grid.attach(widget, int(number_of_plots_per_row) - 1, y - 1, width=1,
                                                        height=1)
                    else:
                        # Just move it one step to the left.
                        if self.debug:
                            print("I need to move {} one step to the left.".format(widget.get_label()))

                        self._plotting_page_grid.remove(widget)
                        self._plotting_page_grid.attach(widget, x - 1, y, width=1, height=1)

        del self._plotting_frames[(device_name, channel_name)]
        del self._mist1_plots[(device_name, channel_name)]

    def show_plotting_frame(self, device_name, channel_name):

        device = self._devices[device_name]
        channel = device.channels()[channel_name]

        # Create a new frame.
        plot_frame = Gtk.Frame(label="{} : {}".format(device.label(), channel.label()))
        plot_frame.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        self._plotting_frames[(device_name, channel_name)] = plot_frame

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_size_request(200, 200)

        plot_frame.add(box)

        if (device_name, channel_name) not in self._mist1_plots.keys():
            mist1_plot = MIST1Plot(variable_name="{}:{}".format(self._devices[device_name].label(),
                                                                self._devices[device_name].channels()[
                                                                    channel_name].label()),
                                   x_s=self._x_values[(device_name, channel_name)],
                                   y_s=self._y_values[(device_name, channel_name)])

            # mist1_plot.get_canvas().set_yscale('log')
            self._mist1_plots[(device_name, channel_name)] = mist1_plot
        else:

            # This does not work for some reason.

            mist1_plot = self._mist1_plots[(device_name, channel_name)]

        box.pack_start(mist1_plot.get_canvas(), True, True, 0)

        window_width = self._main_window.get_size()[0]
        plot_frame_min_width = 500
        number_of_plots_per_row = int(window_width / plot_frame_min_width)

        total_number_of_plot_frames = len(self._plotting_frames.keys())

        if self.debug:
            print("Total plots = {}".format(total_number_of_plot_frames))

        if total_number_of_plot_frames == 1:
            if self.debug:
                print("Total number = 0")

            self._plotting_page_grid.add(plot_frame)
        else:
            # First find the number of rows.
            n_rows = np.ceil(total_number_of_plot_frames / number_of_plots_per_row)

            if (total_number_of_plot_frames % number_of_plots_per_row) == 0:
                current_column_number = number_of_plots_per_row
            else:
                current_column_number = (total_number_of_plot_frames % number_of_plots_per_row)

            if self.debug:
                print("Total rows = {}".format(n_rows))
                print("Current # of columns = {}".format(current_column_number))

            if n_rows == 1.:
                # Always insert "RIGHT TO SIBLING".

                sibling = self._plotting_page_grid.get_child_at(total_number_of_plot_frames - 2, 0)

                if self.debug:
                    print("Inserting to the Right of ({}, {})".format(total_number_of_plot_frames - 2, 0))

                # grid.attach_next_to(label, last_label, Gtk.PositionType.BOTTOM, width=1, height=1)
                self._plotting_page_grid.attach_next_to(plot_frame, sibling, Gtk.PositionType.RIGHT, width=1, height=1)
            else:
                # Always insert "BOTTOM TO SIBLING."

                sibling = self._plotting_page_grid.get_child_at(current_column_number - 1, n_rows - 2)

                if self.debug:
                    print("Inserting to the Bottom of ({}, {})".format(current_column_number - 1, n_rows - 2))

                self._plotting_page_grid.attach_next_to(plot_frame, sibling, Gtk.PositionType.BOTTOM, width=1, height=1)

        self._plotting_page_grid.show_all()

    def plotting_setup_channels_callback(self, button):

        if self.debug:
            print("Opening Plotting Channels Dialog from {}".format(button))

        dialog = MIST1Dialogs.PlottingChannelsDialog(self._main_window, self._plot_page_channels_tree_store,
                                                     self._plotting_frames.keys())

        response = dialog.run()

        if response == Gtk.ResponseType.OK:

            if self.debug:
                print("The OK button was clicked.")

            selections = dialog.get_selection()

            # Go throught the list of self._plotting_frames.keys()
            # and for each key that's not on selection, remove that element.

            for (device_name, channel_name) in self._plotting_frames.keys():
                if (device_name, channel_name) not in selections:
                    self.remove_plotting_frame(device_name, channel_name)

            for (device_name, channel_name) in selections:
                if (device_name, channel_name) not in self._plotting_frames.keys():

                    if self.debug:
                        print("Recreating a new frame for {}, {}".format(device_name, channel_name))

                    self.show_plotting_frame(device_name, channel_name)

        dialog.destroy()

        return 0

    def setup_channels_for_plotting(self):
        # self._plotting_page_grid.set_column_homogeneous(True)
        # self._plotting_page_grid.set_row_homogeneous(True)

        for device_name, device in self._devices.items():

            device_iter = self._plot_page_channels_tree_store.append(None,
                                                                     [False, device.label(),
                                                                      "Device", device.name(), device.name()])

            for channel_name, channel in device.channels().items():

                if channel.mode() == "read" or channel.mode() == "both" and (
                                channel.data_type() == float or channel.data_type() == int):
                    self._plot_page_channels_tree_store.append(device_iter,
                                                               [False,
                                                                channel.label(), "Channel",
                                                                device.name(), channel.name()])

    def setup_plotting_page(self):

        self._plotting_page_grid = Gtk.Grid(column_spacing=10, row_spacing=10, margin=10)
        self._plotting_page_grid.set_column_homogeneous(True)
        self._plotting_page_grid.set_row_homogeneous(True)

        plotting_box = self._builder.get_object("plotting_box")
        plotting_box.add(self._plotting_page_grid)

        self.setup_channels_for_plotting()

    def setup_settings_page(self):

        scrolled_window = self._builder.get_object("settings_scrolled_window")

        # for device_name, device in self._devices.items():

        # device_iter = self._settings_page_tree_store.append(None,
        #                                                     [device.label(), "Device", "edit_device", device.name(),
        #                                                      device.name()])

        # for channel_name, channel in device.channels().items():
        #     channel_iter = self._settings_page_tree_store.append(device_iter,
        #                                                          [channel.label(), "Channel", "edit_channel",
        #                                                           channel.name(), device.name()])
        #
        # channel_iter = self._settings_page_tree_store.append(device_iter,
        #                                                      ["<b>[ Add a New Channel ]</b>", "", "add_new_channel",
        #                                                       device.name(), device.name()])

        self._settings_page_tree_store.append(None, ["<b>[ Add a New Device ]</b>", "", "add_new_device", "", ""])

        title = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Label", title, markup=0)
        self._settings_tree_view.append_column(column)

        column = Gtk.TreeViewColumn("Object Type", title, markup=1)
        self._settings_tree_view.append_column(column)

        select = self._settings_tree_view.get_selection()
        select.connect("changed", self.device_settings_tree_selection_callback)

        scrolled_window.add(self._settings_tree_view)

        self._main_window.show_all()

    def reinitialize(self):

        for device_name, device in self._devices.items():
            if not device.initialized():
                device.initialize()

        # self.set_widget_connections()

        self.setup_communication_threads()

        self._main_window.show_all()

    def main_quit(self, widget):
        """
        Shuts down the program (and threads) gracefully.
        :return:
        """

        if self.debug:
            print("Called main_quit for {}".format(widget))

        self._main_window.destroy()

        self.shut_down_communication_process()
        self.shut_down_procedure_threads()

        Gtk.main_quit()

        return 0

    def shut_down_procedure_threads(self):
        self._keep_critical_procedure_threads_running = False
        self._keep_procedure_thread_running = False

    def shut_down_communication_process(self):
        """
        :return:
        """
        self._keep_communicating = False
        self._com_proc.terminate()
        self._com_proc.join()

        self._query_thread.join()

        return 0

    def run(self):
        """
        :return:
        """
        self.initialize()

        # --- Show the GUI --- #
        self._main_window.maximize()
        self._main_window.show_all()

        Gtk.main()

        return 0

    def statusbar_changed_callback(self, statusbar, context_id, text):
        """
        Callback that handles what happens when a message is pushed in the
        statusbar
        """

        if self.debug:
            print("Called statusbar_changed callback for statusbar {}, ID = {}".format(statusbar, context_id))

        timestr = time.strftime("%d %b, %Y, %H:%M:%S: ", time.localtime())

        self._log_textbuffer.insert(self._log_textbuffer.get_end_iter(), timestr + text + "\n")

        return 0

    def dummy_update(self):
        pass

    def update_plots(self):

        for device_name, channel_name in self._mist1_plots.keys():
            mist1_plot = self._mist1_plots[(device_name, channel_name)]

            x_s = np.array(self._x_values[(device_name, channel_name)])
            y_s = np.array(self._y_values[(device_name, channel_name)])

            mist1_plot.plot(x_s, y_s)

        return self._we_are_on_plot_page

    def notebook_page_changed_callback(self, notebook, page, page_num):
        """
        Callback for when user switches to a different notebook page in the main notebook.
        :param notebook: a pointer to the gtk notebook object
        :param page: a pointer to the top level child of the page
        :param page_num: page number starting at 0
        :return:
        """

        if self.debug:
            print("Debug: Notebook {} changed page to {}".format(notebook, page))

        if page_num == 1:

            self.update_plots()
            self._we_are_on_plot_page = True
            GLib.idle_add(self.update_plots)

        else:

            self._we_are_on_plot_page = False

        return 0

    @staticmethod
    def update_gui(channel):
        """
        Updates the GUI. This is called from the communication threads through idle_add()
        :return:
        """

        # If display on overview page is desired, update:
        if channel.get_parent_device().is_on_overview_page():

            channel.get_overview_page_display().set_value(channel.get_value())

        return False


if __name__ == "__main__":

    mydebug = False

    # # 95432313837351E00271
    control_system = MIST1ControlSystem(server_ip="10.77.0.2", server_port=5000, debug=mydebug)
    # control_system = MIST1ControlSystem(server_ip="127.0.0.1", server_port=5000, debug=mydebug)

    # Setup data logging.
    current_time = time.strftime('%a-%d-%b-%Y_%H-%M-%S-EST', time.localtime())
    control_system.register_data_logging_file(filename="log/{}.h5".format(current_time))

    # ************************************** Actual Running Devices: ************************************************* #
    # --- Set up ion gauge --- #
    ion_gauge_controller = Device("ig_controller",
                                  arduino_id="954313534383514071A0",
                                  label="Ion Gauge Controller",
                                  driver='Arduino',
                                  debug=mydebug)

    ch = Channel(name="p1", label="APG Pressure",
                 upper_limit=1000.0,
                 lower_limit=0.0,
                 precision=4,
                 displayformat="e",
                 data_type=float,
                 mode="read")

    ion_gauge_controller.add_channel(ch)

    ch = Channel(name="p2", label="AIM Pressure",
                 upper_limit=1000.0,
                 lower_limit=0.0,
                 precision=4,
                 displayformat="e",
                 data_type=float,
                 mode="read")

    ion_gauge_controller.add_channel(ch)
    ion_gauge_controller.set_overview_page_presence(True)
    control_system.add_device(ion_gauge_controller)

    # --- Set up the Sensor Box --- #
    sensor_box = Device("sensor_box",
                        arduino_id="954323138373513060D0",
                        label="Sensor Box",
                        debug=mydebug,
                        driver='Arduino')

    for i in range(5):
        ch = Channel(name="f{}".format(i + 1), label="Flow Meter {}".format(i + 1),
                     upper_limit=10.0,
                     lower_limit=0.0,
                     data_type=float,
                     scaling=0.5,
                     unit="l/min",
                     mode="read")

        sensor_box.add_channel(ch)

    for i in range(7):
        ch = Channel(name="t{}".format(i + 1), label="Temperature {}".format(i + 1),
                     upper_limit=100.0,
                     lower_limit=0.0,
                     data_type=float,
                     unit="C",
                     mode="read")

        sensor_box.add_channel(ch)

    sensor_box.set_overview_page_presence(True)
    control_system.add_device(sensor_box)

    # --- Set up the Interlock Box --- #
    interlock_box = Device("interlock_box",
                           arduino_id="954323138373519002A2",
                           label="Interlock Box",
                           debug=mydebug,
                           driver='Arduino')

    for i in range(2):
        ch = Channel(name="i{}".format(i + 1), label="Interlock {}".format(i + 1),
                     upper_limit=1,
                     lower_limit=0,
                     data_type=bool,
                     mode="read",
                     display_order=-(i + 1))

        interlock_box.add_channel(ch)

    # ch = Channel(name="s1", label="Foreline Valve",
    #              upper_limit=1,
    #              lower_limit=0,
    #              data_type=bool,
    #              mode="write",
    #              display_order=-3)
    #
    # interlock_box.add_channel(ch)
    #
    # ch = Channel(name="s2", label="MFC Shutoff Valve",
    #              upper_limit=1,
    #              lower_limit=0,
    #              data_type=bool,
    #              mode="write",
    #              display_order=-4)
    #
    # interlock_box.add_channel(ch)
    interlock_box.set_overview_page_presence(True)
    control_system.add_device(interlock_box)

    # --- Controller for PS's on HV platform
    # platform_temp_controller = Device("HV Platform Temperature",
    #                                   arduino_id="954313534383514011F0",
    #                                   label="HV Platform Temperature",
    #                                   debug=mydebug,
    #                                   driver='Arduino')
    #
    # ch = Channel(name="t1", label="Feedthrough Temperature",
    #              upper_limit=1000.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              display_order=12,
    #              unit="C",
    #              mode="read")
    #
    # platform_temp_controller.add_channel(ch)
    #
    # ch = Channel(name="t2", label="Backplate Temperature",
    #              upper_limit=1000.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              display_order=11,
    #              unit="C",
    #              mode="read")
    #
    # platform_temp_controller.add_channel(ch)
    # platform_temp_controller.set_overview_page_presence(True)
    # control_system.add_device(platform_temp_controller)
    #
    # filament_ps_controller = Device("Filament Power Supplies",
    #                                 arduino_id="954333437333514001B0",
    #                                 label="Filament Heating",
    #                                 debug=mydebug,
    #                                 driver='Arduino')

    # ch = Channel(name="o1", label="Filament Heating On/Off",
    #              upper_limit=1,
    #              lower_limit=0,
    #              data_type=bool,
    #              display_order=10,
    #              mode="write")
    #
    # filament_ps_controller.add_channel(ch)

    # ch = Channel(name="v1", label="Filament Heating Voltage",
    #              upper_limit=7.5,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=5.0 / 7.5,
    #              display_order=9,
    #              unit="V",
    #              mode="both")
    #
    # filament_ps_controller.add_channel(ch)

    # ch = Channel(name="i1", label="Filament Heating Current",
    #              upper_limit=300.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=1.0/300.0,
    #              display_order=8,
    #              unit="A",
    #              mode="read")
    #
    # filament_ps_controller.add_channel(ch)

    # ch = Channel(name="o2", label="Discharge On/Off",
    #              upper_limit=1,
    #              lower_limit=0,
    #              data_type=bool,
    #              display_order=6,
    #              mode="write")
    #
    # filament_ps_controller.add_channel(ch)
    #
    # ch = Channel(name="v2", label="Discharge Voltage",
    #              upper_limit=150.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=10.0 / 150.0,
    #              display_order=5,
    #              unit="V",
    #              mode="write")
    #
    # filament_ps_controller.add_channel(ch)
    #
    # ch = Channel(name="i2", label="Discharge Current",
    #              upper_limit=24.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=10.0 / 24.0,
    #              display_order=4,
    #              unit="A",
    #              mode="both")
    #
    # filament_ps_controller.add_channel(ch)
    #
    # filament_ps_controller.set_overview_page_presence(True)
    # control_system.add_device(filament_ps_controller)

    # --- Set up HV Power Supplies --- #
    # hv_ps_controller = Device("hv_ps_controller",
    #                           arduino_id="95433343733351507011",
    #                           label="HV Power Supplies",
    #                           debug=mydebug,
    #                           driver='Arduino')

    # ch = Channel(name="o2", label="Source HV On/Off",
    #              upper_limit=1,
    #              lower_limit=0,
    #              data_type=bool,
    #              display_order=10,
    #              mode="write")
    #
    # hv_ps_controller.add_channel(ch)
    #
    # ch = Channel(name="v2", label="Source HV Voltage",
    #              upper_limit=20.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=10.0/20.0,
    #              display_order=9,
    #              unit="kV",
    #              mode="both")
    #
    # hv_ps_controller.add_channel(ch)
    #
    # ch = Channel(name="i2", label="Source HV Current",
    #              upper_limit=120.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=10.0/120.0,
    #              display_order=8,
    #              unit="mA",
    #              mode="both")
    #
    # hv_ps_controller.add_channel(ch)
    #
    # ch = Channel(name="o1", label="Einzel Lens On/Off",
    #              upper_limit=1,
    #              lower_limit=0,
    #              data_type=bool,
    #              display_order=6,
    #              mode="write")
    #
    # hv_ps_controller.add_channel(ch)
    #
    # ch = Channel(name="v1", label="Einzel Lens Voltage",
    #              upper_limit=31.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=10.0/30.0,
    #              display_order=5,
    #              unit="kV",
    #              mode="both")
    #
    # hv_ps_controller.add_channel(ch)
    #
    # ch = Channel(name="i1", label="Einzel Lens Current",
    #              upper_limit=40.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=10.0/40.0,
    #              display_order=4,
    #              unit="mA",
    #              mode="both")
    #
    # hv_ps_controller.add_channel(ch)
    # hv_ps_controller.set_overview_page_presence(True)
    # control_system.add_device(hv_ps_controller)

    # --- Mass Flow Controller --- #
    # mfc_controller = Device("mfc_controller",
    #                         arduino_id="FTJRNRWQ_254",
    #                         label="Mass Flow Controller",
    #                         debug=mydebug,
    #                         driver='RS485')
    #
    # ch = Channel(name="wink", label="Blink LED",
    #              upper_limit=1,
    #              lower_limit=0,
    #              data_type=bool,
    #              mode="write")
    #
    # mfc_controller.add_channel(ch)
    #
    # ch = Channel(name="baud_rate", label="Baud Rate",
    #              upper_limit=10000.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              mode="read")
    #
    # ch = Channel(name="set_point_percent", label="SPP",
    #              upper_limit=140.0,
    #              lower_limit=-20.0,
    #              unit="Percent",
    #              data_type=float,
    #              mode="read")
    #
    # ch = Channel(name="set_point_percent", label="Set Point",
    #              upper_limit=140.0,
    #              lower_limit=-20.0,
    #              unit="Percent",
    #              precision=0,
    #              data_type=float,
    #              mode="write")
    #
    # mfc_controller.add_channel(ch)
    # mfc_controller.set_overview_page_presence(True)
    # control_system.add_device(mfc_controller)

    # --- Set up Solenoid Valves --- #
    solenoid_controller = Device("solenoid_valves",
                                 arduino_id="95433343733351502071",
                                 label="Solenoid Valves",
                                 debug=mydebug,
                                 driver='Arduino')

    ch = Channel(name="s1", label="Foreline Valve",
                 upper_limit=1.0,
                 lower_limit=0.0,
                 unit="",
                 precision=0,
                 data_type=bool,
                 mode="write",
                 display_order=-1)

    solenoid_controller.add_channel(ch)

    ch = Channel(name="s2", label="MFC Shutoff Valve",
                 upper_limit=1.0,
                 lower_limit=0.0,
                 unit="",
                 precision=0,
                 data_type=bool,
                 mode="write",
                 display_order=-2)

    solenoid_controller.add_channel(ch)

    ch = Channel(name="s3", label="Vent Valve",
                 upper_limit=1.0,
                 lower_limit=0.0,
                 unit="",
                 precision=0,
                 data_type=bool,
                 mode="write",
                 display_order=-3)

    solenoid_controller.add_channel(ch)

    ch = Channel(name="s4", label="Faraday Cup In/Out",
                 upper_limit=1.0,
                 lower_limit=0.0,
                 unit="",
                 precision=0,
                 data_type=bool,
                 mode="write",
                 display_order=-4)

    solenoid_controller.add_channel(ch)
    solenoid_controller.set_overview_page_presence(True)
    control_system.add_device(solenoid_controller)
    # **************************************************************************************************************** #

    # ************************************* Dummy Devices in Daniel's Office ***************************************** #
    # --- Set up the Dummy PS Controller 1 --- #
    # ps_controller1 = Device("ps_controller1",
    #                         arduino_id="95432313837351706152",
    #                         label="Dummy HV Power Supplies",
    #                         debug=mydebug,
    #                         driver='Arduino')
    #
    # ch = Channel(name="o2", label="Source HV On/Off",
    #              upper_limit=1,
    #              lower_limit=0,
    #              data_type=bool,
    #              display_order=10,
    #              mode="write")
    #
    # ps_controller1.add_channel(ch)
    #
    # ch = Channel(name="v2", label="Source HV Voltage",
    #              upper_limit=20.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=10.0/20.0,
    #              display_order=9,
    #              unit="kV",
    #              mode="both")
    #
    # ps_controller1.add_channel(ch)
    #
    # ch = Channel(name="i2", label="Source HV Current",
    #              upper_limit=120.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=10.0/120.0,
    #              display_order=8,
    #              unit="mA",
    #              mode="both")
    #
    # ps_controller1.add_channel(ch)
    #
    # ch = Channel(name="o1", label="Einzel Lens On/Off",
    #              upper_limit=1,
    #              lower_limit=0,
    #              data_type=bool,
    #              display_order=6,
    #              mode="write")
    #
    # ps_controller1.add_channel(ch)
    #
    # ch = Channel(name="v1", label="Einzel Lens Voltage",
    #              upper_limit=30.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=10.0/30.0,
    #              display_order=5,
    #              unit="kV",
    #              mode="both")
    #
    # ps_controller1.add_channel(ch)
    #
    # ch = Channel(name="i1", label="Einzel Lens Current",
    #              upper_limit=40.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=10.0/40.0,
    #              display_order=4,
    #              unit="mA",
    #              mode="both")
    #
    # ps_controller1.add_channel(ch)
    #
    # ps_controller1.set_overview_page_presence(True)
    # control_system.add_device(ps_controller1)
    #
    # # Dummy Filament Power Supplies
    # ps_controller2 = Device("ps_controller2",
    #                         arduino_id="95432313837351E00271",
    #                         label="Dummy Filament Power Supplies",
    #                         debug=mydebug,
    #                         driver='Arduino')
    #
    # ch = Channel(name="o1", label="Filament Heating On/Off",
    #              upper_limit=1,
    #              lower_limit=0,
    #              data_type=bool,
    #              display_order=10,
    #              mode="write")
    #
    # ps_controller2.add_channel(ch)
    #
    # ch = Channel(name="v1", label="Filament Heating Voltage",
    #              upper_limit=7.5,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=5.0/7.5,
    #              display_order=9,
    #              unit="V",
    #              mode="write")
    #
    # ps_controller2.add_channel(ch)
    #
    # ch = Channel(name="i1", label="Filament Heating Current",
    #              upper_limit=300.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=0.1/300.0,
    #              display_order=8,
    #              unit="A",
    #              mode="write")
    #
    # ps_controller2.add_channel(ch)
    #
    # ch = Channel(name="o2", label="Discharge On/Off",
    #              upper_limit=1,
    #              lower_limit=0,
    #              data_type=bool,
    #              display_order=6,
    #              mode="write")
    #
    # ps_controller2.add_channel(ch)
    #
    # ch = Channel(name="v2", label="Discharge Voltage",
    #              upper_limit=100.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=10.0/100.0,
    #              display_order=5,
    #              unit="V",
    #              mode="write")
    #
    # ps_controller2.add_channel(ch)
    #
    # ch = Channel(name="i2", label="Discharge Current",
    #              upper_limit=10.0,
    #              lower_limit=0.0,
    #              data_type=float,
    #              precision=2,
    #              scaling=10.0/10.0,
    #              display_order=4,
    #              unit="A",
    #              mode="both")
    #
    # ps_controller2.add_channel(ch)
    #
    # ps_controller2.set_overview_page_presence(True)
    # control_system.add_device(ps_controller2)
    # **************************************************************************************************************** #

    # Run the control system, this has to be last as it does
    # all the initializations and adding to the GUI.
    control_system.run()
