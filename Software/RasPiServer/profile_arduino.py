import SerialCOM
import serial
import time

import multiprocessing

from multiprocessing.dummy import Pool as ThreadPool




def test_without_thread(port, msg):
    ser = serial.Serial(port, baudrate=115200, timeout=1.)


    for i in range(10):
        ser.write(msg)
        print i, ser.readline().strip("\r\n")



def test_with_thread(port, msg):
    
    
    def mp_worker(args):
        port, messages = args

        for msg in messages:
            try:
                ser = serial.Serial(port, baudrate=115200, timeout=1.)
                for i in range(10):
                    ser.write(msg)
                    print i, ser.readline().strip("\r\n")
            except Exception as e:
                print "Something went wrong! I'm sorry!", e
    
    machines = [(port, [msg])]    

    try:
        p = ThreadPool(processes=1)
        p.map(mp_worker, machines)
    finally:
        p.close()
        p.join()


if __name__ == "__main__":
        
    msg = "i"
    port = "/dev/ttyACM2"

    print "Without Threading:"
    test_without_thread(port, msg)

    print "\n With Threading:"
    test_with_thread(port, msg)