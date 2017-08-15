#!/usr/bin/env python
import time
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QGroupBox, QTextEdit, QFrame, QLabel, QRadioButton, QScrollArea

from .ui_MainWindow import Ui_MainWindow
from lib.Device import Device
from lib.Channel import Channel

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # aliases
        self._statusbar = self.ui.statusBar
        self._messagelog = self.ui.txtMessageLog
        self._overview = self.ui.fmOverview
        self._pinnedplot = self.ui.pltPinned
        self._tabview = self.ui.tabMain
        self._btnquit = self.ui.btnQuit

        self._current_tab = 'main'
        self._tabview.currentChanged.connect(self.tab_changed)

        ## set up containers
        self._hbox = QHBoxLayout()
        self._overview.setLayout(self._hbox) 

        #self._overview_scroll_area = QScrollArea()
        #self._overview_scroll_area.setWidget(self._overview)

        #self._hbox.addWidget(self._overview_scroll_area)
        #self._overview_scroll_area.setWidget(self._overview)

        ## remove the temporary rate label
        self.ui.label_2.deleteLater()
        self._overview_devices = []

    def tab_changed(self):
        tabName = self._tabview.tabText(self._tabview.currentIndex())
        if tabName == 'Overview':
            self._current_tab = 'main'
        elif tabName == 'Devices':
            self._current_tab = 'devices'

    def add_device_to_overview(self, device):
        #if device in self._overview_devices:
        #    return

        self._overview_devices.append(device)
        
        # create group box for this device, add it to overview frame
        devbox = QGroupBox(device.label)
        devbox.setMinimumSize(250, 300)
        devbox.setMaximumWidth(250)
        self._hbox.addWidget(devbox)

        vbox = QVBoxLayout()
        devbox.setLayout(vbox)

        for chname, ch in reversed(sorted(device.channels.items(), key=lambda x: x[1].display_order)):
            # create frame for channel info
            fm = QGroupBox(ch.label)
            hbox = QHBoxLayout()
            fm.setLayout(hbox)
            if ch.data_type == float:
                txt = QTextEdit(str(ch.value))
                lbl = QLabel(ch.unit)
                hbox.addWidget(txt)
                hbox.addWidget(lbl)
            elif ch.data_type == bool:
                rbOn = QRadioButton('On')
                rbOff = QRadioButton('Off')

                if ch.value == 0:
                    rbOff.toggle()
                elif ch.value == 1:
                    rbOn.toggle()
                hbox.addWidget(rbOn)
                hbox.addWidget(rbOff)

            vbox.addWidget(fm)

    def set_polling_rate(self, text):
        self.ui.lblServPoll.setText('Server polling rate: ' + text + ' Hz')

    def status_message(self, text):
        self._statusbar.showMessage(text)
        self._messagelog.append(time.strftime('[%Y-%m-%d %H:%M:%S] ', time.localtime()) + text)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()

    sys.exit(app.exec_())
