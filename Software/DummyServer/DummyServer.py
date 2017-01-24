from flask import Flask, redirect
from flask import request

from SerialCOM import SerialCOM

from collections import defaultdict


from DummySerial import DummySerial
import sys
import subprocess
import json
import urllib2
import copy
import time
import Messages

import threading

import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.managers import BaseManager
import logging



app = Flask(__name__)

app.debug = True


LOGGER = logging.getLogger('gunicorn.error')




def find_arudinos_connected():
    by_port = {"/dev/ttyACM0": "R2D2", "/dev/ttyACM1": "C3PO", "/dev/ttyACM2": "BB8"}
    by_id = {"R2D2": "/dev/ttyACM0", "C3PO": "/dev/ttyACM1", "BB8": "/dev/ttyACM2"}

    return (by_id, by_port)



def mp_worker(args):

    port, messages = args

    all_responses = []
    for msg in messages:
        try:
            ser = DummySerial(port, 115200)
            ser.write(msg)
            all_responses.append(ser.readline())
        except Exception as e:
            print "Something went wrong! I'm sorry!", e
            all_responses.append(None)
    

    return port, all_responses


def pool_query_arduinos(arduino_ids, queries):
    
    machines = []

    by_arduio_id, by_port = find_arudinos_connected()

    for arduino_id, query in zip(arduino_ids, queries):
        machines.append((by_arduio_id[arduino_id], query))

    parsed_response = dict()

    if len(machines) > 0:
        start = time.time()

        try:

            # p = multiprocessing.Pool(len(machines))
            p = ThreadPool(processes=1)

            start2 = time.time()

            all_responses = p.map(mp_worker, machines)

            end2 = time.time()

        finally:
            p.close()
            p.join()
            pass
            

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

    by_arduio_id, by_port = find_arudinos_connected()

    port = by_arduio_id[arduino_id]

    ser = DummySerial(port, baudrate=115200)
    set_message = Messages.build_set_message([channel_name], [value])

    ser.write(set_message)

    return ser.readline()


@app.route("/")
def hello():
    return "Hey there!"


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


@app.route('/kill', methods=['GET', 'POST'])
def kill():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Shutting down..."


@app.route("/arduino/all")
def all_arduinos():
    return json.dumps(find_arudinos_connected()[1])



@app.route("/arduino/query", methods=['GET', 'POST'])
def query_arduinos():
    # print "We are querying arduinos"
    LOGGER.info("We are querying arduinos")

    # print request.args

    start = time.time()

    if request.method == 'POST':
        all_arduino_ids = json.loads(request.form['arduino_id'])
        all_channel_names = json.loads(request.form['channel_names'])
        all_precisions = json.loads(request.form['precisions'])

    elif request.method == 'GET':
        all_arduino_ids = json.loads(request.args.get('arduino_id'))
        all_channel_names = json.loads(request.args.get('channel_names'))
        all_precisions = json.loads(request.args.get('precisions'))

    all_queries = [(arduino_id, channel_names, precisions) for (arduino_id, channel_names, precisions) in
                   zip(all_arduino_ids, all_channel_names, all_precisions)]

    all_query_messages = [Messages.build_query_message(channel_names, precisions) for
                          (arduino_id, channel_names, precisions) in all_queries]



    LOGGER.info(all_arduino_ids)
    LOGGER.info(all_query_messages)


    arduinos_response = pool_query_arduinos(all_arduino_ids, all_query_messages)

    # print ":the arduino response is", arduinos_response
    end = time.time()

    # print "The response took", (end - start), "seconds."

    return json.dumps(arduinos_response)


if __name__ == "__main__":
    # connected_arduinos_thread = threading.Thread(target=update_arduinos_connected)
    # connected_arduinos_thread.start()


    # app.run(host='0.0.0.0', port=80)
    app.run(host='0.0.0.0', port=5000)
    pass
