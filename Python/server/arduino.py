
from serial_communication import *

import copy
import time
import messages

import multiprocessing
from multiprocessing.managers import BaseManager


class MyManager(BaseManager): pass

def Manager():
	m = MyManager()
	m.start()
	return m 

MyManager.register('SerialCOM', SerialCOM)




data = [
	['49ffb802-50c5-4194-879d-20a87bcfc6ef', '/dev/ttyACM0', 'q03f14f24s13'], ['41b70a36-a206-41c5-b743-1e5b8429b9a1', '/dev/ttyACM1', 'q01s26']
]

# queries = [('49ffb802-50c5-4194-879d-20a87bcfc6ef', 'q03f14f24s13'), ('41b70a36-a206-41c5-b743-1e5b8429b9a1', 'q01s26')]
queries = ['q03f14f24s13', 'q01s26']

# s1 = SerialCOM(arduino_id="49ffb802-50c5-4194-879d-20a87bcfc6ef", port_name="/dev/ttyACM0")
# s2 = SerialCOM(arduino_id="41b70a36-a206-41c5-b743-1e5b8429b9a1", port_name="/dev/ttyACM1")



m_1 = Manager()
s_1 = m_1.SerialCOM(arduino_id="49ffb802-50c5-4194-879d-20a87bcfc6ef", port_name="/dev/ttyACM0")

m_2 = Manager()
s_2 = m_2.SerialCOM(arduino_id="41b70a36-a206-41c5-b743-1e5b8429b9a1", port_name="/dev/ttyACM1")

print s_1.send_message("i")
print s_2.send_message("i")

def mp_worker(serial_com, message):
	return serial_com.send_message(message)
	


results = []
def callback(x):
	results.append(x)


def mp_handler():
	

	p = multiprocessing.Pool(1)

	start = time.time()

	a = p.apply_async(func=mp_worker, args=(s_1, queries[0]), callback=callback)
	b = p.apply_async(func=mp_worker, args=(s_2, queries[1]), callback=callback)

	# p.close()
	# p.join()

	end = time.time()

	print "Took", (end - start), "seconds for apply."

	return a.get(), b.get()

def query_arduinos(arduino_info, queries):

	# Build the data list first.
	worker_data = copy.copy(arduino_info)

	for i, (arduino_id, port_name) in enumerate(worker_data):
		for j, (arduino_to_query, query_string) in enumerate(queries):
			if arduino_to_query == arduino_id:
				worker_data[i].append(query_string)

	p = multiprocessing.Pool(len(arduino_info))

	all_responses = p.map(mp_worker, arduino_info)

	parsed_response = dict()
	for arduino_id, raw_output_message in all_responses:
		parsed_response[arduino_id] = messages.parse_arduino_output_message(raw_output_message)
		
	return parsed_response


if __name__ == '__main__':
	# mp_handler()

	start = time.time()

	# print query_arduinos(data, queries)
	print mp_handler()


	# print results


	# while len(results) == 0:
	# 	print results

	# print results


	end = time.time()



	print
	print "All this took", (end - start), "seconds."