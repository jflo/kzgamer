from adafruit_motorkit import MotorKit
import time
from board import SCL, SDA
import busio

# Import the PCA9685 module. Available in the bundle and here:
#   https://github.com/adafruit/Adafruit_CircuitPython_PCA9685
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo


class TrapDoor:

    def __init__(self):
        self.kit = MotorKit()
        i2c = busio.I2C(SCL, SDA)
        self.pca = PCA9685(i2c, address=96)
        self.pca.frequency = 50 #most servos default to 50hz pulse width
        self.door = servo.Servo(self.pca.channels[0])
        self.home = 80
        self.top = 90
        self.bottom = 30
        self.spring_and_reset()

    def spring_and_reset(self):
        self.kit.motor1.throttle = 1
        time.sleep(.25)
        self.door.angle = self.bottom
        time.sleep(1)
        self.door.angle = self.top
        time.sleep(1)
        self.kit.motor1.throttle = None
        time.sleep(.25)
        self.door.angle = self.home

