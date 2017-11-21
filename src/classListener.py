"""
Leap motion listener where gestures are defined and configured.
"""

# Import native python libraries
import sys
import os
import inspect
from collections import deque
import math

# Import src dependencies
from gesture import Gesture

# Setup environment variables
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
# Windows and Linux
arch_dir = '../LeapSDK/lib/x64' if sys.maxsize > 2**32 else '../LeapSDK/lib/x86'
# Mac
# arch_dir = os.path.abspath(os.path.join(src_dir, '../LeapSDK/lib')
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
sys.path.insert(0, "../LeapSDK/lib")

# Import LeapSDK
import Leap


class MyListener(Leap.Listener):
    FINGERS = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    FINGER_BONES = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']

    def __init__(self):
        """
        The following code is for plotting purposes
        """

        super(self.__class__, self).__init__()
        self.angle_data = []
        self.hand_angle = None
        # four fingers to keep track of
        for i in range(4):
            self.angle_data.append(deque([0] * 1000, 1000))
        self.confidence = 0
        self.avg_a = 0
        self.new_finger_down = 3
        self.finger_down = None

    def on_init(self, controller):
        print("Initialized")

    def on_connect(self, controller):
        if controller.is_connected:
            print ("Connected")
        else:
            print ("ERROR")
            quit()

        # Enable gestures
        self.__enable_controller_gestures(controller)

        if self.__check_controller_gestures_status(controller):
            self.__set_controller_gestures_configuration(controller)
            print("Geastures enabled")
        else:
            print('Device error, gestures can not be enabled, exit code: 4686446')
            quit()

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        previous_frame = controller.frame(1)

        # Get gestures
        my_gesture = Gesture()
        for gesture in frame.gestures():
            if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                gesture_id, state, radius, hand_type, clockwiseness = my_gesture.circle_processing(controller, gesture)
                if state is not "STATE_UPDATE":
                    print "CIRCLE", state, radius, hand_type, clockwiseness

            if gesture.type == Leap.Gesture.TYPE_SWIPE:
                hand_type2 = "caca"
                swipe_direction2 = "mas_caca"

                gesture_id, state, hand_type, swipe_direction = my_gesture.swipe_processing(gesture)

                for _gesture in frame.gestures(previous_frame):
                    if _gesture.type is Leap.Gesture.TYPE_SWIPE:
                        gesture_id2, state2, hand_type2, swipe_direction2 = my_gesture.swipe_processing(_gesture)

                print swipe_direction2, swipe_direction, hand_type2, hand_type
                print "SWIPE", hand_type, swipe_direction

            if gesture.type == Leap.Gesture.TYPE_KEY_TAP:
                gesture_id, state, hand_type = my_gesture.keytap_processing(gesture)
                print "KEY TAP", hand_type

            if gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
                gesture_id, state, hand_type = my_gesture.screentap_processing(gesture)
                print "SCREEN TAP", hand_type

    def is_same_swipe_than_previous(self, hand_type, hand_type2, swipe_direction, swipe_direction2):
        if swipe_direction is not swipe_direction2 or hand_type is not hand_type2:
            return False
        else:
            return True

    def on_exit(self, controller):
        print "Exited"

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        if not controller.is_connected:
            print ("Disconnected")

    def __get_angle_data(self):
        return self.angle_data

    def __pop_new_finger_down_if_any(self):
        finger = self.new_finger_down
        self.new_finger_down = None
        return finger

    def __get_hand_direction(self):
        return self.hand_direction

    def __get_confidence(self):
        return self.confidence

    # hand angle in relation to the eh, "left" vector, (-1, 0, 0).
    def __get_hand_angle(self):
        return self.hand_angle

    def __get_average_angle(self):
        return self.avg_a

    def __set_controller_gestures_configuration(self, controller):
        # Custom values
        circle_min_radius = 30.0  # unit: mm
        circle_min_arc = 1.5 * math.pi  # unit: radians
        swipe_min_length = 150.0  # unit: mm
        swipe_min_velocity = 1000.0  # unit: mm/s
        keytap_min_down_velocity = 1000.0  # unit: mm/s
        keytap_history_seconds = .001  # unit: s
        keytap_min_distance = 50.0  # unit: mm
        screentap_min_forward_velocity = 50.0  # unit: mm/s
        screentap_history_seconds = .001  # unit: s
        screentap_min_distance = 5.0  # unit: mm
        controller.config.set("Gesture.Circle.MinRadius", circle_min_radius)
        controller.config.set("Gesture.Circle.MinArc", circle_min_arc)
        controller.config.set("Gesture.Swipe.MinLength", swipe_min_length)
        controller.config.set("Gesture.Swipe.MinVelocity", swipe_min_velocity)
        controller.config.set("Gesture.KeyTap.MinDownVelocity", keytap_min_down_velocity)
        controller.config.set("Gesture.KeyTap.HistorySeconds", keytap_history_seconds)
        controller.config.set("Gesture.KeyTap.MinDistance", keytap_min_distance)
        controller.config.set("Gesture.ScreenTap.MinForwardVelocity", screentap_min_forward_velocity)
        controller.config.set("Gesture.ScreenTap.HistorySeconds", screentap_history_seconds)
        controller.config.set("Gesture.ScreenTap.MinDistance", screentap_min_distance)
        controller.config.save()

    def __enable_controller_gestures(self, controller):
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def __check_controller_gestures_status(self, controller):
        if controller.is_gesture_enabled(Leap.Gesture.TYPE_CIRCLE) and \
                controller.is_gesture_enabled(Leap.Gesture.TYPE_KEY_TAP) and \
                controller.is_gesture_enabled(Leap.Gesture.TYPE_SCREEN_TAP) and \
                controller.is_gesture_enabled(Leap.Gesture.TYPE_SWIPE):

            return True
        else:
            return False
