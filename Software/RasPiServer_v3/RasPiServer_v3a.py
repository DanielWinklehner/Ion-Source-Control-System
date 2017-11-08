# import time
import sys
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Process, Pipe
from multiprocessing.managers import BaseManager
from flask import Flask, request
import subprocess
import threading
import json
from MIST1DeviceDriver import MIST1DeviceDriver, driver_mapping
from SerialCOM import *
from HtmlPage import * 


class MyManager(BaseManager):
    pass

MyManager.register('SerialCOM', SerialCOM)


def manager():
    m = MyManager()
    m.start()
    return m


# Set up a dictionary with all available drivers (slightly faster than creating them every query)
_my_drivers = {}
for key in driver_mapping.keys():
    _my_drivers[key] = MIST1DeviceDriver(driver_name=key)

# --- This is a nice implementation of a simple timer I found online -DW --- #
_tm = 0


def stopwatch(msg=''):
    tm = time.time()
    global _tm
    if _tm == 0:
        _tm = tm
        return
    print("%s: %.2f ms" % (msg, 1000.0 * (tm - _tm)))
    _tm = tm
# ------------------------------------------------------------------------- #


def serial_watchdog(com_pipe, debug, port_identifyers):
    """
    Function to be called as a process. Watches the serial ports and looks for devices plugged in
    or removed.
    Underscore at beginning prevents flask_classy from making it a route in the Flask server.
    :param com_pipe: this end of the pipe to communicate with main server process.
    :param debug: Flag whether or not debugging should be turned on.
    :param port_identifyers: A list of strings that are used to identify a specific serial port (e.g. "Arduino")
    :return:
    """
    _keep_communicating2 = True
    _com_freq = 2.0  # (Hz)
    _com_period = 1.0 / _com_freq  # (s)
    _debug = debug
    _port_identifyers = port_identifyers
    _current_ports_by_ids = {}
    _new_ports_by_ids = {}

    while _keep_communicating2:

        # Do the timing of this process:
        _thread_start_time = time.time()

        if com_pipe.poll():

            _in_message = com_pipe.recv()

            if _in_message[0] == "com_period":
                _com_period = _in_message[1]

            elif _in_message[0] == "shutdown":
                break

            elif _in_message[0] == "port_identifyers":
                _port_identifyers = _in_message[1]

            elif _in_message[0] == "debug":
                _debug = _in_message[1]

        # Find the serial ports and whether they belong to an arduino
        # TODO: This takes a very long time, is there a faster way?
        proc = subprocess.Popen('/home/mist-1/Work/ControlSystem/RasPiServer_v3/usb.sh',
                                stdout=subprocess.PIPE, shell=True)

        output = proc.stdout.read().strip()

        _device_added = False
        _device_removed = False
        _device_ids = _current_ports_by_ids.keys()

        _obsolete_ports_by_ids = {}
        _added_ports_by_ids = {}

        # Loop through all found devices and add them to a new list, remove them from the current list
        for line in output.split("\n"):

            # Go through all identifyers and see if one is found in this serial port
            _current_identifyer = [identifyer for identifyer in _port_identifyers if identifyer in line]

            if len(_current_identifyer) == 1:

                _current_identifyer = _current_identifyer[0]

                port, raw_info = line.split(" - ")
                serial_number = raw_info.split("_")[-1]

                _new_ports_by_ids[serial_number] = {"port": port,
                                                    "identifyer": _current_identifyer}

                if serial_number not in _device_ids:
                    _device_added = True
                    _added_ports_by_ids[serial_number] = _new_ports_by_ids[serial_number]
                else:
                    del _current_ports_by_ids[serial_number]
            #
            # else:
            #     print(line)

        # Now, let's check if there are any devices still left in the current dict
        if len(_current_ports_by_ids) > 0:
            _device_removed = True
            _obsolete_ports_by_ids = _current_ports_by_ids  # These SerialCOM objects have to be destroyed

        _current_ports_by_ids = _new_ports_by_ids
        _new_ports_by_ids = {}

        if _debug:
            if _device_removed:
                print("Device(s) were removed")
            if _device_added:
                print("Device(s) were added")

        if _device_added or _device_removed:
            # If something has changed:
            if _debug:
                print("Updated List:")
                for _key, item in _current_ports_by_ids.items():
                    print ("{} #{} at port {}".format(item["identifyer"], _key, item["port"]))

            # Reverse ports_by_ids:
            _current_ids_by_ports = {}
            for myid, myport_info in _current_ports_by_ids.items():
                _current_ids_by_ports[myport_info["port"]] = myid

            # Send the new dictionaries back to the server
            pipe_message = ["updated_list",
                            _current_ports_by_ids, _current_ids_by_ports,
                            _obsolete_ports_by_ids, _added_ports_by_ids]

            com_pipe.send(pipe_message)

        # Do the timing of this process:
        _sleepy_time = _com_period - time.time() + _thread_start_time

        if _sleepy_time > 0.0:

            if _debug:
                print("Watchdog alive, sleeping for {} s.".format(_sleepy_time))

            time.sleep(_sleepy_time)

app = Flask(__name__)

# A pool of threads to communicate with the arduinos
# TODO: Let the user decide how many threads to use?
_threadpool = ThreadPool(10)
_mydebug = False
_welcome_message = "Hi, this is the MIST-1 Control System server running on a RasPi."
_pipe_server, pipe_serial_watcher = Pipe()
_ports_by_ids = {}
_ids_by_ports = {}
_watch_proc = Process(target=serial_watchdog, args=(pipe_serial_watcher,
                                                    _mydebug,
                                                    driver_mapping.keys()))
_watch_proc.daemon = True
_keep_communicating = False
_initialized = False
_serial_comms = {}
# TODO: Add another Pipe/Process combo for displaying stuff on our new display


@app.route("/")
def hello():

    return _welcome_message


@app.route("/debug/")
def toggle_debug():
    global _mydebug

    _mydebug = not _mydebug

    if _mydebug:
        mode = "on"
    else:
        mode = "off"

    _pipe_server.send(["debug", _mydebug])

    return "Toggled debug mode {}.".format(mode)


@app.route("/kill/")
def kill():
    """
    Shutdown routine.
    :return:
    """

    if _mydebug:
        print("Shutting Down!")

    global _keep_communicating
    _keep_communicating = False

    _threadpool.terminate()
    _threadpool.join()

    if _watch_proc.is_alive():

        _watch_proc.terminate()
        _watch_proc.join()

        if _mydebug:
            print("Terminated Watchdog.")

    else:

        if _mydebug:
            print("Watchdog already dead.")

    func = request.environ.get('werkzeug.server.shutdown')

    if func is None:

        raise RuntimeError('Not running with the Werkzeug Server')

    func()

    return "Shutting down..."


@app.route("/device/active_table/")
def all_devices_table():
    return devices_as_html(all_devices())

@app.route("/device/active/")
def all_devices():

    global _ports_by_ids
    return json.dumps(_ports_by_ids)


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
    device_data = json.loads(request.form['data'])
    device_data["set"] = True

    # For reference: This is the message from the GUI:
    # device_data = {'device_driver': device_driver_name,
    #                'device_id': device_id,
    #                'locked_by_server': False,
    #                'channel_ids': [channel_ids],
    #                'precisions': [precisions],
    #                'values': [values],
    #                'data_types': [types]}

    old_device_id = device_data['device_id']
    device_id_parts = old_device_id.split("_")
    port_id = device_id_parts[0]
    device_id = device_id_parts[0]

    if len(device_id_parts) > 1:
        device_id = device_id_parts[1]

    if _mydebug:
        print("Device {} with port id = {}, device id = {}:".format(device_data['device_driver'],
                                                                    port_id,
                                                                    device_id))
        for i in range(len(device_data['values'])):
            print("Setting value = {} for channel_name = {} ".format(device_data['values'][i],
                                                                     device_data['channel_ids'][i]))

    driver = _my_drivers[device_data['device_driver']]

    device_data['device_id'] = device_id

    msg = driver.translate_gui_to_device(device_data)

    device_data['device_id'] = old_device_id

    if _mydebug:
        print("The message to the device is: {}".format(msg))

    try:
        # print(port_id)
        # print(_serial_comms[port_id])

        for cmd in msg:
            device_response = _serial_comms[port_id].send_message(cmd)

    except Exception as e:

        device_response = "Error, exception happened: {}".format(e)

    return json.dumps(device_response)


@app.route("/device/query", methods=['GET', 'POST'])
def query_device():

    # Load the data stream
    data = json.loads(request.form['data'])

    if _mydebug:
        print(data)

    message_data = []
    my_driver_names = {}
    disconnected_devices = []
    disconnected_indices = []

    for i, device_data in enumerate(data):
        device_data['set'] = False

        old_device_id = device_data['device_id']
        device_id_parts = old_device_id.split("_")
        port_id = device_id_parts[0]
        device_id = device_id_parts[0]

        if len(device_id_parts) > 1:
            device_id = device_id_parts[1]

        device_data['device_id'] = device_id
        device_messages = _my_drivers[device_data["device_driver"]].translate_gui_to_device(device_data)
        device_data['device_id'] = old_device_id

        if len(device_messages) == 0:
            """ GUI sent no message """
            raise Exception("Error building message for: ", str(device_data))

        else:

            if port_id in _ports_by_ids.keys():
                message_data.append((_ports_by_ids[port_id]["port"], device_messages))
                my_driver_names[port_id] = device_data["device_driver"]
            else:
                """ Device not found on the server """
                print("could not find {}".format(port_id))
                disconnected_devices.append(device_data)
                disconnected_indices.append(i)
    
    # Remove the missing devices from the gui data objecit
    for i in reversed(disconnected_indices):
        data.pop(i)

    devices_responses = dict()

    for device in disconnected_devices:
        devices_responses[device['device_id']] = "ERROR: Device not found on server"

    try:

        if _mydebug:
            # But first let's see if they are all alive
            print("Currently we have {} threads alive!".format(threading.active_count()))

        # Use existing global pool of 10 worker threads
        all_responses = _threadpool.map(mp_worker, message_data)

        if len(all_responses) > 0 and len(all_responses[0]) > 0:
            # responses and device_data are in the same order.
            for response, device_data in zip(all_responses, data):

                device_id, raw_output_message = response

                try:
                    devices_responses[device_data['device_id']] = _my_drivers[
                        my_driver_names[device_id]].translate_device_to_gui(
                        raw_output_message, device_data)

                except Exception as e:
                    print("Exception happened, message data was {}, response from Arduino was {}".format(message_data,
                                                                                                         response))
                    devices_responses[device_data['device_id']] = "ERROR: " + str(e)

    except Exception as e:
        print("Something went wrong! Exception: {}".format(e))

    return json.dumps(devices_responses)


def mp_worker(args):
    port, messages = args

    global _serial_comms
    global _ids_by_ports

    myid = _ids_by_ports[port]

    if _mydebug:
        print("Device {} requires {} query messages.".format(myid, len(messages)))

    all_responses = []

    for msg in messages:

        if _mydebug:
            print("The message to the device is: {}".format(msg))

        try:
            arduino_response = _serial_comms[myid].send_message(msg)
            all_responses.append(arduino_response)

            if _mydebug:
                print("The response from the device was: {}".format(arduino_response))

        except Exception as e:
            print("Something went wrong! I'm sorry! {}".format(e))
            all_responses.append(None)

    return _serial_comms[myid].get_arduino_id(), all_responses


def listen_to_pipe():

    global _ports_by_ids
    global _ids_by_ports

    if _pipe_server.poll():

        gui_message = _pipe_server.recv()

        if gui_message[0] == "updated_list":

            if _mydebug:
                print("Updating ports/ids in main server")

            _ports_by_ids = gui_message[1]
            _ids_by_ports = gui_message[2]
            _obsolete = gui_message[3]
            _added = gui_message[4]

            for _key in _obsolete.keys():
                del _serial_comms[_key]
            for _key, _port_info in _added.items():
                _baud_rate = driver_mapping[_port_info["identifyer"]]["baud_rate"]
                _serial_comms[_key] = manager().SerialCOM(arduino_id=_key,
                                                          port_name=_port_info["port"],
                                                          baud_rate=_baud_rate,
                                                          timeout=1.0)

    if _keep_communicating:
        threading.Timer(0.5, listen_to_pipe).start()


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5000)
