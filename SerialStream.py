#!/usr/bin/env python
# encoding: utf-8
'''
SerialStream -- shortdesc

SerialStream is a description

It defines classes_and_methods

@author:     Ryan Thomas
            
@copyright:  2013 Ryan Thomas. All rights reserved.
            
@license:    undetermined

@contact:    rathomas.mobile@gmail.com
@deffield    updated: Updated
'''

from rpyc.core.stream import Stream
import sys
from rpyc.lib.compat import BYTES_LITERAL, maxint
import time


class SerialStream(Stream):
    """A stream over serial connection - pyserial"""
    
#     MAX_IO_CHUNK = 200
    MAX_IO_CHUNK = 2000
#     MAX_IO_CHUNK = 32000
    
    def __init__(self, serial):
        print("SerialStream created: " + str(serial))
        
        self.data = None
        self.serial = serial
        
#         if self.serial:
#             self.serialThread = SerialMonitorThread(self.serial)
#             self.serialThread.start()
#         else:
#             self.close()
        if not self.serial:
            self.close()
        
    @property
    def closed(self):
        return not self.serial.isOpen()
    
    def close(self):
        if self.serial:
            self.serial.close()
    
    def fileno(self):
        return self.serial.fileno()
    
    def read(self, count):
        data = []
        try:
            while count > 0:
                
                buf = self.serial.read(min(self.MAX_IO_CHUNK, count))
#                 print("read: " + str(buf))
                if not buf:
                    return
#                     raise EOFError("connection closed by peer")
                data.append(buf)
                count -= len(buf)
        except EOFError:
            self.close()
            raise
        except EnvironmentError:
            ex = sys.exc_info()[1]
            self.close()
            raise EOFError(ex)
        return BYTES_LITERAL("").join(data)
    
    def poll(self, timeout, interval = 0.01):
        self.serial.timeout = timeout
        if timeout is None:
                timeout = maxint
        length = 0
        tmax = time.time() + timeout
        try:
            while length == 0:
                length = self.serial.inWaiting()
                if time.time() >= tmax:
                    break
                time.sleep(interval)
        except TypeError:
            ex = sys.exc_info()[1]
            if not self.closed:
                raise
            raise EOFError(ex)
        return length != 0
      
    def write(self, data):
        try:
            while data:
                chunk = data[:self.MAX_IO_CHUNK]
                written = self.serial.write(chunk)
#                 print("write: " + str(chunk))
                data = data[written:]
        except EnvironmentError:
            ex = sys.exc_info()[1]
            self.close()
            raise EOFError(ex)
    
    def __del__(self):
        if self.serial:
            self.serial.close()       
#   
