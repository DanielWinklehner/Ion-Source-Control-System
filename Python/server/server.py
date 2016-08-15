from flask import Flask, redirect
from flask import request
from flask_sqlalchemy import SQLAlchemy

from serial_communication import *

import messages
import json
import urllib2
import time
# import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./arduinos.db'
db = SQLAlchemy(app)



app.debug = True


class Arduino(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _arduino_id = db.Column(db.String(37), unique=True)
    _port = db.Column(db.String(25), unique=True)

    def __init__(self, arduino_id, port):
        self._arduino_id = arduino_id
        self._port = port

    def __repr__(self):
        return self._arduino_id, self._port

    def str(self):
    	return self._arduino_id, self._port

    def get_arduino_id(self):
    	return self._arduino_id

    def get_port(self):
    	return self._port



class Server:
	def __init__(self):
		self._serial_coms = {}

	def add_arduino_connection(self, arduino_id):
		
		print "Adding a new arduino connection."

		# First check if it's already in caches.

		if arduino_id in self._serial_coms.keys():
			return arduino_id

		# Next, check if the arduino id is in the database. 
		db_result = Arduino.query.filter_by(_arduino_id=arduino_id).first()

		

		if db_result != None:
			
			print "Adding connection from DB to cache.", db_result.str()
			
			# Add the connection to cache.
			
			try:
				self._serial_coms[db_result.get_arduino_id()] = SerialCOM(db_result.get_arduino_id(), db_result.get_port())
				return arduino_id
			except Exception as e:
				print "Error", e
				return None

		else:
			# Create a new connection.

			print "Creating a new connection."

			# First, find the correct port.
			
			port = find_port(arduino_id)

			# Add the connection to cache.

			try:
				self._serial_coms[arduino_id] = SerialCOM(arduino_id, port)
			except Exception as e:
				print "Error", e
				return None
			
			# Finally, add an entry to the db.
			new_arduino = Arduino(arduino_id, port)
			db.session.add(new_arduino)
			db.session.commit()			

			return arduino_id

		return None
	
	def get_arduino_ids(self):
		return self._serial_coms.keys()

	def empty_dict(self):
		self._serial_coms = {}

	def send_message_to_arduino(self, arduino_id, msg):

		
	

		print "Sending a message to arduino", arduino_id, msg

		# First, check if the arduino id is present in cache. If yes, just use that SerialCOM.

		if arduino_id in self._serial_coms.keys():
			self._serial_coms[arduino_id].send_message(msg)
		else:
			# Not in cache. 

			print "serial com not in cache."

			# Add a new connection.
			response = self.add_arduino_connection(arduino_id)

			if response != None:
				self.send_message_to_arduino(arduino_id, msg)


		print "i'm done sending all messages"

		return "error"

	def receive_message_from_arduino(self, arduino_id):
		print "Getting a message from arduino"

		# First, check if the arduino id is present in cache. If yes, just use that SerialCOM.

		if arduino_id in self._serial_coms.keys():
			
			print "arduino in cache", self._serial_coms[arduino_id]

			return self._serial_coms[arduino_id].read_message()
		else:
			# Not in cache.

			print "serial com not in cache"

			# Add a new connection.

			response = self.add_arduino_connection(arduino_id)

			if response != None:
				return self.receive_message_from_arduino(arduino_id)

		return ""


# db.create_all()

some_server = Server()

@app.route("/")
def hello():
    return "Hey there!"

@app.route("/arduino/all")
def all_arduinos():
	all_arduino_ids = some_server.get_arduino_ids()

	return json.dumps(all_arduino_ids)

'''
@app.route("/arduino/alive", methods=['POST', 'GET'])
def arduino_alive():
	if request.method == 'POST':
		pass
	elif request.method == 'GET':
		
		arduino_id = request.args.get('arduino_id')

		if arduino_id in some_server.get_arduino_ids():
			some_server.send_message_to_arduino(arduino_id, "i")
			arduino_response = some_server.receive_message_from_arduino(arduino_id)

			print arduino_response.strip() == "device_id={}".format(arduino_id)
			return str(int(arduino_response.strip() == "device_id={}".format(arduino_id)))

		else:
			response = some_server.add_arduino_connection(arduino_id)

			if response != None:
				pass
				# return requests.get("{}{}/?arduino_id=".format(request.url_root, str(request.url_rule)[1:]), arduino_id)

	return "0"
'''

@app.route("/arduino/set", methods=['POST', 'GET'])
def set_channel_value():
	if request.method == 'POST':
		try:

			arduino_id = request.form['arduino_id']
			channel_names = json.loads(request.form['channel_names'])
			values_to_set = json.loads(request.form['values_to_set'])

			set_message = messages.build_set_message(channel_names, values_to_set)

			some_server.send_message_to_arduino(arduino_id, set_message)

			arduino_response = some_server.receive_message_from_arduino(arduino_id)

			return ""

		except Exception as e:
			return "Server Error while setting values: {}".format(e)


			
@app.route("/arduino/connect", methods=['POST', 'GET'])
def connect_arduino():

	if request.method == 'POST':
		if request.form['arduino_id']:
			arduino_id = request.form['arduino_id']
	elif request.method == 'GET':
		arduino_id = request.args.get('arduino_id')
	
	response = some_server.add_arduino_connection(arduino_id)
		
	if response == None:
		return "Server Error: Arduino didn't respond."
	else:
		return "success"

@app.route("/arduino/query", methods=['GET', 'POST'])
def query_arduino():
	
	some_server.empty_dict()

	if request.method == 'POST':
		arduino_id = request.form['arduino_id']
		channel_names = json.loads(request.form['channel_names'])
		precisions = json.loads(request.form['precisions'])
		
	elif request.method == 'GET':
		arduino_id = request.args.get('arduino_id')
		channel_names = json.loads(request.args.get('channel_names'))
		precisions = json.loads(request.args.get('precisions'))
	

	
	try:
		print "querying arduino with", arduino_id, channel_names

		query_message = messages.build_query_message(channel_names, precisions)

		print "the query message is", query_message

		some_server.send_message_to_arduino(arduino_id, query_message)
		
		#time.sleep(0.5)

		arduino_response = some_server.receive_message_from_arduino(arduino_id)
		
		print "got a response from arduino", arduino_response

		parsed_response = messages.parse_arduino_output_message(arduino_response)
		
		print "the parsed response is", parsed_response
		
		return json.dumps(parsed_response)

	except Exception as e:
		return str(e)
		# return "Server Error while querying: {}".format(e) 


	return "query"
		
			

if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=80)
    app.run(host='0.0.0.0', port=5000)
