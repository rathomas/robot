'''
Created on Aug 16, 2013

@author: rthomas
'''
import math
from datetime import datetime
from time import sleep,time
from TweenedProxy import TweenedProxy
from Tasks import Task, MovementTask
from ArduinoConnector import ArduinoConnector
from Frame import ServoMovementFrame, PinUpdateFrame, WaitFrame, MotorDriveFrame, BaseFrame
from copy import copy
import subprocess
from util.piTweener import Tweener
from pyfirmata.mockup import MockupBoard
from posix import wait

class PhysicalController:
    def __init__(self):
        print("PhysicalController created.")
            
        self.lc = None
        self.parallelFrameQueue = []
        self.executedQueue = []
        self.laserOnPersist = False
        self.movingForward = False
        self.curve = 0
        self.sleepFrame = 0
        
    def registerMaster(self, master):
        self.master = master
        
    def registerLogicalController(self, lc):
        self.lc = lc
        
    def configureArduino(self):
        self.arduino = ArduinoConnector()
        self.config = self.arduino.config
       
    def wait(self, timeInSeconds):
        frames = []
        if int(timeInSeconds) > 0:
            numOfFrames = int(round((int(timeInSeconds) * 1000)/self.config.arduinoLoopDelay))
            for x in range(0,numOfFrames): 
                frames.append(WaitFrame(self))
                
            self.addQueueGroup(frames)
            
#         self.addQueueGroup([WaitFrame(self) for x in range(0,numOfFrames)])
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
        referenceVolts = 5.0
        resistanceFactor = 0.0
        R1 = 2158.0
        R2 = 1000.0
        resistanceFactor = (R2/(R1+R2))
         
        volts = 0.0
        voltsReadings = []
        voltsAvgCalc = 0.0
        
        for x in range(samples):
            a0 = self.arduino.board.analog[0].value;
            if a0 and a0 >= 0:
                volts = (a0/resistanceFactor) * referenceVolts;
                voltsReadings.append(volts)
                voltsAvgCalc = sum(voltsReadings) / len(voltsReadings)
                print("input: " + str(a0) +" resistanceFactor:"+ str(resistanceFactor) +" volts:"+ str(volts) +" (avg: "+ str(voltsAvgCalc) + ")")
            
        
        if len(voltsReadings) == 0:
            print("input: " + str(0) +" resistanceFactor:"+ str(resistanceFactor) +" volts:"+ str(volts) +" (avg: "+ str(voltsAvgCalc) + ")")
            
        return voltsAvgCalc
    
    def shutdownSystem(self, restart=False):
#         a0 = self.arduino.board.analog[0].value;
#         returnCode = subprocess.call(cmdHostname, shell=True)
#         print(returnCode)

        cmdHostname = "hostname -s"
        output = subprocess.check_output(cmdHostname, shell=True)
        print(output)

        # SHUTDOWN
#         if(output == 'scoobie-do-bot'):
#             print("uh-oh...")
        if restart:
            print("initiating restart...")
            cmdShutdown = "shutdown -r now"
        else:                
            print("initiating shutdown ...")
            cmdShutdown = "shutdown -h now"
            
        returnCode = subprocess.call(cmdShutdown, shell=True)
        print(returnCode)
            
        return 1
# //---------------------------------------------------------------------
# //
# // Motor Commands
# //
# //--------------------------------------------------------------------- 
    # //---------------------------------------------------------------------
    # // Queue Commands
    # //--------------------------------------------------------------------- 
    def driveForward(self,s=180):
        self.addQueueItem(MotorDriveFrame(self,s))
        return 1
        
    def turnLeft(self,s=180):
        self.addQueueItem(MotorDriveFrame(self,s,0,0))
        return 1
        
    def turnRight(self,s=180):
        self.addQueueItem(MotorDriveFrame(self,s,1,1))
        return 1
    
    def driveBackward(self,s=180):
        self.addQueueItem(MotorDriveFrame(self,s,0,1))
        return 1
    
    # //---------------------------------------------------------------------
    # // Exec Commands
    # //--------------------------------------------------------------------- 
    def setDriveConfig(self,s=0,ld=1,rd=0,lb=0,rb=0,c=0):
        self.movingForward = ld >= rd

        self.curve = c
        self.speed = s
        
        if self.speed != 0:
            lt = float(self.speed - self.curve + 1) / 255
            rt = float(self.speed + self.curve - 1) / 255
            
            autoStop = Task('a4', self.lc)
            autoStop.executeTask()
        else:
            self.movingForward = False

            lt = 0
            rt = 0

            removeAutoStop = Task('d4', self.lc)
            removeAutoStop.executeTask()

        self.arduino.board.digital[self.config.leftDriveDirectionPin].write(ld)
        self.arduino.board.digital[self.config.rightDriveDirectionPin].write(rd)

        self.arduino.board.digital[self.config.leftDriveBrakePin].write(lb)
        self.arduino.board.digital[self.config.rightDriveBrakePin].write(rb)
        
        print(str(lt) + "<-(*)->" + str(rt) + "  " + str(c));
        self.arduino.board.digital[self.config.leftDriveSpeedPin].write(lt);
        self.arduino.board.digital[self.config.rightDriveSpeedPin].write(rt);

    def getNetSpeed(self):
        return abs(self.speed)

# //---------------------------------------------------------------------
# //
# // Head Movement Commands
# //
# //--------------------------------------------------------------------- 
    def tiltHead(self,d=95):
        t = MovementTask("qt" + str(d), self.lc)
        t.executeTask()
        return 1
    def rotateHead(self,d=95):
        t = MovementTask("qp" + str(d), self.lc)
        t.executeTask()
        return 1
    # //---------------------------------------------------------------------
    # // Queue Commands
    # //--------------------------------------------------------------------- 
    
    def queueTiltHead(self,d=95):
#         self.addQueueGroup(self.createServoMovementFrameGroup(self.config.headYawServoPin,d))
        self.addQueueGroup(self.createServoMovementFrameGroup(self.config.headYawServoPin,d,True))
        return 1

    def queueRotateHead(self,d=90):
#         self.addQueueGroup(self.createServoMovementFrameGroup(self.config.headPanServoPin,d))
        self.addQueueGroup(self.createServoMovementFrameGroup(self.config.headPanServoPin,d,True))
        return 1
    
    
    
    # //---------------------------------------------------------------------
    # // Exec Commands
    # //---
    def getHeadTilt(self):
        return self.arduino.board.digital[self.config.headYawServoPin].read()

    def getHeadRotate(self):
        return self.arduino.board.digital[self.config.headPanServoPin].read()
    
    def getHeadMeasuredTilt(self, n=1):
        return self.executePulse(self.config.xAxisPin, n);
    
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
        boundary = {'x':0, 'y':0, 'z':0, 'r':0, 'bx':0, 'by':0, 'bz':0}
        currentRotation = 90-self.getHeadRotate()
        boundary['bx'] = float(d) * math.sin(math.radians(currentRotation))
        boundary['by'] = float(d) * math.cos(math.radians(currentRotation))
        return boundary
               
    def executePing(self, pin, n=1):
        if not self.arduino.connected:
            return -1
        
        pingAvg = []
        for pingId in range(n):
            self.arduino.board.getPing(self.config.headPingPin)
            sleep(.05) #TODO: change to event
            pingAvg.append(self.arduino.board.get_ping_distance(pin))
            pingAvgCalc = sum(pingAvg) / len(pingAvg)
#             print("Ping " + str(pingId) + " " + str(self.arduino.board.get_ping_distance(pin)) + " avg: " + str(pingAvgCalc))
        return pingAvgCalc
    
    def getMeasuredPingDistance(self, n=1):
        return self.executePing(self.config.headPingPin, n);
    
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
        if not self.arduino.board:
            return 0;
        
        pulseAvg = []
        for pulseId in range(n):
            self.arduino.board.getPulse(pin)
            sleep(.05) #TODO: change to event
            pulseAvg.append(self.arduino.board.get_pulse_duration(pin))
            pulseAvgCalc = sum(pulseAvg) / len(pulseAvg)
#             print("Pulse " + str(pulseId) + " " + str(self.arduino.board.get_pulse_duration(pin)) + " avg: " + str(pulseAvgCalc))
            
        return pulseAvgCalc
  
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
        self.arduino.board.digital[self.config.pirSensorEnablePin].write(e)
        print("pir sensor enabled: " + str(self.arduino.board.digital[self.config.pirSensorPin].write(e)))
        return 1

# //---------------------------------------------------------------------
# //
# // Gyro Commands
# //
# //--------------------------------------------------------------------- 
    # //---------------------------------------------------------------------
    # // Queue Commands
    # //---    
    def readGyro(self,propId):
        for x in range(10):
            self.arduino.board.requestGyro(self.config.gyroI2CAddress, propId)
            sleep(.2)
        return 1
          
# //---------------------------------------------------------------------
# //
# // Laser Commands
# //
# //--------------------------------------------------------------------- 
    # //---------------------------------------------------------------------
    # // Queue Commands
    # //---
    def laserEnabled(self,e,p=False):
        self.arduino.board.digital[self.config.laserControlPin].write(e)
        #if laser is turned on manually, then persist this behavior
        if e == 1 and p == True:
            self.laserOnPersist = True
        elif e == 0 and p == True:
            self.laserOnPersist = False
        return 1
   
#//---------------------------------------------------------------------
#// 
#// Servo Frames
#// 
#//---------------------------------------------------------------------
    def createServoMovementFrameGroup(self,servoPin,newAngle=5, easing=False):
        if easing:
            return self.createEasedServoMovementFrameGroup(servoPin,newAngle)
        else:
            cAngle = self.arduino.board.digital[servoPin].read()
            frames = []
    
            #Confidence rating must be greater than 0
            i = self.lc.confidence.getCurrentRating()
            
            if cAngle and i > 0:
                while True:
                    remainingAngle = abs(cAngle-int(newAngle))

                    #Confidence rating is used for increment in
                    #linear servo adjustments
                    if remainingAngle < i:
                        adjustAngle = remainingAngle
                    else:
                        adjustAngle = i
                        
                    if int(newAngle) > cAngle:
                        cAngle = cAngle + adjustAngle 
                    else:
                        cAngle = cAngle - adjustAngle
                        
                    frames.append(ServoMovementFrame(self,servoPin,cAngle))
                    print("Create Frame: pin " + str(servoPin) + " to " + str(cAngle))
                    if cAngle == int(newAngle): break
            else:
                print("Servo not initialized, may be disconnected")
        return frames
            
    def createEasedServoMovementFrameGroup(self,servoPin,newAngle):
        
        cAngle = self.arduino.board.digital[servoPin].read()
        print cAngle
        
        #Confidence rating must be greater than 0
        i = self.lc.confidence.getCurrentRating()
            
        frames = []
        tObj = TweenedProxy()
        tObj.setValue(cAngle)
        tw = Tweener()
        mt = tw.add_tween( tObj, 
                          setValue=newAngle, 
                          tween_type=tw.IN_OUT_CUBIC, 
                          tween_time=20/i,
                          on_complete_function=tObj.complete, 
                          on_update_function=tObj.update )
        
#         mt = tw.get_tweens_affecting_object(tObj)[0]
#         tweenable = mt.get_tweenable("setValue")
#         tw.add_tween(tweenable, change=newAngle, tween_time=2)
        
        stepResolution = .008 
        transitionTime = 0
        while tw.has_tweens():
            tw.update( transitionTime )
                
            #Create New Eased Frame
            frames.append(ServoMovementFrame(self,servoPin,int(tObj.getValue())))
            print len(frames)
            print(tObj.getValue())
            
            transitionTime = transitionTime + stepResolution  
        return frames
#     def createEasedServoMovementFrameGroup(self,servoPin,d=5):
#         frames = []
#         tObj = TweenedProxy()
#         tw = Tweener()
#         mt = tw.addTween( tObj, setY=1000, tweenTime=d, tweenType=tw.OUT_EXPO, y=1, onCompleteFunction=tObj.complete, onUpdateFunction=tObj.update )
#         lastNow = datetime.now()
#         changed = False
#         while tw.hasTweens():
#             now = datetime.now()
#             d = now - lastNow
#             lastNow = now
#             tw.update( d )
#                 
#             #Create New Eased Frame
#             frames.append(ServoMovementFrame(self,servoPin,tObj.getValue()))
#             
#             print(tObj.getValue())
#             
#             if mt.delta > 1.0 and not changed:
#                 changed = True
#         return frames
    
#//---------------------------------------------------------------------
#// 
#// Execute Frames
#// 
#//---------------------------------------------------------------------
    def executeFramesInParallel(self, confidence, usePing=False, useAccelerometer=False):
        boundaries = []
        tiltRecordsX = []
        tiltRecordsY = []
        
        while True:
            moreFrames = self.updateFrame()
            
            if(usePing):
                boundary = self.pingToCoordinates(self.getMeasuredPingDistance(3))
                boundaries.append(boundary)
#                 self.lc.createBoundaryVisual(boundary)
            if(useAccelerometer):
                self.executePulse(self.config.xAxisPin, 1)
                tiltRecordsX.append(self.arduino.board.get_pulse_duration(self.config.xAxisPin))
            
            #Set Speed of loop
            sleep(confidence.getCurrentReactionIntervalSleep())
            
            if not moreFrames: break
        return boundaries
            
    def updateFrame(self):
        if self.parallelFrameQueue:
            print("##--> Exec Queue (Parallel) | Queue length:" + str(len(self.parallelFrameQueue)))
            for x in self.parallelFrameQueue:
                if x:
                    print("##----> Exec Queue Item:" + str(len(x)) + " frames from parallelFrameQueue[" +str(self.parallelFrameQueue.index(x)) + "] | Queue length:" + str(len(self.parallelFrameQueue)))
                    frame = x.pop(0)
                    
                    if isinstance(frame, WaitFrame):
                        frame.executeFrame()
                        
                    elif isinstance(frame, MotorDriveFrame):
                        frame.executeFrame()
                        
                    elif isinstance(frame, PinUpdateFrame):
                        
                        if frame.pin == self.config.headPanServoPin or frame.pin == self.config.headYawServoPin:
                            self.laserEnabled(1)
                            
                        frame.executeFrame()
                        
#                         if self.arduino.connected:
#                             self.arduino.board.digital[frame.pin].write(frame.pinValue)
    #                         print("Setting pin " + str(pin + " to " + str(pinValue))
#                         else:
#                             print("Arduino not connected. Simulation Setting pin " + str(frame.pin) + " to " + str(frame.pinValue))

                    if self.executedQueue.count(x) == 0:
                        self.executedQueue.append(copy(x))
                         
                    self.executedQueue[self.executedQueue.index(x)].append(copy(frame))
                else:
                    self.removeQueueGroup(x)
                    
            if not self.laserOnPersist:
                self.laserEnabled(0)
            
            return True
        else:
            return False

    def clearFrames(self, pin):
        if self.parallelFrameQueue:
            for x in self.parallelFrameQueue:
                if x and len(x) > 0:
                    frame = x.pop(0)
                    if frame.pin == pin:
                        self.removeQueueGroup(x)
                else:
                    self.removeQueueGroup(x)
         
    def addQueueItem(self,frame):
        if isinstance(frame, BaseFrame):
            self.parallelFrameQueue.append([frame])
            
    def addQueueGroup(self,frames):
        print("##Queue Atempting to Add:" + str(len(frames)) + " frames | Queue length:" + str(len(self.parallelFrameQueue)))
        framesToAdd = [x for x in frames if isinstance(x, BaseFrame)]
        if len(framesToAdd):
            self.parallelFrameQueue.append(framesToAdd)
            print("##Queue Group Added:" + str(len(framesToAdd)) + " frames | Queue length:" + str(len(self.parallelFrameQueue)))
                              
    def removeQueueGroup(self, x):
        print("##Queue Remove Group: from parallelFrameQueue[" +str(self.parallelFrameQueue.index(x)) + "] | Queued/Executed length:" + str(len(self.parallelFrameQueue)) + " / " + str(len(self.executedQueue)))
        del self.parallelFrameQueue[self.parallelFrameQueue.index(x)]
        
    def destroy(self):
        self.arduino.disconnectArduino()
        del self 
        
    #Connect using RPyC      
    def connect(self, remoteHost):
        print (" -Connect not available from this endpoint. Master needs to initiate the connection" + self.remoteHost + " ...")        
        return 1           
