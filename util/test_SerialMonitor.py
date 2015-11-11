'''
Created on Sep 28, 2013

@author: rthomas
'''
import threading
import serial

class SerialThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run (self):
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=50)
        while 1:
            value = ser.readline()
            v = value.decode("utf-8").rstrip('\r\n')
            print(int(v))
            
SerialThread().start()
