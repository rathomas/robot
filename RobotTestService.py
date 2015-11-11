'''
Created on Oct 4, 2013

@author: rthomas
'''
from RobotConfig import RPYC_CONN_PORT
from rpyc.utils.server import ThreadedServer
'''
Created on Oct 4, 2013

@author: rthomas
'''
import rpyc
import datetime

class RobotTestService(rpyc.Service):
    def on_connect(self):
        print("Sevice " + str(self) + " Connected.")

    def on_disconnect(self):
        print("Sevice " + str(self) + " Disconnected.")
        
    def exposed_test(self):
        print("Test Requested: " + str(datetime.datetime.now()))
        return "Test Reply at: "+ str(datetime.datetime.now())
    
if __name__ == "__main__":
    t = ThreadedServer(RobotTestService, port = RPYC_CONN_PORT)
    t.start()