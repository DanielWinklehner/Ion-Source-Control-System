from flask import Flask, redirect
from flask import request


from serial_communication import SerialCOM

import messages
import json
import urllib2
# import requests

app = Flask(__name__)

app.debug = True



class Server:
	def __init__(self):
		self._serial_coms = {}

	def add_arduino_connection(self, arduino_id):
		
		print "Trying to connect to the arduino", arduino_id

		try:
			self._serial_coms[arduino_id] = SerialCOM(arduino_id)
			return arduino_id
		except Exception as e:
			print "Error"
			return None
		
	def get_arduino_ids(self):
		return self._serial_coms.keys()

	def send_message_to_arduino(self, arduino_id, msg):
		self._serial_coms[arduino_id].send_message(msg)

	def receive_message_from_arduino(self, arduino_id):
		return self._serial_coms[arduino_id].read_message()

some_server = Server()

@app.route("/")
def hello():
    return "Hey buddy!"

@app.route("/arduino/all")
def all_arduinos():
	all_arduino_ids = some_server.get_arduino_ids()

	return json.dumps(all_arduino_ids)

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


@app.route("/arduino/connect", methods=['POST'])
def connect_arduino():

	if request.method == 'POST':
		if request.form['arduino_id']:
			arduino_id = request.form['arduino_id']
			response = some_server.add_arduino_connection(arduino_id)
	
		
	if response == None:
		return "error"
	else:
		return "success"

@app.route("/arduino/query", methods=['GET', 'POST'])
def query_arduino():
	
	if request.method == 'POST':
		try:
			arduino_id = request.form['arduino_id']
			channel_names = json.loads(request.form['channel_names'])
			precisions = json.loads(request.form['precisions'])

			query_message = messages.build_query_message(channel_names, precisions)

			some_server.send_message_to_arduino(arduino_id, query_message)

			arduino_response = some_server.receive_message_from_arduino(arduino_id)
			parsed_response = messages.parse_arduino_output_message(arduino_response)


			return json.dumps(parsed_response)

		except Exception as e:
			return "error"
		print query_message

	return "query"
		
			

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)