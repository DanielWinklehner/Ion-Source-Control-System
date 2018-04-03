# import time
import sys
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Process, Pipe
from multiprocessing.managers import BaseManager
from flask import Flask, request
import threading
import json
from MIST1DeviceDriver import MIST1DeviceDriver, driver_mapping
from SerialCOM import *
from HtmlPage import *
from DeviceFinder import *


class MyManager(BaseManager):
    pass


MyManager.register('SerialCOM', SerialCOM)
MyManager.register('FTDICOM', FTDICOM)

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


def serial_watchdog(com_pipe, debug, port_identifiers):
    """
    Function to be called as a process. Watches the serial ports and looks for devices plugged in
    or removed.
    Underscore at beginning prevents flask_classy from making it a route in the Flask server.
    :param com_pipe: this end of the pipe to communicate with main server process.
    :param debug: Flag whether or not debugging should be turned on.
    :param port_identifiers: A list of strings that are used to identify a specific serial port (e.g. "Arduino")
    :return:
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
                                                    driver_mapping))
_watch_proc.daemon = True
_keep_communicating = False
_initialized = False
_comms = {}
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
    try:
        return devices_as_html(all_devices(), currentResponses)
    except:
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
        # print(_comms[port_id])
        print(msg)
        for cmd in msg:
            device_response = _comms[port_id].send_message(cmd)

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
                    #print(e.message(), "Exception happened, message data was {}, response from Arduino was {}".format(message_data, response))
                    devices_responses[device_data['device_id']] = "ERROR: " + str(e)

    except Exception as e:
        print("Something went wrong! Exception: {}".format(e))

    global currentResponses
    currentResponses = json.dumps(devices_responses)
    return currentResponses
    #return json.dumps(devices_responses)

#@app.route("/device/query_table/")
#def query_table():
#    return currentResponses

def mp_worker(args):
    port, messages = args

    global _comms
    global _ids_by_ports

    myid = _ids_by_ports[port]
    if _mydebug:
        print("Device {} requires {} query messages.".format(myid, len(messages)))

    all_responses = []

    for msg in messages:

        if _mydebug:
            print("The message to the device is: {}".format(msg))

        try:
            arduino_response = _comms[myid].send_message(msg)
            all_responses.append(arduino_response)

            if _mydebug:
                print("The response from the device was: {}".format(arduino_response))

        except Exception as e:
            print("Something went wrong! I'm sorry! {}".format(e))
            all_responses.append(None)

    return _comms[myid].get_device_id(), all_responses


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
            for name, finder_result in message_info.iteritems():
                if name == 'serial':
                    for key, val in finder_result['current'].iteritems():
                        temp_ports_by_ids[key] = val
                        temp_ids_by_ports[val['port']] = key
                    _obsolete = finder_result['obsolete']
                    _added = finder_result['added']

                    for _key in _obsolete.keys():
                        del _comms[_key]
                    for _key, _port_info in _added.items():
                        _baud_rate = driver_mapping[_port_info["identifier"]]["baud_rate"]
                        _comms[_key] = manager().SerialCOM(arduino_id=_key,
                                                           port_name=_port_info["port"],
                                                           baud_rate=_baud_rate,
                                                           timeout=1.0)
                elif name == 'ftdi':
                    for key, val in finder_result['current'].iteritems():
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
                    '''
                    # this code doesn't work because the ftd2xx library is not thread safe
                    # but it represents what we want to do eventually...
                    if _added != {}:
                        # we are adding one or more devices
                        i = 0
                        while True:
                            try:
                                dev = ftd2xx.open(i)
                                # create FTDICOM object for each new device (= number of valid opens before break)
                                ftdi_key = dev.eeRead().SerialNumber
                                dev.close()
                                _comms[ftdi_key] = manager().FTDICOM(ftdi_key, i)
                                temp_ports_by_ids[ftdi_key] = {'port': i, 'identifier': 'CO Series'}
                                temp_ids_by_ports[i] = ftdi_key

                                print('device added')
                                i += 1
                            except Exception as e:
                                print(i, e, e.args, e.message)
                                if e.message == 'DEVICE_NOT_FOUND':
                                    # we have gone too far
                                    break
                                elif e.message == 'DEVICE_NOT_OPENED':
                                    # device already opened
                                    i += 1
                                    continue
                                else:
                                    print(e)

                    if _obsolete != {}:
                        # we are removing one or more devices
                        for key, comm in _comms.items():
                            if isinstance(comm, FTDICOM):
                                try:
                                    _ = comm.serial_number
                                except Exception as e:
                                    if e.message == 'EEPROM_NOT_FOUND':
                                        # remove device
                                        print('device removed')
                                        del _comms[key]
                    '''
            # update the server's dictionaries all at once
            _ports_by_ids = temp_ports_by_ids
            _ids_by_ports = temp_ids_by_ports

    if _keep_communicating:
        threading.Timer(0.5, listen_to_pipe).start()


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5000)
