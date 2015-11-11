'''
Created on Aug 16, 2013

@author: rthomas
'''
from pyfirmata.mockup import MockupBoard
from pyfirmata.util import Iterator
from RobotConfig import ARDUINOS

class ArduinoConnector:

    def __init__(self):
        print("ArduinoConnector created.")
        
        self.connected = False

        self.board = None
        
#         try:
        self.board = self.connectArduino()
#         except:
#         except AttributeError:
#             pass

        if self.board:
            print(self.board)
            self.connected = True
        else:
            print("ERROR: Arduino not found!")
            
            print("Arduino not connected!! Using Simulation MODE")
#             print("Connected to Arduino: " + str(self.board.get_firmata_version()))

            self.board = MockupBoard()
            
        board = self.board

        self.config = ArduinoConfiguration()
        if self.connected:
            #Load Configuration
#             self.config = ArduinoConfiguration()
            config = self.config
    
            #General Firmata Config
            board.general_config(config.arduinoLoopDelay)
            
            #Battery monitor    
    #         board.digital_out_config(config.laserControlPin)
    #         board.analog_in_config(absToAnalogPinNumber(config.batteryMonitorPin))
            board.analog_in_config(0)
            
            #LASER    
    #         board.digital_out_config(config.laserControlPin)
            board.digital_out_config(config.rightDriveDirectionPin)
                
            #SERVOS
            board.head_servos_config(config.headPanServoPin, config.headYawServoPin)
            
            #PIR SENSOR
    #         board.pir_config(config.pirSensorEnablePin, config.pirSensorPin)
            
            #PING
            
            #ACCELEROMETER (HEAD)
    #         board.pulse_config(config.xAxisPin, 1)
                
    #         board.pulse_config(config.yAxisPin, 1)
            
            #GYROSCOPE (HEAD)
            board.gyro_config(config.gyroI2CReadDelay, config.gyroI2CAddress, config.gyroWritePin, config.gyroReadPin)
            
            #DIRECTION
            
            #BRAKE
    
            #SPEED
            board.motor_config(config.leftDriveDirectionPin,
                                        config.rightDriveDirectionPin, 
                                        config.leftDriveBrakePin, 
                                        config.rightDriveBrakePin,
                                        config.leftDriveSpeedPin,
                                        config.rightDriveSpeedPin);
    #         
            #Start pyfirmata iteration
            iterator = Iterator(board)
            iterator.start()
            
    def connectArduino(self):
        boardConn = None
        
        for a in ARDUINOS:
            try:
                print("Tying to connect to Arduino: " + a['dev'] + " ...")
                boardConn = a['type'](a['dev'], baudrate=a['baud'])
            except:
                print(" ... Failed")
                pass
            else:
                return boardConn
#         raise AttributeError
            
    def disconnectArduino(self):
        if self.board:
            self.board = None
            self.connected = False
        
    def absToAnalogPinNumber(self, p):
            if p >= 14:
                return p-14
            else:
                return -1

class ArduinoConfiguration:

    def __init__(self):
            
        #General Firmata Config
            self.arduinoLoopDelay = 100 #(>10ms)
            
    ## PINS CONFIG -----------------##
        
        #Battery Monitor
            self.batteryMonitorPin = 17
            
        #ACCELEROMETER (HEAD)
            self.xAxisPin = 2
            self.yAxisPin = 10
            
        #LASER    
#             self.laserControlPin = 13
            self.laserControlPin = 12
#             self.laserControlPin = 4
            
        #SERVOS
            self.headPanServoPin = 10
            self.headYawServoPin = 13
#             self.headPanServoPin = 5
#             self.headYawServoPin = 6
        
        #PING
            self.headPingPin = 7
        
        #PIR SENSOR
            self.pirSensorEnablePin = 15
            self.pirSensorPin = 16
        
#         GYROSCOPE (HEAD)
            self.gyroReadPin = 18   #SDA
            self.gyroWritePin = 19  #SCL
            self.gyroI2CReadDelay = 50
            self.gyroI2CAddress = 105
          
        ## MOTOR CONTROLLER  
        #DIRECTION
#             self.leftDriveDirectionPin = 13
            self.leftDriveDirectionPin = 12
            self.rightDriveDirectionPin = 4 ##testing
#             self.rightDriveDirectionPin = 12 ##testing
             
        #BRAKE
            self.leftDriveBrakePin = 9
            self.rightDriveBrakePin = 8
             
        #SPEED
            self.leftDriveSpeedPin = 3
            self.rightDriveSpeedPin = 11
