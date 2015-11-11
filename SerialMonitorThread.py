'''
Created on Sep 26, 2013

@author: rthomas
'''
import threading
import serial

class SerialMonitorThread(threading.Thread):

    def __init__(self, serialPort):
        threading.Thread.__init__(self)
        print("SerialMonitorThread created: " + str(serial))
        self.serialPort = serialPort
        self.dataIn = ""
        self.dataOut = ""
    
    def run(self):
        print("SerialMonitorThread Thread is Running.")
#         self.data = self.serialPort.read(1)
        while True:
            nIn = self.serialPort.inWaiting()
            if nIn:
                self.dataIn = self.dataIn + self.serialPort.read(nIn)
#                 print("StreamInData: " + str(self.dataIn))
            elif len(self.dataOut):
                nOut = self.serialPort.write(self.dataOut)
                self.dataOut = self.dataOut[nOut:]

    def readData(self, count):
        chunk = self.dataIn[:count]
        self.dataIn = self.dataIn[len(chunk):]
        return chunk

    def writeData(self, data):
        self.dataOut = data
          
    def kill ( self ):
        if self.isAlive():
            del self