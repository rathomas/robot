'''
Created on Aug 16, 2013

@author: rthomas
'''
import threading
from Tkinter import Tk
from Tkconstants import ALL


# --Visualizer Window ----    
# Visualizer Window thread class:
class VisualizerWindowTread( threading.Thread ):
    def __init__(self, lc):
        self.lc = lc
        threading.Thread.__init__(self)
        
    def callback(self):
        self.root.quit()
        
    def run(self):
        self.root=Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        self.dataWindow = VisualizerWindowTread(self.root)
#         self.dataWindow = Label(self.dataWindow, text="Scoobie-Doo-Bot")
#         self.dataWindow.pack()
#         self.dataWindow = Canvas(self.dataWindow, width=1000, height=1000)
#         self.dataWindow.pack()
        
#         self.viewBoundaryData()
        
        self.root.mainloop()
   
    def listBoundaryData(self):
        for b in self.lc.boundaryData:
            print(str(b))
        return 1
     
    def viewBoundaryData(self):
        if not self.dataWindow:
            self.run()
            
        for i in self.lc.boundaryData:
            self.createBoundaryVisual(i)
        return 1
     
    def createBoundaryVisual(self, i):
        if self.dataWindow:
            scale = 4
            self.dataWindow.create_line(300, 250, i['bx']+300, i['by']+250)
            self.dataWindow.create_line(300, 450, 300-(i['bx']*scale), 450-(i['by']*scale))
            return 1
        return 0
     
    def clearBoundaryView(self):
        self.dataWindow.delete(ALL)
        return 1
 
    def removeBoundaryWindow(self):
        self.root.destroy()