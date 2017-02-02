import Messages
import subprocess
import json
import urllib2
import copy
import time
import threading
import multiprocessing


from collections import defaultdict
from flask import Flask, redirect
from flask import request
from SerialCOM import *
from multiprocessing.managers import BaseManager
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial

sys.path.append('../Drivers/')

from MIST1DeviceDriver import MIST1DeviceDriver



class MyManager(BaseManager): pass

def Manager():
    m = MyManager()
    m.start()
    return m 

MyManager.register('SerialCOM', SerialCOM)




app = Flask(__name__)



app.debug = True

p = ThreadPool()
    




all_active_device_ids = []    # Key => device_id; value => (device_id, port_name)
all_active_managers = {}    # Key => device_id; value => Manager(SerialCOM())


def update_devices_connected():
    global all_active_device_ids
    global all_active_managers



    port_by_id, id_by_port = find_devices_connected()

    # print "I am updating arduinos connected."

    # while True:
    # for count_abc in range(2):

 
    #all_active_devices = all_arduinos
    #all_active_managers = [Manager().SerialCOM(arduino_id=arduino[0], port_name=arduino[1]) for arduino in all_active_devices]
    

    for device_id, port in port_by_id.items():

        arduinos_to_remove = []
        
        for already_added_device_id in all_active_device_ids:
            already_added_port = port_by_id[already_added_device_id]

            if already_added_device_id == device_id and already_added_port == port:
                # Both arduino id and port name matches. Do nothing.
                pass
            elif already_added_device_id == device_id and already_added_port != port:
                # Arduino id matches but port name does not. Replace them with new entries.
                all_active_managers[device_id] = Manager().SerialCOM(arduino_id=device_id, port_name=port)
                time.sleep(1)
                all_active_managers[device_id].send_message("i")
            else:
                pass

            if already_added_device_id not in port_by_id.keys() or already_added_port not in id_by_port.keys():
                arduinos_to_remove.append(already_added_device_id)

        for arduino_id_to_remove in arduinos_to_remove:
            try:
                all_active_device_ids.remove(arduino_id_to_remove)
                del all_active_managers[already_added_device_id]
            except ValueError:
                pass

        # Next, "brand new" arduinos that we've never added before.
        if device_id in all_active_device_ids:
            #print "arduino already added"
            pass
        else:

            new_manager = Manager().SerialCOM(arduino_id=device_id, port_name=port)

            all_active_device_ids.append(device_id)
            all_active_managers[device_id] = new_manager

            print device_id, all_active_device_ids

    threading.Timer(1., update_devices_connected).start()

class QueryMachine:
    def __init__(self, serial_com, queries):
        self._serial_com = serial_com
        self._queries = queries

    def serial_com(self):
        return self._serial_com

    def queries(self):
        return self._queries

    def __str__(self):
        return str(self._serial_com) + "; " + str(self._queries)

def mp_worker(args):

    port, messages = args
    by_id, by_port = find_devices_connected()

    serial_com = all_active_managers[by_port[port]]

    print messages

    all_responses = []
    for msg in messages:
        # print "The message I am going to send is", msg


        try:
            arduino_response = serial_com.send_message(msg)
            all_responses.append(arduino_response)

            print "Got the response",  arduino_response

        except Exception as e:
            print "Something went wrong! I'm sorry!", e
            all_responses.append(None)
    
    return serial_com.get_arduino_id(), all_responses




def set_channel_value_to_arduino(arduino_id, channel_name, value):
    global all_active_managers
    
    print "Setting value = {} for channel_name = {} for arduino_id = {}".format(value, channel_name, arduino_id)

    manager = filter(lambda x: x.get_arduino_id() == arduino_id, all_active_managers)[0]
    set_message = Messages.build_set_message([channel_name], [value])
    
    print "My set message is", set_message

    arduino_response = manager.send_message(set_message)

    return arduino_response





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

@app.route("/display")
def display():

    process = subprocess.call("sudo python /var/www/html/Ion-Source-Control-System/Python/server/display_plain.py &", shell=True)

    return "Started display code."


@app.route("/arduino/set", methods=['GET', 'POST'])
def set_arduino_values():
    if request.method == 'POST':
        arduino_id = request.form['arduino_id']
        channel_name = request.form['channel_name']
        value_to_set = request.form['value_to_set']
    elif request.method == 'GET':
        arduino_id = request.args.get('arduino_id')
        channel_name = request.args.get('channel_name')
        value_to_set = request.args.get('value_to_set')
    
    response = set_channel_value_to_arduino(arduino_id, channel_name, value_to_set)

    return json.dumps(response)


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

        print "This is the response I got", all_responses

        if len(all_responses) == 0 or len(all_responses[0]) == 0:
            return None
        else:
            for device_id, raw_output_message in all_responses:
                
                print "hey buddy", device_id, raw_output_message

                try:
                    devices_responses[device_id] = my_drivers[device_id].translate_device_to_gui(raw_output_message)
                except Exception as e:

                    devices_responses[device_id] = "ERROR: " + str(e)


    except Exception as e:
        print("Something went wrong! Exception: {}".format(e))

    return json.dumps(devices_responses)






if __name__ == "__main__":
    
    # update_devices_connected()


    # connected_arduinos_thread = threading.Thread(target=update_arduinos_connected)
    threading.Timer(0.1, update_devices_connected).start()

    # update_arduinos_connected()

    # app.run(host='0.0.0.0', port=80)
    app.run(host='0.0.0.0', port=5000)