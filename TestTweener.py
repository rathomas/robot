'''
Created on Apr 22, 2013

@author: rthomas
'''
import time
from util.pyTweener import Tweener
from Tkinter import Canvas, Tk, Label

class TestObj:
    def __init__(self):
        print("TestObj created.")
        self.setX(1)
        self.setY(1)
        self.dataWindow = None
        
    def getX(self):
        return self.x
   
    def setX(self, nx):
        self.x = nx
        
    def getY(self):
        return self.y
   
    def setY(self, ny):
        self.y = ny
   
    def update(self):
#         print("->")
#         print("TestObj.update()")
        self.setX(self.getX() + 1)
        
    def complete(self):
        print("TestObj.complete()")

    def toString(self):
        print("TestObj.toString()")
        
def main():
    print("TweenTest!...")
    
    root = Tk()
    dataWindow = Label(root, text="TweenTest!")
    dataWindow.pack()
    dataWindow = Canvas(root, width=1000, height=1000)
    dataWindow.pack()
    
    tObj=TestObj()
    
    tw = Tweener()
    mt = tw.addTween( tObj, setY=1000, tweenTime=1.0, tweenType=tw.OUT_EXPO, y=1, onCompleteFunction=tObj.complete, onUpdateFunction=tObj.update )
    
    
    s = time.clock()
    changed = False
    while tw.hasTweens():
#         print tObj.getX(), tObj.getY()
        tm = time.clock()
        d = tm - s
        s = tm
        tw.update( d )
        if mt.delta > 1.0 and not changed:
            tweenable = mt.getTweenable( "setY" )
            changed = True
        #print mt.duration,
        dataWindow.create_line(tObj.getX()/10, 1000, tObj.getX()/10, 1000-tObj.getY())
#         time.sleep(0.06)
        
#     print (tObj.getX(), tObj.getY())
    root.mainloop();
    
if __name__ == '__main__': main()
    