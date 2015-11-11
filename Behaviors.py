'''
Created on Aug 15, 2013

@author: rthomas
'''
from Tasks import Task, ScanTask, MovementTask

class BaseBehavior:
    def __init__(self, p=None):
        self.parentBehavior = p
        self.subBehaviors = []
            
        if isinstance(self.parentBehavior, BaseBehavior): 
            self.lc = self.parentBehavior.lc;
            self.generation = self.parentBehavior.generation + 1
            self.parentBehavior.addSubBevahior(self)
            print("  " * self.generation + "SubBehavior created.")
        else: 
            self.lc = self.parentBehavior;
            self.generation = 0
        
        self.pc = self.lc.getPhysicalController()
#         print("Behavior created.")
    
    def addSubBevahior(self, b):
        b.parentBehavior = self
        self.subBehaviors.append(b)
    
    def added(self):
        self.addedPlaceholder = None
#       implement to reset values on add
        
    def removed(self):
        self.removedPlaceholder = None
#       implement to set values on removal

        
    def traceSelf(self):
        print(self);
        for sb in self.subBehaviors: sb.traceSelf()
      
class DontTouchBehavior(BaseBehavior):
    def __init__(self, p=None):
        BaseBehavior.__init__(self, p)
        self.correctionIndex = 0
        self.measureTask = Task('m1', self.lc)
        
    def executeBevahior(self):
        distance = self.measureTask.executeTask()
        currentHeadTilt = int(self.pc.getHeadTilt())
        
        if distance <= 6 and distance > 0:
            moveTask = Task('c20', self.lc)
            Task('t' + str(currentHeadTilt - 20), moveTask)
            Task('c2', moveTask)
            moveTask.executeTask()
            self.correctionIndex = self.correctionIndex + 1
            return 1
        elif self.correctionIndex > 0 and distance > 3:
            moveTask = Task('c5', self.lc)
            Task('t' + str(currentHeadTilt + 20), moveTask)
            Task('c2', moveTask)
            moveTask.executeTask()
            self.correctionIndex = self.correctionIndex - 1
            return 1
        return 0
      
class AcknowlegePresenseBehavior(BaseBehavior):
    def __init__(self, p=None):
        BaseBehavior.__init__(self, p)
        self.measureTask = Task('m1', self.lc)
        self.ticksSinceAcknowlegement = 20
        
    def executeBevahior(self):
        distance = self.measureTask.executeTask()
#         print(str(distance))
        if distance <= 60 and distance > 3 and self.ticksSinceAcknowlegement > 20:
            
            showLaserTask = Task('a5', self.lc)
            Task('w3', showLaserTask)
            showLaserTask.executeTask()
            
            shakeHeadTask1 = Task('c40', self.lc)
            Task('p' + str(int(self.pc.getHeadRotate()) - 10), shakeHeadTask1)
            Task('p' + str(int(self.pc.getHeadRotate()) + 10), shakeHeadTask1)
            Task('p' + str(int(self.pc.getHeadRotate()) - 10), shakeHeadTask1)
            Task('p' + str(self.pc.getHeadRotate()), shakeHeadTask1)
            Task('w1', shakeHeadTask1)
            Task('c2', shakeHeadTask1)
            shakeHeadTask1.executeTask()
            
            nodHeadTask1 = Task('c2', self.lc)
            Task('t' + str(int(self.pc.getHeadTilt()) - 30), nodHeadTask1)
            Task('w1', nodHeadTask1)
            Task('c4', nodHeadTask1)
            Task('t' + str(int(self.pc.getHeadTilt()) + 30), nodHeadTask1)
            Task('t100', nodHeadTask1)
            Task('d5', nodHeadTask1)
            Task('c4', nodHeadTask1)
            nodHeadTask1.executeTask()
            
            self.ticksSinceAcknowlegement = 0
            return 1
        
        self.ticksSinceAcknowlegement = self.ticksSinceAcknowlegement + 1
        
        return 0
      
class ScanBehavior(BaseBehavior):
    def __init__(self, p=None):
        BaseBehavior.__init__(self, p)
        self.measureTask = Task('m1', self.lc)
        self.ticksSinceAcknowlegement = 200
        
    def executeBevahior(self):
        distance = self.measureTask.executeTask()
        
        if distance <= 60 and distance > 10 and self.ticksSinceAcknowlegement > 200:
            scanTask = Task('c1', self.lc)
            ScanTask('p' + str(1), scanTask)
            ScanTask('p' + str(150), scanTask)
            ScanTask('p' + str(1), scanTask)
            Task('p' + str(self.pc.getHeadRotate()), scanTask)
            Task('c2', scanTask)
            scanTask.executeTask()
            
            self.ticksSinceAcknowlegement = 0
            return 1
        
        self.ticksSinceAcknowlegement = self.ticksSinceAcknowlegement + 1
        
        return 0
      
class WallDetectBehavior(BaseBehavior):
    def __init__(self, p=None):
        BaseBehavior.__init__(self, p)
    
        self.measureTask = Task('m1', self.lc)
        
    def executeBevahior(self):
        distance = self.measureTask.executeTask()
        
        if self.pc.movingForward:
             
    #  Calc cuttoff dist from the current speed
            cuttoffDist = self.pc.getSpeed() / 8
    
            if distance <= cuttoffDist and distance > 0:
                print('Whoa Dog! Hold up! ' + str(cuttoffDist))
                stopTask = Task('c1', self.lc)
                MovementTask('f0', stopTask)
                stopTask.executeTask()
                return 1;
        return 0
      
class MoveTestBehavior(BaseBehavior):
    def __init__(self, p=None):
        BaseBehavior.__init__(self, p)
    
        self.measureTask = Task('m1', self.lc)
        
    def executeBevahior(self):
#         distance = self.measureTask.executeTask()
        
#         if distance <= 12 and distance > 0:
        movementTask = Task('c1', self.lc)
        MovementTask('f200', movementTask)
        w1 = Task('w1', movementTask)
        
        m2 = MovementTask('f0', w1)
        w2 = Task('w1', m2)
        
        m3 = MovementTask('b200', w2)
        Task('w1', m3)
        
        m4 = MovementTask('b0', movementTask)
        Task('w1', m4)
        
        movementTask.executeTask()
        
        return 1;
#         return 0
      
class MoveHeadTestBehavior(BaseBehavior):
    def __init__(self, p=None):
        BaseBehavior.__init__(self, p)
    
        self.measureTask = Task('m1', self.lc)
        
    def executeBevahior(self):
        t1 = Task('t110', self.lc)
        t11 = Task('p20', t1, True)
        Task('p110', t11)
        Task('t80', t11)
        t12 = Task('w1', t1, True)
        Task('p130', t12)
        Task('t140', t12)
        t13 = Task('w1', t1, True)
        Task('p20', t13)
        Task('t80', t13)
        t14 = Task('t135', t1, True)
        Task('t70', t14)
        Task('p130', t14)
        t1.executeTask();
        return 1
      
class MoveHeadTestBehavior2(BaseBehavior):
    def __init__(self, p=None):
        BaseBehavior.__init__(self, p)
    
        self.measureTask = Task('m1', self.lc)
        
    def executeBevahior(self):
        t1 = MovementTask('t110', self.lc)
        t11 = MovementTask('p20', t1, True)
        MovementTask('p110', t11)
        MovementTask('t80', t11)
        t12 = MovementTask('w1', t1, True)
        MovementTask('p130', t12)
        MovementTask('t140', t12)
        t13 = MovementTask('w1', t1, True)
        MovementTask('p20', t13)
        MovementTask('t80', t13)
        t14 = MovementTask('t135', t1, True)
        MovementTask('t70', t14)
        MovementTask('p130', t14)
        t1.executeTask();
        return 1
      
class LaserBlinkBehavior(BaseBehavior):
    def __init__(self, p=None):
        BaseBehavior.__init__(self, p)
    
        self.ticksSinceAcknowlegement = 3
    
    def executeBevahior(self):
        
        self.ticksSinceAcknowlegement = self.ticksSinceAcknowlegement + 1
        #print('laser tick ------' + str(self.ticksSinceAcknowlegement))
        
        if self.ticksSinceAcknowlegement == 2:
            #print('laser on' + str(self.ticksSinceAcknowlegement))
            t = Task('l1', self.lc)
            t.executeTask()
        elif self.ticksSinceAcknowlegement == 4:
            #print('laser off' + str(self.ticksSinceAcknowlegement))
            t = Task('l0', self.lc)
            t.executeTask()
            self.ticksSinceAcknowlegement = 0
            return 1;
        
        return 0
      
class MeasureTiltBehavior(BaseBehavior):
    def __init__(self, p=None):
        BaseBehavior.__init__(self, p)
        self.tiltAngleStart = round(self.pc.getHeadMeasuredTilt(10))
        self.lc.confidence.setCurrentReactionInterval(5)
        
        self.changeTollerance = 3
#         Task('c4', self.lc).executeTask()
        
    def added(self):
        self.tiltAngleStart = round(self.pc.getHeadMeasuredTilt(10))
        self.lc.confidence.setCurrentReactionInterval(7)
#       implement to reset values on add
        
    def removed(self):
        self.lc.confidence.setCurrentReactionInterval(4)
#       implement to set values on removal

    def executeBevahior(self):
        tiltAngle = round(self.pc.getHeadMeasuredTilt(2))
#         if not tiltAngle == self.tiltAngleStart:
        if tiltAngle <= (self.tiltAngleStart - self.changeTollerance) or tiltAngle > (self.tiltAngleStart + self.changeTollerance):
            servoAngle = self.pc.getHeadTilt()
            tiltDelta = round(self.tiltAngleStart-tiltAngle)
            newServoAngle = int(round(servoAngle + tiltDelta + 90))
            self.pc.clearFrames(self.pc.arduino.headYawServoPin)
#             print("  -Task created: " + self.job)
            Task('t' + str(newServoAngle), self.lc).executeTask()
        return 1
      
class BatteryCheckBehavior(BaseBehavior):
    def __init__(self, p=None):
        BaseBehavior.__init__(self, p)
        self.warningVoltage = 10.5
        self.criticalWarningVoltage = 10.1
        self.minOperatingVoltage = 10.0
        self.ticksSinceLastMeasure = 0
        
    def added(self):
        self.batteryVoltage = round(self.pc.getBatteryVoltage(100))
        
    def removed(self):
        self.lc.confidence.setCurrentReactionInterval(4)
#       implement to set values on removal

    def executeBevahior(self):
        if self.ticksSinceLastMeasure > 200:
            self.ticksSinceLastMeasure = 0;
            self.batteryVoltage = round(self.pc.getBatteryVoltage(10))

            if self.batteryVoltage <= self.warningVoltage:
                if self.batteryVoltage > self.criticalWarningVoltage:
                    print("Warning: battery is low!: " + str(self.batteryVoltage))
                else:
                    if self.batteryVoltage > self.minOperatingVoltage:
                        print("Warning: battery is critically low!!!: " + str(self.batteryVoltage))
                    else:
                        print("Warning: battery is Dead, shutting down system!: " + str(self.batteryVoltage))
            else:
                print("Battery level is all good: " + str(self.batteryVoltage))
        
        self.ticksSinceLastMeasure = self.ticksSinceLastMeasure + 1
        
        return 1