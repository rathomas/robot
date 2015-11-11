'''
Created on Aug 16, 2013

@author: rthomas
'''
from datetime import datetime

class BaseFrame:
    def __init__(self,pc):
        self.pc = pc
        self.createdTimestamp = datetime.now()
        self.lifespan = 0
#         print("Frame created.") 
#         print("Frame created." + self.traceSelf()) 
       
    def __str__(self):
        return "Frame: %s" % self.createdTimestamp
       
    def executeFrame(self):
        self.executedTimestamp = datetime.now()
        self.lifespan = self.executedTimestamp - self.createdTimestamp
        print("executeFrame: " + self.traceSelf() + " / lifespan: " + str(self.lifespan))
        
    def traceSelf(self):
        return str(self);
        
class WaitFrame(BaseFrame):
    def __init__(self,pc):
        BaseFrame.__init__(self,pc)
#         print(self.traceSelf()) 

    def executeFrame(self):
#         super(WaitFrame, self).executeFrame()
        print("executeFrame: " + self.traceSelf() + " / lifespan: " + str(self.lifespan))

    def __str__(self):
        return "WaitFrame: at " +  str(self.createdTimestamp)
    
class PinUpdateFrame(BaseFrame):
    def __init__(self,pc,pin=-1,pinValue=None):
        BaseFrame.__init__(self,pc)
        self.pin = pin
        self.pinValue = pinValue

    def executeFrame(self):
        BaseFrame.executeFrame(self)
        self.pc.arduino.board.digital[self.pin].write(self.pinValue)
#     def traceSelf(self):
#         if self and self.pin and self.pinValue:
#             return (str(self) + " pin:" + str(self.pin) + ":" + str(self.pinValue));
#         return "Possible error, invalid frame created"
    
class ServoMovementFrame(PinUpdateFrame):
    def __init__(self,pc,pin=-1,pinValue=None):
        PinUpdateFrame.__init__(self,pc,pin,pinValue)
        print(self.traceSelf()) 
       
    def __str__(self):
        return "ServoMovementFrame: pin[" + str(self.pin) +"]: "+ str(self.pinValue) +" at "+ str(self.createdTimestamp)

    def executeFrame(self):
        PinUpdateFrame.executeFrame(self)

#     def traceSelf(self):
#         super(ServoMovementFrame,self).traceSelf()
#         return (" Servo:")

class MotorDriveFrame(BaseFrame):
    def __init__(self,pc,s=0,ld=1,rd=0,lb=0,rb=0,c=0):
        BaseFrame.__init__(self,pc)
        self.speed = s
        self.leftDriveDirection = ld
        self.rightDriveDirection = rd
        self.leftDriveBrake = lb
        self.rightDriveBrake = rb
        self.curve = c
        print(self.traceSelf()) 

    def executeFrame(self):
#         super(MotorDriveFrame,self).executeFrame()
#         super(MotorDriveFrame, self).executeFrame()
#         BaseFrame.executeFrame()
        
        self.pc.setDriveConfig(self.speed,
                               self.leftDriveDirection,
                               self.rightDriveDirection,
                               self.leftDriveBrake,
                               self.rightDriveBrake,
                               self.curve)
        print("executeFrame: " + self.traceSelf() + " / lifespan: " + str(self.lifespan))
        
    def __str__(self):
        return "MotorDriveFrame: speed=" + str(self.speed) +" curve="+ str(self.curve) +" at "+ str(self.createdTimestamp)

#     def traceSelf(self):
#         print(" ")
#         return (str(self) +" speed:"+ str(self.speed) +":"+ str(self.curve));

if __name__ == '__main__':
    print("Please Run Robot.py")
