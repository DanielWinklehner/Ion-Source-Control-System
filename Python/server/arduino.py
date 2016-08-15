
from serial_communication import *

import copy
import time
import messages

import multiprocessing



data = (
    ['49ffb802-50c5-4194-879d-20a87bcfc6ef', '/dev/ttyACM0'], ['41b70a36-a206-41c5-b743-1e5b8429b9a1', '/dev/ttyACM1']
)

queries = [('49ffb802-50c5-4194-879d-20a87bcfc6ef', 'q03f14f24s13'), ('41b70a36-a206-41c5-b743-1e5b8429b9a1', 'q01s26')]

def mp_worker(inputs):

    arduino_id = inputs[0]
    port = inputs[1]
    message = inputs[2]

    s = SerialCOM(arduino_id=arduino_id, port_name=port, timeout=1.)

    return arduino_id, s.send_message(message)


def mp_handler():
    p = multiprocessing.Pool(2)
    p.map(mp_worker, data)


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
    print query_arduinos(data, queries)