from API import API
from Display import Display
from Distance import Distance
import RPi.GPIO as GPIO
import time

RELAY_VCC = 6
RELAY_GND = 12
DISTANCE_SENSOR = 14
MOTOR_1 = 17
MOTOR_2 = 22
MOTOR_3 = 18
MOTOR_4 = 23

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_VCC, GPIO.OUT)
GPIO.setup(RELAY_GND, GPIO.OUT)
GPIO.setup(MOTOR_1, GPIO.OUT)
GPIO.setup(MOTOR_2, GPIO.OUT)
GPIO.setup(MOTOR_3, GPIO.OUT)
GPIO.setup(MOTOR_4, GPIO.OUT)

GPIO.output(RELAY_VCC, GPIO.HIGH)
GPIO.output(RELAY_GND, GPIO.LOW)
GPIO.output(MOTOR_1, GPIO.HIGH)
GPIO.output(MOTOR_2, GPIO.HIGH)
GPIO.output(MOTOR_3, GPIO.HIGH)
GPIO.output(MOTOR_4, GPIO.HIGH)

api = API()
display = Display()
distance = Distance(DISTANCE_SENSOR)
      
def dispense_drink(order):
    for item in order:
        control_motor(item["motor"], True)
        print(item["motor"])
        time.sleep(item["dispense_time"])
        control_motor(item["motor"], False)
        print("turning off")
        

def control_motor(motor, on):
    if motor == "1":
        GPIO.output(MOTOR_1, not on)
    elif motor == "2":
        GPIO.output(MOTOR_2, not on)
    elif motor == "3":
        GPIO.output(MOTOR_3, not on)
    elif motor == "4":
        GPIO.output(MOTOR_4, not on)
        
def display_order(order):
    display.clear()
    display.print("Drink for " + order["user"]["name"], "#FFFF00")
    display.println()
    display.println()
    for ingredient in order["order"].keys():
        dispenseAmount = str(round(order["order"][ingredient], 2))
        display.print(ingredient + ": ", "#FFFF00")
        display.print(dispenseAmount)
        display.println(" oz")
    display.println()
    amountDrank = str(round(order["user"]["amount_drank_today"], 2))
    display.print("Drank Today: ", "#FFFF00")
    display.println(amountDrank + " oz")
  
def main():
    order_just_dispensed = True
    while True:
        r = api.get_order()
        if r.status_code == 200:
            order = r.json()
            display_order(order)
            display.println()
            display.print("Waiting to detect a cup...")
            while (distance.get() > 20.0):
                time.sleep(.5)
            display.clearln()
            display.println("Dispensing...")
            dispense_drink(order['dispense_instructions'])
            order_just_dispensed = True
        else:
            if order_just_dispensed:
                display.clear()
                display.println("Waiting for an order...")
                order_just_dispensed = False
        
if __name__ == "__main__":
    main()
        