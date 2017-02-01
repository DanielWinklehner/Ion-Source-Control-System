from flask import Flask
from flask import request
# from SerialCOM import SerialCOM
# from collections import defaultdict
from DummySerial import DummySerial
# import sys
# import subprocess
import json
# import urllib2
# import copy
import time
import Messages
import threading
from multiprocessing.dummy import Pool as ThreadPool
# from multiprocessing.managers import BaseManager
import logging

app = Flask(__name__)

# Opening a pool of threads to re-use.
# TODO: Think about proper termination! (Use 127.0.0.1:5000/kill)
# TODO: Also, what happens if another query comes along while these are still working?
p = ThreadPool()

app.debug = False

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


def find_arduinos_connected():
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


def pool_query_arduinos(arduino_ids, queries):
    machines = []

    by_arduio_id, by_port = find_arduinos_connected()

    for arduino_id, query in zip(arduino_ids, queries):
        machines.append((by_arduio_id[arduino_id], query))

    parsed_response = dict()

    if len(machines) > 0:
        # start = time.time()

        try:

            # p = multiprocessing.Pool(len(machines))
            # p = ThreadPool()

            # start2 = time.time()

            all_responses = p.map(mp_worker, machines)

            # end2 = time.time()

        finally:

            # p.close()
            # p.join()

            pass

        if len(all_responses) == 0 or len(all_responses[0]) == 0:

            return None

        else:

            for port, raw_output_message in all_responses:

                arduino_id = by_port[port]
                # print arduino_id, raw_output_message

                try:
                    parsed_response[arduino_id] = Messages.parse_arduino_output_message(raw_output_message)
                except Exception as e:
                    parsed_response[arduino_id] = str(e[0]) + ": " + str(e[1])

    return parsed_response


def set_channel_value_to_arduino(arduino_id, channel_name, value):
    by_arduio_id, by_port = find_arduinos_connected()

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
    p.terminate()
    p.join()
    func()
    return "Shutting down..."


@app.route("/arduino/all")
def all_arduinos():

    return json.dumps(find_arduinos_connected()[1])


@app.route("/arduino/query", methods=['GET', 'POST'])
def query_arduinos():
    # print "We are querying arduinos"
    # LOGGER.info("We are querying arduinos")

    # print request.args
    # start = time.time()

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

    # LOGGER.info(all_arduino_ids)
    # LOGGER.info(all_query_messages)

    arduinos_response = pool_query_arduinos(all_arduino_ids, all_query_messages)

    # arduinos_response = {
    #     "C3PO": {"i1": 0.4121000000000001, "v1": 0.4121000000000001,
    #              "v2": 0.4121000000000001, "i2": 0.4121000000000001,
    #              "x1": 0.4121000000000001},
    #     "R2D2": {"i1": 0.4121000000000001, "v1": 0.4121000000000001,
    #              "v2": 0.4121000000000001, "i2": 0.4121000000000001,
    #              "x1": 0.4121000000000001}}

    # print ":the arduino response is", arduinos_response
    # end = time.time()

    # print "The response took", (end - start), "seconds."

    return json.dumps(arduinos_response)


@app.route("/arduino/query2", methods=['GET', 'POST'])
def query_arduinos2():
    # print "We are querying arduinos"
    # LOGGER.info("We are querying arduinos")

    # print request.args
    # start = time.time()

    arduinos_response = dict()

    if request.method == 'POST':

        # Load the data stream
        data = json.loads(request.form['data'])

        port_by_id, id_by_port = find_arduinos_connected()

        # TODO: This has to be moved into the Driver class, so that we just call:
        # TODO: my_driver = Driver(device_data["device_driver"])
        # TODO: message_data = my_driver.translate_gui_to_device(data)

        message_data = []
        for device_data in data:
            device_data["set"] = False
            message_data.append((port_by_id[device_data["device_id"]],
                                 Messages.build_query_message(device_data['channel_ids'],
                                                              device_data['precisions'])))

        # TODO: END

        try:

            # Use existing global pool of 10 worker threads
            # TODO: Let the user decide how many threads to use?
            # But first let's see if they are all alive
            print("Currently we have {} threads alive!".format(threading.active_count()))

            all_responses = p.map(mp_worker, message_data)

            # TODO: This has to be moved into the Driver class as well
            if len(all_responses) == 0 or len(all_responses[0]) == 0:

                return None

            else:

                for port, raw_output_message in all_responses:

                    arduino_id = id_by_port[port]

                    try:
                        arduinos_response[arduino_id] = Messages.parse_arduino_output_message(raw_output_message)

                    except Exception as e:

                        arduinos_response[arduino_id] = str(e[0]) + ": " + str(e[1])

            # TODO: END

        except Exception as e:

            print("Something went wrong! Exception: {}".format(e))

    elif request.method == 'GET':

        # TODO: Implement GET method?
        pass

    # LOGGER.info(all_arduino_ids)
    # LOGGER.info(all_query_messages)
    #
    # arduinos_response = {
    #     "C3PO": {"i1": 0.4121000000000001, "v1": 0.4121000000000001,
    #              "v2": 0.4121000000000001, "i2": 0.4121000000000001,
    #              "x1": 0.4121000000000001},
    #     "R2D2": {"i1": 0.4121000000000001, "v1": 0.4121000000000001,
    #              "v2": 0.4121000000000001, "i2": 0.4121000000000001,
    #              "x1": 0.4121000000000001}}

    # print ":the arduino response is", arduinos_response
    # end = time.time()

    # print "The response took", (end - start), "seconds."

    return json.dumps(arduinos_response)


if __name__ == "__main__":
    # connected_arduinos_thread = threading.Thread(target=update_arduinos_connected)
    # connected_arduinos_thread.start()
    # app.run(host='0.0.0.0', port=80)
    app.run(host='0.0.0.0', port=5000)
