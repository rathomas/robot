'''
Created on Aug 16, 2013

@author: rthomas
'''
import sys
from Tasks import Task
from leapmotion.Leap import Controller
class LeapMotionConnector():

    def __init__(self, controller):
        print("LeapMotionConnector created.")
        self.lc = controller
        
    def connect(self):
        # Create a sample listener and controller
        self.leapMotionListener = LeapMotionListener()
        self.leapMotionListener.registerLogicalController(self.lc)
        
        self.leapMotionController = Controller()
    
        # Have the sample listener receive events from the controller
        self.leapMotionController.add_listener(self.leapMotionListener)
    
        # Keep this process running until Enter is pressed
        print "Press Enter to quit..."
        sys.stdin.readline()
    
        # Remove the sample listener when done
        self.leapMotionController.remove_listener(self.leapMotionListener)
        
        stopTask = Task('f0', self.lc)
        stopTask.executeTask()
        
class LeapMotionListener(LeapMotionListener):
    def on_init(self, controller):
        print "Initialized"

    def registerLogicalController(self, controller):
        self.lc = controller
        
    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

#         print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
#               frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

        if not frame.hands.empty:
            # Get the first hand
            hand = frame.hands[0]

            # Check if the hand has any fingers
            fingers = hand.fingers
            if not fingers.empty:
                # Calculate the hand's average finger tip position
                avg_pos = Vector()
                for finger in fingers:
                    avg_pos += finger.tip_position
                avg_pos /= len(fingers)
#                 print "Hand has %d fingers, average finger tip position: %s" % (
#                       len(fingers), avg_pos)

            # Get the hand's sphere radius and palm position
#             print "Hand sphere radius: %f mm, palm position: %s" % (
#                   hand.sphere_radius, hand.palm_position)

            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction

            # Calculate the hand's pitch, roll, and yaw angles
#             print "Hand pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
#                 direction.pitch * Leap.RAD_TO_DEG,
#                 normal.roll * Leap.RAD_TO_DEG,
#                 direction.yaw * Leap.RAD_TO_DEG)
            
#             headTiltAdjustment = Task('t' + str(90 - int(direction.pitch * Leap.RAD_TO_DEG)), self.lc)
#             headTiltAdjustment.executeTask()
#             headPanAdjustment = Task('p' + str(90 + int(direction.yaw * Leap.RAD_TO_DEG)), self.lc)
#             headPanAdjustment.executeTask()
            
            iPitch = int(direction.pitch * RAD_TO_DEG)
            iRoll = int(normal.roll * RAD_TO_DEG)
            iYaw = int(direction.yaw * RAD_TO_DEG)
            
            if len(fingers) >= 4:
                headAdjustment = Task('c1', self.lc)
                Task('t' + str(90 - iPitch), headAdjustment)
                Task('p' + str(90 + iYaw), headAdjustment)
                headAdjustment.executeTask()
            elif len(fingers) < 4 and len(fingers) > 1:
                moveAdjustment = Task('c1', self.lc)
                Task('u' + str(iRoll), moveAdjustment)
                if iPitch < -8:
                    Task('f' + str(iPitch * -1 + 75), moveAdjustment)
                elif iPitch >= -10 and iPitch < 10:
                    Task('f0', moveAdjustment)
                else:
                    Task('b' + str(iPitch + 75), moveAdjustment)
                moveAdjustment.executeTask()

            # Gestures
            for gesture in frame.gestures():
                if gesture.type == Gesture.TYPE_CIRCLE:
                    circle = CircleGesture(gesture)

                    # Determine clock direction using the angle between the pointable and the circle normal
                    if circle.pointable.direction.angle_to(circle.normal) <= PI/4:
                        clockwiseness = "clockwise"
                    else:
                        clockwiseness = "counterclockwise"

                    # Calculate the angle swept since the last frame
                    swept_angle = 0
                    if circle.state != Gesture.STATE_START:
                        previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
                        swept_angle =  (circle.progress - previous_update.progress) * 2 * PI

                    print "Circle id: %d, %s, progress: %f, radius: %f, angle: %f degrees, %s" % (
                            gesture.id, self.state_string(gesture.state),
                            circle.progress, circle.radius, swept_angle * RAD_TO_DEG, clockwiseness)

                if gesture.type == Gesture.TYPE_SWIPE:
                    swipe = SwipeGesture(gesture)
                    print "Swipe id: %d, state: %s, position: %s, direction: %s, speed: %f" % (
                            gesture.id, self.state_string(gesture.state),
                            swipe.position, swipe.direction, swipe.speed)

                if gesture.type == Gesture.TYPE_KEY_TAP:
                    keytap = KeyTapGesture(gesture)
                    print "Key Tap id: %d, %s, position: %s, direction: %s" % (
                            gesture.id, self.state_string(gesture.state),
                            keytap.position, keytap.direction )

                if gesture.type == Gesture.TYPE_SCREEN_TAP:
                    screentap = ScreenTapGesture(gesture)
                    print "Screen Tap id: %d, %s, position: %s, direction: %s" % (
                            gesture.id, self.state_string(gesture.state),
                            screentap.position, screentap.direction )

#         if not (frame.hands.empty and frame.gestures().empty):
#             print ""

    def state_string(self, state):
        if state == Gesture.STATE_START:
            return "STATE_START"

        if state == Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Gesture.STATE_INVALID:
            return "STATE_INVALID"