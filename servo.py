import RPi.GPIO as gp  
import time
 

controlPin = 12
gp.setmode(gp.BOARD)  
gp.setup(controlPin,gp.OUT)  
print("gp setup")
pwm=gp.PWM(controlPin,50)  
print("pwm instantiated")
time.sleep(.5)
pwm.start(0)  
print("pwm started")
time.sleep(.5)
def set_angle(angle):
  print(f"setting angle to {angle}")
  duty_cycle = angle / 18 + 2
  gp.output(controlPin, True)
  pwm.ChangeDutyCycle(duty_cycle)
  time.sleep(1)
  gp.output(controlPin, False)
  pwm.ChangeDutyCycle(0)

set_angle(0)
time.sleep(1)
set_angle(0)
time.sleep(1)
set_angle(0)
pwm.stop()  

gp.cleanup() 
