from __future__ import division

import time

class Procedure:

	def __init__(self, name, conditions, actions, priority=1):
		"""Summary
		
		Args:
		    name (TYPE): Description
		    conditions (list[ tuple(function, channel) ]): A list of tuples of two elements- (lambda) function and channel. e.g., [ (lambda x: return not x, interlock_box.micro_switch#1) ]
		    actions (list[ tuple(function, kwargs) ]): A list of tuples of two elements- function and kwargs. For function, the string "emergency_stop" is also accepted. If you use "emergency_stop" as the "function", use None or an empty dict for kwargs. 
		    priority (int, optional): lower number = higher priority. A priority of -1 gets its own thread.
		
		Deleted Parameters:
		    channel_to_act_on (TYPE): Description
		    action (TYPE): Description
		"""

		print actions[0][1]

		self._name = name
		self._conditions = conditions
		self._actions = actions
		self._priority = priority


	def get_name(self):
		return self._name

	def get_conditions(self):
		return self._conditions

	def get_actions(self):
		return self._actions

	def get_priority(self):
		return self._priority

	def should_perform_procedure(self):
		condition_satisfied = 0

		condition_count = 0
		for condition_func, channel in self._conditions:
			
			# This is so that, in cases where conditions = [] is an empty list, we don't act on it. 
			if condition_count == 0:
				condition_satisfied += 1

			if condition_func( channel.get_value() ):
				condition_satisfied *= 1

			condition_count += 1


		return bool(condition_satisfied)


	def act(self):
		
		"""Summary
		
		Returns:
		    TYPE: Returns either 	STOP => Perform an emergency stop.
									True => The procedure was successful. 
									False => The procedure was not successful.
		"""

		print "acting the procedure"

		if self.should_perform_procedure():
			for action, kwargs in self._actions:
				if action == "emergency_stop":
					return "STOP"
				else:
					action_function = action

					def dummy_func(**kwargs):
						print kwargs.keys()
						# func(kwargs)


					# print kwargs
					# dummy_func(**kwargs)

					action_function(**kwargs)


		return False