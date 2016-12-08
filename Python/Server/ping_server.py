from __future__ import division
from flask import Flask, redirect
from flask import request
from flask_sqlalchemy import SQLAlchemy

from serial_communication import *

import messages
import json
import urllib2
import time

import sys
from datetime import datetime
import requests
import re

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./arduinos.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/html/Ion-Source-Control-System/Python/server/arduinos.db'
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
		pass

	def add_arduino_connection(self, arduino_id, port=None):
		
		print "Adding a new arduino connection."
		
		if port == None and find_port(arduino_id) == None:		
			return


		# Next, check if the arduino id is in the database. 
		db_result = Arduino.query.filter_by(_arduino_id=arduino_id).first()
		
		if db_result != None:				# Arduino already in DB.
			if db_result.get_port() != port:	# Has an incorrect port name, just update the port name.

				db_result._port = port
				db.session.commit()

				return arduino_id
			else:
				# Nothing to do.
				pass


		else:	# Not in the DB.

			# Create a new connection.

			#print "Creating a new connection."			

			# Add the connection to cache.

			try:
				s = SerialCOM(arduino_id, port, timeout=1.)
			except Exception as e:
				print "Error", e
				return None
			
			# Finally, add an entry to the db.
			new_arduino = Arduino(arduino_id, port)
			db.session.add(new_arduino)
			db.session.commit()			

			return arduino_id

		return None
	
	def delete_all_arduinos_from_db(self):
		num_rows_deleted = db.session.query(Arduino).delete()
		return  num_rows_deleted

	def connect_to_all_arduinos_connected(self):
		# Delete all rows in the DB first.
		self.delete_all_arduinos_from_db()		
		
		all_arduinos = find_arudinos_connected()
		
		for arduino_id, port_name in all_arduinos:
			print "adding ", arduino_id,  port_name
			self.add_arduino_connection(arduino_id, port_name)
	


#db.create_all()

#db.session.rollback()

some_server = Server()

while True:
	print "\n"
	print "=" * 50
	some_server.connect_to_all_arduinos_connected()
	time.sleep(0.1)

