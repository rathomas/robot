'''
Created on Sep 15, 2013

@author: rthomas
'''
from rpyc.core.service import Service
import datetime
from RobotConfig import RPYC_CONN_PORT
from rpyc.utils.server import ThreadedServer

def ExecutableCommandLineService(commandLineController):

    class CommandLineService(Service):

        def on_connect(self):
            print("Sevice " + str(self) + " Started.")
            self.isConnected = True

        def on_disconnect(self):
            print("Sevice " + str(self) + " Disconnected.")
            self.isConnected = False
                
        def exposed_isConnected(self): # this is an exposed method
            return self.isConnected
                
        def exposed_greetings(self): # this is an exposed method
            print("greeting requested at: " + str(datetime.datetime.now()))
            return "greetings at: " + str(datetime.datetime.now())
            
        def exposed_executeCommand(self, command, traceCommand=False):
            if commandLineController:
                print("Executing: " + command + " from remote master.")
                return commandLineController.executeCommand(command, traceCommand)
            else:
                return "exposed_executeCommand: commandLineController does not exist!  Check Registration through registerCommandLineController()"

    
    return CommandLineService

if __name__ == "__main__":
    t = ThreadedServer(ExecutableCommandLineService(), port = RPYC_CONN_PORT)
    t.start()