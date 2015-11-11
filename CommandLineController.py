'''
Created on Aug 16, 2013

@author: rthomas
'''
import rpyc
from RobotConfig import *
from VisualizerThread import VisualizerWindowTread
from ProxiedPhysicalController import ProxiedPhysicalController
from DisconnectedPhysicalController import DisconnectedPhysicalController
from rpyc.utils.server import ThreadedServer
import logging
from PhysicalController import PhysicalController
import serial
from SerialStream import SerialStream
from ExecutableCommandLineService import ExecutableCommandLineService
from RobotMasterService import RobotMasterService

# from rpyc.utils import classic
# from rpyc.core.service import SlaveService

class CommandLineController:
    def __init__(self, master, pc):
        print("CommandLineController created.")
        self.master = master
        self.pc = pc
        self.previousCommands = []
        self.serialConn = None
        self.executableCommandLineService = None
       
    def createService(self, connectPort=RPYC_CONN_PORT):
        self.executableCommandLineService = ExecutableCommandLineService(self)
        self.commandLineService = ThreadedServer(self.executableCommandLineService, port=connectPort, logger=logging.getLogger("ExecutableCommandLine." + str(connectPort)))
        self.commandLineService.start()
        return 1
       
    def createStreamService(self):
        print("CommandLineController.createStreamService()")

        self.serialConn = self.createSerialConn()
        
        print("Serial Connection Open: " + str(self.serialConn))
        self.serialStream = SerialStream(self.serialConn)
           
#         self.robotTestService = RobotTestService(self)
        self.executableCommandLineService = ExecutableCommandLineService(self)
        print("Serial Connection Service Started: " + str(self.executableCommandLineService))
        
        try:
#             self.conn = rpyc.connect_stream(self.serialStream, service=RobotTestService, config={'allow_all_attrs': True})  
            self.conn = rpyc.connect_stream(self.serialStream, self.executableCommandLineService, config={'allow_all_attrs': True}) 
            self.remote = self.conn.root
        
        except:
            print(" -could not connect")
            return 1
        
#         self.commandLineService = ThreadedServer(self.conn)
#         self.commandLineService.start()
        return 1

    def stopService(self):
        self.commandLineService.stop()
        self.commandLineService = None
        return 1
       
    def connect(self, remoteHost, remotePort=RPYC_CONN_PORT):
#         self.conn = rpyc.classic.connect(remoteHost)
#         self.conn = rpyc.connect(remoteHost, remotePort, CommandLineService)
        try:
            self.conn = rpyc.connect(remoteHost, remotePort, config={'allow_public_attrs': True})
#             self.conn = rpyc.connect(remoteHost, remotePort, CommandLineService)
        except:
            print(" -could not connect")
            return 1
        #Set Physical Controller State

        self.pc = ProxiedPhysicalController(self.pc.master)
        print("Connected.")
        return 1
    
    def connectStream(self):
        print("CommandLineController.connectStream()")

        self.serialConn = self.createSerialConn()
        self.serialStream = SerialStream(self.serialConn)
        
        try:
            self.conn = rpyc.connect_stream(self.serialStream, service=RobotMasterService, config={'allow_all_attrs': True}) 
#             self.robot = self.conn.root
        except:
            print(" -could not connect")
            return 1
        
        # Test exchange text
#         sleep(1)
#         print("Checking RPyC")
#         print(" -Request Greeting: " + self.conn.root.test())
#         print("Robot is: " + str(self.robot)) 
        
#         print("Pinging Remote Robot: " + )
#         try:
#             self.serialStream.pi 
#         
        #Set Physical Controller State to proxied
        master = self.master
        self.pc = ProxiedPhysicalController()
        self.pc.registerMaster(master)
        print("Connected.")
        return 1
    
    def disconnect(self):
        self.conn.close()
        
        #Set Physical Controller State
        self.pc = DisconnectedPhysicalController(self.pc.master)
        print("Not Connected.")

    def executeCommand(self, command, traceCommand=False):
        #Not Connected 
        if isinstance(self.pc, DisconnectedPhysicalController) and command.count("connect") == 0:
            print(" -Action not available: not connected.")
            return 1
        #Run the command remotly through RPyC 
        elif isinstance(self.pc, ProxiedPhysicalController):
            print(" -executing command remotely:")
            return self.conn.root.executeCommand(command, traceCommand)
        elif isinstance(self.pc, PhysicalController):
            print(" -executing command locally:")
            commandResult = 0
    #         commandValue = -1
    
            commandType = "".join([x for x in command if x.isalpha()])
            commandValueStr = "".join([x for x in command if not x.isalpha()])
            
            if traceCommand: self.broadcastPrint ("command: " + commandType +" value=" + commandValueStr)
                    
            if commandType == "connect" and commandValueStr != None:
                if traceCommand: self.broadcastPrint ("connect " + commandValueStr)
                commandResult = self.pc.connect(commandValueStr)
                    
            if commandType == "server" and commandValueStr != None:
                if traceCommand: self.broadcastPrint ("server " + commandValueStr)
                commandResult = self.pc.createServer(commandValueStr)
                
            if commandType == "p" and commandValueStr != None:
                if traceCommand: self.broadcastPrint ("pan " + commandValueStr)
                commandResult = self.pc.rotateHead(int(commandValueStr))
                    
            if commandType == "qp" and commandValueStr != None:
                if traceCommand: self.broadcastPrint ("pan " + commandValueStr)
                commandResult = self.pc.queueRotateHead(int(commandValueStr))
            
            elif commandType == "t" and commandValueStr != None: 
                if traceCommand: self.broadcastPrint ("tilt " + commandValueStr)
                commandResult = self.pc.tiltHead(int(commandValueStr))
    
            elif commandType == "qt" and commandValueStr != None: 
                if traceCommand: self.broadcastPrint ("tilt " + commandValueStr)
                commandResult = self.pc.queueTiltHead(int(commandValueStr))
            
            elif commandType == "f" and commandValueStr != None: 
                if traceCommand: self.broadcastPrint ("forward " + commandValueStr)
                commandResult = self.pc.driveForward(int(commandValueStr))
            
            elif commandType == "b" and commandValueStr != None: 
                if traceCommand: self.broadcastPrint ("backward " + commandValueStr)
                commandResult = self.pc.driveBackward(int(commandValueStr))
            
            elif commandType == "u" and commandValueStr != None: 
                if traceCommand: self.broadcastPrint ("set curve " + commandValueStr)
                commandResult = self.pc.setCurve(int(commandValueStr))
            
            elif commandType == "g" and commandValueStr != None: 
                if traceCommand: self.broadcastPrint ("turn left " + commandValueStr)
                commandResult = self.pc.turnLeft(int(commandValueStr))
            
            elif commandType == "h" and commandValueStr != None: 
                if traceCommand: self.broadcastPrint ("turn right " + commandValueStr)
                commandResult = self.pc.turnRight(int(commandValueStr))
            
            elif commandType == "m" and commandValueStr != None: 
                if traceCommand: self.broadcastPrint ("ping " + commandValueStr)
                commandResult = self.pc.getMeasuredPingDistance(int(commandValueStr))
            
            elif commandType == "q" and commandValueStr != None: 
                if traceCommand: self.broadcastPrint ("pir sensor " + commandValueStr)
                commandResult = self.pc.pirSensorEnabled(int(commandValueStr))
            
            elif commandType == "k" and commandValueStr != None: 
                if traceCommand: self.broadcastPrint ("read gyro " + commandValueStr)
                commandResult = self.pc.readGyro(int(commandValueStr))
            
            elif commandType == "n" and commandValueStr != None: 
                if traceCommand: self.broadcastPrint ("tilt " + commandValueStr)
                commandResult = self.pc.getHeadMeasuredTilt(int(commandValueStr))
            
            elif commandType == "l" and commandValueStr != None: 
                if traceCommand: self.broadcastPrint ("laser " + commandValueStr)
                commandResult = self.pc.laserEnabled(int(commandValueStr), True)
            
            elif commandType == "c" and commandValueStr != None: 
                if traceCommand: self.broadcastPrint ("confidence " + commandValueStr)
                commandResult = self.pc.lc.confidence.setCurrentRating(int(commandValueStr))
            
            elif commandType == "i" and commandValueStr != None: 
                if traceCommand: self.broadcastPrint ("interval " + commandValueStr)
                commandResult = self.pc.lc.confidence.setCurrentReactionInterval(int(commandValueStr))
            
            elif commandType == "w" and commandValueStr != None: 
                if traceCommand: self.broadcastPrint ("wait " + commandValueStr)
                commandResult = self.pc.wait(int(commandValueStr))
            
            elif commandType == "a": 
                if traceCommand: self.broadcastPrint ("adding behavior:")
                commandResult = self.pc.lc.addBehavior(int(commandValueStr))
            
            elif commandType == "d": 
                if traceCommand: self.broadcastPrint ("removing behavior:")
                commandResult = self.pc.lc.removeBehavior(int(commandValueStr))
            
            elif commandType == "s": 
                if traceCommand: self.broadcastPrint ("scan commands :")
                commandResult = self.execute(True)
            
            elif commandType == "x": 
                if traceCommand: self.broadcastPrint ("clear boundary data :")
                commandResult = self.visualizerWindowTread.removeBoundaryWindow()
    
            elif commandType == "y": 
                if traceCommand: self.broadcastPrint ("list boundary data :")
                commandResult = self.visualizerWindowTread.listBoundaryData()
    
            elif commandType == "z": 
                if traceCommand: self.broadcastPrint ("show boundary data :")
                commandResult = self.showVisualizerWindow()
                
            elif commandType == "r": 
                if traceCommand: self.broadcastPrint ("running commands:")
                commandResult = self.execute()
                
            elif commandType == "shutdown": 
                if traceCommand: self.broadcastPrint ("shutdown:")
                commandResult = self.pc.shutdownSystem(False)
                
            elif commandType == "restart": 
                if traceCommand: self.broadcastPrint ("shutdown:")
                commandResult = self.pc.shutdownSystem(True)
                
            elif commandType == "bat": 
                if traceCommand: self.broadcastPrint("battery voltage :")
                if commandValueStr:
                    commandResult = self.pc.getBatteryVoltage(float(commandValueStr))
                else:
                    commandResult = self.pc.getBatteryVoltage()
                if commandResult == 0:
                    commandResult = 1
                
            elif commandType == "exit": 
                if isinstance(self.pc, ProxiedPhysicalController):
                    commandResult = self.pc.disconnect()
                else:
                    if traceCommand: 
                        self.broadcastPrint ("Exiting System!!")
                        
                    self.broadcastPrint("Bye.") 
                    self.broadcastPrint("") 

                    self.master.alive = False
                
            # deal wiith oincorect commands                     
            if commandType != "exit": 
                if commandResult == 0:
                    self.broadcastPrint("Unknown Command: '" + commandType + "'") 
                    commandResult = 1
                else:
                    self.previousCommands.append(command)
                
            return commandResult
    
    def execute(self, usePing=False, useAccelerometer=False):
        self.pc.executeFramesInParallel(self.pc.lc.confidence, usePing, useAccelerometer)
        return 1
    
    def getPhysicalController(self):
        return self.pc
    
    def showVisualizerWindow(self):
        if not self.visualizerWindowTread:
            self.visualizerWindowTread = VisualizerWindowTread(self).start()
            return 1
        return 0
      
    def destroy(self):
        if self.conn:
            self.disconnect()
            
        if self.commandLineService:
            self.commandLineService.stop();
        
        del self
        
    def __del__(self):
        self.commandLineThread.kill()
        self.serialStream.close()
        self.serialConn.close()
        
        try:
            UART.close()
        except:
            pass
            

    ###
    # UTIL   
    ###
    def createSerialConn(self):
        serialConn = None
        
        for xb in XBEE_INTERFACES:
            try:
                print("Tying to connect to Wireless: " + xb['type'] + " on " + xb['dev'] + " ...")
                
                serialConn = serial.Serial(port=xb['dev'], baudrate=xb['baud'])
                serialConn.close()
                serialConn.open()
                if serialConn.isOpen():
                    print("Wireless Serial is open: " + xb['dev'])
                    return serialConn
            except:
                print(" ... Failed")
                pass
            else:
                return serialConn
#         raise AttributeError

    def broadcastPrint(self, s):
#         if self.executableCommandLineService and self.executableCommandLineService.isConnected():
#             print(self.remote.broadcastPrint(s))
#         else:
        print(s)