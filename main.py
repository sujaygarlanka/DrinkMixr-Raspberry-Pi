from api import API
from display import Display
from distance import Distance
import RPi.GPIO as GPIO
import time
import os

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
    num_motors_in_parallel = 2
    dispense_instructions = {}
    
    # Initially add max amount of instructions that can be executed in parallel (i.e. motors that can run in parallel)
    for _ in range(num_motors_in_parallel):
        if (len(order) > 0):
            instruction = order.pop()
            dispense_instructions[instruction["motor"]] = instruction["dispense_time"]
            control_motor(instruction["motor"], True)
            print("turning on " + instruction["motor"])

    # Dispense from motors in dispense instructions. As one finishes another is added
    while bool(dispense_instructions):
        motor = min(dispense_instructions, key=dispense_instructions.get)
        min_time = dispense_instructions[motor]
        time.sleep(min_time)
        control_motor(motor, False)
        del dispense_instructions[motor]
        dispense_instructions = {k:v-min_time for (k,v) in dispense_instructions.items()}
        print("turning off " + motor)

        if (len(order) > 0):
            instruction = order.pop()
            dispense_instructions[instruction["motor"]] = instruction["dispense_time"]
            control_motor(instruction["motor"], True)
            print("turning on " + instruction["motor"])
        
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
    
def wifi_connected():
    stream = os.popen("iwgetid")
    output = stream.read()
    if "wlan0" in output:
        return True
    return False

def get_ip_address():
    stream = os.popen("ifconfig wlan0 | grep inet | awk '{ print $2 }'")
    output = stream.read()
    return output.splitlines()[0]
  
def main():
    should_refresh_screen = True
    while True:
        if wifi_connected():
            ip = get_ip_address()
            try:
                r = api.get_order()
                if r.status_code == 200:
                    order = r.json()
                    display_order(order)
                    display.println()
                    display.print("Waiting to detect a cup...")
                    while (distance.get() > 20.0):
                        time.sleep(.5)
                    display_order(order)
                    display.println()
                    display.print("Dispensing...")
                    dispense_drink(order['dispense_instructions'])
                    should_refresh_screen = True
                else:
                    if should_refresh_screen:
                        display.clear()
                        display.println(font_size=5)
                        display.println(ip, font_size=12, color="#FFFF00") 
                        display.println("Waiting for an order...")
                        display.displayImage("/home/pi/DrinkMixr-Raspberry-Pi/media/drink.png", x=95, y=50, height=170, width=119)
                        should_refresh_screen = False
            except:
                display.displayVideo("/home/pi/DrinkMixr-Raspberry-Pi/media/loading_2.gif")
                should_refresh_screen = True
        else:
            display.displayVideo("/home/pi/DrinkMixr-Raspberry-Pi/media/loading_2.gif")
            should_refresh_screen = True
        
if __name__ == "__main__":
    main()
        
