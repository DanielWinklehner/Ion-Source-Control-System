#!/usr/bin/env python

import socket
import time
import threading

from devices.pico import Pico

TCP_IP = '0.0.0.0'
TCP_PORT = 5000
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

# set up devices
p = Pico('/dev/ttyUSB0')
pico_thread = threading.Thread(target=p.run)
pico_thread.start()

def poll():
    # dummy function, actually get values from devices here
    values = [p.current_value, 13439.0, 165.1, 34509.11]
    return ' '.join([str(val) for val in values])

def vset():
    pass

def hmove():
    pass

def vmove():
    pass

def move():
    pass

# mapping of received words to function calls
fmap = {
        b'poll': poll,
        b'vset': vset,
        b'hmove': hmove,
        b'vmove': vmove
       }

print("Scanner DAQ Server accepting connections")

try:
    # outer loop to continuously accept connections
    while True:
        conn, addr = s.accept()
        print("got connection at {}".format(addr))
        # inner loop to handle messages with current connection
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            print("received data: {}".format(data))
            #call function corresponding to what was sent
            conn.send(fmap[data]())
        conn.close()
except KeyboardInterrupt:
    p.terminate()
    pico_thread.join()
