'''
Created on Aug 16, 2013

@author: rthomas
'''
from PhysicalController import PhysicalController

class ProxiedPhysicalController(PhysicalController):
    def __init__(self):
        PhysicalController.__init__(self)
        self.remoteHost = None
        print("ProxiedPhysicalController created.")
        
    #Connect using RPyC      
    def connect(self, remoteHost):
        print (" -Already connected to " + self.remoteHost + " ...")        
        return 1
        
    #Connect using RPyC      
    def disconnect(self):
        if self.remoteHost:
            self.master.commandLineController.disconnect()
            print ("Disconnecting from:  " + self.remoteHost + " ...")
        else:
            print (" -Not Connected ...")
        return 1
