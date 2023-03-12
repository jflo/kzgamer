import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
ledPin = 11
GPIO.setup(ledPin, GPIO.OUT)

GPIO.output(ledPin, 1)
time.sleep(5)
GPIO.output(ledPin,0)

GPIO.cleanup()
