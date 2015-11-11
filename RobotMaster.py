#!/usr/local/bin/python2.7
'''
Created on Mar 13, 2012
====================
===Scoobie-Do-Bot===
====================
@author: rthomas
'''

from CommandLineThread import CommandLineThread
from DisconnectedPhysicalController import DisconnectedPhysicalController
from CommandLineController import CommandLineController

# from leapmotion import *
# import leapmotion.Leap as Leap
# from leapmotion.Leap import *

__version__ = "0.0.1"

class RobotMaster:
    
    def main(self):
        print("Scoobie-Do-Bot Master is alive!...")
        self.physicalController = DisconnectedPhysicalController()
        self.physicalController.registerMaster(self)
        
        self.commandLineController = CommandLineController(self, self.physicalController)
    # --Leap Motion ----    
        # Create a sample listener and controller
    #     leapMotionConnector = LeapMotionConnector(logicalController)
    #     leapMotionConnector.connect()
    
    # --Command Line Thread ----    
        self.commandLineThread = CommandLineThread(self.commandLineController).start()

    #     VisualizerWindowTread(logicalController).start()
        
        # MAIN LOOP    
        while True:
#             self.commandLineController.executeBehaviors()
#             sleep(self.physicalController.config.arduinoLoopDelay/100)
            try:
                self.commandLineController.previousCommands.index('')
                break
            except:
                pass
            
        self.shutdown()
        
    def shutdown(self):
        print("Shutdown Scoobie-Do-Bot...")
        if self.physicalController: self.physicalController.destroy()
        if self.commandLineController: self.commandLineController.destroy()
        self.destroy()
        
    def destroy(self):
        del self
        
    def __del__(self):
        # SLEEP SETTINGS
        self.commandLineThread.kill()
        
if __name__ == '__main__': 
    robotMaster = RobotMaster()
    robotMaster.main()
