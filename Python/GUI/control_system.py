from __future__ import division

import gi

gi.require_version('Gtk', '3.0')

import json, ast
import copy
import time
import random
import threading
import datetime
import uuid
import requests

from collections import deque

from gi.repository import Gtk, GLib, GObject, Gdk

from client import Client
from procedure import Procedure
from device import Device, Channel
from MIST1_Control_System_GUI_Widgets import *

import data_logging

import dialogs as MIST1Dialogs
from MPLCanvasWrapper3 import MPLCanvasWrapper3
from MIST1Plot import MIST1Plot
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
import matplotlib.cm as cm

from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar

# Maybe have a dedicated add_channel() method just like add_device() so that it can take care of everything,
# like adding the correct channel to the logger, updating the tree view, etc.

__author__ = "Aashish Tripathee and Daniel Winklehner"
__doc__ = """GUI without actual functionality"""


class MIST1ControlSystem:
    """
    Main class that runs the GUI for the MIST-1 control system
    """

    def __init__(self, server_ip="127.0.0.1", server_port=80):
        """
        Initialize the control system GUI
        """

        self._server_ip = server_ip
        self._server_port = server_port
        self._server_url = "http://{}:{}/".format(server_ip, server_port)

        # --- Load the GUI from XML file and initialize connections --- #
        self._builder = Gtk.Builder()
        self._builder.add_from_file("mist_control_system_main_gui.glade")
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

        # --- The main device dict --- #
        self._devices = {}
        self._device_name_arduino_id_map = {}

        self._initialized = False

        self._keep_communicating = False
        self._communication_thread = None

        # key = device_name, value = 'read' / 'write' i.e. which direction the communication is
        # supposed to happen. It's from POV of the GUI i.e. the direction is GUI -> Arduino.
        self._communication_thread_mode = None
        self._communication_thread_poll_count = None
        self._communication_thread_start_time = time.time()
        self._arduino_status_bars = {}

        self._set_value_for_widget = None

        # HDF5 logging.
        self._data_logger = None

        self._last_checked_for_devices_alive = time.time()
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

        # Dictionaries of last self._retain_last_n_values.
        # Key = Tuple(device_name, channel_name)
        # Value = collection.deque(maxlen=self._retain_last_n_values)
        self._x_values = {}
        self._y_values = {}

    def register_data_logging_file(self, filename):
        self._data_logger = data_logging.DataLogging(log_filename=filename)
        self._data_logger.initialize()

    def log_data(self, channel):
        self._data_logger.log_value(channel=channel)

    # pass

    def about_program_callback(self, menu_item):
        """
        :param menu_item:
        :return:
        """
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
                    print "Adding a new device."
                    self.add_device(device)

            self.reinitialize()

        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

        dialog.destroy()

    def edit_device_callback(self, button):

        dialog = MIST1Dialogs.EditDevicesDialog(self._main_window)

        dialog.add_pre_existing_devices(self._devices)

        dialog.initialize()

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            # Reinitialize all devices.

            print "Save Changes clicked."

            # for device_name, device in self._devices.items():

            # 	# if not device.initialized():
            # 	# 	del self._devices[device_name]
            # 	# 	print "Adding a new device."
            # 	# 	self.add_device(device)

            self.reinitialize()

        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

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

            print("Open clicked")
            print("File selected: " + filename)

            device = Device.load_from_json(filename)

            if device.name() not in self._devices.keys():
                self.add_device(device)

                self.initialize()

                self._devices[device.name()].get_overview_frame().show_all()


        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

        return 0

    def set_widget_connections(self):
        for device_name, device in self._devices.items():
            for channel_name, channel in device.channels().items():

                if channel.mode() == "both" or channel.mode() == "write":  # TODO: Find a better way to do this.

                    widget = channel.get_overview_page_display()

                    try:  # According to http://stackoverflow.com/questions/1549801/differences-between-isinstance-and-type-in-python, better to use try-except than check type / instanceof.
                        widget.get_radio_buttons()[0].connect("toggled", self.set_value_callback, widget)
                    except Exception as e:
                        pass

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

            for i in range(len(self._settings_page_tree_store)):
                if device.name() == self._settings_page_tree_store[i][-1]:
                    position = i
                    device_path = Gtk.TreePath.new_from_string("{}".format(i))
                    device_iter = self._settings_page_tree_store.get_iter(device_path)
                    break

            print device_iter, self._settings_page_tree_store.get_value(device_iter, 0)

            channel_iter = self._settings_page_tree_store.insert(device_iter, 0,
                                                                 [channel.label(), "Channel", "edit_channel",
                                                                  channel.name(), device.name()])

            print channel_iter, self._settings_page_tree_store.get_value(channel_iter, 0)

            channel_iter = self._settings_page_tree_store.append(device_iter,
                                                                 ["<b>[ Add a New Channel ]</b>", "", "add_new_channel",
                                                                  device.name(), device.name()])

            self._settings_tree_view.show_all()

        return 0

    def add_procedure(self, procedure):
        # TODO: NOT IN USE RIGHT NOW.

        if procedure.get_priority() == -1:
            # Gets its own thread so is a "critical" procedure.
            self._critical_procedures[procedure.get_name()] = procedure
        else:
            self._procedures[procedure.get_name()] = procedure

    def send_message_to_server(self, purpose=None, args=[]):

        url = self._server_url
        data = {}

        if purpose == "register_device":

            url += "arduino/connect"
            data['arduino_id'] = args[0]

        elif purpose == "query_values":

            url += "arduino/query"
            data['arduino_id'] = json.dumps(args[0])
            data['channel_names'] = json.dumps(args[1])
            data['precisions'] = json.dumps(args[2])

        elif purpose == "set_values":

            url += "arduino/set"
            data['arduino_id'] = args[0]
            data['channel_names'] = args[1]
            data['values_to_set'] = args[2]

        try:

            # start = time.time()
            r = requests.post(url, data=data)
            response_code = r.status_code
            response = r.reason
            # end = time.time()
            # print "The request part took {} seconds.".format(end - start)

            # print r.text
            if response_code == 200:
                return r.text
            else:
                return r"{}"

        except Exception as e:

            print e

        return r"{}"

    def register_device_with_server(self, device):
        # return self.send_message_to_server("register_device", [device.get_arduino_id()])
        pass
    

    def get_all_channel_values(self, devices):

        arduino_ids = [device.get_arduino_id() for device_name, device in devices.items()]
        channel_names = [[name for name, ch in device.channels().items() if ch.mode() == 'read'] for device_name, device in devices.items()]
        precisions = [[4] * len(device.channels()) for device_name, device in devices.items()]


        # print "Trying to get channel values for ", arduino_id
        start = time.time()
        response = self.send_message_to_server(purpose='query_values', args=[arduino_ids, channel_names, precisions])
        end = time.time()


        print "It took", (end - start), "seconds to get a response."

        if response.strip() != r"{}" and "error" not in str(response).lower():
            parsed_response = json.loads(response)

            for arduino_id in parsed_response:
                device_name = self._device_name_arduino_id_map[arduino_id]
                device = self._devices[device_name]

                for channel_name, value in parsed_response[arduino_id].items():
                    # print channel_name, value
                    device.get_channel_by_name(channel_name).set_value(value)


        '''
        try:
            if response.strip() != r"{}" and "error" not in str(response).lower():
                # print response
                for channel_name, value in ast.literal_eval(response).items():

                    device.get_channel_by_name(channel_name).set_value(value)

                return True

            else:
                # print "got an error"
                pass
                # self._status_bar.push(2, "Error: " + str(response))
                return False

        except Exception as e:

            self._status_bar.push(2, str(e))
            return False
        '''
        return True
    
    '''
    def get_channel_values(self, device):

        arduino_id = device.get_arduino_id()
        channel_names = [name for name, ch in device.channels().items() if ch.mode() == 'read']
        precisions = [4] * len(channel_names)  # For sensor box, precision = 5 needs messages longer than 128 bytes.

        # print "Trying to get channel values for ", arduino_id
        response = self.send_message_to_server(purpose='query_values', args=[arduino_id, channel_names, precisions])

        print "the server response is", response

        try:
            if response.strip() != r"{}" and "error" not in str(response).lower():
                # print response
                for channel_name, value in ast.literal_eval(response).items():

                    device.get_channel_by_name(channel_name).set_value(value)

                return True

            else:
                # print "got an error"
                pass
                # self._status_bar.push(2, "Error: " + str(response))
                return False

        except Exception as e:

            self._status_bar.push(2, str(e))
            return False

        return False
    '''

    def update_channel_values_to_arduino(self, device):

        arduino_id = device.get_arduino_id()
        
        channel_names = [channel_name for channel_name, ch in device.channels().items() if ch.mode() == "write" or ch.mode() == "both"]
        values_to_set = [ch.read_value() for channel_name, ch in device.channels().items()]

        response = self.send_message_to_server(purpose='set_values', args=[arduino_id, channel_names, values_to_set])

        # print response

    def add_device(self, device):
        """
        Adds a device to the control system
        :return:
        """

        # Register device with the server.
        # server_response = self.register_device_with_server(device)

        # if server_response == "error":
        #     print "There's no arduino with device_id={} connected to the server.".format(device.get_arduino_id())
        #     self._status_bar.push(2, "There's no arduino with device_id={} connected to the server.".format(device.get_arduino_id()))
        #     return


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
            channel_iter = self._settings_page_tree_store.append(device_iter,
                                                                 [channel.label(), "Channel", "edit_channel",
                                                                  channel.name(), device.name()])

            # Add to "values".
            # Initialize with current time and 0.0 this will eventually flush out of the deque
            self._x_values[(device.name(), channel_name)] = deque(np.linspace(time.time()-5, time.time(),
                                                                              self._retain_last_n_values),
                                                                  maxlen=self._retain_last_n_values)
            self._y_values[(device.name(), channel_name)] = deque(np.zeros(self._retain_last_n_values),
                                                                  maxlen=self._retain_last_n_values)

        channel_iter = self._settings_page_tree_store.append(device_iter,
                                                             ["<b>[ Add a New Channel ]</b>", "", "add_new_channel",
                                                              device.name(), device.name()])

        self._settings_tree_view.show_all()

        return 0


    def set_value_callback(self, button, widget):

        # print "Set callback called by {}".format(widget.get_name())

        parent_channel = widget.get_parent_channel()

        self._set_value_for_widget = widget
        self._communication_thread_mode = "write"

    def listen_for_reconnected_devices(self, devices):
        for device in devices:
            if device.name() in self._devices.keys() and device.name() not in self._alive_device_names:
                print "Reinitializing device ", device.name()
                device.reinitialize()

    def check_for_alive_devices(self, devices):
        # Check which Arduinos are still alive.

        '''
        for device in devices:
            if device.is_alive():

                self._alive_device_names.add(device.name())

                if device.locked():
                    device.unlock()
            else:
                print "Device = {} not alive.".format(device.name())
                print "Locking device", device.name()
                device.lock()
                self._alive_device_names.discard(device.name())

        self._last_checked_for_devices_alive = time.time()

        print "The set of all alive devices = ", self._alive_device_names
        '''

        pass

    def update_stored_values(self, device_name, channel_name):

        self._x_values[(device_name, channel_name)].append(time.time())
        self._y_values[(device_name, channel_name)].append(
            self._devices[device_name].channels()[channel_name].get_value())

        return False

    def communicate(self):
        """
        :param devices:
        :return:
        """

        while self._keep_communicating:

            devices = self._devices

            # if (time.time() - self._last_checked_for_devices_alive) > self._check_for_alive_interval:
            # 	self.check_for_alive_devices(devices)
            # 	self.listen_for_reconnected_devices(devices)

            # GLib.idle_add(self.dummy_update)

            if self.get_all_channel_values(devices): # Returns true only if successfully got a value.

                for device_name, device in devices.items():

                    # For each device that belongs to the same arduino (i.e same thread) we do this
                    # Find out whether we're supposed to read in values or write values at this time.

                    # THOUGHT: Maybe implement a device.locked thing and don't
                    # operate on a given device unless that lock is released?
                    # Ideally, even all the methods in the Device class would
                    # respect that lock.

                    if not device.locked():

                        arduino_id = device.get_arduino_id()

                        # print "Trying to communicate with device {} @ arduino {}".format(device.name(), arduino_id)

                        if self._communication_thread_mode == "read":

                        
                            
                            self._communication_thread_poll_count += 1

                            # print self._communication_thread_poll_count

                            # Find all the channels, see if they are in 'read' or 'both' mode,
                            # then update the widgets with those values.

                            for channel_name, channel in device.channels().items():

                                # if channel.initialized() and (channel.mode() == "read" or channel.mode() == "both"):
                                if channel.mode() == "read" or channel.mode() == "both":

                                    try:


                                        try:
                                            # Log data.
                                            self.log_data(channel)

                                        except Exception as e:
                                            print "Exception caught while trying to log data."
                                            print e
                                            pass

                                        try:
                                            GLib.idle_add(self.update_stored_values, device.name(), channel_name)

                                        except Exception as e:
                                            print "Exception caught while updating stored values."
                                            print e
                                            pass

                                        
                                        GLib.idle_add(self.update_gui, channel)

                                    except Exception as e:
                                        "Got an exception", e

                    # elif self._communication_threads_mode[arduino_id] == "write" \
                    #         and self._set_value_for_widget is not None:
                    #
                    #     print "Setting value."
                    #
                    #     widget_to_set_value_for = self._set_value_for_widget
                    #     channel_to_set_value_for = self._set_value_for_widget.get_parent_channel()
                    #
                    #     print "Communicating updated value for widget {}".format(widget_to_set_value_for.get_name())
                    #
                    #     # Check if the channel is actually a writable channel (channel.mode() ?= "write" or "both").
                    #
                    #     if channel_to_set_value_for.mode() == "write" or channel_to_set_value_for.mode() == "both":
                    #
                    #         try:
                    #             value_to_update = widget_to_set_value_for.get_value()
                    #         except ValueError:
                    #             value_to_update = -1
                    #
                    #         print "Setting value = {}".format(value_to_update)
                    #
                    #         try:
                    #             channel_to_set_value_for.set_value(value_to_update)
                    #         except Exception, e:
                    #             # Setting value failed. There was some exception.
                    #             # Write the error message to the status bar.
                    #             self._status_bar.push(2, str(e))
                    #
                    #     self.update_channel_values_to_arduino(device)
                    #
                    #     self._communication_threads_mode[arduino_id] = "read"
                    #     self._set_value_for_widget = None

        print "Closing communication thread."

        return 0

    def emergency_stop(self, widget):
        """
        Callback for STOP button, but may also be called if interlock is broken or
        in any other unforseen sircumstance that warrants shutting down all power supplies.
        :param widget:
        :return:
        """

        self._status_bar.push(1, "Emergency stop button was pushed!")
        self.shut_down_communication_threads()

        return 0

    def monitor_procedures(self):
        # TODO: NOT IN USE RIGHT NOW.

        # This is the method that all non-critical procedure threads run.

        while self._keep_procedure_thread_running:

            # print "Monitoring all non-critical threads here."

            # TODO:
            # THOUGHT: Should this also have a while loop? I mean, so that we keep on trying to do the procedure until it succeeds.

            for procedure_name, procedure in self._procedures.items():
                if procedure.should_perform_procedure():
                    procedure.act()

    def monitor_critical_procedure(self, critical_procedure):

        # TODO: NOT IN USE RIGHT NOW.

        # This is the method that all critical procedure threads run. Each of them run in a separate thread.


        while self._keep_critical_procedure_threads_running:

            # print "Critical thread running on its own thread."


            # Technically, we don't have to check this here since it's checked in the Procedure class before actually performing the procedure.
            # But double-checking it probably won't hurt (will have some non-zero cost associated with retrieving values and then computing whether or not all the conditions are satisfied).


            # The second conditional is so that we can keep trying to perform the procedure until we succeed. This is crucial for "critical" procedures.
            while critical_procedure.should_perform_procedure() and (not critical_procedure.act()):
                critical_procedure.act()

    def setup_procedure_threads(self):
        # TODO: NOT IN USE RIGHT NOW.

        # For N critical threads, there's going to be (N + 1) total threads. The N threads are one each for the "crtical" (procedure.priority = -1) procedures. All remaining procedures are processed with just 1 thread.

        # TODO: Need to implement proper thread waiting, especially for "critical" threads.
        # Because critical threads need to have higher priorities than "communication threads".

        # First, setup a general thread i.e. one thread for all non-critical procedures.


        # TODO: THOUGHT: We could pass a list / dictionary of all the procedures we want to monitor here as kwargs.
        # But, that way, the thread would only act only on those procedures that were created at the very beginning.
        # There wouldn't be a straightforward way for this thread to also handle the procedures that were added later on.

        if self._procedure_thread == None:
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


        communication_thread = threading.Thread(target=self.communicate)

        self._communication_thread = communication_thread
        self._communication_thread_mode = 'read'
        self._communication_thread_poll_count = 0
        self._communication_thread_start_time = time.time()

        self._keep_communicating = True

        self._communication_thread.start()

        return 0

    def get_arduino_vbox(self):
        return self._arduino_vbox

    def save_as_devices_callback(self, button):

        def select_all_callback(widget, checkboxes):
            for device_name, checkbox in checkboxes.items():
                checkbox.set_active(True)

        def unselect_all_callback(widget, checkboxes):
            for device_name, checkbox in checkboxes.items():
                checkbox.set_active(False)

        dialog = Gtk.FileChooserDialog("Save Device", self._main_window,
                                       Gtk.FileChooserAction.SELECT_FOLDER,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        ("_Save"), Gtk.ResponseType.OK),
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

        select_all_handler_id = select_all_label.connect("clicked", select_all_callback, device_checkboxes)
        select_all_handler_id = unselect_all_label.connect("clicked", unselect_all_callback, device_checkboxes)

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
        self._settings_tree_view.expand_all()

    def settings_collapse_all_callback(self, button):
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



    def initialize(self):
        """
        :return:
        """
        # Initialize the ankered devices first
        for device_name, device in self._devices.items():
            device.initialize()

        # Setup connections for widgets (for radio buttons for example).
        self.set_widget_connections()

        # Any and all remaining initializations go here
        self.setup_communication_threads()

        self.setup_settings_page()

        self.setup_plotting_page()

        # self.setup_procedure_threads()

        self._initialized = True

        return 0

    def settings_add_device_callback(self, button, params):

        device_name = params['name'].get_text()
        device_label = params['label'].get_text()
        arduino_id = params['arduino_id'].get_text()
        overview_page_presence = params['overview_page_presence'].get_active()

        print "Got a new device!"

        new_device = Device(name=device_name, label=device_label, arduino_id=arduino_id)
        new_device.set_overview_page_presence(overview_page_presence)

        self.add_device(new_device)

        self.reinitialize()

    # if self._edit_frame != None:
    # 	self._builder.get_object("settings_page_settings_box").remove(self._edit_frame)

    def settings_add_channel_callback(self, button, device_name, params):
        # Default values.
        data_type, mode = float, "both"

        data_type_iter = params['data_type'].get_active_iter()

        if data_type_iter != None:
            model = params['data_type'].get_model()
            data_type, data_type_str = model[data_type_iter][:2]
            data_type = eval(data_type)

        mode_iter = params['mode'].get_active_iter()

        if mode_iter is not None:
            model = params['mode'].get_model()
            mode, mode_str = model[mode_iter][:2]

        # Create a new channel.
        ch = Channel(name=params['name'].get_text(),
                     label=params['label'].get_text(),
                     upper_limit=float(params['upper_limit'].get_text()),
                     lower_limit=float(params['lower_limit'].get_text()),
                     data_type=data_type,
                     mode=mode,
                     unit=params['unit'].get_text())

        # Add the newly created channel to the correct device.
        self.add_channel(ch, self._devices[device_name])

    # if self._edit_frame != None:
    # 	self._builder.get_object("settings_page_settings_box").remove(self._edit_frame)

    def device_settings_tree_selection_callback(self, selection):

        if self._edit_frame != None:
            self._builder.get_object("settings_page_settings_box").remove(self._edit_frame)

        model, treeiter = selection.get_selected()

        if treeiter != None:

            label = model[treeiter][0]
            object_type = model[treeiter][1]
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

                for label_text, entry in zip(labels, entries):

                    label = Gtk.Label(xalign=1)
                    label.set_markup("<span foreground='#888a85'>" + label_text + "</span>");

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

        # # max_y depends on whether or not the bottom-most row has just one plot. If it is, that row will eventually be removed since all the plots move one step back.
        # if (total_number_of_plot_frames % number_of_plots_per_row) == 1:
        # 	print "bingo! new max_y is",
        # 	max_y = int(n_rows) - 1
        # 	print max_y
        # else:
        # 	max_y = int(n_rows)

        for y in range(int(n_rows)):

            if y < int(n_rows) - 1:
                max_x = int(number_of_plots_per_row)
            else:
                print "bingo"
                max_x = total_number_of_plot_frames % number_of_plots_per_row

            print "max x is", max_x

            if y < position[1]:
                # Elements before the row where the removal happened. These need not do anything.
                pass
            elif y == position[1]:
                # Elements in the row where the removal happened. What happens to each frame depends on what column it occupied.

                for x in range(max_x):

                    print "Current x, y = ", (x, y)

                    widget = self._plotting_page_grid.get_child_at(x, y)

                    if x < position[0]:
                        # Elements before the column where the remove happened. These need not do anything either.
                        pass
                    elif x >= position[1]:
                        # Just shift it one step to the left.

                        print "I need to move {} one step to the left.".format(widget.get_label())
                        self._plotting_page_grid.remove(widget)
                        self._plotting_page_grid.attach(widget, x - 1, y, width=1, height=1)

            elif y > position[1]:
                #

                for x in range(max_x):

                    print "Current x, y = ", (x, y)

                    widget = self._plotting_page_grid.get_child_at(x, y)

                    if x == 0:
                        # This needs to move to the previous row.

                        print "I need to move {} to the previous row.".format(widget.get_label())

                        self._plotting_page_grid.remove(widget)
                        self._plotting_page_grid.attach(widget, int(number_of_plots_per_row) - 1, y - 1, width=1,
                                                        height=1)
                    else:
                        # Just move it one step to the left.

                        print "I need to move {} one step to the left.".format(widget.get_label())

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

        print "Total plots = ", total_number_of_plot_frames

        if total_number_of_plot_frames == 1:

            print "Total number = 0"

            self._plotting_page_grid.add(plot_frame)
        else:
            # First find the number of rows.
            n_rows = np.ceil(total_number_of_plot_frames / number_of_plots_per_row)

            if (total_number_of_plot_frames % number_of_plots_per_row) == 0:
                current_column_number = number_of_plots_per_row
            else:
                current_column_number = (total_number_of_plot_frames % number_of_plots_per_row)

            print "Total rows =", n_rows
            print "Current col.  =", current_column_number

            if n_rows == 1.:
                # Always insert "RIGHT TO SIBLING".

                sibling = self._plotting_page_grid.get_child_at(total_number_of_plot_frames - 2, 0)
                print "Inserting to the Right of", (total_number_of_plot_frames - 2, 0)

                # grid.attach_next_to(label, last_label, Gtk.PositionType.BOTTOM, width=1, height=1)
                self._plotting_page_grid.attach_next_to(plot_frame, sibling, Gtk.PositionType.RIGHT, width=1, height=1)
            else:
                # Always insert "BOTTOM TO SIBLING."

                sibling = self._plotting_page_grid.get_child_at(current_column_number - 1, n_rows - 2)

                print "Inserting to the Bottom of ", (current_column_number - 1, n_rows - 2)

                self._plotting_page_grid.attach_next_to(plot_frame, sibling, Gtk.PositionType.BOTTOM, width=1, height=1)

        self._plotting_page_grid.show_all()

    def plotting_setup_channels_callback(self, button):

        print "Opening Plotting Channels Dialog"

        dialog = MIST1Dialogs.PlottingChannelsDialog(self._main_window, self._plot_page_channels_tree_store,
                                                     self._plotting_frames.keys())

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            print "The OK button was clicked."
            selections = dialog.get_selection()

            # Go throught the list of self._plotting_frames.keys()
            # and for each key that's not on selection, remove that element.

            for (device_name, channel_name) in self._plotting_frames.keys():
                if (device_name, channel_name) not in selections:
                    self.remove_plotting_frame(device_name, channel_name)

            for (device_name, channel_name) in selections:
                if (device_name, channel_name) not in self._plotting_frames.keys():
                    print "Recreating a new frame for", device_name, channel_name
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

                    channel_iter = self._plot_page_channels_tree_store.append(device_iter,
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

        # 	device_iter = self._settings_page_tree_store.append(None, [device.label(), "Device", "edit_device", device.name(), device.name()])

        # 	for channel_name, channel in device.channels().items():
        # 		channel_iter = self._settings_page_tree_store.append(device_iter, [channel.label(), "Channel", "edit_channel", channel.name(), device.name()])

        # 	channel_iter = self._settings_page_tree_store.append(device_iter, ["<b>[ Add a New Channel ]</b>", "", "add_new_channel", device.name(), device.name()])

        device_iter = self._settings_page_tree_store.append(None,
                                                            ["<b>[ Add a New Device ]</b>", "", "add_new_device", "",
                                                             ""])

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

        self.set_widget_connections()

        self.setup_communication_threads()

        self._main_window.show_all()

    def main_quit(self, widget):
        """
        Shuts down the program (and threads) gracefully.
        :return:
        """

        self._main_window.destroy()

        self.shut_down_communication_threads()
        self.shut_down_procedure_threads()

        Gtk.main_quit()

        return 0

    def shut_down_procedure_threads(self):
        self._keep_critical_procedure_threads_running = False
        self._keep_procedure_thread_running = False

    def shut_down_communication_threads(self):
        """
        :return:
        """
        self._keep_communicating = False

        return 0

    def run(self):
        """
        :return:
        """
        self.initialize()

        # --- Show the GUI --- #
        self._main_window.maximize()
        self._main_window.show_all()

        # GLib.timeout_add(1000, self.update_plots)
        GLib.idle_add(self.update_plots)

        Gtk.main()

        return 0

    def statusbar_changed_callback(self, statusbar, context_id, text):
        """
        Callback that handles what happens when a message is pushed in the
        statusbar
        """

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

        if page_num == 1:
            self.update_plots()
            self._we_are_on_plot_page = True
            GLib.idle_add(self.update_plots)
        else:
            self._we_are_on_plot_page = False

        return 0

    def update_gui(self, channel):
        """
        Updates the GUI. This is called from the communication threads through idle_add()
        :return:
        """
        # Update the polling rate (frequency) for this arduino:
        arduino_id = channel.get_arduino_id()
        count = self._communication_thread_poll_count

        # print arduino_id

        if count >= 10:
            elapsed = time.time() - self._communication_thread_start_time
            frequency = self._communication_thread_poll_count / elapsed

            self._communication_thread_start_time = time.time()
            self._communication_thread_poll_count = 0

            self._arduino_status_bars[arduino_id].set_value(frequency)

        # If display on overview page is desired, update:
        if channel.get_parent_device().is_on_overview_page():
            # if count == 9:
            # 	print "Updating", channel.name(), channel.get_value()
            channel.get_overview_page_display().set_value(channel.get_value())

        return False


if __name__ == "__main__":

    # control_system = MIST1ControlSystem(server_ip="10.77.0.188", server_port=80)
    control_system = MIST1ControlSystem(server_ip="127.0.0.1", server_port=5000)

    # Setup data logging.
    current_time = time.strftime('%a-%d-%b-%Y_%H-%M-%S-EST', time.localtime())
    control_system.register_data_logging_file(filename="log/{}.h5".format(current_time))

    # *** Generate Devices *** #
    # Each device is connected to a single arduino, several devices can be connected to the
    # same Arduino, but never several arduinos to a single device!
    # 
    # --- Actual Arduinos ---- #
    # SensorBox: 49ffb802-50c5-4194-879d-20a87bcfc6ef
    # InterlockBox: bd0f5a84-a2eb-4ff3-9ff2-597bf3b2c20a
    # IonGaugeController: cf436e6b-ba3d-479a-b221-bc387c37b858
    # 
    # ----- Test Arduinos ------ #
    # Daniel's dummy Arduino: 43d581f6-2ad5-4b51-b8f6-a945a26ab5f5
    # Aashish's Sensor Arduino: 2cc580d6-fa29-44a7-9fec-035acd72340e
    # Test Interlock Arduino => 41b70a36-a206-41c5-b743-1e5b8429b9a1
    # ************************ #

    interlock_box = Device("interlock_box",
                           arduino_id="41b70a36-a206-41c5-b743-1e5b8429b9a1",
                           label="Interlock Box",
                           on_overview_page=True)

    # Test three Arduinos running the sensor box software for now
    sensor_box_ids = ["41b70a36-a206-41c5-b743-1e5b8429b9a1",
                      "49ffb802-50c5-4194-879d-20a87bcfc6ef"]
    # sensor_box_ids = ["2cc580d6-fa29-44a7-9fec-035acd72340e"]

    for j, sensor_id in enumerate(sensor_box_ids):
        sensor_box = Device("sensor_box_{}".format(j),
                            arduino_id=sensor_id,
                            label="Sensor Box",
                            on_overview_page=True)

        # Add channels to the sensor box
        # 5 Flow Meters:
        for i in range(5):
            ch = Channel(name="f{}".format(i), label="Flow Meter {}".format(i),
                         upper_limit=1,
                         lower_limit=0,
                         data_type=float,
                         mode="read",
                         unit="lpm",
                         display_order=(100 - i))

            sensor_box.add_channel(ch)

        # 8 Temperature Sensors: 7 for now (#8 is not connected)
        for i in range(7):
            ch = Channel(name="t{}".format(i), label="Temperature Sensor {}".format(i),
                         upper_limit=1,
                         lower_limit=0,
                         data_type=float,
                         mode="read",
                         unit="C",
                         display_order=(50 - i))

            sensor_box.add_channel(ch)

        # Add our device to the control system.
        control_system.add_device(sensor_box)

    # Add channels to the interlock box
    # 2 Microswitches
    for i in range(2):
        ch = Channel(name="m{}".format(i), label="Micro Switch {}".format(i),
                     upper_limit=1,
                     lower_limit=0,
                     data_type=bool,
                     mode="read",
                     display_order=(11 - 5 - i))

        interlock_box.add_channel(ch)

    # 2 Solenoid valves
    for i in range(2):
        ch = Channel(name="s{}".format(i), label="Solenoid Valve {}".format(i),
                     upper_limit=1,
                     lower_limit=0,
                     data_type=bool,
                     mode="write",
                     display_order=(11 - 5 - 2 - i))

        interlock_box.add_channel(ch)

    # Vacuum Valves. x2.
    for i in range(2):
        ch = Channel(name="v{}".format(i), label="Vacuum Valve {}".format(i),
                     upper_limit=1,
                     lower_limit=0,
                     data_type=bool,
                     mode="read",
                     display_order=(11 - 5 - 2 - 2 - i))

        interlock_box.add_channel(ch)

    # control_system.add_device(interlock_box)

    # Run the control system, this has to be last as it does
    # all the initializations and adding to the GUI.
    control_system.run()
