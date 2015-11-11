'''
Created on Aug 15, 2013

@author: rthomas
'''

class BaseTask:
    def __init__(self, job, p=None, parallel=False):
        self.job = job
        self.parentTask = p
        self.parallel = parallel
        self.subTasks = []
        self.runMode = 'r'
 
        if isinstance(self.parentTask, BaseTask): 
            self.lc = self.parentTask.lc;
            self.generation = self.parentTask.generation + 1
            self.parentTask.addSubTask(self)
#             print("  " * self.generation + "  -SubTask created: " + self.job)
        else:
            self.lc = self.parentTask;
            self.generation = 0
#             print("  -Task created: " + self.job)
      
    def executeTask(self):
        self.commandResult = 0
        
        #Create Frames 
        commandResult = self.lc.executeCommand(self.job)
        
        #Execute Frames 
        if not isinstance(self.parentTask, BaseTask) or not self.parentTask.parallel:
            self.lc.executeCommand(self.runMode)
            
        for t in self.subTasks:
            t.executeTask()

        #execute the run command to dump the commands into execution
        if self.parallel:
            self.lc.executeCommand(self.runMode)
            
        return commandResult
    
    def addSubTask(self, t):
        t.parentTask = self
        self.subTasks.append(t)
        
    def traceSelf(self):
        print("  " * self.generation + str(self) + ": " + self.job);
        for st in self.subTasks: st.traceSelf()
        
class Task(BaseTask):
    def __init__(self, job, p=None, parallel=False):
        BaseTask.__init__(self, job, p, parallel)
        
class ScanTask(BaseTask):
    def __init__(self, lc, job, p=None, parallel=False):
        BaseTask.__init__(self, job, p, parallel)
        self.runMode = 's'
        
class MovementTask(BaseTask):
    def __init__(self, job, p=None, parallel=False):
        BaseTask.__init__(self, job, p, parallel)

