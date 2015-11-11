#!/usr/local/bin/python2.7
'''
Created on Mar 13, 2012
====================
===Scoobie-Do-Bot===
====================
@author: rthomas
'''

from time import sleep
 
from RobotConfig import *
from LogicalController import LogicalController
from CommandLineThread import CommandLineThread
from CommandLineController import CommandLineController
from Tasks import Task
from PhysicalController import PhysicalController
# from leapmotion import *
# import leapmotion.Leap as Leap
# from leapmotion.Leap import *

__version__ = "0.0.1"

class Robot:
    
    def main(self):
        print("Scoobie-Do-Bot is alive!...")
        
        self.physicalController = PhysicalController()
        self.physicalController.registerMaster(self)
        self.physicalController.configureArduino()
        
        self.logicalController = LogicalController(self, self.physicalController)
        self.physicalController.registerLogicalController(self.logicalController)
        
        # DEFAULT SETTINGS
#         startBatteryMonitorTask = Task('a0', self.logicalController, True)
#         startBatteryMonitorTask.executeTask()

        # Align Servos        
#         defaultTask = Task('w0', self.logicalController, True)
#         Task('t95', defaultTask)
#         Task('p90', defaultTask)
#         defaultTask.traceSelf()
#         defaultTask.executeTask()

#         testGyroReadingTask = Task('k1', self.logicalController, True)
#         testGyroReadingTask.executeTask()

#         mt = Task('a7', self.logicalController, True)
#         Task('c5', mt)
#         mt.executeTask()
        
    
    
    # --Command Line Thread ----    
        self.commandLineController = CommandLineController(self, self.physicalController)
        
    # --Command Line Thread ----    
        self.commandLineThread = CommandLineThread(self.commandLineController)
        self.commandLineThread.start()
        
        self.commandLineController.createStreamService()
    #     VisualizerWindowTread(logicalController).start()
        
        self.alive = True
        
        # MAIN LOOP    
        while self.alive:
            self.logicalController.executeBehaviors()
            sleep(self.physicalController.config.arduinoLoopDelay/100)
             
            try:
                self.commandLineController.previousCommands.index('')
                break
            except:
                pass
             
        self.shutdown()
     
    def shutdown(self):
        print("Shutdown Scoobie-Do-Bot...")
        self.alive = False
        self.destroy()
         
    def destroy(self):
        del self
         
    def __del__(self):
        # SLEEP SETTINGS
        defaultTask = Task('w0', self.logicalController, True)
        Task('t95', defaultTask)
        Task('p90', defaultTask)
        defaultTask.traceSelf()
        defaultTask.executeTask()
        #physicalController.rotateHead(8,confidence.getCurrentReactionInterval(),confidence.rating) 
        #physicalController.tiltHead(10,confidence.getCurrentReactionInterval(),confidence.rating)
        #physicalController.executeFramesInParallel(confidence)
        self.commandLineThread.kill()

        if self.physicalController: self.physicalController.destroy()
        if self.logicalController: self.logicalController.destroy()
        if self.commandLineController: self.commandLineController.destroy()
        
        quit()
        
if __name__ == '__main__': 
    robot = Robot()
    robot.main()



