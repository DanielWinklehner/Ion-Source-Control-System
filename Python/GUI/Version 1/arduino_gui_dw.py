import gi

import random

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GLib, GObject

from serial import SerialException

# from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas

from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas

import matplotlib.animation as animation
from matplotlib import pyplot as plt

import matplotlib.dates as md

import control_system_serial
import serial

import time
import threading
import datetime

from device import Device, Channel, SerialCOM

import uuid

pressure_arduino_id = ""
interlock_flow_arduino_id = ""  # This includes 5 flow meters and 5 temperature sensors.
interlock_others_arduino_id = "9de3d90f-cdf7-4ef8-9604-548243401df6"  # This includes 2 each of solenoid valves, vacuum valves and microswitches.


# ser = serial.Serial('/dev/ttyACM0', 9600)

class Handler:
    def __init__(self):

        GLib.threads_init()

        self._device_addresses = {}  # key = COM Address; value = Device ID

        self._devices = {}  # Contains actual Device objects, keyed by their names (maybe ids?)

        self._device_ids = {}  # Key = common name, value = device id

        self._read_ion_gauge_data = False
        self._read_interlock_flow_data = False
        self._read_interlock_others_data = False

        self._builder = Gtk.Builder()
        self._builder.add_from_file("arduino_gui.glade")
        self._builder.connect_signals(self)

        self._window = self._builder.get_object("main_window")

        self._window.connect("destroy", Gtk.main_quit)

        read_serial_ports_thread = threading.Thread(target=self.read_and_identify_devices)
        read_serial_ports_thread.start()

        # Setup all device units.

        # self.setup_ion_gauge()
        self.setup_interlock_flow()
        self.setup_interlock_others()

        # Need some way to keep track of all threads, like when it says to stop reading data,
        # that thread should stop. Right now, once a thread has started, it never stops.

    # ================================================================================================================ #
    # =========================================== Setup Device Units ================================================= #
    # ================================================================================================================ #

    def setup_ion_gauge(self):
        start_gauge1_button = self._builder.get_object("start_gauge1_button")
        start_gauge1_button.connect("clicked", self.start_gauge1)

        start_gauge2_button = self._builder.get_object("start_gauge2_button")
        start_gauge2_button.connect("clicked", self.start_gauge2)

        read_pressure_button = self._builder.get_object("read_pressure_button")
        read_pressure_button.connect("clicked", self.start_reading_ion_gauge_data)

        # Maybe have one function and use arguments instead? No becaue we need individual
        # threads for each unit as we want to read all of them in parallel.

        self._ion_gauge_data_reading_thread = threading.Thread(target=self.read_ion_gauge_data)

        # These are for the pressure plot.

        self._plot_box = self._builder.get_object('plot_box')

        self._figure = plt.figure()
        self._axis = self._figure.add_subplot(1, 1, 1)
        self._canvas = False

        self._timestamps = []
        self._pressures = []

    # self._ani = None

    def setup_interlock_flow(self):
        read_interlock_flow_button = self._builder.get_object("interlock_flow_start_reading_button")
        read_interlock_flow_button.connect("clicked", self.start_reading_interlock_flow_data)

        self._interlock_flow_data_reading_thread = threading.Thread(target=self.read_interlock_flow_data)

    def setup_interlock_others(self):
        read_interlock_others_button = self._builder.get_object("interlock_others_start_reading_button")
        read_interlock_others_button.connect("clicked", self.start_reading_interlock_others_data)

        self._interlock_others_data_reading_thread = threading.Thread(target=self.read_interlock_others_data)

    # ==============================================================================================================================
    # =================================================== Setup Device Units Ends ==================================================
    # ==============================================================================================================================



    # ==============================================================================================================================
    # ================================================== Start Data Reading Threads ================================================
    # ==============================================================================================================================


    def start_reading_ion_gauge_data(self, button):

        self.write_to_logger("Starting reading data.")

        self._read_ion_gauge_data = True
        self._data_reading_thread.start()  # This thread is associated with the "read_ion_gauge_data()" method.

    # self.create_plot()

    def start_reading_interlock_others_data(self, button):

        self.write_to_logger("Starting reading interlock others data.")

        self._read_interlock_others_data = True
        self._interlock_others_data_reading_thread.start()  # This thread is associated with the "read_interlock_others_data()" method.

    def start_reading_interlock_flow_data(self, button):

        self.write_to_logger("Starting reading interlock flow data.")

        self._read_interlock_flow_data = True
        self._interlock_flow_data_reading_thread.start()  # This thread is associated with the "read_interlock_flow_data()" method.

    # ==============================================================================================================================
    # =============================================== Start Data Reading Threads Ends===============================================
    # ==============================================================================================================================

    def start_gauge1(self, button):

        device = self._devices[self._device_ids['pressure']]
        gauge_1_state_channel = device.get_channel_by_name('gauge_1_state')

    # gauge_1_state_channel.set_value("1")

    def start_gauge2(self, button):

        device = self._devices[self._device_ids['pressure']]
        gauge_2_state_channel = device.get_channel_by_name('gauge_2_state')

    # gauge_2_state_channel.set_value("1")

    def create_plot(self):
        self._ani = animation.FuncAnimation(self._figure, self.update_plot, interval=1000, blit=True, frames=200)

    def update_plot(self, interval):

        x = md.date2num(self._timestamps)
        y_1 = [a for (a, b) in self._pressures]
        y_2 = [b for (a, b) in self._pressures]

        self._axis.plot(x, y_1, color="red", lw=5, alpha=0.5)
        self._axis.plot(x, y_2, color="blue", lw=5, alpha=0.5)

        self._axis.set_yscale('log')

        if not self._canvas:
            self._canvas = FigureCanvas(self._figure)
            self._plot_box.pack_start(self._canvas, True, True, 0)
            self._canvas.show()
        self._canvas.draw()
        xfmt = md.DateFormatter('%H:%M:%S')
        self._axis.xaxis.set_major_formatter(xfmt)

        # self._figure.autoscale(True)

    def update_stuff(self, value):
        # Update the value textbox.
        # self._builder.get_object("current_pressure_reading").set_text(str(value))

        '''
        # Update the plot.
        if len(self._pressures) > 0:
            self.update_plot(1000)
        '''

        return False

    def read_ion_gauge_data(self):

        list_size = 10

        self._read_ion_gauge_data = True  # This should later be controlled by another button or something that allows us to "Start" reading data and then, at some point, "Stop" reading them.

        while self._read_ion_gauge_data:

            print "Reading data!"

            # Just pressure data for now.
            device = self._devices[self._device_ids['pressure']]

            timestamp = time.time()

            gauge_1_state_channel = device.get_channel_by_name('gauge_1_state')
            gauge_1_pressure_channel = device.get_channel_by_name('gauge_1_pressure')
            gauge_2_state_channel = device.get_channel_by_name('gauge_2_state')
            gauge_2_pressure_channel = device.get_channel_by_name('gauge_2_pressure')

            gauge_1_state, gauge_1_pressure = gauge_1_state_channel.read_value(), gauge_1_pressure_channel.read_value()
            gauge_2_state, gauge_2_pressure = gauge_2_state_channel.read_value(), gauge_2_pressure_channel.read_value()

            self._builder.get_object("gauge1_state").set_text(gauge_1_state)
            self._builder.get_object("gauge1_torr").set_text(gauge_1_pressure)
            self._builder.get_object("gauge2_state").set_text(gauge_2_state)
            self._builder.get_object("gauge2_torr").set_text(gauge_2_pressure)

            pressure_1 = gauge_1_pressure
            pressure_2 = gauge_2_pressure

            try:

                float(pressure_1)
                float(pressure_2)

                if float(pressure_1) >= 0. and float(pressure_2) >= 0.:
                    self._timestamps.append(datetime.datetime.fromtimestamp(timestamp))
                    self._pressures.append((float(pressure_1), float(pressure_2)))

                GLib.idle_add(self.update_stuff, pressure_1)

            except ValueError:
                pass

            time.sleep(1)

    def read_interlock_others_data(self):

        print "reading other"

        list_size = 10

        self._read_interlock_others_data = True  # This should later be controlled by another button or something that allows us to "Start" reading data and then, at some point, "Stop" reading them.

        while self._read_interlock_others_data:

            print "Reading interlock others data!"

            # Interlock data.
            device = self._devices[self._device_ids['interlock_others']]

            timestamp = time.time()

            # First get all channels.
            channels = {}

            # Solenoid Valves. x 2
            for i in range(1, 2):
                channels['solenoid_valve_' + str(i)] = device.get_channel_by_name('solenoid_valve_' + str(i))

            '''
            # Vacuum Valves. x 2
            for i in range(1, 3):
                channels['vacuum_valve_' + str(i)] = device.get_channel_by_name('vacuum_valve_' + str(i))
            '''

            # Reed Switches. x 2
            for i in range(1, 2):
                channels['micro_switch_' + str(i)] = device.get_channel_by_name('micro_switch_' + str(i))

            # We have all the channels we need.

            # Now read in values (for those where we can read in).

            for channel_name in channels.keys():
                if channels[channel_name].mode() != "write":
                    self._builder.get_object(channel_name + "_value").set_text(channels[channel_name].read_value())

            time.sleep(1)

    def read_interlock_flow_data(self):

        list_size = 10

        self._read_interlock_flow_data = True  # This should later be controlled by another button or something that allows us to "Start" reading data and then, at some point, "Stop" reading them.

        while self._read_interlock_flow_data:

            print "Reading interlock flow data!"

            # Interlock data.
            device = self._devices[self._device_ids['interlock_flow']]

            timestamp = time.time()

            # First get all channels.
            channels = {}

            # Flow Meters. x 5

            for i in range(1, 6):
                channels['flow_meter_' + str(i)] = device.get_channel_by_name('flow_meter_' + str(i))

            # Temperature sensor. x 5

            for i in range(1, 6):
                channels['temperature_sensor_' + str(i)] = device.get_channel_by_name('temperature_sensor_' + str(i))

            # We have all the channels we need.

            # Now read in values (for those where we can read in).

            for channel_name in channels.keys():
                if channels[channel_name].mode() != "write":
                    self._builder.get_object(channel_name + "_value").set_text(channels[channel_name].read_value())

            time.sleep(1)

    def read_and_identify_devices(self):

        print "Reading and identifying devices!"

        self.port_names = control_system_serial.get_all_serial_ports()

        self.identify_devices()

        self.write_all_serial_port_names()

        # Define all necessary devices and corresponding classes here.

        for port_name in self._device_addresses:

            # ION GAUGE CONTROLLER.

            if self._device_addresses[
                port_name] == pressure_arduino_id:  # Replace this with another hashmap of arduino IDs against what those units are.
                # This is our pressure unit.

                print "Working with device=pressure."

                # Assign a new device id.
                device_id = uuid.uuid4()
                channel_id = uuid.uuid4()

                pressure_serial_com = SerialCOM(channel_id=channel_id, arduino_id=pressure_arduino_id,
                                                arduino_port=port_name)

                # Do we need to have the user require to define an id_channel? Because every Device would need to have an associated id with it and
                # because we need to query the id's much before we define all the necessary channels.

                id_channel = Channel(name="id", serial_com=pressure_serial_com, message_header="id", upper_limit=1,
                                     lower_limit=0, uid=uuid.uuid4(), data_type="bool", unit=None, scaling=1,
                                     mode="read")

                gauge_1_state_channel = Channel(name="gauge_1_status", serial_com=pressure_serial_com,
                                                message_header="gauge_1_state", upper_limit=1, lower_limit=0,
                                                uid=uuid.uuid4(), data_type="string", unit=None, scaling=1, mode="both")
                gauge_1_pressure_channel = Channel(name="gauge_1_pressure", serial_com=pressure_serial_com,
                                                   message_header="gauge_1_pressure", upper_limit=1000000,
                                                   lower_limit=0, uid=uuid.uuid4(), data_type="float", unit=None,
                                                   scaling=1, mode="read")
                gauge_2_state_channel = Channel(name="gauge_2_status", serial_com=pressure_serial_com,
                                                message_header="gauge_2_state", upper_limit=1, lower_limit=0,
                                                uid=uuid.uuid4(), data_type="float", unit=None, scaling=1, mode="both")
                gauge_2_pressure_channel = Channel(name="gauge_2_pressure", serial_com=pressure_serial_com,
                                                   message_header="gauge_2_pressure", upper_limit=1000000,
                                                   lower_limit=0, uid=uuid.uuid4(), data_type="float", unit=None,
                                                   scaling=1, mode="read")

                pressure_channels = {'id': id_channel, 'gauge_1_state': gauge_1_state_channel,
                                     'gauge_1_pressure': gauge_1_pressure_channel,
                                     'gauge_2_state': gauge_2_state_channel,
                                     'gauge_2_pressure': gauge_2_pressure_channel}

                pressure_unit = Device(name="Ion Gauge Controller", arduino_device_id=device_id,
                                       channels=pressure_channels)

                self._devices[device_id] = pressure_unit

                self._device_ids['pressure'] = device_id

            # ION GAUGE CONTROLLER ENDS.


            # Interlock Others Unit Begins.
            # This includes 2 each of solenoid valves, vacuum valves and reed switches.

            if self._device_addresses[port_name] == interlock_others_arduino_id:

                print "Working with device=Interlock Others System."

                # Assign a new device id.
                device_id = uuid.uuid4()
                channel_id = uuid.uuid4()

                interlock_others_serial_com = SerialCOM(channel_id=channel_id, arduino_id=interlock_others_arduino_id,
                                                        arduino_port=port_name)

                interlock_others_channels = {}

                # Solenoid Valves. x 2

                for i in range(1, 3):
                    interlock_others_channels['solenoid_valve_' + str(i)] = Channel(name="solenoid_valve_" + str(i),
                                                                                    serial_com=interlock_others_serial_com,
                                                                                    message_header="solenoid_valve_" + str(
                                                                                        i), upper_limit=1,
                                                                                    lower_limit=0, uid=uuid.uuid4(),
                                                                                    data_type="bool", unit=None,
                                                                                    scaling=1, mode="write")

                # Vacuum Valves. x 2
                for i in range(1, 3):
                    interlock_others_channels['vacuum_valve_' + str(i)] = Channel(name="vacuum_valve_" + str(i),
                                                                                  serial_com=interlock_others_serial_com,
                                                                                  message_header="vacuum_valve_" + str(
                                                                                      i), upper_limit=1, lower_limit=0,
                                                                                  uid=uuid.uuid4(), data_type="bool",
                                                                                  unit=None, scaling=1, mode="read")

                # Reed Switches. x 2
                for i in range(1, 3):
                    temp_name = "micro_switch_%i" % i
                    interlock_others_channels[temp_name] = Channel(name=temp_name,
                                                                   serial_com=interlock_others_serial_com,
                                                                   message_header=temp_name,
                                                                   upper_limit=1, lower_limit=0,
                                                                   uid=uuid.uuid4(), data_type="bool",
                                                                   unit=None, scaling=1, mode="read")

                interlock_others_unit = Device(name="Interlock Others System", arduino_device_id=device_id,
                                               channels=interlock_others_channels)

                self._devices[device_id] = interlock_others_unit
                self._device_ids['interlock_others'] = device_id

            # Interlock Others Unit Ends.

            # Interlock Flow Unit Begins.
            if self._device_addresses[port_name] == interlock_flow_arduino_id:

                print "Working with device=Interlock Flow System."

                # Assign a new device id.
                device_id = uuid.uuid4()
                channel_id = uuid.uuid4()

                interlock_flow_serial_com = SerialCOM(channel_id=channel_id, arduino_id=interlock_flow_arduino_id,
                                                      arduino_port=port_name)

                interlock_flow_channels = {}

                # Flow meters. x 5
                for i in range(1, 6):
                    # This reads square wave frequencies.
                    interlock_flow_channels['flow_meter_' + str(i)] = Channel(name="flow_meter_" + str(i),
                                                                              serial_com=interlock_flow_serial_com,
                                                                              message_header="flow_meter_" + str(i),
                                                                              upper_limit=10000000, lower_limit=0,
                                                                              uid=uuid.uuid4(), data_type="float",
                                                                              unit="Hz", scaling=1, mode="read")

                # Temperature sensors. x 5
                for i in range(1, 6):
                    interlock_flow_channels['temperature_sensor_' + str(i)] = Channel(
                        name="temperature_sensor_" + str(i), serial_com=interlock_flow_serial_com,
                        message_header="temperature_sensor_" + str(i), upper_limit=1000, lower_limit=0,
                        uid=uuid.uuid4(), data_type="float", unit="K", scaling=1, mode="read")

                interlock_flow_unit = Device(name="Interlock Flow System", arduino_device_id=device_id,
                                             channels=interlock_flow_channels)

                self._devices[device_id] = interlock_flow_unit
                self._device_ids['interlock_flow'] = device_id

            # Interlock Flow Unit Ends.

            # Other devices.

        print "All setup complete!"

    def write_to_logger(self, message):
        text_buffer = self._builder.get_object("footer_logger").get_buffer()
        iterator = text_buffer.get_end_iter()
        message = "[{:%Y-%b-%d %H:%M:%S}]: {}\n".format(datetime.datetime.now(), message)
        text_buffer.insert(iterator, message)

    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def write_all_serial_port_names(self):

        print "Mapping ports to their IDs!"

        for port_name in self.port_names:
            self._builder.get_object('devices_combobox').append_text(
                port_name + " ({})".format(self._device_addresses[port_name][:8]))

        print "Mapping complete!"
        print

    def identify_devices(self):

        print "Identifying devices connected!"

        self.write_to_logger("Identifying devices connected!")

        for port_name in self.port_names:

            # print port_name

            try:
                ser = serial.Serial(port_name,
                                    timeout=3)  # Needs a more systematic and consistent way to do timeouts. Also, need to implement timeouts for a lot of message passing.
                ser.close()
                ser.open()
            except SerialException:
                print 'Port already open!'

            output_msg = ser.readline().strip()
            input_message = "query:identification=?"

            while True:

                input_message = "query:identification=?"

                ser.write(input_message)
                line1 = ser.readline().strip()

                ser.write(input_message)
                line2 = ser.readline().strip()

                print "reading lines"

                print line1, line2

                device_id_reported_by_arduino = line2[17:]

                if line1 == line2:
                    # if True:
                    self._device_addresses[port_name] = device_id_reported_by_arduino
                    ser.write("set:identified=1")

                    # print line2[17:], pressure_arduino_id

                    if device_id_reported_by_arduino == pressure_arduino_id:

                        self._builder.get_object("pressure_port_name").set_text(port_name)

                        # Do it better than just using [17:]. The output is always going to be "output:device_id={}".
                        # So use something like split() instead of hard coding character lengths.

                        self._builder.get_object("pressure_device_id").set_text(
                            "( {} )".format(device_id_reported_by_arduino))

                    elif device_id_reported_by_arduino == interlock_others_arduino_id:
                        self._builder.get_object("interlock_port_name").set_text(port_name)
                        self._builder.get_object("interlock_device_id").set_text(
                            "( {} )".format(device_id_reported_by_arduino))

                    self.write_to_logger(
                        "Identified device id = {} on port {}.".format(device_id_reported_by_arduino, port_name))

                    ser.flushInput()
                    ser.flushOutput()
                    ser.close()

                    break

        noun = "devices" if len(self._device_addresses) > 1 else "device"
        self.write_to_logger("{} {} successfully identified!".format(len(self._device_addresses), noun))


if __name__ == "__main__":
    hand = Handler()

    hand._window.show_all()
    hand._window.maximize()

    Gtk.main()
