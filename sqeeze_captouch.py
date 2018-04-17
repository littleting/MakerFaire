from gpiozero import Button
from time import sleep
from datetime import datetime

import subprocess
import RPi.GPIO as GPIO

import sys
import time
import Adafruit_MPR121.MPR121 as MPR121

#captouch pin number
CAPPIN = 256
#location
LOCATION = "uk"

print ("Hello Maker Faire UK - Sqeeze button and Cap Touch")

#squeez button type
squeeze_button = Button(4)

#emergency button. Enable all buttons to trigger the capturing process
emergency_button = Button(5)

#toggle_status: 1press-->enable; 2press-->disable; hold-->trigger the capturing process when enabled
toggle_status = False

#emergency status led: on-->activated; off-->deactivated
status_led = LED(18)
status_led.off()

#emergency_status: emergency status is enabled with the emergency
#emergency_status is enable (True) when toggle status is True
emergency_status = False

#countdown led
countdown_led = LED(17)
countdown_led.off()

# Create MPR121 instance.
cap = MPR121.MPR121()

# Initialize communication with MPR121 using default I2C bus of device, and
# default I2C address (0x5A).  On BeagleBone Black will default to I2C bus 0.
if not cap.begin():
    print('Error initializing MPR121.  Check your wiring!')
    sys.exit(1)

print('Press Ctrl-C to quit.')
cap.set_thresholds(8,4)
last_touched = cap.touched()

def squeeze_being_squeezed():
    print("I am squeezed!!")
    sleep(0.5)

def squeeze_take_photo():
    print("I am squeezed and will a take photo")
    take_photo()
    sleep(0.5)

def cap_take_photo():
    print("I am being touched!!! and will take a photo")
    sleep(0.5)

def take_photo():
    filename_1 = str(datetime.now().strftime('%d%m%Y'))
    filename_2 = str(datetime.now().strftime('%H%M%S'))
    filename = filename_1+"_"+filename_2+"_"+LOCATION
    #photo_process = subprocess.call("fswebcam "+filename+".jpg", shell=True)
    photo_process = subprocess.Popen("fswebcam -r 1280x960 "+filename+".jpg", shell=True)
    photo_process.wait()
    print("Captured: "+filename)

while True:
    squeeze_button.when_pressed = squeeze_take_photo
    
    #cap_touch check touch
    current_touched = cap.touched()
    # Check each pin's last and current state to see if it was pressed or released.
    for i in range(12):
        # Each pin is represented by a bit in the touched value.  A value of 1
        # means the pin is being touched, and 0 means it is not being touched.
        pin_bit = 1 << i
        
        # First check if transitioned from not touched to touched.
        if current_touched & pin_bit and not last_touched & pin_bit:
            print('{0} touched!'.format(i))
            #check is Pin 8 is touched
            if current_touched & CAPPIN:
                cap_take_photo()
            
            #print('{0} touched!'.format(i))
        # Next check if transitioned from touched to not touched.
        #if not current_touched & pin_bit and last_touched & pin_bit:
            #print('{0} released!'.format(i))
    # Update last state and wait a short period before repeating.
    last_touched = current_touched
    sleep(0.5)
