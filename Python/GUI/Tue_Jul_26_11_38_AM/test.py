from __future__ import division
import copy


import numpy as np
import matplotlib.pyplot as plt

plt.axis([0, 100, 0, 1])
plt.ion()


for i in range(100):
    
    x_s = [i, i + 1, i + 2]
    # y_s = [np.random.random(), np.random.random(), np.random.random()]
    y_s = [0.5, 0.5, 0.5]

    # plt.scatter(i, y)
    plt.plot(x_s, y_s, c="red", lw=1)
    plt.pause(0.05)

while True:
    plt.pause(0.05)