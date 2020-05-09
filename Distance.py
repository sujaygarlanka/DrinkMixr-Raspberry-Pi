import time  
import RPi.GPIO as GPIO  

class Distance:
    
    def __init__(self, pin):
        self.pin = pin
    
    def get(self):
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, 0)
        time.sleep(0.000002)
        
        #send trigger signal
        GPIO.output(self.pin, 1)
        time.sleep(0.000005)
        GPIO.output(self.pin, 0)
        
        GPIO.setup(self.pin, GPIO.IN)
        while GPIO.input(self.pin)==0:
          starttime=time.time()
        while GPIO.input(self.pin)==1:
          endtime=time.time()
        duration=endtime-starttime
        # Distance is defined as time/2 (there and back) * speed of sound 34000 cm/s
        distance=duration*34000/2
        
        return distance