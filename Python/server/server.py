from flask import Flask, redirect
from flask import request

from serial_communication import *

import messages
import json
import urllib2
import copy
import time
import messages
# import requests

import multiprocessing


app = Flask(__name__)



app.debug = True

	

all_arduinos_info = (
    ['49ffb802-50c5-4194-879d-20a87bcfc6ef', '/dev/ttyACM0'], ['41b70a36-a206-41c5-b743-1e5b8429b9a1', '/dev/ttyACM1']
)

queries = [('49ffb802-50c5-4194-879d-20a87bcfc6ef', 'q03f14f24s13'), ('41b70a36-a206-41c5-b743-1e5b8429b9a1', 'q01s26')]

def mp_worker(inputs):

    arduino_id = inputs[0]
    port = inputs[1]
    message = inputs[2]

    s = SerialCOM(arduino_id=arduino_id, port_name=port, timeout=1.)

    return arduino_id, s.send_message(message)



def build_arduino_port_map(arduino_ids):
	
	arduinos_map = []

	found = True
	for arduino_id in arduino_ids:
		for arduino in all_arduinos_info:
			if arduino_id == arduino[0]:
				arduinos_map.append(  [arduino_id, arduino[1]] )
				found = True
				break

		if not found:
			arduinos_map.append( [arduino_id, None] )

		found = False

	return arduinos_map


def pool_query_arduinos(arduino_ids, queries):

	arduino_info = build_arduino_port_map(arduino_ids)

	# Build the data list first.
	worker_data = copy.copy(arduino_info)

	elems_to_remove = []
	for i, (arduino_id, port_name) in enumerate(worker_data):		
		
		for j, (arduino_to_query, query_string) in enumerate(queries):
			if arduino_to_query == arduino_id:
				worker_data[i].append(query_string)
		
		if port_name == None:
			elems_to_remove.append(worker_data[i])

	
	for i in range(len(elems_to_remove)):
		worker_data.remove(elems_to_remove[i])
	
	
	p = multiprocessing.Pool(len(worker_data))

	all_responses = p.map(mp_worker, worker_data)

	parsed_response = dict()
	for arduino_id, raw_output_message in all_responses:
		parsed_response[arduino_id] = messages.parse_arduino_output_message(raw_output_message)
		
	return parsed_response





@app.route("/")
def hello():
    return "Hey there!"

@app.route("/arduino/all")
def all_arduinos():

	return json.dumps(all_arduinos)


@app.route("/arduino/query", methods=['GET', 'POST'])
def query_arduinos():
	
	if request.method == 'POST':
		all_arduino_ids = json.loads(request.form['arduino_id'])
		all_channel_names = json.loads(request.form['channel_names'])
		all_precisions = json.loads(request.form['precisions'])
		
	elif request.method == 'GET':
		all_arduino_ids = json.loads(request.args.get('arduino_id'))
		all_channel_names = json.loads(request.args.get('channel_names'))
		all_precisions = json.loads(request.args.get('precisions'))
		

	all_queries = [(arduino_id, channel_names, precisions) for (arduino_id, channel_names, precisions) in zip(all_arduino_ids, all_channel_names, all_precisions)]
	
	all_query_messages = [(arduino_id, messages.build_query_message(channel_names, precisions)) for (arduino_id, channel_names, precisions) in all_queries]

	arduinos_response = pool_query_arduinos(all_arduino_ids, all_query_messages)

	
	return json.dumps(arduinos_response)

			

if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=80)
    app.run(host='0.0.0.0', port=5000)
