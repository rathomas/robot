from collections import deque
from pyfirmata import *
from boards import BOARDS

class MockupSerial(deque):
    """ 
    A Mockup object for python's Serial. Functions as a fifo-stack. Push to
    it with ``write``, read from it with ``read``.
    
    >>> s = MockupSerial('someport', 4800)
    >>> s.read()
    ''
    >>> s.write(chr(100))
    >>> s.write('blaat')
    >>> s.write(100000)
    >>> s.read(2)
    ['d', 'blaat']
    >>> s.read()
    100000
    >>> s.read()
    ''
    >>> s.read(2)
    ['', '']
    >>> s.close()
    """
    def __init__(self, port, baudrate, timeout=0.02):
        self.port = port or 'somewhere'
        
    def read(self, count=1):
        if count > 1:
            val = []
            for i in range(count):
                try:
                    val.append(self.popleft())
                except IndexError:
                    val.append('')
        else:
            try:
                val = self.popleft()
            except IndexError:
                val = ''
        return val
            
    def write(self, value):
        """
        Appends items flat to the deque. So iterables will be unpacked.
        """
        if hasattr(value, '__iter__'):
            self.extend(value)
        else:
            self.append(value)
            
    def close(self):
        self.clear()
        
    def inWaiting(self):
        return len(self)
        
class MockupBoard(Board):

    def __init__(self, port=1, layout=BOARDS['mock_board'], values_dict={}):
        self.sp = MockupSerial(port, 57600)
        self.setup_layout(layout)
        self.values_dict = values_dict
        self.id = 1
        self.name = "MockBoard"
        
    def reset_taken(self):
        for key in self.taken['analog']:
            self.taken['analog'][key] = False
        for key in self.taken['digital']:
            self.taken['digital'][key] = False
        
    def update_values_dict(self):
        for port in self.digital_ports:
            port.values_dict = self.values_dict
            port.update_values_dict()
        for pin in self.analog:
            pin.values_dict = self.values_dict
            
    def _handle_report_firmware(self, *data):
        self.firmware_version = (0, 0)
        self.firmware = "mock_firmware"
        
    def add_cmd_handler(self, cmd, func):
        pass
    
    def iterate(self):
        pass
    
    def __str__(self):
        return 'Board is Mock %s on %s' % (self.name, self.sp.port)
    
        
class MockupPort(Port):
    def __init__(self, board, port_number):
        self.board = board
        self.port_number = port_number
        self.reporting = False
        
        self.pins = []
        for i in range(54):
            pin_nr = i + self.port_number * 8
            pin = MockupPin(self.board, pin_nr, type=DIGITAL, port=self)
            self.pins.append(pin)

    def update_values_dict(self):
        for pin in self.pins:
            pin.values_dict = self.values_dict
        
class MockupPin(Pin):
    def __init__(self, *args, **kwargs):
        self.values_dict = kwargs.get('values_dict', {})
        try:
            del kwargs['values_dict']
        except KeyError:
            pass
        
        super(MockupPin, self).__init__(*args, **kwargs)
    
    def read(self):
        if self.value is None:
            try:
                type = self.port and 'd' or 'a'
                return self.values_dict[type][self.pin_number]
            except KeyError:
                return None
        else:
            return self.value
            
    def get_in_output(self):
        if not self.port and not self.mode: # analog input
            return 'i'
        else:
            return 'o'
            
    def set_active(self, active):
        self.is_active = active
        
    def get_active(self):
        return self.is_active
        
    def write(self, value):
        if self.mode == UNAVAILABLE:
            raise IOError, "Cannot read from pin %d" \
                           % (self.pin_number)
        if self.mode == INPUT:
            raise IOError, "%s pin %d is not an output" \
                            % (self.port and "Digital" or "Analog", self.get_pin_number())
        if not self.port:
            raise AttributeError, "AnalogPin instance has no attribute 'write'"
        # if value != self.read():
        self.value = value
        
class Iterator(object):
    def __init__(self, *args, **kwargs):
        pass
    def start(self):
        pass
    def stop(self):
        pass

if __name__ == '__main__':
    import doctest
    doctest.testmod()