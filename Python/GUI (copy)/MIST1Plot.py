from __future__ import division

import time
import copy

import matplotlib.pyplot as plt

from MPLCanvasWrapper3 import MPLCanvasWrapper3


class MIST1Plot:
    def __init__(self, variable_name=""):
        print "Initializing a new MIST1Plot object."

        self._variable_name = variable_name

        self._x_s = [time.time(), time.time() + 5]
        self._y_s = [1, 2]

        self._canvas_wrapper = MPLCanvasWrapper3(nbp=0)
        self._canvas_wrapper.set_title("")
        self._canvas_wrapper.set_autoscale(True)
        self._canvas_wrapper.xtime = True

        self._plot = self._canvas_wrapper.plot(self._x_s, self._y_s, c="red", label=self._variable_name,
                                               linestyle="solid")

        self._canvas_wrapper.append_legend_entries_flag(True)

        self.plot()

    def plot(self):
        # TODO:
        # You should really be calling this just once.
        # Right now this is called every time there is an update.
        # Fix it.

        start = time.time()

        # settings = self._canvas_wrapper.get_settings()

        
        # self._canvas_wrapper.clear()


        # TODO: Remove the following two lines.
        
        self._plot = self._canvas_wrapper.plot(self._x_s, self._y_s, c="red", label=self._variable_name,
                                               linestyle="solid")
        
        # self._canvas_wrapper.set_settings(settings)
        # self._canvas_wrapper.set_yscale('log')

        end = time.time()

        # print "Clearing took {} seconds.".format(end - start)

        pass

    def update_values(self, x_s, y_s):
        self._x_s = x_s
        self._y_s = y_s
        #
        # # Update the values of our plot object (<matplotlib.lines.Line2D>)
        #
        # self._plot[0].set_xdata(copy.deepcopy(self._x_s))
        # self._plot[0].set_ydata(copy.deepcopy(self._y_s))

        self._plot[0].set_data(x_s, y_s)

        # self._plot[0].set_ydata(y_s)
        #
        
        plt.draw()

        # self._canvas_wrapper.canvas.draw()
        # self._canvas_wrapper.draw_idle()

    def get_canvas(self):
        return self._canvas_wrapper
