#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Procedure class

import operator

class Procedure:
    def __init__(self, name, rules, actions, critical=False, email='', sms=''):

        # Rules dict:
        # key = arduino_id, device, channel, comparison, value

        # Action dict:
        # key = arduino_id, device, channel, value to set

        self._name = name
        self._rules = {}
        self._actions = {}
        self._actions = actions
        self._critical = critical
        
        # these will trigger sending email/sms if not blank
        self._email = email
        self._sms = sms

        @property
        def name(self):
            return self._name

        @property
        def condition(self):
            return self._condition

        @property
        def actions(self):
            return self._actions

        @property
        def critical(self):
            return self._critical

        def should_perform_procedure(self):
            condition_satisfied = True
            for arduino_id, rule in self._rules.items():
                if not rule['comparison'](channel.value, rule['value']):
                    condition_satisfied = False
                    break

            return condition_satisfied
        
        def do_actions(self):
            for arduino_id, action in self._actions.items():
                print('setting value of {}.{} to {}'.format(action['device'].name,
                                                            action['channel'].name,
                                                            action['value'].name))

            if self._email != '':
                # send email
                pass

            if self._sms != '':
                # send text
                pass
