'''
Created on Aug 16, 2013

@author: rthomas
'''
class TweenedProxy:
    def __init__(self):
        print("TweenedProxy created.")
        self.setValue(1)
        
    def getValue(self):
        return self.v
   
    def setValue(self, v):
        self.v = v

    def update(self):
        print("TweenedProxy.update()")
        
    def complete(self):
        print("TweenedProxy.complete()")

    def toString(self):
        print("TweenedProxy.toString()")