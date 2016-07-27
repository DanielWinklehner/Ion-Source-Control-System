from __future__ import division

import time
import socket
import struct

from threading import Thread 
from SocketServer import ThreadingMixIn 

from serial_communication import SerialCOM
 


class Server:

	def __init__(self, tcp_ip='0.0.0.0', tcp_port=0, buffer_size=1024):
		
		self._tcp_ip = tcp_ip
		self._tcp_port = tcp_port

		self._tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

		self._all_serial_ports = SerialCOM.get_all_serial_ports()

		self._serial_coms = {}	# Key = integer. Value = SerialCOM.
		self._arduino_ids = []


	def connect(self):
		self._tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._tcp_server.bind((self._tcp_ip, self._tcp_port)) 

	def get_tcp_server(self):
		return self._tcp_server

	def get_connection_ip_port(self):
		(conn, (ip, port)) = self._tcp_server.accept()
		return (conn, (ip, port))

	def listen(self):
		self._tcp_server.listen(4)


	def find_key_for_arduino_connection(self):
		if len(self._serial_coms.keys()) == 0:
			return 0
		else:
			return max(self._serial_coms.keys()) + 1

	def add_arduino_connection(self, arduino_id):

		key = self.find_key_for_arduino_connection()

		self._serial_coms[key] = SerialCOM(arduino_id)

		self._arduino_ids.append(arduino_id)

		return key
		
	def get_arduino_ids(self):
		return self._arduino_ids




# Multithreaded Python server : TCP Server Socket Thread Pool
class ClientThread(Thread): 
 
	def __init__(self, server, connection, ip, port): 
		Thread.__init__(self) 
		self._server = server 				# NOT Thread SAFE. But okay since there will only be one client connected to the server at a time.
		self._connection = connection
		self._ip = ip 
		self._port = port 
		
		print "[+] New server socket thread started for " + self._ip + ":" + str(self._port) 


 	def send_message(self, msg):
		# Prefix each message with a 4-byte length (network byte order)
		msg = struct.pack('>I', len(msg)) + msg
		self._connection.sendall(msg)

	def receive_message(self):
		# Read message length and unpack it into an integer
		raw_msglen = self.receive_all(4)
		if not raw_msglen:
			return None
		msglen = struct.unpack('>I', raw_msglen)[0]
		# Read the message data
		return self.receive_all(msglen)

	def receive_all(self, n):
		# Helper function to recv n bytes or return None if EOF is hit
		data = ''
		while len(data) < n:
			packet = self._connection.recv(n - len(data))
			if not packet:
				return None
			data += packet
		return data


	def run(self): 
		
		output_message = ""

		while True : 
			
			
			input_message = self.receive_message()
			
			print "Server received data:", input_message

			if "connect_arduino" in input_message:

				arduino_ids = input_message.split(":")[1].split(",")

				print arduino_ids
				
				for arduino_id in arduino_ids:
					if arduino_id not in self._server.get_arduino_ids():
						key = self._server.add_arduino_connection(arduino_id)
						output_message = "connected:{}={}".format(arduino_id, key)
						
				
			elif "q:" in input_message:
				pass


			print "sending message", output_message
			self.send_message(output_message)
			

			MESSAGE = raw_input("Enter Response from Server/Enter exit:")
			
			if MESSAGE == 'exit':
				print "exit enterred"
				break
			else:
				"Continuing"
				continue
			
			
		print "Loop exited"
		self._connection.close()
 		print "Connection closed."


def start_server():

	some_server = Server(tcp_port=1192)
	some_server.connect()

	

	threads = [] 
	 
	while True: 
		
		some_server.listen()
				
		(conn, (ip, port)) = some_server.get_connection_ip_port() 
		
		new_client_thread = ClientThread(some_server, conn, ip, port) 
		
		new_client_thread.start() 
		
		threads.append(new_client_thread) 

		message = raw_input("Enter something")
		if message == "exit":
			break
	 
	for t in threads: 
		t.join() 



if __name__ == "__main__":
	start_server()

