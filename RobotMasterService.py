'''
Created on Oct 4, 2013

@author: rthomas
'''
import rpyc
import datetime
from RobotConfig import RPYC_CONN_PORT
from rpyc.utils.server import ThreadedServer

class RobotMasterService(rpyc.Service):
    def on_connect(self):
        print("Sevice " + str(self) + " Connected.")

    def on_disconnect(self):
        print("Sevice " + str(self) + " Disconnected.")
        
    def exposed_print(self, s):
        print("Remote: " + str(s))
        return s
    
    def exposed_test(self):
        print("Test Requested: " + str(datetime.datetime.now()))
        return "Test Reply at: "+ str(datetime.datetime.now())

if __name__ == "__main__":
    t = ThreadedServer(RobotMasterService, port = RPYC_CONN_PORT)
    t.start()
    