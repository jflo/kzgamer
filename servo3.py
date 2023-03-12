from gpiozero import Servo
from time import sleep

servo = Servo(18)

try:
    while True:
        servo.min()
        sleep(.5)
        servo.max()
        sleep(1.5)
except KeyboardInterrupt:
    servo.max()
    print("Program stopped")
