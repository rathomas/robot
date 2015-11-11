'''
Created on Oct 2, 2013

@author: rthomas
'''
from pyfirmata import Arduino, ArduinoMega

## Arduino
ARDUINO_BAUD_RATE = 57600
ARDUINO_DEF_CONTROLLER = {'type': Arduino,
                          'dev': '/dev/tty.usbmodem1421',
                          'baud': ARDUINO_BAUD_RATE
                         }
ARDUINO_DEF_ROBOT = {'type': ArduinoMega,
#                      'dev': '/dev/ttyACM0',
                     'dev': '/dev/tty.usbmodem1411',
                     'baud': ARDUINO_BAUD_RATE
                    }
ARDUINO_DEF_ROBOT2 = {'type': ArduinoMega,
                     'dev': '/dev/ttyACM1',
                     'baud': ARDUINO_BAUD_RATE
                    }
ARDUINOS = [ARDUINO_DEF_CONTROLLER, ARDUINO_DEF_ROBOT]

## Socket
SOCKET_ROBOT_HOST = "localhost"
SOCKET_ROBOT_PORT = 18860

## Xbee
XBEE_BAUD_RATE = 38400;
XBEE_DEF_CONTROLLER = {'type': 'XBee Pro 900 (local)',
                       'dev': '/dev/tty.usbserial-13W9L5V2',
                       'baud': XBEE_BAUD_RATE
                      }
XBEE_DEF_ROBOT = {'type': 'XBee Pro 900 (remote)',
                   'dev': '/dev/ttyO2',
                   'baud': XBEE_BAUD_RATE
                 }
XBEE_INTERFACES = [XBEE_DEF_CONTROLLER, XBEE_DEF_ROBOT]

RPYC_CONN_PORT = 18861