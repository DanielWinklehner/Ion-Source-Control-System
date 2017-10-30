#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Custom pyqtgraph PlotWidget class with a timestamp axis

import datetime as dt

import pyqtgraph as pg
import pyqtgraph.widgets.RemoteGraphicsView

class DateTimeAxis(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        strings = []
        for v in values:
            val = dt.datetime.fromtimestamp(v).strftime('%H:%M:%S')
            strings.append(val)
        return strings

#view = pg.widgets.RemoteGraphicsView.RemoteGraphicsView()
#view.pg.setConfigOptions(antialias=True) ## prettier plots at no cost to the main process! 

## Create a PlotItem in the remote process that will be displayed locally
#rplt = view.pg.PlotItem()
#rplt._setProxyOptions(deferGetattr=True)  ## speeds up access to rplt.plot
#view.setCentralItem(rplt)

###class DateTimePlot(pg.PlotWidget):
class DateTimePlotWidget(pg.widgets.RemoteGraphicsView.RemoteGraphicsView):
    """ Plot Widget with date time axis, and ability to copy settings """
    def __init__(self, *args, **kwargs):
        # Give the settings parameter from kwargs a default value
        settings = kwargs.pop('settings', None)

        super().__init__(*args, **kwargs)

        # Initialize this widget with the DateTimeAxis by appending it to the kwargs
        #self._dateaxis = DateTimeAxis(orientation='bottom')
        #nkwargs = kwargs
        #nkwargs['axisItems'] = {'bottom': self._dateaxis}
        self._plot = self.pg.PlotItem() #*args, **nkwargs)
        self._plot._setProxyOptions(deferGetattr=True)  ## speeds up access to rplt.plot

        self.setCentralItem(self._plot)

        self._settings = settings
        self._curve = self._plot.plot()
        self.update_settings()

    @property
    def curve(self):
        return self._curve

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, newsettings):
        self._settings = newsettings
        self.update_settings()

    def update_settings(self):
        if self._settings is None:
            return

        autorangeaxes = ''
        if self._settings['x']['mode'] != 'auto':
            self._plot.setXRange(self._settings['x']['min'],
                           self._settings['x']['max'],
                           padding=0.0)
        else:
            autorangeaxes += 'x'

        if self._settings['y']['mode'] != 'auto':
            self._plot.setYRange(self._settings['y']['min'],
                           self._settings['y']['max'],
                           padding=0.0)
        else:
            autorangeaxes += 'y'

        if autorangeaxes != '':
            self._plot.enableAutoRange(axis = autorangeaxes)

        self._plot.setLogMode(x=self._settings['x']['log'],
                        y=self._settings['y']['log'])

        self._plot.showGrid(x=self._settings['x']['grid'],
                      y=self._settings['y']['grid'])

        self._curve.setData(pen = self._settings['widget']['color'])

