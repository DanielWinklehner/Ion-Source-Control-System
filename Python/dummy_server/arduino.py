
from serial_communication import *
from collections import defaultdict

import copy
import time
import messages
import threading
import multiprocessing
from multiprocessing.managers import BaseManager


class MyManager(BaseManager): pass

def Manager():
	m = MyManager()
	m.start()
	return m 

MyManager.register('SerialCOM', SerialCOM)


# =========================================================================================================================================================

channel_values = {}				# key = arduino id; value = dictionary (key = channel name; value = float/int/bool).
device_channel_names = defaultdict(list)	# key = arduino id; value = list( channel names ).

all_active_arduinos = []
all_active_managers = []

def update_arduinos_connected():
	global all_active_arduinos
	global all_active_managers

	while True:
		all_arduinos = find_arudinos_connected()

		for i, arduino in enumerate(all_arduinos):

			arduinos_to_remove = []
			
			for j, arduino_already_added in enumerate(all_active_arduinos):

				#print arduino, arduino_already_added

				if arduino_already_added[0] == arduino[0] and arduino_already_added[1] == arduino[1]:
					# Both arduino id and port name matches. Do nothing.
					#print "Case I"
					pass
				elif arduino_already_added[0] == arduino[0] and arduino_already_added[1] != arduino[1]:
					# Arduino id matches but port name does not. Replace them with new entries.
					#print "Case 2"
					all_active_arduinos[j] = arduino
					all_active_managers[j] = Manager().SerialCOM(arduino_id=arduino[0], port_name=arduino[1])
					all_active_managers[j].send_message("c")
				else:
					pass

				if arduino_already_added not in all_arduinos:
					arduinos_to_remove.append(arduino_already_added)

			for arduino_to_remove in arduinos_to_remove:
				print arduino_to_remove, "no longer there so removing it."
				try:
					all_active_arduinos.remove(arduino_to_remove)
				except ValueError:
					pass

			# Next, "brand new" arduinos that we've never added before.
			if arduino in all_active_arduinos:
				#print "arduino already added"
				pass
			else:
				#print "nope! Not there!"

				new_manager = Manager().SerialCOM(arduino_id=arduino[0], port_name=arduino[1])

				all_active_arduinos.append(arduino)
				all_active_managers.append(new_manager)
				channel_values[arduino[0]] = {}				

				all_channels = messages.decode_channel_names( new_manager.send_message("c") )

				for channel in all_channels:
					device_channel_names[arduino[0]].append(channel)
					
		'''	
		# Next, update values for all devices.
		for manager in all_active_managers:
			arduino_id = manager.get_arduino_id()

			channel_names = device_channel_names[arduino[0]][0:3]

			# Build a query message.
			query_message = messages.build_query_message(channel_names, [3] * len(channel_names))
			
			if arduino_id in channel_values:
				# Get current value.
				response = manager.send_message(query_message)
				parsed_response = messages.parse_arduino_output_message(response)
				#print value				
				#channel_values[arduino_id] = 
				pass
		'''
		#print all_active_arduinos
		#print all_active_managers
		#print device_channel_names




connected_arduinos_thread = threading.Thread(target=update_arduinos_connected)
connected_arduinos_thread.start()





def mp_worker(manager, channel_names):
	
	
	query_message = messages.build_query_message(channel_names, [2] * len(channel_names))
	
	response = manager.send_message(query_message)
	parsed_response = messages.parse_arduino_output_message(response)

	print 

	return manager.get_arduino_id(), parsed_response
	#return parsed_response
	
results = []
def callback(x):
	print x	
	results.append(x)
	channel_values[x[0]] = x[1]
	


def mp_handler():
	
	all_arduinos = find_arudinos_connected()

	p = multiprocessing.Pool(len(all_arduinos))

	start = time.time()
	
	time.sleep(2)
	print "Length of all active managers =", len(all_active_managers)
	for i in range(len(all_active_managers)):
		p.apply_async(func=mp_worker, args=(all_active_managers[i], device_channel_names[all_active_managers[i].get_arduino_id()]), callback=callback)
		#p.apply(func=mp_worker, args=(all_active_managers[i], device_channel_names[all_active_managers[i].get_arduino_id()]))

	p.close()
	p.join()
	
	end = time.time()
	
	print
	print "Took", (end - start), "seconds for apply."

	return 0





if __name__ == '__main__':

	# mp_handler()

	start = time.time()
	
	
	mp_handler()
	
	
	# print query_arduinos(data, queries)
	#print mp_handler()

	
	print "all active arduinos are", all_active_arduinos

	
	while len(results) == 0:
		print results
	print results
	
	print "End result = ", channel_values
	


	end = time.time()
	

	print
	print "All this took", (end - start), "seconds."
