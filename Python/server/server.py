from flask import Flask, redirect
from flask import request

from serial_communication import *

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

	


managers = [Manager(), Manager()]


all_arduinos_to_use = []
all_managers_to_use = []

def update_arduinos_connected():
	global all_arduinos_to_use
	global all_managers_to_use

	while True:
		all_arduinos = find_arudinos_connected()

		#all_arduinos_to_use = all_arduinos
		#all_managers_to_use = [Manager().SerialCOM(arduino_id=arduino[0], port_name=arduino[1]) for arduino in all_arduinos_to_use]
		

		for i, arduino in enumerate(all_arduinos):

			arduinos_to_remove = []
			
			for j, arduino_already_added in enumerate(all_arduinos_to_use):

				#print arduino, arduino_already_added

				if arduino_already_added[0] == arduino[0] and arduino_already_added[1] == arduino[1]:
					# Both arduino id and port name matches. Do nothing.
					#print "Case I"
					pass
				elif arduino_already_added[0] == arduino[0] and arduino_already_added[1] != arduino[1]:
					# Arduino id matches but port name does not. Replace them with new entries.
					#print "Case 2"
					all_arduinos_to_use[j] = arduino
					all_managers_to_use[j] = Manager().SerialCOM(arduino_id=arduino[0], port_name=arduino[1])
					all_managers_to_use[j].send_message("i")
				else:
					pass

				if arduino_already_added not in all_arduinos:
					arduinos_to_remove.append(arduino_already_added)

			for arduino_to_remove in arduinos_to_remove:
				print arduino_to_remove, "no longer there so removing it."
				all_arduinos_to_use.remove(arduino_to_remove)

			# Next, "brand new" arduinos that we've never added before.
			if arduino in all_arduinos_to_use:
				#print "arduino already added"
				pass
			else:
				#print "nope! Not there!"
				all_arduinos_to_use.append(arduino)
				all_managers_to_use.append( Manager().SerialCOM(arduino_id=arduino[0], port_name=arduino[1]) )


		#print all_arduinos_to_use
		#print all_managers_to_use


# update_arduinos_connected()


connected_arduinos_thread = threading.Thread(target=update_arduinos_connected)
connected_arduinos_thread.start()






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

		for i in range(len(all_managers_to_use)):
			
			if all_managers_to_use[i].get_arduino_id() == arduino_id:
				serial_coms_to_use.append( all_managers_to_use[i] )
				queries_to_use.append( query )


	start = time.time()

	p = multiprocessing.Pool(len(serial_coms_to_use))
	
	all_responses = []

	for serial_com, query in zip(serial_coms_to_use, queries_to_use):
		start2 = time.time()

		all_responses.append( p.apply(func=mp_worker, args=(serial_com, query)) )

		end2 = time.time()

		#print "it took", (end2 - start2), "seconds for each arduino response."

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


@app.route("/display")
def display():

    process = subprocess.call("sudo python /var/www/html/Ion-Source-Control-System/Python/server/display_plain.py &", shell=True)

    return "Started display code."



@app.route("/arduino/all")
def all_arduinos():
	return json.dumps(find_arudinos_connected())


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
    pass


