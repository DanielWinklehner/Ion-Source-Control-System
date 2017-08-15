#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Thomas Wester <twester@mit.edu>
# Code adapted from MIST1ControlSystem.py (Python 2/gtk3+ version)
import time
import sys

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QPushButton, QTextEdit, QVBoxLayout, QWidget

from gui import MainWindow
from lib.Device import Device
from lib.Channel import Channel #, Procedure

class Listener(QObject):
    """ Gets info from server pipe & passes it to main thread, so that GUI updates are thread-safe """
    sig_status = pyqtSignal(str) # signal for sending status messages
    sig_done = pyqtSignal(str) # signal for process end
    sig_update = pyqtSignal(str) # signal for process update

    def __init__(self):
        super().__init__()
        self._terminate = False # flag to stop listening process

    @pyqtSlot()
    def listen(self):
        
        self.sig_status.emit('Listener started')
        """
        while True:
            # main code will go here
            self.sig_update.emit('test')
            app.processEvents()
            if self._terminate:
                self.sig_status.emit('Listener terminating...')
                break
        """
        #self.sig_done.emit('Listener done')

    def terminate(self):
        self.sig_status.emit('Listener received terminate signal')
        self._terminate = True

class ControlSystem(QWidget):
    def __init__(self, server_ip='127.0.0.1', server_port=80, debug=False):
        ## Set up Qt UI
        #self._app = QApplication(sys.argv)
        #self._window = MainWindow.MainWindow()
                
        super().__init__()

        self.setWindowTitle("Thread Example")
        form_layout = QVBoxLayout()
        self.setLayout(form_layout)
        self.resize(400, 800)

        self.button_start_threads = QPushButton()
        self.button_start_threads.clicked.connect(self.setup_communication_threads)
        form_layout.addWidget(self.button_start_threads)

        self.log = QTextEdit()
        form_layout.addWidget(self.log)

        QThread.currentThread().setObjectName('main')

        ##  Initialize RasPi server
        self.debug = debug
        self._server_url = 'http://{}:{}/'.format(server_ip, server_port)
        self.log.append('Initialization complete.')
        self._threads = None

    def setup_communication_threads(self):
        """ For each device, we create a thread to communicate with the corresponding Arduino. """
        self._threads = []
        # Create listener object, and start listener process
        # Also connect all Qt signals/slots
        listener = Listener()
        print('made listener')
        query_thread = QThread()
        self._threads.append((query_thread, listener))
        #query_thread.setObjectName('listener_thread')
        listener.moveToThread(query_thread)
        print('put listener on thread')
        listener.sig_update.connect(self.on_listener_update)
        listener.sig_status.connect(self.on_listener_status)
        query_thread.started.connect(listener.listen)
        print('connected slots')
        query_thread.start()
        print('started thread')
        self.log.append('Com started')

    @pyqtSlot(str)
    def on_listener_update(self, data):
        """ do something with thread message """
        print('listen update')
        print(data)
        self.log.append(data)

    @pyqtSlot(str)
    def on_listener_status(self, data):
        """ do something with thread message """
        print('listen status')
        print(data)
        self.log.append(data)

if __name__ == '__main__':
    app = QApplication([])
    cs = ControlSystem(server_ip='10.77.0.3', server_port=5000, debug=False)
    cs.show()
    sys.exit(app.exec_())
