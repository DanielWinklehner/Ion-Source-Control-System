from __future__ import division
import time
import socket
import struct
import messages

class Client:
	def __init__(self):
		self._host = socket.gethostname()
		self._port = 2492
		self._buffer_size = 2048

		self._tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def connect(self):
		self._tcp_client.connect((self._host, self._port))

	def close_connection(self):
		self._tcp_client.close()

	def ask_server_to_connect_arduino(self, arduino_id):
		print "Asking the server to connect arduino", arduino_id
		self.send_message("connect_arduino:{}".format(arduino_id))

		print "Sent the message to the server."

		return self.receive_message()

	def send_message(self, msg):
		# Prefix each message with a 4-byte length (network byte order)
		msg = struct.pack('>I', len(msg)) + msg
		self._tcp_client.sendall(msg)

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
			packet = self._tcp_client.recv(n - len(data))
			if not packet:
				return None
			data += packet
		return data

	def query_channels(self, arduino_id, channel_names, precisions=[]):
		if len(precisions) == 0:
			# Default precision values.
			precisions = [4] * len(channel_names)

		query_message = messages.build_query_message(arduino_id, channel_names, precisions)
		self.send_message(query_message)

		query_response = self.receive_message()

		return messages.parse_arduino_output_message(query_response)






# host = socket.gethostname() 
# port = 7817
# BUFFER_SIZE = 2000 
# MESSAGE = raw_input("tcpClientA: Enter message/ Enter exit:") 
 
# tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
# tcpClientA.connect((host, port))
 
# while MESSAGE != 'exit':
#     tcpClientA.send(MESSAGE)     
#     data = tcpClientA.recv(BUFFER_SIZE)
#     print " Client2 received data:", data
#     MESSAGE = raw_input("tcpClientA: Enter message to continue/ Enter exit:")
 
# tcpClientA.close() 