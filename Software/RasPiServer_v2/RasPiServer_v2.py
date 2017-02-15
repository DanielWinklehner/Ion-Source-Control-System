# import os
import time
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Process, Pipe, Manager
from flask import Flask, request
from flask_classy import FlaskView, route
import subprocess
import threading
import json

# --- This is a nice implementation of a simple timer I found online -DW --- #
_tm = 0


def stopwatch(msg=''):
    tm = time.time()
    global _tm
    if _tm == 0:
        _tm = tm
        return
    print("%s: %.2f ms" % (msg, 1000.0 * (tm - _tm)))
    _tm = tm
# ------------------------------------------------------------------------- #


def serial_watchdog(com_pipe, debug):
    """
    Function to be called as a process. Watches the serial ports and looks for devices plugged in
    or removed.
    Underscore at beginning prevents flask_classy from making it a route in the Flask server.
    :param com_pipe: this end of the pipe to communicate with main server process.
    :param debug: Flag whether or not debugging should be turned on.
    :return:
    """
    _keep_communicating2 = True
    _com_freq = 2.0  # (Hz)
    _com_period = 1.0 / _com_freq  # (s)
    _debug = debug

    _current_ports_by_ids = {}
    _new_ports_by_ids = {}

    while _keep_communicating2:

        # Do the timing of this process:
        _thread_start_time = time.time()

        if com_pipe.poll():

            _in_message = com_pipe.recv()

            if _in_message[0] == "com_period":
                _com_period = _in_message[1]

            if _in_message[0] == "shutdown":
                break

        # Find the serial ports and whether they belong to an arduino
        # TODO: This takes a very long time, is there a faster way?
        proc = subprocess.Popen('/home/mist-1/Work/ControlSystem/usb.sh',
                                stdout=subprocess.PIPE, shell=True)

        output = proc.stdout.read().strip()

        _device_added = False
        _device_removed = False
        _device_ids = _current_ports_by_ids.keys()

        # Loop through all found devices and add them to a new list, remove them from the current list
        for line in output.split("\n"):

            if "Arduino" in line:

                port, raw_info = line.split(" - ")
                serial_number = raw_info.split("_")[-1]

                _new_ports_by_ids[serial_number] = port

                if serial_number not in _device_ids:
                    _device_added = True
                else:
                    del _current_ports_by_ids[serial_number]

        # Now, let's check if there are any devices still left in the current dict
        if len(_current_ports_by_ids) > 0:
            _device_removed = True

        _current_ports_by_ids = _new_ports_by_ids
        _new_ports_by_ids = {}

        if _debug:
            if _device_removed:
                print("Arduino(s) were removed")
            if _device_added:
                print("Arduino(s) were added")

        if _device_added or _device_removed:

            if _debug:
                print("Updated List:")
                for key, item in _current_ports_by_ids.items():
                    print ("Arduino {} at port {}".format(key, item))

            # Reverse ports_by_ids:
            _current_ids_by_ports = {}
            for myid, myport in _current_ports_by_ids.items():
                _current_ids_by_ports[myport] = myid

            pipe_message = ["updated_list", _current_ports_by_ids, _current_ids_by_ports]
            com_pipe.send(pipe_message)
            # _ports_by_ids = _current_ports_by_ids
            # _ids_by_ports = _current_ids_by_ports

        # Do the timing of this process:
        _sleepy_time = _com_period - time.time() + _thread_start_time

        if _sleepy_time > 0.0:

            if _debug:
                print("Watchdog alive, sleeping for {} s.".format(_sleepy_time))

            time.sleep(_sleepy_time)


class ServerView(FlaskView):
    def __init__(self):
        self._debug = False

        # A pool of threads to communicate with the arduinos
        self._threadpool = ThreadPool(10)

        self._welcome_message = "Hi, this is the MIST-1 Control System server running on a RasPi."

        self._pipe_server, pipe_serial_watcher = Pipe()

        # self._manager = Manager()
        # self._ports_by_ids = self._manager.dict()
        # self._ids_by_ports = self._manager.dict()

        self._watch_proc = Process(target=serial_watchdog, args=(pipe_serial_watcher,
                                                                 self._debug,))
        self._watch_proc.daemon = True

        # self._watchdog_thread = None

        self._keep_communicating = False
        self._initialized = False

        # TODO: Add another Pipe/Process combo for displaying stuff on our new display

    def kill(self):
        """
        Shutdown routine.
        :return:
        """
        print("Shutting Down!")

        self._keep_communicating = False

        self._threadpool.terminate()
        self._threadpool.join()

        if self._watch_proc.is_alive():

            self._watch_proc.terminate()
            self._watch_proc.join()

        else:

            print("Watchdog already dead.")

        func = request.environ.get('werkzeug.server.shutdown')

        if func is None:

            raise RuntimeError('Not running with the Werkzeug Server')

        func()

        return "Shutting down..."

    @route("/device/all/")
    def all_devices(self):

        return json.dumps(self._ports_by_ids.copy())

    def initialize(self):

        if self._initialized:

            return "Server has already been initialized"

        else:

            self._keep_communicating = True

            threading.Timer(0.1, self._listen_to_pipe).start()
            # self._watchdog_thread = threading.Thread(target=self._listen_to_pipe)
            # self._watchdog_thread.start()

            time.sleep(0.2)

            response = self._start_watchdog()

            self._initialized = True

            return "Initializing Control System RasPi server services...{}".format(response)

    def hello(self):

        return self._welcome_message

    def _start_watchdog(self):

        if not self._watch_proc.is_alive():

            self._watch_proc.start()

            return "Started the watchdog process."

        else:

            return "There was already a watchdog process running!"

    def _listen_to_pipe(self):

        if self._pipe_server.poll():

            gui_message = self._pipe_server.recv()

            if gui_message[0] == "updated_list":

                if self._debug:
                    print("Updating ports/ids in main server")

                self._ports_by_ids = gui_message[1]
                self._ids_by_ports = gui_message[2]

                print(self._ports_by_ids)
                print(self._ids_by_ports)

        if self._keep_communicating:
            threading.Timer(1.0, self._listen_to_pipe).start()


if __name__ == "__main__":

    app = Flask(__name__)
    # server = ServerView()
    ServerView.register(app)
    app.run(host='0.0.0.0', port=5000)
