#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Handles dialog and widget creation

import time
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, \
                            QGroupBox, QLineEdit, QFrame, QLabel, \
                            QRadioButton, QScrollArea, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

import pyqtgraph as pg
from pyqtgraph.widgets.RemoteGraphicsView import RemoteGraphicsView

from .ui_MainWindow import Ui_MainWindow
from .dialogs.PlotChooseDialog import PlotChooseDialog 
from lib.Device import Device
from lib.Channel import Channel

class MainWindow(QMainWindow):
    # signal to be emitted to main program when plots change on plotting page
    sig_plots_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # aliases
        self._statusbar = self.ui.statusBar
        self._messagelog = self.ui.txtMessageLog
        self._overview = self.ui.fmOverview
        self._plots = self.ui.fmPlots
        self._pinnedplot = self.ui.pltPinned
        self._gbpinnedplot = self.ui.gbPinnedPlot
        self._tabview = self.ui.tabMain
        self._btnquit = self.ui.btnQuit
        self._btnplotchoose = self.ui.btnSetupDevicePlots

        self._btnplotchoose.clicked.connect(self.show_PlotChooseDialog)

        self._current_tab = 'main'
        self._tabview.currentChanged.connect(self.tab_changed)

        ## set up containers
        self._overview_layout = QHBoxLayout()
        self._overview.setLayout(self._overview_layout) 
        self._overview.setLayoutDirection(Qt.RightToLeft)
        self._overview_layout.addStretch()

        self._gbox = QGridLayout()
        self._plots.setLayout(self._gbox)

        ## remove the temporary rate label
        self.ui.label_2.deleteLater()
        self._overview_devices = {}
        self._plotted_channels = {}

    @property
    def current_tab(self):
        return self._current_tab

    def tab_changed(self):
        tabName = self._tabview.tabText(self._tabview.currentIndex())
        if tabName == 'Overview':
            self._current_tab = 'main'
        elif tabName == 'Devices':
            self._current_tab = 'devices'
        elif tabName == 'Plotting':
            self._current_tab = 'plots'

    def add_device_to_overview(self, device):
        if device in [x['device'] for _a, x in self._overview_devices.items()]:
            return

        # create group box for this device, add it to overview frame
        devbox = QGroupBox(device.label)
        devbox.setMaximumWidth(250)
        # add groupbox to first row, nth column
        self._overview_layout.addWidget(devbox) #, Qt.AlignLeft)
        self._overview_layout.setAlignment(devbox, Qt.AlignLeft)
        vbox = QVBoxLayout()
        devbox.setLayout(vbox)

        self._overview_devices[device.arduino_id] = {'device': device, 
                                                     'groupbox': devbox,
                                                     'layout': vbox}

        # dict of signals needed from these controls by the main control system
        emitters = {} 

        # dict of QTextEdits to have their text set by the main control system (read values)
        readboxes = {}

        for chname, ch in reversed(sorted(device.channels.items(), key=lambda x: x[1].display_order)):
            # create frame for channel info
            gb = QGroupBox(ch.label)

            if ch.data_type == float:
                # set the group box to vertical layout
                vl = QVBoxLayout()
                gb.setLayout(vl)

                if ch.mode == 'write' or ch.mode == 'both':
                    # create a row with a text box, add it to group box
                    row = QFrame()
                    hl = QHBoxLayout()
                    hl.setContentsMargins(0, 0, 0, 0)
                    row.setLayout(hl)

                    txt = QLineEditX(ch)
                    lbl = QLabel(ch.unit)
                    hl.addWidget(txt)
                    hl.addWidget(lbl)
                    vl.addWidget(row)

                    # save the emitter from text box enter press
                    emitters[chname] = txt.returnPressedX
                
                if ch.mode == 'read' or ch.mode == 'both':
                    # add read channel
                    row2 = QFrame()
                    hl2 = QHBoxLayout()
                    hl2.setContentsMargins(0, 0, 0 ,0)
                    row2.setLayout(hl2)

                    txt2 = QLineEdit()
                    txt2.setDisabled(True)
                    lbl2 = QLabel(ch.unit)
                    hl2.addWidget(txt2)
                    hl2.addWidget(lbl2)
                    vl.addWidget(row2)

                    readboxes[chname] = { 'textbox' : txt2, 'channel' : ch }

                vbox.addWidget(gb)

            elif ch.data_type == bool:
                # need two radio buttons
                hbox = QHBoxLayout()
                gb.setLayout(hbox)
                rbOn = QRadioButtonX('On', ch)
                rbOff = QRadioButtonX('Off', ch)

                if ch.value == 0:
                    rbOff.toggle()
                elif ch.value == 1:
                    rbOn.toggle()
                emitters[chname] = rbOn.toggledX
                hbox.addWidget(rbOn)
                hbox.addWidget(rbOff)

                vbox.addWidget(gb)

        return readboxes, emitters
    
    def on_device_error(self, arduino_id, err_msg = 'Error'):
        """ Disable group box if server gives an error """ 
        if self._overview_devices[arduino_id]['groupbox'].isEnabled():
            self._overview_devices[arduino_id]['groupbox'].setEnabled(False)
            lblError = QLabel()
            lblError.setText('<font color="red">' + err_msg.split('ERROR: ')[1] + "</font>")
            self._overview_devices[arduino_id]['layout'].insertWidget(0, lblError)

    def on_device_working(self, arduino_id):
        """ Re-enable group box if server does not give an error """ 
        if not self._overview_devices[arduino_id]['groupbox'].isEnabled():
            self._overview_devices[arduino_id]['groupbox'].setEnabled(True)
            lbl = self._overview_devices[arduino_id]['layout'].takeAt(0)
            lbl.widget().deleteLater()

    def set_polling_rate(self, text):
        self.ui.lblServPoll.setText('Server polling rate: ' + text + ' Hz')

    def status_message(self, text):
        self._statusbar.showMessage(text)
        self._messagelog.append(time.strftime('[%Y-%m-%d %H:%M:%S] ', time.localtime()) + text)

    def show_PlotChooseDialog(self):
        devdict = {}
        for devname, data in self._overview_devices.items():
            devdict[devname] = data['device']

        _plotchoosedialog = PlotChooseDialog(devdict, self._plotted_channels)
        # dialog returns a tuple (bool, list), bool is true if closed via 'Done' button
        # list contains channel objects to be plotted
        accept, chs = _plotchoosedialog.exec_()
        if accept:
            # update plotted channels
            self._plotted_channels = {}
            for ch in chs:
                dev = ch.parent_device
                self._plotted_channels[(dev.name, ch.name)] = {'channel': ch, 
                                                               'curve': None,
                                                               'btnPin': None,
                                                               'color' : 'r'}
            self.update_plots()

    def update_plots(self):
        self.clearLayout(self._gbox)
        row = 0
        col = 0
        for names, data in self._plotted_channels.items():
            ch = data['channel']
            chbox = QGroupBox(ch.parent_device.label + " / " + ch.label)
            vbox = QVBoxLayout()
            chbox.setLayout(vbox)
            self._gbox.addWidget(chbox, row, col)
            #view = RemoteGraphicsView() #PlotWidget()
            pltBox = pg.PlotWidget()
            vbox.addWidget(pltBox)
            #vbox.addWidget(view)
            #pltBox = view.pg.PlotItem()
            #pltBox._setProxyOptions(deferGetattr=True) ## speeds up access
            #view.setCentralItem(pltBox)
            self._plotted_channels[(ch.parent_device.name, ch.name)]['curve'] = pltBox.plot(pen=data['color'])
            pinbutton = QPushButtonX('Pin', ch)
            self._plotted_channels[(ch.parent_device.name, ch.name)]['btnPin'] = pinbutton.clickedX
            vbox.addWidget(pinbutton)
            row += 1
            if row == 2:
                row = 0
                col += 1
        self.sig_plots_changed.emit(self._plotted_channels)

    def clearLayout(self ,layout):
        """ Removes all items from a QLayout """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

# ----- Custom Controls ----- #
class QLineEditX(QLineEdit):
    """ QLineEdit which returns a dict of channel info on returnPressed """
    returnPressedX = pyqtSignal(dict)

    def __init__(self, channel):
        super().__init__()
        self.ch = channel
        self.setText(str(self.ch.value))
        self.returnPressed.connect(self.on_return_pressed)

    @pyqtSlot()
    def on_return_pressed(self):
        try:
            value = self.ch.data_type(self.text()) #will fail here if input is bad
            if value != max(self.ch.lower_limit, min(value, self.ch.upper_limit)):
                raise ValueError('Value not within channel limits')
            data = {'channel': self.ch,
                    'value': value, 
                    'emitter':self.returnPressedX}
            self.returnPressedX.emit(data)
            self.setText(str(value))
        except:
            print("bad input")

class QPushButtonX(QPushButton):
    """ QPushButton which returns a dict of channel info on clicked """
    clickedX = pyqtSignal(tuple)

    def __init__(self, text, channel):
        super().__init__()
        self.ch = channel
        self.setText(text)
        self.clicked.connect(self.on_clicked)

    @pyqtSlot()
    def on_clicked(self):
        data = (self.ch.parent_device, self.ch)
        self.clickedX.emit(data)

class QRadioButtonX(QRadioButton):
    """ QRadioButton which returns a dict of channel info on toggled """
    toggledX = pyqtSignal(dict)

    def __init__(self, text, channel):
        super().__init__()
        self.ch = channel
        self.setText(text)
        self.toggled.connect(self.on_toggled)

    def on_toggled(self):
        value = float(self.isChecked())
        data = {'channel': self.ch,
                'value' : value,
                'emitted': self.toggledX}
        self.toggledX.emit(data)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()

    sys.exit(app.exec_())
