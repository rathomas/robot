'''
Created on Aug 16, 2013

@author: rthomas
'''
import threading

# Command thread class:
class CommandLineThread ( threading.Thread ):

    # Override Thread's __init__ method to accept the parameters needed:
    def __init__ (self, commandLineController):
        self.commandLineController = commandLineController
        threading.Thread.__init__ ( self )
        print("CommandLine Thread Created.")

    def run ( self ):
        print("CommandLine Thread is Running.")
        while True:
            command = raw_input("Scoobie-Doo-Bot do:")
            if not self.commandLineController.executeCommand(command): break
#             if not self.lc.executeCommand(command, True): break
#             break
#         self.kill()
    
    def kill ( self ):
        if self.isAlive():
            del self
