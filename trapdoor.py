from gpiozero import Servo
import time


class TrapDoor:

    def __init__(self):
        self.servo = Servo(18)
        self.servo.max()

    def springAndReset(self):
        self.servo.min()
        time.sleep(.5)
        self.servo.max()

