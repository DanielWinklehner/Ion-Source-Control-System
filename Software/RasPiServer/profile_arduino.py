import SerialCOM
import serial
import time

import multiprocessing



# N = 50

# ser = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=1.)

# start = time.time()

# for i in range(N):
#     ser.write("q05i14i24v14v24x14")
#     x = ser.readline()

#     print x

#     if len(x.strip()) == 0:
#         raise Exception("Empty response.")

# end = time.time()


# print "Took {} seconds for {} queries.".format((end - start), N)
# print "That's an average of {} per query.".format((end - start)/N)




class QueryMachine:
    def __init__(self, serial_com, queries):
        self._serial_com = serial_com
        self._queries = queries

    def serial_com(self):
        return self._serial_com

    def queries(self):
        return self._queries

    def __str__(self):
        return str(self._serial_com) + "; " + str(self._queries)





all_arduinos = ["/dev/ttyACM0"]
all_messages = [["q05i14i24v14v24x14"]]


# machines = []
# for (port, message) in zip(all_arduinos, all_messages):

#         ser = serial.Serial(port, baudrate=115200, timeout=1.)

#         machines.append(QueryMachine(ser, messages))

machines = [QueryMachine(serial.Serial(port, baudrate=115200, timeout=1.), messages) for (port, messages) in zip(all_arduinos, all_messages)]

def worker_my(arg):
    print arg


print machines
p = multiprocessing.Pool(len(machines))

p.map(worker_my, machines)