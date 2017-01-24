from flask import Flask, redirect
from flask import request

from SerialCOM import *
import Messages

from collections import defaultdict

import subprocess
import json
import urllib2
import copy
import time

import threading

import multiprocessing
from multiprocessing.managers import BaseManager
# from multiprocessing.pool import ThreadPool
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial


import serial


app = Flask(__name__)



app.debug = True

    


def mp_worker(args):

    
    start = time.time()

    # print machine
    port, messages = args


    all_responses = []
    for msg in messages:
        # print "The message I am going to send is", msg


        try:
            # serial_com = SerialCOM(port)
            # arduino_response = serial_com.send_message(msg)
            # all_responses.append(arduino_response)

            start456 = time.time()
            ser = serial.Serial(port, baudrate=115200, timeout=1.0)
            end456 = time.time()

            print "It took {} seconds to initialize serial connection.".format(end456 - start456)

            for i in range(10):
                ser.write(msg)
                response = ser.readline()
                print response.strip("\r\n")
                if len(response.strip("\r\n")) > 0:
                    break

            print "The response is", response

            all_responses.append(response)

            # print "Got the response",  arduino_response

        except Exception as e:
            print "Something went wrong! I'm sorry!", e
            all_responses.append(None)
    


    end = time.time()

    print "it took", (end - start), "to get a message from the arduino"
    

    return port, all_responses
    # return None




def pool_query_arduinos(arduino_ids, queries):
    



    # Using multiprocessing.
    # First, find correct SerialCOM objects to use.

    
    machines = []

    by_arduio_id, by_port = find_arudinos_connected()

    for arduino_id, query in zip(arduino_ids, queries):
        machines.append((by_arduio_id[arduino_id], query))



    parsed_response = dict()

    if len(machines) > 0:
        start = time.time()

        # print "Pooling all arduinos"

        try:

            # p = multiprocessing.Pool(len(machines))
            p = ThreadPool(processes=1)

            start2 = time.time()

            all_responses = p.map(mp_worker, machines)

            end2 = time.time()

        finally:
            p.close()
            p.join()
            # p.shutdown()
            pass
            

        end = time.time()

        #print "It took", (end - start), "seconds to collect all the responses."

        

        # if len(all_responses) == 0 or len(all_responses[0]) == 0:
        if len(all_responses) == 0 or len(all_responses[0]) == 0:
            return None
        else:
            for response in all_responses:
                for port, raw_output_message in all_responses:

                    arduino_id = by_port[port]
                    # print arduino_id, raw_output_message

                    try:
                        parsed_response[arduino_id] = Messages.parse_arduino_output_message(raw_output_message)
                    except Exception as e:
                        parsed_response[arduino_id] = str(e[0]) + ": " + str(e[1])
            
    return parsed_response




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



@app.route("/arduino/all")
def all_arduinos():
    return json.dumps(find_arudinos_connected())

@app.route("/arduino/active")
def active_arduinos():
    return json.dumps(all_active_arduinos)

@app.route("/arduino/query", methods=['GET', 'POST'])
def query_arduinos():


    start123 = time.time()


    # print "I've been queried at:", time.strftime("%H:%M:%S:%m")


    

    if request.method == 'POST':
        all_arduino_ids = json.loads(request.form['arduino_id'])
        all_channel_names = json.loads(request.form['channel_names'])
        all_precisions = json.loads(request.form['precisions'])
        
    elif request.method == 'GET':
        all_arduino_ids = json.loads(request.args.get('arduino_id'))
        all_channel_names = json.loads(request.args.get('channel_names'))
        all_precisions = json.loads(request.args.get('precisions'))
        

    all_queries = [(arduino_id, channel_names, precisions) for (arduino_id, channel_names, precisions) in zip(all_arduino_ids, all_channel_names, all_precisions)]
    
    all_query_messages = [Messages.build_query_message(channel_names, precisions) for (arduino_id, channel_names, precisions) in all_queries]

    # print "all query messages:"
    # print all_query_messages


    start2 = time.time()

    arduinos_response = pool_query_arduinos(all_arduino_ids, all_query_messages)

    end2 = time.time()

    print "The arduino response is", arduinos_response

    end123 = time.time()

    print "\n"*2

    print "The function query_arduinos() took", (end123 - start123), "seconds."

    print "Out of that:"

    print "It took {} to collect responses [pool_query_arduinos()].".format(end2 - start2)

    print "\n"*2

    # print "I sent a response at:", time.strftime("%H:%M:%S:%m")

    return json.dumps(arduinos_response)
    
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'






if __name__ == "__main__":
    

    # update_arduinos_connected()

    # app.run(host='0.0.0.0', port=80)
    app.run(host='0.0.0.0', port=5000)