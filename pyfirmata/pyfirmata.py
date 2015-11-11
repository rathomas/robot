
import inspect
import time
import itertools
from locale import str
from util import to_two_bytes, from_two_bytes, two_byte_iter_to_str
from serial.urlhandler.protocol_hwgrep import Serial
from boards import BOARDS

# Message command bytes - straight from Firmata.h
DIGITAL_MESSAGE = 0x90      # send data for a digital pin
ANALOG_MESSAGE = 0xE0       # send data for an analog pin (or PWM)
DIGITAL_PULSE = 0x91        # SysEx command to send a digital pulse

# PULSE_MESSAGE = 0xA0      # proposed pulseIn/Out msg (SysEx)
# SHIFTOUT_MESSAGE = 0xB0   # proposed shiftOut msg (SysEx)
REPORT_ANALOG = 0xC0        # enable analog input by pin #
REPORT_DIGITAL = 0xD0       # enable digital input by port pair
START_SYSEX = 0xF0          # start a MIDI SysEx msg
SET_PIN_MODE = 0xF4         # set a pin to INPUT/OUTPUT/PWM/etc
END_SYSEX = 0xF7            # end a MIDI SysEx msg
REPORT_VERSION = 0xF9       # report firmware version
SYSTEM_RESET = 0xFF         # reset from MIDI
QUERY_FIRMWARE = 0x79       # query the firmware name

EXTENDED_ANALOG = 0x6F      # analog write (PWM, Servo, etc) to any pin
PIN_STATE_QUERY = 0x6D      # ask for a pin's current mode and value
PIN_STATE_RESPONSE = 0x6E   # reply with pin's current mode and value
CAPABILITY_QUERY = 0x6B     # ask for supported modes and resolution of all pins
CAPABILITY_RESPONSE = 0x6C  # reply with supported modes and resolution
ANALOG_MAPPING_QUERY = 0x69 # ask for mapping of analog to pin numbers
ANALOG_MAPPING_RESPONSE = 0x6A  # reply with mapping info
SYSEX_NON_REALTIME = 0x7E   # MIDI Reserved for non-realtime messages
# these are DEPRECATED to make the naming more consistent
FIRMATA_STRING = 0x71       # same as STRING_DATA
SYSEX_I2C_REQUEST = 0x76    # same as I2C_REQUEST
SYSEX_I2C_REPLY = 0x77      # same as I2C_REPLY
SYSEX_SAMPLING_INTERVAL = 0x7A  # same as SAMPLING_INTERVAL

# extended command set using sysex (0-127/0x00-0x7F)
# 0x00-0x0F reserved for user-defined commands */
SERVO_CONFIG = 0x70         # set max angle, minPulse, maxPulse, freq
STRING_DATA = 0x71          # a string message with 14-bits per char

PING_CONFIG = 0x80          # ping config
PING_REQUEST = 0x72         # ping request
PING_REPLY = 0x73           # ping reply

PULSE_CONFIG = 0x81         # pulse config
PULSE_REQUEST = 0x62        # pulse request
PULSE_REPLY = 0x63          # pulse reply

PIR_CONFIG = 0x82           # pulse config


GYRO_REQUEST = 0x56         # send an Gyro read/write request
GYRO_REPLY = 0x57           # a reply to a Gyro read request
GYRO_CONFIG = 0x58          # config Gyro settings such as delay times and power pins

GYRO_WRITE = 0x00                   # B00000000
GYRO_READ = 0x08                    # B00001000
GYRO_READ_CONTINUOUSLY = 0x10       # B00010000
GYRO_STOP_READING = 0x18            # B00011000
GYRO_READ_WRITE_MODE_MASK = 0x18    # B00011000
GYRO_10BIT_ADDRESS_MODE_MASK = 0x20 # B00100000

CTRL_REG1 = 0x20  #32
CTRL_REG2 = 0x21  #33
CTRL_REG3 = 0x22  #34
CTRL_REG4 = 0x23  #35
CTRL_REG5 = 0x24  #36

GYRO_X_H = 0x29 # MSB's
GYRO_Y_H = 0x2B
GYRO_Z_H = 0x2D
GYRO_X_L = 0x28 # LSB's 
GYRO_Y_L = 0x2A
GYRO_Z_L = 0x2C

SHIFT_DATA = 0x75           # a bitstream to/from a shift register
I2C_REQUEST = 0x76          # send an I2C read/write request
I2C_REPLY = 0x77            # a reply to an I2C read request
I2C_CONFIG = 0x78           # config I2C settings such as delay times and power pins
REPORT_FIRMWARE = 0x79      # report name and version of the firmware
SAMPLING_INTERVAL = 0x7A    # set the poll rate of the main loop
SYSEX_NON_REALTIME = 0x7E   # MIDI Reserved for non-realtime messages
SYSEX_REALTIME = 0x7F       # MIDI Reserved for realtime messages

#define I2C_WRITE B00000000
I2C_WRITE = 0x00
#define I2C_READ B00001000
I2C_READ = 0x08
#define I2C_READ_CONTINUOUSLY B00010000
I2C_READ_CONTINUOUSLY = 0x10
#define I2C_STOP_READING B00011000
I2C_STOP_READING = 0x18
#define I2C_READ_WRITE_MODE_MASK B00011000
I2C_READ_WRITE_MODE_MASK = 0x18
#define I2C_10BIT_ADDRESS_MODE_MASK B00100000
I2C_10BIT_ADDRESS_MODE_MASK = 0x20

# Pin modes.
# except from UNAVAILABLE taken from Firmata.h
UNAVAILABLE = -1 
INPUT = 0          # as defined in wiring.h
OUTPUT = 1         # as defined in wiring.h
ANALOG = 2         # analog pin in analogInput mode
PWM = 3            # digital pin in PWM output mode
SERVO = 4          # digital pin in SERVO mode
I2C = 5            # digital pin in I2C mode
SHIFT = 6          # digital pin in SHIFT mode
PING = 7           # digital pin in PING mode
PULSE = 8          # digital pin in PULSE mode
PIR = 9           # digital pin in PIR mode
GYRO = 10         # digital pin in GYRO mode

# Pin types
DIGITAL = OUTPUT   # same as OUTPUT below
# ANALOG is already defined above

# Time to wait after initializing serial, used in Board.__init__
BOARD_SETUP_WAIT_TIME = 3

class PinAlreadyTakenError(Exception):
    pass

class InvalidPinDefError(Exception):
    pass
    
class NoInputWarning(RuntimeWarning):
    pass
    
class Board(object):
    """
    Base class for any board
    """
    firmata_version = None
    firmware = None
    firmware_version = None
    _command_handlers = {}
    _command = None
    _stored_data = []
    _parsing_sysex = False
    _ping_distance = 0
    _pulse_duration = 0
    
    gyroResultX_H = 0
    gyroResultX_L = 0
    gyroResultY_H = 0
    gyroResultY_L = 0
    gyroResultZ_H = 0
    gyroResultZ_L = 0

    msbRegisters = {'x':GYRO_X_H, 'y':GYRO_Y_H, 'z':GYRO_Z_H}
    lsbRegisters = {'x':GYRO_X_L, 'y':GYRO_Y_L, 'z':GYRO_Z_L}
    
    msbResults = {'x':gyroResultX_H, 'y':gyroResultY_H, 'z':gyroResultZ_H}
    lsbResults = {'x':gyroResultX_L, 'y':gyroResultY_L, 'z':gyroResultZ_L}

    axisMap = ['x','y','z']
    bitGroups = [msbRegisters, lsbRegisters, msbResults, lsbResults]
    
    def __init__(self, port, layout, baudrate=57600, name=None):
        self.sp = Serial(port, baudrate)
        # Allow 5 secs for Arduino's auto-reset to happen
        # Alas, Firmata blinks it's version before printing it to serial
        # For 2.3, even 5 seconds might not be enough.
        # TODO Find a more reliable way to wait until the board is ready
        self.pass_time(BOARD_SETUP_WAIT_TIME)
        self.name = name
        if not self.name:
            self.name = port
        self.setup_layout(layout)
        # Iterate over the first messages to get firmware data
        while self.bytes_available():
            self.iterate()
        # TODO Test whether we got a firmware name and version, otherwise there 
        # probably isn't any Firmata installed
        
    def __str__(self):
        return "Board %s on %s" % (self.name, self.sp.port)
        
    def __del__(self):
        ''' 
        The connection with the a board can get messed up when a script is
        closed without calling board.exit() (which closes the serial
        connection). Therefore also do it here and hope it helps.
        '''
        self.exit()
        
    def send_as_two_bytes(self, val):
        self.sp.write(chr(val % 128) + chr(val >> 7))
        
    def setup_layout(self, board_layout):
        """
        Setup the Pin instances based on the given board-layout. Maybe it will
        be possible to do this automatically in the future, by polling the
        board for its type.
        """
        # Create pin instances based on board layout
        self.analog = []
        for i in board_layout['analog']:
            self.analog.append(Pin(self, i))

        self.digital = []
        self.digital_ports = []
        for i in xrange(0, len(board_layout['digital']), 8):
            num_pins = len(board_layout['digital'][i:i+8])
            port_number = i / 8
            self.digital_ports.append(Port(self, port_number, num_pins))

        # Allow to access the Pin instances directly
        for port in self.digital_ports:
            self.digital += port.pins
        
        # Setup PWM pins
        for i in board_layout['pwm']:
            self.digital[i].PWM_CAPABLE = True

        # Disable certain ports like Rx/Tx and crystal ports
        for i in board_layout['disabled']:
            self.digital[i].mode = UNAVAILABLE

        # Create a dictionary of 'taken' pins. Used by the get_pin method
        self.taken = { 'analog' : dict(map(lambda p: (p.pin_number, False), self.analog)),
                       'digital' : dict(map(lambda p: (p.pin_number, False), self.digital)) }

        # Setup default handlers for standard incoming commands
        self.add_cmd_handler(ANALOG_MESSAGE, self._handle_analog_message)
        self.add_cmd_handler(ANALOG_MAPPING_RESPONSE, self._handle_analog_mapping_response)
        self.add_cmd_handler(DIGITAL_MESSAGE, self._handle_digital_message)
        self.add_cmd_handler(REPORT_VERSION, self._handle_report_version)
        self.add_cmd_handler(REPORT_FIRMWARE, self._handle_report_firmware)
        self.add_cmd_handler(PING_REPLY, self._handle_ping_reply)
        self.add_cmd_handler(PULSE_REPLY, self._handle_pulse_reply)
        self.add_cmd_handler(I2C_REPLY, self._handle_i2c_reply)

    def add_cmd_handler(self, cmd, func):
        """
        Adds a command handler for a command.
        """
        len_args = len(inspect.getargspec(func)[0])
        def add_meta(f):
            def decorator(*args, **kwargs):
                f(*args, **kwargs)
            decorator.bytes_needed = len_args - 1 # exclude self
            decorator.__name__ = f.__name__
            return decorator
        func = add_meta(func)
        self._command_handlers[cmd] = func
        
    def get_pin(self, pin_def):
        """
        Returns the activated pin given by the pin definition.
        May raise an ``InvalidPinDefError`` or a ``PinAlreadyTakenError``.
        
        :arg pin_def: Pin definition as described in TODO,
            but without the arduino name. So for example ``a:1:i``.
        
        """
        if type(pin_def) == list:
            bits = pin_def
        else:
            bits = pin_def.split(':')
        a_d = bits[0] == 'a' and 'analog' or 'digital'
        part = getattr(self, a_d)
        pin_nr = int(bits[1])
        if pin_nr >= len(part):
            raise InvalidPinDefError('Invalid pin definition: %s at position 3 on %s' % (pin_def, self.name))
        if getattr(part[pin_nr], 'mode', None)  == UNAVAILABLE:
            raise InvalidPinDefError('Invalid pin definition: UNAVAILABLE pin %s at position on %s' % (pin_def, self.name))
        if self.taken[a_d][pin_nr]:
            raise PinAlreadyTakenError('%s pin %s is already taken on %s' % (a_d, bits[1], self.name))
        # ok, should be available
        pin = part[pin_nr]
        self.taken[a_d][pin_nr] = True
        if pin.type is DIGITAL:
            if bits[2] == 'p':
                pin.mode = PWM
            elif bits[2] == 's':
                pin.mode = SERVO
            elif bits[2] is not 'o':
                pin.mode = INPUT
        else:
            pin.enable_reporting()
        return pin
        
    def pass_time(self, t):
        """ 
        Non-blocking time-out for ``t`` seconds.
        """
        cont = time.time() + t
        while time.time() < cont:
            time.sleep(0)
            
    def send_sysex(self, sysex_cmd, data=[]):
        """
        Sends a SysEx msg.
        
        :arg sysex_cmd: A sysex command byte
        :arg data: A list of 7-bit bytes of arbitrary data (bytes may be 
            already converted to chr's)
        """
        self.sp.write(chr(START_SYSEX))
        self.sp.write(chr(sysex_cmd))
        for byte in data:
            try:
                byte = chr(byte)
            except TypeError:
                pass # byte is already a chr
            except ValueError:
                raise ValueError('Sysex data can be 7-bit bytes only. '
                    'Consider using utils.to_two_bytes for bigger bytes.')
            self.sp.write(byte)
        self.sp.write(chr(END_SYSEX))
        
    def bytes_available(self):
        return self.sp.inWaiting()

    def iterate(self):
        """ 
        Reads and handles data from the microcontroller over the serial port.
        This method should be called in a main loop, or in an
        :class:`Iterator` instance to keep this boards pin values up to date
        """
        byte = self.sp.read()
        if not byte:
            return
        data = ord(byte)
        received_data = []
        handler = None
        if data < START_SYSEX:
            # These commands can have 'channel data' like a pin nummber appended.
            try:
                handler = self._command_handlers[data & 0xF0]
            except KeyError:
                return
            received_data.append(data & 0x0F)
            while len(received_data) < handler.bytes_needed:
                received_data.append(ord(self.sp.read()))
        elif data == START_SYSEX:
            data = ord(self.sp.read())
            handler = self._command_handlers.get(data)
            if not handler:
                return
            data = ord(self.sp.read())
            while data != END_SYSEX:
                received_data.append(data)
                data = ord(self.sp.read())
        else:
            try:
                handler = self._command_handlers[data]
            except KeyError:
                return
            while len(received_data) < handler.bytes_needed:
                received_data.append(ord(self.sp.read()))
        # Handle the data
        try:
            handler(*received_data)
        except ValueError:
            pass
         
    def send_analog_mapping_query(self):
        self.send_sysex(ANALOG_MAPPING_QUERY)
        
    def get_firmata_version(self):
        """
        Returns a version tuple (major, mino) for the firmata firmware on the
        board.
        """
        return self.firmata_version
         
                     
    def head_servos_config(self, headPanServoPin, headYawServoPin):
        self.servo_config(headPanServoPin, 600, 1600, 90)
        self.servo_config(headYawServoPin, 544, 2400, 90)
        
    def motor_config(self, leftDirectionPin, rightDirectionPin, leftBrakePin, rightBrakePin, leftSpeedPin, rightSpeedPin):
        #DIRECTION
        self.digital[leftDirectionPin].mode = OUTPUT
        self.digital[rightDirectionPin].mode = OUTPUT

        #BRAKE
        self.digital[leftBrakePin].mode = OUTPUT
        self.digital[rightBrakePin].mode = OUTPUT
        
        #SPEED
        self.digital[leftSpeedPin].mode = PWM
        self.digital[rightSpeedPin].mode = PWM
        
    def servo_config(self, pin, min_pulse=544, max_pulse=2400, angle=0):
        """
        Configure a pin as servo with min_pulse, max_pulse and first angle.
        ``min_pulse`` and ``max_pulse`` default to the arduino defaults.
        """
        if pin > len(self.digital) or self.digital[pin].mode == UNAVAILABLE:
            raise IOError("Pin %s is not a valid servo pin")
        data = itertools.chain([pin], to_two_bytes(min_pulse),
                                        to_two_bytes(max_pulse))
        self.send_sysex(SERVO_CONFIG, data)
        
        # set pin._mode to SERVO so that it sends analog messages
        # don't set pin.mode as that calls this method
        self.digital[pin]._mode = SERVO
        self.digital[pin].write(angle)

#  //---------------------------------------------------------------------
#  //
#  // gen config
#  //
#  //---------------------------------------------------------------------
    def general_config(self, arduinoLoopDelay):
        self.send_sysex(REPORT_FIRMWARE)
        self.send_sysex(REPORT_VERSION)
        
        data = itertools.chain(to_two_bytes(arduinoLoopDelay))
        self.send_sysex(SAMPLING_INTERVAL, data) #(MINIMUM_SAMPLING_INTERVAL=10)
        
        self.send_analog_mapping_query()
        
        
        
#  //---------------------------------------------------------------------
#  //
#  // Ping)))
#  //
#  //---------------------------------------------------------------------
    def ping_config(self, pin):
        """
        Configure a pin as pulse with high/low, timeout settings.
        """
        if pin > len(self.digital) or self.digital[pin].mode == UNAVAILABLE:
            raise IOError("Pin %s is not a valid Ping))) pin")
        data = itertools.chain([pin])
        self.send_sysex(PING_CONFIG, data)
        
        # set pin._mode to PULSE so that it sends messages
        # don't set pin.mode as that calls this method
        self.digital[pin]._mode = PULSE
        self.getPulse(pin)
                    
    def getPing(self, pin):
        data = itertools.chain([pin])
        self.send_sysex(PING_REQUEST, data)

    def _handle_ping_reply(self, *data):
        self._ping_distance = data[0]
#         print (self._ping_distance)
            
    def get_ping_distance(self, pin):
        return self._ping_distance
        
#  //---------------------------------------------------------------------
#  //
#  // Analog Pin Config In/Out
#  //
#  //---------------------------------------------------------------------
    def analog_in_config(self, pin):
        self.get_pin('a:' + str(pin) + ':i').mode = ANALOG

    def analog_out_config(self, pin):
        self.get_pin('d:' + str(pin) + ':o').mode = ANALOG
#  //---------------------------------------------------------------------
#  //
#  // Digital Pin Config In/Out
#  //
#  //---------------------------------------------------------------------
    def digital_in_config(self, pin):
        self.get_pin('d:' + str(pin) + ':i').mode = DIGITAL

    def digital_out_config(self, pin):
        self.get_pin('d:' + str(pin) + ':o').mode = DIGITAL

#  //---------------------------------------------------------------------
#  //
#  // Gyroscope Pin Config Read/Write
#  //
#  //---------------------------------------------------------------------
    def gyro_config(self, i2cDelay, i2cAddr, writePin, readPin):
        
#         data_dely = itertools.chain(to_two_bytes(i2cDelay))
        self.send_sysex(I2C_CONFIG, [0])
#         self.send_sysex(I2C_CONFIG, data_dely)

#         writeI2C(CTRL_REG1, 0x1F);    // Turn on all axes, disable power down
        self.writeI2CRegister(i2cAddr, CTRL_REG1, 0x1F)
                
#         writeI2C(CTRL_REG2, 0x08);    //High Pass Filter
#         self.writeI2CRegister(i2cAddr, CTRL_REG2, 0x08)
 
#         writeI2C(CTRL_REG3, 0x08);    // Enable control ready signal
        self.writeI2CRegister(i2cAddr, CTRL_REG3, 0x08)
 
#         writeI2C(CTRL_REG3, 0x08);    // Enable control ready signal
        self.writeI2CRegister(i2cAddr, CTRL_REG4, 0x80)
 
#         writeI2C(CTRL_REG4, 0x80);    // Set scale (500 deg/sec)
#         self.writeI2CRegister(i2cAddr, CTRL_REG5, 0x80)
 
#         if(scale == 250)  writeRegister(L3G4200D_Address, CTRL_REG4, 0b00000000);
#   if(scale == 500)  writeRegister(L3G4200D_Address, CTRL_REG4, 0b00010000);
#   if(scale == 2000) writeRegister(L3G4200D_Address, CTRL_REG4, 0b00110000);
#   writeRegister(L3G4200D_Address, CTRL_REG5, 0b00000000);
        
    def requestGyro(self, i2cAddr, axisId):
        self.sendRequestGyro(i2cAddr, self.msbRegisters, axisId); # MSB
        self.sendRequestGyro(i2cAddr, self.lsbRegisters, axisId ); # LSB
        
    def sendRequestGyro(self, i2cAddr, registers, propId):
        self.send_sysex(I2C_REQUEST, itertools.chain([i2cAddr], [I2C_READ], to_two_bytes(registers[self.axisMap[propId]]), to_two_bytes(1)))

    def processGyroResults(self, i2cReply, axis):

        self.msb_r = self.msbRegisters[axis]
#         self.msb = self.msbResults[axis]
        self.lsb_r = self.lsbRegisters[axis]
#         self.lsb = self.lsbResults[axis]
        
        if i2cReply[1] == self.msb_r:
            self.msbResults[axis] = i2cReply[2]

        if i2cReply[1] == self.lsb_r:
            self.lsbResults[axis] = i2cReply[2]
            
        if self.msbResults[axis] > 0 and self.lsbResults[axis] > 0:
            print(str(self.msbResults[axis]) +":"+ str(self.lsbResults[axis]))
            print(axis + "=" + str(float(self.msbResults[axis] << 8 | self.lsbResults[axis]) / 114)) 
#  //---------------------------------------------------------------------
#  //
#  // I2C
#  //s
#  //---------------------------------------------------------------------
    def _handle_i2c_reply(self, *data):
        i2cReply = self.decode_i2c_data(data)
        [self.processGyroResults(i2cReply, self.axisMap[axisId]) for axisId in range(0,2)]
        [self.processGyroResults(i2cReply, self.axisMap[axisId]) for axisId in range(0,2)]
        
        
    def decode_i2c_data(self, data):
        dataList = list(data)
        items = []
        while dataList:
            lsb = dataList.pop(0)
            try:
                msb = dataList.pop(0)
            except IndexError:
                msb = 0x00
            items.append(from_two_bytes((lsb, msb)))
        return items
    def writeI2CRegister(self, i2cAddr, i2cRegister, i2cValue):
        self.send_sysex(I2C_REQUEST, itertools.chain([i2cAddr], [I2C_WRITE], to_two_bytes(i2cRegister),  to_two_bytes(i2cValue)))
  
  
#  //---------------------------------------------------------------------
#  //
#  // PIR Pin Config Read/Write
#  //
#  //---------------------------------------------------------------------
    def pir_config(self, pirSensorEnablePin, pirSensorPin):
        self.digital_out_config(pirSensorEnablePin)
        self.digital_in_config(pirSensorPin)
        
        data = itertools.chain([pirSensorEnablePin], [pirSensorPin])
        self.send_sysex(PIR_CONFIG, data)
        
#  //---------------------------------------------------------------------
#  //
#  // Pulse In/Out
#  //
#  //---------------------------------------------------------------------
    def pulse_config(self, pin, lowOrHigh=1, timeout=1000):
        """
        Configure a pin as pulse with high/low, timeout settings.
        """
        if pin > len(self.digital) or self.digital[pin].mode == UNAVAILABLE:
            raise IOError("Pin %s is not a valid pulse pin")
        data = itertools.chain([pin], [lowOrHigh], to_two_bytes(timeout))
        self.send_sysex(PULSE_CONFIG, data)
        
        # set pin._mode to PULSE so that it sends messages
        # don't set pin.mode as that calls this method
        self.digital[pin]._mode = PULSE
#         self.getPulse(pin)
                    
    def getPulse(self, pin):
        data = itertools.chain([pin])
        self.send_sysex(PULSE_REQUEST, data)
        
    def _handle_pulse_reply(self, *data):
        self._pulse_duration = from_two_bytes(data)
                  
    def get_pulse_duration(self, pin):
        return self._pulse_duration

    def exit(self):
        """ Call this to exit cleanly. """
        # First detach all servo's, otherwise it somehow doesn't want to close...
        # FIXME
        if hasattr(self, 'digital'):
            for pin in self.digital:
                if pin.mode == SERVO:
                    pin.mode = OUTPUT
                    
        if hasattr(self, 'sp'):
            self.sp.close()
        
    # Command handlers
    def _handle_analog_mapping_response(self, *data):
        self._analog_mapping_response = two_byte_iter_to_str(data)
       
        
    def _handle_analog_message(self, pin_nr, lsb, msb):
        value = round(float((msb << 7) + lsb) / 1023, 4)
        # Only set the value if we are actually reporting
        try:
            if self.analog[pin_nr].reporting:
                self.analog[pin_nr].value = value
        except IndexError:
            raise ValueError

    def _handle_digital_message(self, port_nr, lsb, msb):
        """
        Digital messages always go by the whole port. This means we have a
        bitmask wich we update the port.
        """
        mask = (msb << 7) + lsb
        try:
            self.digital_ports[port_nr]._update(mask)
        except IndexError:
            raise ValueError

    def _handle_report_version(self, major, minor):
        self.firmata_version = (major, minor)
        
    def _handle_report_firmware(self, *data):
        major = data[0]
        minor = data[1]
        self.firmware_version = (major, minor)
        self.firmware = two_byte_iter_to_str(data[2:])

class Arduino(Board):
    """
    A board that wil set itself up as a normal Arduino.
    """
    def __init__(self, *args, **kwargs):
        args = list(args)
        args.append(BOARDS['arduino'])
        super(Arduino, self).__init__(*args, **kwargs)
        
    def __str__(self):
        return 'Arduino %s on %s at %s' % (self.name, self.sp.port, self.sp.baudrate)
    
class ArduinoMega(Board):
    """
    A board that wil set itself up as an Arduino Mega.
    """
    def __init__(self, *args, **kwargs):
        args = list(args)
        args.append(BOARDS['arduino_mega'])
        super(ArduinoMega, self).__init__(*args, **kwargs)
    
    def __str__(self):
        return 'Arduino Mega %s on %s' % (self.name, self.sp.port)
    
class ArduinoMicro(Board):
    """
    A board that wil set itself up as an Arduino Mega.
    """
    def __init__(self, *args, **kwargs):
        args = list(args)
        args.append(BOARDS['arduino_micro'])
        super(ArduinoMicro, self).__init__(*args, **kwargs)
    
    def __str__(self):
        return 'Arduino Micro %s on %s' % (self.name, self.sp.port)
    
class Port(object):
    """ An 8-bit port on the board """
    def __init__(self, board, port_number, num_pins=8):
        self.board = board
        self.port_number = port_number
        self.reporting = False
        
        self.pins = []
        for i in range(num_pins):
            pin_nr = i + self.port_number * 8
            self.pins.append(Pin(self.board, pin_nr, type=DIGITAL, port=self))
            
    def __str__(self):
        return "Digital Port %i on %s" % (self.port_number, self.board)
        
    def enable_reporting(self):
        """ Enable reporting of values for the whole port """
        self.reporting = True
        msg = chr(REPORT_DIGITAL + self.port_number)
        msg += chr(1)
        self.board.sp.write(msg)
        for pin in self.pins:
            if pin.mode == INPUT:
                pin.reporting = True # TODO Shouldn't this happen at the pin?
        
    def disable_reporting(self):
        """ Disable the reporting of the port """
        self.reporting = False
        msg = chr(REPORT_DIGITAL + self.port_number)
        msg += chr(0)
        self.board.sp.write(msg)
                
    def write(self):
        """Set the output pins of the port to the correct state"""
        mask = 0
        for pin in self.pins:
            if pin.mode == OUTPUT:
                if pin.value == 1:
                    pin_nr = pin.pin_number - self.port_number * 8
                    mask |= 1 << pin_nr
        msg = chr(DIGITAL_MESSAGE + self.port_number)
        msg += chr(mask % 128)
        msg += chr(mask >> 7)
        self.board.sp.write(msg)
        
    def _update(self, mask):
        """
        Update the values for the pins marked as input with the mask.
        """
        if self.reporting:
            for pin in self.pins:
                if pin.mode is INPUT:
                    pin_nr = pin.pin_number - self.port_number * 8
                    pin.value = (mask & (1 << pin_nr)) > 0

class Pin(object):
    """ A Pin representation """
    def __init__(self, board, pin_number, type=ANALOG, port=None):
        self.board = board
        self.pin_number = pin_number
        self.type = type
        self.port = port
        self.PWM_CAPABLE = False
        self._mode = (type == DIGITAL and OUTPUT or INPUT)
        self.reporting = False
        self.value = None
        
    def __str__(self):
        type = {ANALOG : 'Analog', DIGITAL : 'Digital'}[self.type]
        return "%s pin %d" % (type, self.pin_number)

    def _set_mode(self, mode):
        if mode is UNAVAILABLE:
            self._mode = UNAVAILABLE
            return
        if self._mode is UNAVAILABLE:
            raise IOError("%s can not be used through Firmata" % self)
        if mode is PWM and not self.PWM_CAPABLE:
            raise IOError("%s does not have PWM capabilities" % self)
        if mode == SERVO:
            if self.type != DIGITAL:
                raise IOError("Only digital pins can drive servos! %s is not"
                    "digital" % self)
            self._mode = SERVO
            self.board.servo_config(self.pin_number)
        if mode == PING:
            if self.type != DIGITAL:
                raise IOError("Only digital pins can drive Ping)))! %s is not"
                    "digital" % self)
            self.board.ping_config(self.pin_number)
        if mode == PING:
            if self.type != DIGITAL:
                raise IOError("Only digital pins can drive pulseIn! %s is not"
                    "digital" % self)
            self.board.pulse_config(self.pin_number)
            return
        
        # Set mode with SET_PIN_MODE message
        self._mode = mode
        command = chr(SET_PIN_MODE)
        command += chr(self.pin_number)
        command += chr(mode)
        self.board.sp.write(command)
        if mode == INPUT:
            self.enable_reporting()
        
    def _get_mode(self):
        return self._mode
        
    mode = property(_get_mode, _set_mode)
    """
    Mode of operation for the pin. Can be one of the pin modes: INPUT, OUTPUT,
    ANALOG, PWM or SERVO (or UNAVAILABLE)
    """
    
    def enable_reporting(self):
        """ Set an input pin to report values """
        if self.mode is not INPUT:
            raise IOError, "%s is not an input and can therefore not report" % self
        if self.type == ANALOG:
            self.reporting = True
            msg = chr(REPORT_ANALOG + self.pin_number)
            msg += chr(1)
            self.board.sp.write(msg)
        else:
            self.port.enable_reporting() # TODO This is not going to work for non-optimized boards like Mega
        
    def disable_reporting(self):
        """ Disable the reporting of an input pin """
        if self.type == ANALOG:
            self.reporting = False
            msg = chr(REPORT_ANALOG + self.pin_number)
            msg += chr(0)
            self.board.sp.write(msg)
        else:
            self.port.disable_reporting() # TODO This is not going to work for non-optimized boards like Mega
    
    def read(self):
        """
        Returns the output value of the pin. This value is updated by the
        boards :meth:`Board.iterate` method. Value is alway in the range 0.0 - 1.0
        """
        if self.mode == UNAVAILABLE:
            raise IOError, "Cannot read pin %s"% self.__str__()
        return self.value
        
    def write(self, value):
        """
        Output a voltage from the pin

        :arg value: Uses value as a boolean if the pin is in output mode, or
            expects a float from 0 to 1 if the pin is in PWM mode. If the pin 
            is in SERVO the value should be in degrees.
        
        """
        if self.mode is UNAVAILABLE:
            raise IOError, "%s can not be used through Firmata" % self
        if self.mode is INPUT:
            raise IOError, "%s is set up as an INPUT and can therefore not be written to" % self
        if value is not self.value:
            self.value = value
            if self.mode is OUTPUT:
                if self.port:
                    self.port.write()
                else:
                    msg = chr(DIGITAL_MESSAGE)
                    msg += chr(self.pin_number)
                    msg += chr(value)
                    self.board.sp.write(msg)
            elif self.mode is PWM:
                value = int(round(value * 255))
                msg = chr(ANALOG_MESSAGE + self.pin_number)
#                 print(value)
                msg += chr(value % 128)
                msg += chr(value >> 7)
                self.board.sp.write(msg)
            elif self.mode is SERVO:
                value = int(value)
                msg = chr(ANALOG_MESSAGE + self.pin_number)
                msg += chr(value % 128)
                msg += chr(value >> 7)
                self.board.sp.write(msg)