import sys
import json
import time
import threading
import logging

from flask import Flask
from flask import request
from DummySerial import DummySerial
from multiprocessing.dummy import Pool as ThreadPool

sys.path.append('../Drivers/')

from MIST1DeviceDriver import MIST1DeviceDriver





app = Flask(__name__)

# Opening a pool of threads to re-use.
# TODO: Think about proper termination! (Use 127.0.0.1:5000/kill)
# TODO: Also, what happens if another query comes along while these are still working?
p = ThreadPool()

app.debug = True

LOGGER = logging.getLogger('gunicorn.error')

# --- This is a nice implementation of a simple timer I found online -DW --- #
_tm = 0


def stopwatch(msg=''):
    tm = time.time()
    global _tm
    if _tm == 0:
        _tm = tm
        return
    print("%s: %.2f ms" % (msg, 1000.0 * (tm-_tm)))
    _tm = tm
# ------------------------------------------------------------------------- #


def find_devices_connected():
    by_port = {"/dev/ttyACM0": "R2D2", "/dev/ttyACM1": "C3PO", "/dev/ttyACM2": "BB8"}
    by_id = {"R2D2": "/dev/ttyACM0", "C3PO": "/dev/ttyACM1", "BB8": "/dev/ttyACM2"}

    return by_id, by_port


def mp_worker(args):
    port, messages = args

    all_responses = []
    for msg in messages:

        try:
            ser = DummySerial(port, 115200)
            ser.write(msg)
            all_responses.append(ser.readline())
        except Exception as e:
            print("Something went wrong! Exception: {}".format(e))
            all_responses.append(None)

    return port, all_responses



def set_channel_value_to_device(device_driver, device_id, channel_name, value):
    by_device_id, by_port = find_devices_connected()

    port = by_device_id[device_id]

    ser = DummySerial(port, baudrate=115200)
    
    my_driver = MIST1DeviceDriver(device_driver) 


    data = dict(set=True, device_id=device_id, channel_name=channel_name, value=value)
    set_message = my_driver.translate_gui_to_device(data)

    return ser.readline()


@app.route("/")
def hello():
    return "Hey there!"


@app.route('/kill', methods=['GET', 'POST'])
def kill():

    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    
    p.terminate()
    p.join()
    
    func()
    
    return "Shutting down..."


@app.route("/device/all")
def all_devices():
    return json.dumps(find_devices_connected()[1])


@app.route("/device/set", methods=['GET', 'POST'])
def set_device_values():
    if request.method == 'POST':
        device_driver = request.form['device_driver']
        device_id = request.form['device_id']
        channel_name = request.form['channel_name']
        value_to_set = request.form['value_to_set']
    elif request.method == 'GET':
        device_driver = request.args.get('device_driver')
        device_id = request.args.get('device_id')
        channel_name = request.args.get('channel_name')
        value_to_set = request.args.get('value_to_set')
    
    response = set_channel_value_to_device(device_driver, device_id, channel_name, value_to_set)

    return json.dumps(response)


@app.route("/device/query", methods=['GET', 'POST'])
def query_device():
    # print "We are querying devices"
    # LOGGER.info("We are querying devices")

    # print request.args
    # start = time.time()

    # Load the data stream
    if request.method == 'POST':
        data = json.loads(request.form['data'])
    elif request.method == 'GET':
        data = json.loads(request.args.get('data'))


    print data

    port_by_id, id_by_port = find_devices_connected()

    my_drivers = dict()
    message_data = []
    for device_data in data:
        
        my_driver = MIST1DeviceDriver(device_data['device_driver']) 

        my_driver.load_driver()

        device_data['set'] = False

        device_message = my_driver.translate_gui_to_device(device_data)

        if len(device_message) == 0:
            raise Exception("Error building message for: ", str(device_data))
        else:
            message_data.append((port_by_id[device_data["device_id"]], device_message))
        
        my_drivers[device_data['device_id']] = my_driver


    devices_responses = dict()

    try:

        # Use existing global pool of 10 worker threads
        # TODO: Let the user decide how many threads to use?
        # But first let's see if they are all alive
        print("Currently we have {} threads alive!".format(threading.active_count()))

        all_responses = p.map(mp_worker, message_data)

        if len(all_responses) == 0 or len(all_responses[0]) == 0:
            return None
        else:
            for port, raw_output_message in all_responses:
                
                device_id = id_by_port[port]
                
                try:
                    devices_responses[device_id] = my_drivers[device_id].translate_device_to_gui(raw_output_message)
                except Exception as e:

                    devices_responses[device_id] = "ERROR: " + str(e)


    except Exception as e:
        print("Something went wrong! Exception: {}".format(e))

    return json.dumps(devices_responses)


if __name__ == "__main__":
    # connected_devices_thread = threading.Thread(target=update_devices_connected)
    # connected_devices_thread.start()
    # app.run(host='0.0.0.0', port=80)
    app.run(host='0.0.0.0', port=5000)
