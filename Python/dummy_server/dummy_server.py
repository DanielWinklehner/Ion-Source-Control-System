from flask import Flask, redirect
from flask import request

from serial_communication import *
from collections import defaultdict

import subprocess
import messages
import json
import urllib2
import copy
import time
import messages

import threading

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

	


channel_values = {}				# key = arduino id; value = dictionary (key = channel name; value = float/int/bool).
device_channel_names = defaultdict(list)	# key = arduino id; value = list( channel names ).

all_active_arduinos = []
all_active_managers = []

def update_arduinos_connected():
	global all_active_arduinos
	global all_active_managers

	while True:
		all_arduinos = find_arudinos_connected()

		#all_active_arduinos = all_arduinos
		#all_active_managers = [Manager().SerialCOM(arduino_id=arduino[0], port_name=arduino[1]) for arduino in all_active_arduinos]
		

		for i, arduino in enumerate(all_arduinos):

			arduinos_to_remove = []
			
			for j, arduino_already_added in enumerate(all_active_arduinos):

				#print arduino, arduino_already_added

				if arduino_already_added[0] == arduino[0] and arduino_already_added[1] == arduino[1]:
					# Both arduino id and port name matches. Do nothing.
					#print "Case I"
					pass
				elif arduino_already_added[0] == arduino[0] and arduino_already_added[1] != arduino[1]:
					# Arduino id matches but port name does not. Replace them with new entries.
					#print "Case 2"
					all_active_arduinos[j] = arduino
					all_active_managers[j] = Manager().SerialCOM(arduino_id=arduino[0], port_name=arduino[1])
					all_active_managers[j].send_message("c")
				else:
					pass

				if arduino_already_added not in all_arduinos:
					arduinos_to_remove.append(arduino_already_added)

			for arduino_to_remove in arduinos_to_remove:
				print arduino_to_remove, "no longer there so removing it."
				try:
					all_active_arduinos.remove(arduino_to_remove)
				except ValueError:
					pass

			# Next, "brand new" arduinos that we've never added before.
			if arduino in all_active_arduinos:
				#print "arduino already added"
				pass
			else:
				#print "nope! Not there!"

				new_manager = Manager().SerialCOM(arduino_id=arduino[0], port_name=arduino[1])

				all_active_arduinos.append(arduino)
				all_active_managers.append(new_manager)
				channel_values[arduino[0]] = {}				

				all_channels = messages.decode_channel_names( new_manager.send_message("c") )

				for channel in all_channels:
					device_channel_names[arduino[0]].append(channel)
					



connected_arduinos_thread = threading.Thread(target=update_arduinos_connected)
connected_arduinos_thread.start()






def mp_worker(serial_com, message):

	start = time.time()

	print "The message is", message

	arduino_response = serial_com.send_message(message)
	
	print "this is the arduino response", arduino_response

	end = time.time()

	#print "it took", (end - start), "to get a message from the arduino"

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

		print arduino_id, query

		for i in range(len(all_active_managers)):
			
			if all_active_managers[i].get_arduino_id() == arduino_id:
				serial_coms_to_use.append( all_active_managers[i] )
				queries_to_use.append( query )


	start = time.time()

	p = multiprocessing.Pool(len(serial_coms_to_use))
	
	all_responses = []

	for serial_com, query in zip(serial_coms_to_use, queries_to_use):
		start2 = time.time()


		all_responses.append( p.apply(func=mp_worker, args=(serial_com, query)) )

		print all_responses
		end2 = time.time()

		#print "it took", (end2 - start2), "seconds for each arduino response."

	p.close()
	p.join()

	end = time.time()

	#print "It took", (end - start), "seconds to collect all the responses."
	print messages.parse_arduino_output_message(all_responses[0][1])

	parsed_response = dict()
	for arduino_id, raw_output_message in all_responses:
		parsed_response[arduino_id] = messages.parse_arduino_output_message(raw_output_message)
		
	return parsed_response

def set_channel_value_to_arduino(arduino_id, channel_name, value):
	global all_active_managers
	
	print "Setting value = {} for channel_name = {} for arduino_id = {}".format(value, channel_name, arduino_id)

	manager = filter(lambda x: x.get_arduino_id() == arduino_id, all_active_managers)[0]
	set_message = messages.build_set_message([channel_name], [value])
	
	print "My set message is", set_message

	arduino_response = manager.send_message(set_message)

	return arduino_response





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
	return json.dumps(find_arudinos_connected())

@app.route("/arduino/active")
def active_arduinos():
	return json.dumps(all_active_arduinos)

@app.route("/arduino/query", methods=['GET', 'POST'])
def query_arduinos():
	
	print "We are querying arduinos"


	print request.args

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


	print ":the arduino response is", arduinos_response
	end = time.time()

	#print "The response took", (end - start), "seconds."

	return json.dumps(arduinos_response)


if __name__ == "__main__":
		# app.run(host='0.0.0.0', port=80)
		app.run(host='0.0.0.0', port=5000)
		pass


