#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Handles widget creation in the main window

import time
import copy
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, \
                            QGroupBox, QLineEdit, QFrame, QLabel, \
                            QRadioButton, QScrollArea, QPushButton, \
                            QWidget, QSizePolicy, QAction, QTreeWidgetItem, \
                            QComboBox
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QIcon

import pyqtgraph as pg

from .ui_MainWindow import Ui_MainWindow
from .dialogs.AboutDialog import AboutDialog
from .dialogs.ErrorDialog import ErrorDialog
from lib.Device import Device
from lib.Channel import Channel
from lib.Procedure import Procedure

class MainWindow(QMainWindow):

    # signal to be emitted when device/channel is changed
    sig_device_channel_changed = pyqtSignal(object, dict)

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

        # add a right-aligned About tool bar button
        spc = QWidget()
        spc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        spc.setVisible(True)
        self.ui.toolBar.addWidget(spc)
        self._btnAbout = QAction('About', None)
        self.ui.toolBar.addAction(self._btnAbout)

        # icons
        self._btnquit.setIcon(QIcon(QPixmap('gui/images/icons/process-stop.png')))
        self._btnAbout.setIcon(QIcon(QPixmap('gui/images/icons/help-browser.png')))
        self.ui.btnExpand.setIcon(QIcon(QPixmap('gui/images/icons/list-add.png')))
        self.ui.btnCollapse.setIcon(QIcon(QPixmap('gui/images/icons/list-remove.png')))

        # dialog connection
        self._btnAbout.triggered.connect(self.show_AboutDialog)

        # tab changes
        self._current_tab = 'main'
        self._tabview.currentChanged.connect(self.tab_changed)

        ## set up containers
        self._overview_layout = QHBoxLayout()
        self._overview.setLayout(self._overview_layout)
        self._overview_layout.addStretch()

        self._plot_layout = QGridLayout()
        self._plots.setLayout(self._plot_layout)

        # settings page
        self.ui.treeDevices.setHeaderLabels(['Label', 'Type'])
        self.ui.treeDevices.currentItemChanged.connect(self.on_settings_row_changed)
        self.ui.btnExpand.clicked.connect(self.ui.treeDevices.expandAll)
        self.ui.btnCollapse.clicked.connect(self.ui.treeDevices.collapseAll)
        self._devvbox = QVBoxLayout()
        self.ui.fmDeviceSettings.setLayout(self._devvbox)

        # local copies of data
        self._settings_devices = {}

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

    # ---- Tab Update Functions ----
    def update_overview(self, devices):
        self.clearLayout(self._overview_layout)
        for device_name, device in devices.items():
            if 'overview' in device.pages:
                self._overview_layout.insertWidget(0, device._overview_widget)
        self._overview_layout.addStretch()

    def update_plots(self, devices, plotted_channels):
        """ Draw the plotted channels, as specified by the PlotChooseDialog """
        self.clearLayout(self._plot_layout)
        row = 0
        col = 0
        for device_name, device in devices.items():
            for channel_name, channel in device.channels.items():
                if channel._plot_widget is not None and channel.data_type == float and channel in plotted_channels:
                    self._plot_layout.addWidget(channel._plot_widget, row, col)
                    row += 1
                    if row == 2:
                        row = 0
                        col += 1

    def update_device_settings(self, devices):
        """ Populates the treeview on the devices tab """
        self.ui.treeDevices.clear()
        for device_name, device in devices.items():
            devrow = QTreeWidgetItem(self.ui.treeDevices)
            devrow.setText(0, device.label)
            devrow.setText(1, 'Device')
            self._settings_devices[device.name] = {'device': device, 'row': devrow, 'channels': {}}
            for chname, ch in reversed(sorted(device.channels.items(), key=lambda x: x[1].display_order)):
                chrow = QTreeWidgetItem(devrow)
                chrow.setText(0, ch.label)
                chrow.setText(1, 'Channel')
                self._settings_devices[device.name]['channels'][ch.name] = {'channel': ch, 'row': chrow}
            newchrow = QTreeWidgetItem(devrow)
            newchrow.setText(0, '[Add a new Channel]')
            #newchrow.setText(1, 'Channel')

        newdevrow = QTreeWidgetItem(self.ui.treeDevices)
        newdevrow.setText(0, '[Add a new Device]')
        #newdevrow.setText(1, 'Device')

        self.ui.treeDevices.expandAll()

    def update_procedures(self, procedures):
        # Add procedures to the procedures tab
        self.clearLayout(self.ui.vboxProcedures)
        for procedure_name, procedure in procedures.items():
            self.ui.vboxProcedures.addWidget(procedure._widget)
        self.ui.vboxProcedures.addStretch()

    # ---- Settings page functions ----
    def on_settings_row_changed(self, item):
        """ Creates the edit controls when selecting rows in the tree view """
        if item == None:
            # if nothing is selected, do nothing
            return

        self.clearLayout(self._devvbox)
        # recover the associated object to change
        obj = None
        parent = None

        for device_name, device_data in self._settings_devices.items():
            # are we editing an existing device/channel?
            if device_data['row'] == item:
                obj = device_data['device']
                break
            else:
                for channel_name, channel_data in device_data['channels'].items():
                    if channel_data['row'] == item:
                        obj = channel_data['channel']
                        parent = device_data['device']
                        break

        if (obj, parent) == (None, None):
            # adding a new device or channel
            if 'channel' in item.text(0).lower():
                for device_name, device_data in self._settings_devices.items():
                    if device_data['row'] == item.parent():
                            parent = device_data['device']
                            break


        if parent is None:
            # set up device entry form
            title = ''
            if obj is not None:
                title = obj.label
            else:
                title = 'New Device'

            lblTitle = QLabel(title)
            font = QFont()
            font.setPointSize(14)
            lblTitle.setFont(font)
            self._devvbox.addWidget(lblTitle)
            gbox = QGridLayout()

            property_list = sorted([(name, x) for name, x in Device.user_edit_properties().items()], 
                                   key=lambda y: y[1]['display_order'])

            for i, prop in enumerate(property_list):
                lbl = QLabel(prop[1]['display_name'])
                gbox.addWidget(lbl, i, 0)

                if obj is not None:
                    val = getattr(obj, prop[0])
                else:
                    val = ''
                    
                if prop[0] != 'driver':
                    txt = QLineEdit(val)
                    gbox.addWidget(txt, i, 1)
                else:
                    cb = QComboBox()
                    driver_list = Device.driver_list()
                    cb.addItems(driver_list)
                    gbox.addWidget(cb, i, 1)
                    if val != '':
                        cb.setCurrentIndex(driver_list.index(val))
                    else:
                        cb.setCurrentIndex(0)

            self._devvbox.addLayout(gbox)

            hbox = QHBoxLayout()
            hbox.addStretch()

            if obj is not None:
                btnSave = QPushButtonObj('Save Changes', obj)
            else:
                btnSave = QPushButtonObj('Save Changes', 'device')
            btnSave.clicked_.connect(self.on_save_changes_click)
            hbox.addWidget(btnSave)
            hbox.addStretch()

            self._devvbox.addLayout(hbox)

            self._devvbox.addStretch()

            if obj is not None:
                hbox = QHBoxLayout()
                hbox.addStretch()
                btnDel = QPushButtonObj('Delete Device', obj)
                hbox.addWidget(btnDel)
                hbox.addStretch()
                self._devvbox.addLayout(hbox)
                
        else:
            # set up channel entry form
            title = '{}/{}'.format(parent.label,'New Channel')
            if obj is not None:
                title = '{}/{}'.format(obj.parent_device.label, obj.label)
            lblTitle = QLabel(title)
            font = QFont()
            font.setPointSize(14)
            lblTitle.setFont(font)
            self._devvbox.addWidget(lblTitle)
            gbox = QGridLayout()

            property_list = sorted([(name, x) for name, x in Channel.user_edit_properties().items()], 
                                   key=lambda y: y[1]['display_order'])


            for i, prop in enumerate(property_list):
                lbl = QLabel(prop[1]['display_name'])
                gbox.addWidget(lbl, i, 0)

                if obj is not None:
                    val = getattr(obj, prop[0])
                else:
                    val = ''
                    
                if prop[0] == 'data_type':
                    cb = QComboBox()
                    type_list = ['Float', 'Bool', 'Int']
                    cb.addItems(type_list)
                    gbox.addWidget(cb, i, 1)
                    if val != '':
                        cb.setCurrentIndex(type_list.index(str(val).split("'")[1].title()))
                    else:
                        cb.setCurrentIndex(0)
                elif prop[0] == 'mode':
                    cb = QComboBox()
                    mode_list = ['Read', 'Write', 'Both']
                    cb.addItems(mode_list)
                    gbox.addWidget(cb, i, 1)
                    if val != '':
                        cb.setCurrentIndex(mode_list.index(val.title()))
                    else:
                        cb.setCurrentIndex(0)

                else:
                    txt = QLineEdit(str(val))
                    gbox.addWidget(txt, i, 1)


            self._devvbox.addLayout(gbox)

            hbox = QHBoxLayout()
            hbox.addStretch()
            if obj is not None:
                btnSave = QPushButtonObj('Save Changes', obj)
            else:
                btnSave = QPushButtonObj('Save Changes', ('channel', parent))
            btnSave.clicked_.connect(self.on_save_changes_click)
            hbox.addWidget(btnSave)
            hbox.addStretch()

            self._devvbox.addLayout(hbox)

            self._devvbox.addStretch()
            if obj is not None:
                hbox = QHBoxLayout()
                hbox.addStretch()
                btnDel = QPushButtonObj('Delete Channel', obj)
                hbox.addWidget(btnDel)
                hbox.addStretch()
                self._devvbox.addLayout(hbox)

    def on_save_changes_click(self, obj):
        newobj = None
        newvals = {}
        if isinstance(obj, Device) or (isinstance(obj, str) and 'device' in obj.lower()):
            # TODO This is hard-coded to avoid passing references to all the controls around
            # probably not the best solution.

            # order is: name, arduino_id, label -> (1, 3, 5)
            gbox = self._devvbox.itemAt(1).layout()

            property_list = sorted([(name, x) for name, x in Device.user_edit_properties().items()], 
                                   key=lambda y: y[1]['display_order'])
            
            if isinstance(obj, Device):
                # we are modifying a device
                newobj = obj
                newvals = {}
                for i, prop in enumerate(property_list):
                    if prop[0] != 'driver':
                        val = gbox.itemAt(2 * i + 1).widget().text()
                    else:
                        val = gbox.itemAt(2 * i + 1).widget().currentText()
                    newvals[prop[0]] = val
            else:
                # we are adding a new device. No need to set newvals
                newobj = Device()
                for i, prop in enumerate(property_list):
                    if prop[0] != 'driver':
                        setattr(newobj, prop[0], gbox.itemAt(2 * i + 1).widget().text())
                    else:
                        setattr(newobj, prop[0], gbox.itemAt(2 * i + 1).widget().currentText())

        else:
            gbox = self._devvbox.itemAt(1).layout()

            property_list = sorted([(name, x) for name, x in Channel.user_edit_properties().items()], 
                                   key=lambda y: y[1]['display_order'])
            
            types = {'Float': float, 'Int': int, 'Bool': bool}

            if isinstance(obj, Channel):
                # modifying a channel. Set newobj and newvals
                newobj = obj
                newvals = {}
                for i, prop in enumerate(property_list):
                    if prop[0] not in ['mode', 'data_type']:
                        val = gbox.itemAt(2 * i + 1).widget().text()
                        if prop[0] in ['upper_limit', 'lower_limit']:
                            try: 
                                val = obj.data_type(val)
                            except:
                                print('bad values for limits')
                                return
                        elif prop[0] == 'display_order':
                            try:
                                val = int(val)
                            except:
                                print('display_order must be an int')
                                return
                        elif prop[0] == 'scaling':
                            try:
                                val = float(val)
                            except:
                                print('scaling must be a float')
                                return
                    else:
                        val = gbox.itemAt(2 * i + 1).widget().currentText()
                        if prop[0] == 'data_type':
                            val = types[val]
                    newvals[prop[0]] = val
            else:
                # adding a new channel, only set newobj
                newobj = Channel()
                for i, prop in enumerate(property_list):
                    if prop[0] not in ['mode', 'data_type']:
                        val = gbox.itemAt(2 * i + 1).widget().text()
                        if prop[0] in ['upper_limit', 'lower_limit']:
                            pass
                        elif prop[0] == 'display_order':
                            try:
                                val = int(val)
                            except:
                                print('display_order must be an int')
                                return
                        elif prop[0] == 'scaling':
                            try:
                                val = float(val)
                            except:
                                print('scaling must be a float')
                                return
                    else:
                        val = gbox.itemAt(2 * i + 1).widget().currentText()
                        if prop[0] == 'data_type':
                            val = types[val]
                    setattr(newobj, prop[0], val)

                parent = obj[1] # if we are here, we are passed a tuple with the parent device
                newobj.parent_device = parent

        self.clearLayout(self._devvbox)
        self.sig_device_channel_changed.emit(newobj, newvals)

    # ---- Misc functions ---
    def show_AboutDialog(self):
        _aboutdialog = AboutDialog()
        _aboutdialog.exec_()

    @pyqtSlot()
    def show_ErrorDialog(self, error_message='Error'):
        _errordialog = ErrorDialog(error_message)
        _errordialog.exec_()

    def set_polling_rate(self, text):
        self.ui.lblServPoll.setText('Server polling rate: ' + text + ' Hz')

    def status_message(self, text):
        self._statusbar.showMessage(text)
        self._messagelog.append(time.strftime('[%Y-%m-%d %H:%M:%S] ', time.localtime()) + text)

    def clearLayout(self, layout):
        """ Removes all widgets from a QLayout. Does not delete the widget """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
            elif child.layout():
                self.clearLayout(child)

# ----- Custom Controls ----- #
class QPushButtonObj(QPushButton):
    """ QPushButton which returns an object on click """
    clicked_ = pyqtSignal(object)

    def __init__(self, text, obj):
        super().__init__()
        self.obj = obj
        self.setText(text)
        self.clicked.connect(self.on_clicked)

    @pyqtSlot()
    def on_clicked(self):
        self.clicked_.emit(self.obj)
