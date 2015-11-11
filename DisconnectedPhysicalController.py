'''
Created on Aug 16, 2013

@author: rthomas
'''
from PhysicalController import PhysicalController
# import rpyc
from RobotConfig import *

class DisconnectedPhysicalController(PhysicalController):
    def __init__(self):
        PhysicalController.__init__(self)
        print("DisconnectedPhysicalController created.")
       
    def registerRobotVars(self):
        pass
    
    def registerLogicalController(self, lc):
        self.lc = lc
       
    #Connect using RPyC      
    def connect(self, remoteHost):
        print ("Trying Connect:  " + remoteHost + " ...")   
        self.master.commandLineController.connectStream()
#         self.master.commandLineController.connect(SOCKET_ROBOT_HOST, SOCKET_ROBOT_PORT)
        return 1
        
    #Connect using RPyC      
    def disconnect(self):
        print (" -Not Connected ...")
        return 1
# //---------------------------------------------------------------------
# //
# // Battery Monitor
# //
# //--------------------------------------------------------------------- 
    # //---------------------------------------------------------------------
    # // Execute Commands
    # //--------------------------------------------------------------------- 
    def getBatteryVoltage(self, samples=10):
        return self.handleNotConnected()
    
    def shutdownSystem(self, samples=10):
        return self.handleNotConnected()
# //---------------------------------------------------------------------
# //
# // Motor Commands
# //
# //--------------------------------------------------------------------- 
    # //---------------------------------------------------------------------
    # // Queue Commands
    # //--------------------------------------------------------------------- 
    def driveForward(self,s=180):
        return self.handleNotConnected()
        
    def turnLeft(self,s=180):
        return self.handleNotConnected()
    
    def turnRight(self,s=180):
        return self.handleNotConnected()
    
    def driveBackward(self,s=180):
        return self.handleNotConnected()
    
    # //---------------------------------------------------------------------
    # // Exec Commands
    # //--------------------------------------------------------------------- 
    def setDriveConfig(self,s=0,ld=1,rd=0,lb=0,rb=0,c=0):
        return self.handleNotConnected()

    def getNetSpeed(self):
        return self.handleNotConnected()
# //---------------------------------------------------------------------
# //
# // Head Movement Commands
# //
# //--------------------------------------------------------------------- 
    def tiltHead(self,d=95):
        return self.handleNotConnected()
       
    def rotateHead(self,d=95):
        return self.handleNotConnected()
    # //---------------------------------------------------------------------
    # // Queue Commands
    # //--------------------------------------------------------------------- 
    
    def queueTiltHead(self,d=95):
        return self.handleNotConnected()

    def queueRotateHead(self,d=90):
        return self.handleNotConnected()
    
    # //---------------------------------------------------------------------
    # // Exec Commands
    # //---
    def getHeadTilt(self):
        return self.handleNotConnected()

    def getHeadRotate(self):
        return self.handleNotConnected()
    
    def getHeadMeasuredTilt(self, n=1):
        return self.handleNotConnected()    
# //---------------------------------------------------------------------
# //
# // Ping Commands
# //
# //--------------------------------------------------------------------- 
    # //---------------------------------------------------------------------
    # // Queue Commands
    # //---
    
    # //---------------------------------------------------------------------
    # // Exec Commands
    # //---
    def pingToCoordinates(self, d):
        return self.handleNotConnected()
               
    def executePing(self, pin, n=1):
        return self.handleNotConnected()
    
    def getMeasuredPingDistance(self, n=1):
        return self.handleNotConnected()
    
# //---------------------------------------------------------------------
# //
# // Accelerometer Commands
# //
# //--------------------------------------------------------------------- 
    # //---------------------------------------------------------------------
    # // Queue Commands
    # //---    

    # //---------------------------------------------------------------------
    # // Exec Commands
    # //---    
    def executePulse(self, pin, n = 1):
        return self.handleNotConnected()
  
# //---------------------------------------------------------------------
# //
# // PIR Sensor Commands
# //
# //--------------------------------------------------------------------- 
    # //---------------------------------------------------------------------
    # // Queue Commands
    # //---
    
    # //---------------------------------------------------------------------
    # // Exec Commands
    # //---
    def pirSensorEnabled(self,e,p=False):
        return self.handleNotConnected()

# //---------------------------------------------------------------------
# //
# // Gyro Commands
# //
# //--------------------------------------------------------------------- 
    # //---------------------------------------------------------------------
    # // Queue Commands
    # //---    
    def readGyro(self,propId):
        return self.handleNotConnected()
          
# //---------------------------------------------------------------------
# //
# // Laser Commands
# //
# //--------------------------------------------------------------------- 
    # //---------------------------------------------------------------------
    # // Queue Commands
    # //---
    def laserEnabled(self,e,p=False):
        return self.handleNotConnected()
   
#//---------------------------------------------------------------------
#// 
#// Servo Frames
#// 
#//---------------------------------------------------------------------
    def createServoMovementFrameGroup(self,servoPin,newAngle=5, easing=False):
        return self.handleNotConnected()
    
#//---------------------------------------------------------------------
#// 
#// Execute Frames
#// 
#//---------------------------------------------------------------------
    def executeFramesInParallel(self, confidence, usePing=False, useAccelerometer=False):
        return self.handleNotConnected()
            
    def updateFrame(self):
        return self.handleNotConnected()

    def clearFrames(self, pin):
        return self.handleNotConnected()
         
    def addQueueItem(self,frame):
        return self.handleNotConnected()
            
    def addQueueGroup(self,frames):
        return self.handleNotConnected()
            
    def handleNotConnected(self):
        print("Action not available: not connected")
        return 1
                              
    def removeQueueGroup(self, x):
        print("##Queue Remove Group: from parallelFrameQueue[" +str(self.parallelFrameQueue.index(x)) + "] | Queued/Executed length:" + str(len(self.parallelFrameQueue)) + " / " + str(len(self.executedQueue)))
        del self.parallelFrameQueue[self.parallelFrameQueue.index(x)]
        
    def destroy(self):
        del self            
