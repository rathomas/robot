'''
Created on Oct 4, 2013

@author: rthomas
'''
from SerialStream import SerialStream
from ExecutableCommandLineService import ExecutableCommandLineService
import rpyc
from RobotConfig import XBEE_INTERFACES
import serial
import datetime
from RobotTestService import RobotTestService

class main:
    def __init__(self):
        self.remote = None
        self.connectStream()
#         print("Hey Dude, whats up? Anyone home? " + self.remote.greetings())
        
        while True:
            command = raw_input("Send: ")
            print("Calling test()->" + self.remote.test())
    
    def exposed_greetings(self): # this is an exposed method
        return "greetings at: " + datetime.datetime.now()
    
    def exposed_get_answer(self): # this is an exposed method
        return 42

    def get_question(self):  # while this method is not exposed
        return "what is the airspeed velocity of an unladen swallow?"
    
    def connectStream(self):

        self.serialConn = self.createSerialConn()
        self.serialStream = SerialStream(self.serialConn)
        
#         self.executableCommandLineService = ExecutableCommandLineService(self)
        self.conn = rpyc.connect_stream(self.serialStream, service=RobotTestService, config={'allow_all_attrs': True}) 
        self.remote = self.conn.root

    def createSerialConn(self):
        serialConn = None
        
        for xb in XBEE_INTERFACES:
            try:
                print("Tying to connect to Wireless: " + xb['type'] + " on " + xb['dev'] + " ...")
                
                serialConn = serial.Serial(port=xb['dev'], baudrate=xb['baud'])
                serialConn.close()
                serialConn.open()
                if serialConn.isOpen():
                    print("Wireless Serial is open: " + xb['dev'])
                    return serialConn
            except:
                print(" ... Failed")
                pass
            else:
                return serialConn
#         raise AttributeError

if __name__ == '__main__':
    main()