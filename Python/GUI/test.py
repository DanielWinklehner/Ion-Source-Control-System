from __future__ import division
import copy


def test_func(x):
	return len(x.split(","))

a = copy.deepcopy( test_func )


print a(1)