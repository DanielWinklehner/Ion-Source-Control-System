#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Thomas Wester <twester@mit.edu>
#
# GUI for running the emittance scanners

import sys
import socket
import select
import time
import timeit
import queue
from collections import deque

import numpy as np

from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QFileDialog

from gui import MainWindow

class CouldNotConnectError(Exception):
    pass

class Comm(QObject):

    sig_poll_rate = pyqtSignal(float)
    sig_data = pyqtSignal(bytes)
    sig_done = pyqtSignal() # emit if shutting down because of error

    def __init__(self, server_ip, server_port):
        super().__init__()

        self._ip = server_ip
        self._port = server_port

        self._buffer = 1024

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(1)

        self._polling_rate = 60 # Hz, 2 x the receive rate

        self._command_queue = queue.Queue()

        # try to connect to the server
        try:
            self._socket.connect((self._ip, self._port))
        except socket.error:
            raise CouldNotConnectError
            return

        self._terminate = False

    @property
    def server_ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    def poll(self):
        # send poll command or read from server if there is data
        recv = True # true if OK to send new info to server, false if waiting
        pollcount = 0
        sleep_time = 1. / self._polling_rate
        while not self._terminate:
            loop_start = timeit.default_timer()

            if recv:
                if pollcount == 0:
                    start_time = timeit.default_timer()

                # send any messages in the queue to the server
                if not self._command_queue.empty():
                    try:
                        cmd = self._command_queue.get_nowait()
                    except socket.timeout:
                        print('timeout')
                    self._socket.send(cmd.encode())
                    continue

                # otherwise just send a poll request
                try:
                    self._socket.send(b'poll')
                except socket.timeout:
                    print('timeout')

            ready = select.select([self._socket], [], [], 0)[0]
            if ready:
                data = self._socket.recv(self._buffer)
                if not data:
                    self.sig_done.emit()
                    self._terminate = True
                    break

                self.sig_data.emit(data)
                recv = True
                pollcount += 1
                if pollcount == 5:
                    rate = 5./ (timeit.default_timer() - start_time)
                    self.sig_poll_rate.emit(rate)
                    pollcount = 0
            else:
                recv = False

            net_sleep = sleep_time - (timeit.default_timer() - loop_start)
            if net_sleep > 0:
                time.sleep(net_sleep)

    def terminate(self):
        self._terminate = True

class DaqView(QObject):

    sig_connected = pyqtSignal()
    sig_disconnected = pyqtSignal()

    def __init__(self):
        self._window = MainWindow.MainWindow()
        self._window.btnConnect.clicked.connect(self.connect_to_server)

        self._window.ui.btnVStepTest.clicked.connect(self.test_stepper)

        self._values = {'vol': 0.0, 'ver': 0.0, 'hor': 0.0, 'cur': 0.0}
        self._deques = {'vol': deque(maxlen=10), 'ver': 0.0, 'hor': 0.0, 'cur': deque(maxlen=5)}

        # set up main device dictionary
        device_name_list = ['pico', 'vstepper', 'hstepper', 'vreg']
        self._devices = dict()

        for name in device_name_list:
            self._devices[name] = {'value': 0.0,
                                   'deque': deque(maxlen=10),
                                   'hasErr': False,
                                   'label': None,
                                   'name': '',
                                   'unit': '',
                                   'status': '',
                                   'fmt': '{0:.2f}',
                                   }

        # manually assign labels & properties to each device
        self._devices['pico']['label'] = self._window.lblCur
        self._devices['vstepper']['label'] = self._window.lblVer
        self._devices['hstepper']['label'] = self._window.lblHor
        self._devices['vreg']['label'] = self._window.lblV

        self._devices['pico']['name'] = 'Current'
        self._devices['vstepper']['name'] = 'Vertical'
        self._devices['hstepper']['name'] = 'Horizontal'
        self._devices['vreg']['name'] = 'Voltage'

        self._devices['pico']['unit'] = 'A'
        self._devices['vstepper']['unit'] = 'cm'
        self._devices['hstepper']['unit'] = 'cm'
        self._devices['vreg']['unit'] = 'kV'

        # exceptions to default values
        self._devices['pico']['fmt'] = '{0:.4e}'
        self._devices['vstepper']['status'] = 'Not calibrated'
        self._devices['hstepper']['status'] = 'Not calibrated'

        self._vercalib = False
        self._horcalib = False

        self._com_thread = QThread()

        self.update_display_values()

    def test_stepper(self):
        rnd = np.random.normal(250000, 100000)
        msg = 'vmove {}'.format(int(rnd))
        self._comm._command_queue.put(msg)

    def connect_to_server(self):

        if self._window.btnConnect.text() == 'Stop':
            self.shutdown_communication()
            return

        try:
            server_ip = self._window.txtIp.text()
            socket.inet_aton(server_ip)
        except socket.error:
            self._window.lblServerMsg.show()
            self._window.lblServerMsg.setText('Invalid IP entered!')
            return

        try:
            server_port = int(self._window.txtPort.text())
        except ValueError:
            self._window.lblServerMsg.show()
            self._window.lblServerMsg.setText('Invalid port entered!')
            return

        try:
            self._comm = Comm(server_ip, server_port)
        except CouldNotConnectError:
            self._window.lblServerMsg.show()
            self._window.lblServerMsg.setText('Could not connect to server!')
            return

        self._comm.sig_poll_rate.connect(self.on_poll_rate)
        self._comm.sig_data.connect(self.on_data)
        self._comm.sig_done.connect(self.shutdown_communication)
        self._comm.moveToThread(self._com_thread)
        self._com_thread.started.connect(self._comm.poll)
        self._com_thread.start()
        self._window.lblServerMsg.hide()

        self._window.statusBar.showMessage(
                'Server connection at {}:{} started.'.format(
                self._comm.server_ip, self._comm.port))

        self._window.btnConnect.setText('Stop')
        self._window.tabCalib.setEnabled(True)

    def shutdown_communication(self):
        self._comm.terminate()
        self._com_thread.quit()

        self._window.statusBar.showMessage(
                'Server connection at {}:{} closed.'.format(
                self._comm.server_ip, self._comm.port))

        # reset gui elements
        self._window.btnConnect.setText('Connect')
        self._window.tabCalib.setEnabled(False)
        self._window.tabScan.setEnabled(False)

    def on_poll_rate(self, rate):
        self._window.lblPollRate.setText('Polling rate: {0:.2f} Hz'.format(rate))

    def on_data(self, data):
        data = data.decode("utf-8")
        cur, ver, hor, vol = [float(x) if x != 'ERR' \
                                else 'ERR' for x in data.split(' ')]

        self._devices['pico']['value'] = cur
        self._devices['vstepper']['value'] = ver
        self._devices['hstepper']['value'] = hor
        self._devices['vreg']['value'] = vol

        for device_name, info in self._devices.items():
            if info['value'] == 'ERR':
                info['hasErr'] = True
            else:
                info['hasErr'] = False
                info['deque'].append(
                        info['value']
                    )

        self.update_display_values()

    def update_display_values(self):

        for device_name, info in self._devices.items():
            if info['hasErr']:
                info['label'].setText('{0}: Error!'.format(info['name']))
            else:
                info['label'].setText('{0}: {1} {2} {3}'.format(
                        info['name'], info['fmt'].format(info['value']),
                        info['unit'], '(%s)' % (info['status']) if \
                            info['status'] != '' else ''
                    )
                )

    def run(self):
        self._window.show()

if __name__ == '__main__':
    app = QApplication([])

    dq = DaqView()
    dq.run()
    sys.exit(app.exec_())
