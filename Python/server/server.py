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
from multiprocessing.managers import BaseManager

class MyManager(BaseManager): pass

def Manager():
	m = MyManager()
	m.start()
	return m 

MyManager.register('SerialCOM', SerialCOM)




app = Flask(__name__)



app.debug = True

	


managers = [Manager(), Manager()]
all_serial_coms = [ managers[0].SerialCOM(arduino_id="49ffb802-50c5-4194-879d-20a87bcfc6ef", port_name="/dev/ttyACM0"), managers[1].SerialCOM(arduino_id="41b70a36-a206-41c5-b743-1e5b8429b9a1", port_name="/dev/ttyACM1") ]
# all_serial_coms = [ managers[0].SerialCOM(arduino_id="49ffb802-50c5-4194-879d-20a87bcfc6ef", port_name="/dev/ttyACM1"), managers[1].SerialCOM(arduino_id="41b70a36-a206-41c5-b743-1e5b8429b9a1", port_name="/dev/ttyACM2") ]

for serial_com in all_serial_coms:
	print serial_com.send_message("i")


def mp_worker(serial_com, message):

	start = time.time()

	arduino_response = serial_com.send_message(message)
	
	end = time.time()

	print "it took", (end - start), "to get a message from the arduino"

	return serial_com.get_arduino_id(), arduino_response


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

	# First, find correct SerialCOM objects to use.

	serial_coms_to_use = []
	queries_to_use = []

	for arduino_id, query in zip(arduino_ids, queries):

		for i in range(len(all_serial_coms)):
			
			if all_serial_coms[i].get_arduino_id() == arduino_id:
				serial_coms_to_use.append( all_serial_coms[i] )
				queries_to_use.append( query )


	start = time.time()

	p = multiprocessing.Pool(len(serial_coms_to_use))
	
	all_responses = []

	for serial_com, query in zip(serial_coms_to_use, queries_to_use):
		start2 = time.time()

		all_responses.append( p.apply(func=mp_worker, args=(serial_com, query)) )

		end2 = time.time()

		print "it took", (end2 - start2), "seconds for each arduino response."

	# p.close()
	# p.join()

	end = time.time()

	print "It took", (end - start), "seconds to collect all the responses."


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
	
	start = time.time()

	if request.method == 'POST':
		all_arduino_ids = json.loads(request.form['arduino_id'])
		all_channel_names = json.loads(request.form['channel_names'])
		all_precisions = json.loads(request.form['precisions'])
		
	elif request.method == 'GET':
		all_arduino_ids = json.loads(request.args.get('arduino_id'))
		all_channel_names = json.loads(request.args.get('channel_names'))
		all_precisions = json.loads(request.args.get('precisions'))
		

	all_queries = [(arduino_id, channel_names, precisions) for (arduino_id, channel_names, precisions) in zip(all_arduino_ids, all_channel_names, all_precisions)]
	
	all_query_messages = [messages.build_query_message(channel_names, precisions) for (arduino_id, channel_names, precisions) in all_queries]

	arduinos_response = pool_query_arduinos(all_arduino_ids, all_query_messages)

	end = time.time()

	print "The response took", (end - start), "seconds."

	return json.dumps(arduinos_response)

			

if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=80)
    app.run(host='0.0.0.0', port=5000)
