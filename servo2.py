import RPi.GPIO as gp  
import time
 

controlPin = 12
gp.setmode(gp.BOARD)  
gp.setup(controlPin,gp.OUT)  
pwm=gp.PWM(controlPin,50)  
pwm.start(0)  
pwm.ChangeDutyCycle(0)
gp.output(controlPin, True)
time.sleep(1)
gp.output(controlPin, False)
pwm.ChangeDutyCycle(50)
gp.output(controlPin, True)
time.sleep(1)
gp.output(controlPin, False)
pwm.ChangeDutyCycle(0)
gp.output(controlPin, True)
time.sleep(1)
gp.output(controlPin, False)


pwm.stop()  
gp.cleanup() 
