from gpiozero import Button
from gpiozero import LED
from time import sleep
import subprocess
from datetime import datetime

button = Button(5)
button.hold_time = 1.5

led = LED(18)
#Toggle button state. Default is False --> deactivated.
toggle_state = False
led.off()

countdown_led = LED (17)
countdown_led.off()

#Emergency state --> False when toggle_state is deactivated
emergency_state = False

def check_toggle():
    global toggle_state
    global emergency_state
    if not toggle_state and not emergency_state: #light was off --> to on
        print("on")
        led.on()
        toggle_state = True
    else:  #light was on --> to off
        led.off()
        print("off")
        toggle_state = False
        emergency_state = False

def being_hold():
    global toggle_state
    global emergency_state
    if toggle_state and not emergency_state:
        emergency_state = True
        countdown_timer()
        led.off()
        countdown_led.off()
        toggle_state = False
        print("Hold")

def countdown_timer():
    for i in range (3):
        print(i)
        countdown_led.off()
        sleep(0.25)
        countdown_led.on()
        sleep(0.25)
    sleep(1)

while True:
    button.when_released = check_toggle
    if(button.is_held):
        being_hold()
    sleep(1)
        
