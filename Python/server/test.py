from __future__ import division

import serial
import time



s = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=1.)


s.flushInput()
s.flushOutput()




s.write("i")
print s.readline()

start = time.time()


for i in range(10):
	s.write("q03f14f24s13")
	print s.readline()

# print s.read(8)
# print s.read(8)

# s.write("i")
# print s.read(128)



end = time.time()

print "Each request on average took", (end - start) / 10, "seconds."