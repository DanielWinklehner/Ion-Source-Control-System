## Testing PyQtGraph, to replace Matplotlib

import json
import time
from multiprocessing import Process, Pipe
import threading

import PyQt5
import pyqtgraph as pg
import requests
from collections import deque
import numpy as np

url = "http://10.77.0.3:5000/"

data = deque(maxlen=500)

def query_server(inpipe, server_url):
    print("listening...")
    dev_list = None
    while True:
        if inpipe.poll():
            message = inpipe.recv()
            #print(message)
            if message[0] == "device_or_channel_changed":
                dev_list = message[1]
        if dev_list is not None:
            _url = server_url + "device/query"
            _data = {'data': json.dumps(dev_list)}
            r = requests.post(_url, data=_data)
            #print(r.text)
            if r.text.strip() != r"{}":
                parsed_response = json.loads(r.text)
                inpipe.send(["query_response", parsed_response])
        time.sleep(0.05)

def listen_to_pipe(inpipe):
    while True:
        if inpipe.poll():
            message = inpipe.recv()
            val = message[1]['95432313837351706152']['v2']
            data.append(val)
            update_plot()
            #print(data)
    time.sleep(0.05)

app = pg.QtGui.QApplication([])
win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')

pg.setConfigOptions(antialias=True)
plt = win.addPlot(title="Updating plot")
curve = plt.plot(pen='r')


def update_plot():
        global curve, data, plt
        xs = np.arange(0, len(data))
        curve.setData(xs,data)
        app.processEvents()

if __name__=="__main__":

    try:
        r = requests.get(url + "initialize/")

        if r.status_code != 200:
            exit()
        else:
            print(r.text)
    except Exception as e:
        print(e)
        exit()

    r = requests.get(url + "device/active/")

    listen_pipe, com_pipe = Pipe()

    dev_list = [ {'device_driver': 'Arduino', 
                  'device_id': '95432313837351706152',
                  'locked_by_server': False,
                  'channel_ids': ['v2', 'v1', 'i2', 'i1'],
                  'precisions': [2, 2, 2, 2],
                  'values': [None, None, None, None],
                  'data_types': ["<class 'float'>", "<class 'float'>", "<class 'float'>", "<class 'float'>"]}]

    listen_pipe.send(["device_or_channel_changed", dev_list])

    proc = Process(target=query_server, args=(com_pipe, url))
    proc.start()

    query_thread = threading.Thread(target=listen_to_pipe, args=(listen_pipe,))
    query_thread.start()
    

    app.exec_()
