from __future__ import division
import time
import socket



class Client:
	def __init__(self):
		self._host = socket.gethostname()
		self._port = 7817
		self._buffer_size = 2048

		self._tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def connect(self):
		self._tcp_client.connect((self._host, self._port))

	def close_connection(self):
		self._tcp_client.close()

	def send_message(self, message):
		self._tcp_client.send(message)

	def receive_message(self):
		return self._tcp_client.recv(self._buffer_size)



some_client = Client()

some_client.connect()

some_client.send_message("connect_arduino:2cc580d6-fa29-44a7-9fec-035acd72340e")

response = some_client.receive_message()
arduino_key = response.split("=")[1]

time.sleep(2)
some_client.send_message("q@{}:fm1,fm2,fm3")

some_client.close_connection()


# Messages begin with arduino id and a number of lines thing. That tells the server to pass the next N lines to that arduino.

# Or a better option would be to have a connect and disconnect message.
# Maybe have connect:<arduino id> and then the server will keep passing all messages to that arduino  until it receives a disconnect:<arduino id> message.

# Maybe have the server assign an integer, which it will tell back to the GUI, that links it to the correct arduino id?
# This way we'll always know which arduino a particular message is intended for. 
# This is important since multiple arduino messages must probably be done in parallel (kind of parallel, more like arduino 1, arduino 1, arduino 2, arduino 1, arduino 1, arduino 2, arduino 2, arduino 1)