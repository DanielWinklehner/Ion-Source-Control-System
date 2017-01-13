from __future__ import division
from MPLCanvasWrapper3 import MPLCanvasWrapper3
import time
import numpy as np


class MIST1Plot:

    def __init__(self, variable_name="", x_s=np.ones(1)*time.time(), y_s=np.zeros(1)):

        print "Initializing a new MIST1Plot object."

        self._variable_name = variable_name
        self._number_of_data_points = len(x_s)

        self._x_s = x_s
        self._y_s = y_s

        self._canvas_wrapper = MPLCanvasWrapper3(nbp=0)
        self._canvas_wrapper.set_title("")
        self._canvas_wrapper.set_autoscale(True)
        self._canvas_wrapper.xtime = True

        self._plot = self._canvas_wrapper.plot(self._x_s, self._y_s, c="red", label=self._variable_name,
                                               linestyle="solid")

        self._canvas_wrapper.append_legend_entries_flag(True)

        self._canvas_wrapper.draw_idle()

    def recreate(self):
        """
        Completely clears the canvas and plots the data.
        This is only done when the number of stored data points changes.
        :return:
        """
        settings = self._canvas_wrapper.get_settings()
        self._canvas_wrapper.clear()

        self._plot = self._canvas_wrapper.plot(self._x_s, self._y_s, c="red", label=self._variable_name,
                                               linestyle="solid")

        self._canvas_wrapper.set_settings(settings)

    def update(self):
        """
        This only updates the values in the plot. Should be faster and a full update is only
        necessary when the number of stored data points changes...
        :return:
        """

        self._plot[0].set_data(self._x_s, self._y_s)
        self._canvas_wrapper.axis.relim()
        self._canvas_wrapper.axis.autoscale_view(True, True, True)
        self._canvas_wrapper.draw_canvas()

    def plot(self, x_s, y_s):

        self._x_s = x_s
        self._y_s = y_s

        if len(x_s) != self._number_of_data_points:
            self.recreate()
            self._number_of_data_points = len(x_s)
        else:
            self.update()

    def get_canvas(self):

        return self._canvas_wrapper
