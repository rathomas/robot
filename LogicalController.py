'''
Created on Aug 16, 2013

@author: rthomas
'''
from Tasks import Task
from Behaviors import AcknowlegePresenseBehavior, DontTouchBehavior,\
    ScanBehavior, MoveTestBehavior, WallDetectBehavior, LaserBlinkBehavior,\
    MeasureTiltBehavior, MoveHeadTestBehavior, BatteryCheckBehavior,\
    MoveHeadTestBehavior2

    
class LogicalController:
    def __init__(self, master, pc):
        print("LogicalController created.")
        self.master = master
        self.pc = pc
        self.confidence = Confidence()
        self.confidence.setCurrentRating(1)
        self.confidence.setCurrentReactionInterval(2)

        self.registeredBehaviors = [
                                        BatteryCheckBehavior(self),
                                        AcknowlegePresenseBehavior(self),   # a0, d0
                                        DontTouchBehavior(self),            # a1, d1
                                        ScanBehavior(self),                 # a2, d2
                                        MoveTestBehavior(self),             # a3, d3
                                        WallDetectBehavior(self),           # a4, d4
                                        LaserBlinkBehavior(self),           # a5, d5
                                        MeasureTiltBehavior(self),          # a6, d6
                                        MoveHeadTestBehavior(self),         # a7, d7
                                        MoveHeadTestBehavior2(self)         # a7, d7
                                    ]   
          
        print("--Quick Assign Behaviors:")
        for rb in self.registeredBehaviors: rb.traceSelf()
            
        self.behaviors = []
        self.boundaryData = []
        
    def addBehavior(self, i):
        try:
            self.behaviors.index(self.registeredBehaviors[i])
            print(str(self.registeredBehaviors[i]) + ' behavior already active')
        except:
            self.behaviors.append(self.registeredBehaviors[i])
            self.registeredBehaviors[i].added();
            print('adding behavior ' + str(self.registeredBehaviors[i]))
#             print('error adding behavior with index=' + str(i))
        return 1
        
    def removeBehavior(self, i):
        try:
            self.registeredBehaviors[i].removed();
            del self.behaviors[self.behaviors.index(self.registeredBehaviors[i])]
            print('removing behavior ' + str(self.registeredBehaviors[i]))
        except:
            print('error removing behavior with index=' + str(i))
        return 1
     
    def executeBehaviors(self):
        for b in self.behaviors:
            self.executeBehavior(b)
        
    def executeBehavior(self, behavior):
        behavior.executeBevahior()
        
    def executeTask(self, task):
        task.executeTask()
        
    def executeCommand(self, command, traceCommand=False):
        self.master.commandLineController.executeCommand(command, traceCommand)
        
    def getPhysicalController(self):
        return self.pc
    
    def destroy(self):
        del self
    
class Confidence:
    def __init__(self,r=0,i=.1):
        self.rating = r
        self.reactionInterval = i
#         print("Confidence created at rating:" + str(self.rating))
        
    def increase(self,a=1):
        self.rating += a
#         self.report()
        
    def decrease(self,a=1):
        self.rating += a
#         self.report()

    def getCurrentRating(self):
        return self.rating

    def setCurrentRating(self,r):
        self.rating = r
#         self.report()
        return 1

    def getCurrentReactionInterval(self):
        return self.reactionInterval * 100

    def getCurrentReactionIntervalSleep(self):
        return self.reactionInterval

    def setCurrentReactionInterval(self,r):
        self.reactionInterval = r / float(100)
        self.report()
        return 1

    def report(self):
        print("Confidence rating is:" + str(self.rating) + " with reaction interval of " + str(self.getCurrentReactionInterval()))

    
    