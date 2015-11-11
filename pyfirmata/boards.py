BOARDS = {
    'arduino' : {
        'digital' : tuple(x for x in range(20)),
        'analog' : tuple(x for x in range(6)),
        'pwm' : (3, 5, 6, 9, 10, 11),
        'servo' : (3, 5, 6, 9, 10, 11),
        'ping' : tuple(x for x in range(20)),
        'pulse' : tuple(x for x in range(20)),
        'use_ports' : True,
        'disabled' : (0, 1) # Rx, Tx, Crystal
    },
    'arduino_mega' : {
        'digital' : tuple(x for x in range(54)),
        'analog' : tuple(x for x in range(16)),
        'pwm' : tuple(x for x in range(2,14)),
        'servo' : tuple(x for x in range(2,14)),
        'ping' : tuple(x for x in range(54)),
        'pulse' : tuple(x for x in range(54)),
        'use_ports' : True,
        'disabled' : (0, 1) # Rx, Tx, Crystal
    },
    'arduino_micro' : {
        'digital' : (4,6,8,9,10,12),
        'analog' : tuple(x for x in range(11)),
        'pwm' : (3, 5, 6, 9, 10, 11, 13),
        'servo' : (3, 5, 6, 9, 10, 11, 13),
        'ping' : tuple(x for x in range(20)),
        'pulse' : tuple(x for x in range(20)),
        'use_ports' : True,
        'disabled' : (0, 1) # Rx, Tx, Crystal
    },
#     'mock_board' : {
#         'digital' : tuple(x for x in range(54)),
#         'analog' : tuple(x for x in range(16)),
#         'pwm' : tuple(x for x in range(2,14)),
#         'servo' : tuple(x for x in range(2,14)),
#         'ping' : tuple(x for x in range(54)),
#         'pulse' : tuple(x for x in range(54)),
#         'use_ports' : True,
#         'disabled' : (0, 1) # Rx, Tx, Crystal
#     }
    'mock_board' : {
        'digital' : (),
        'analog' : (),
        'pwm' : (),
        'ping' : (),
        'pulse' : (),
        'use_ports' : True,
        'disabled' : () # Rx, Tx, Crystal
    }
}
