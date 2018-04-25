from gpiozero import Button
from gpiozero import LED
from time import sleep
from datetime import datetime

import subprocess
import RPi.GPIO as GPIO

import sys
import time
import Adafruit_MPR121.MPR121 as MPR121
from pygame import mixer
import pygame
import requests

#website URL
URL = 'http://makeusefulstuff.herokuapp.com/upload'

#Pipsta
PIPSTAPRINT_TEXT = "python BasicPrint.py"
PIPSTAPRINT_QR = "python qr.py"

#captouch pin number
CAPPIN = 256
#location
LOCATION = "uk"

#music file
MUSIC = "person_cheering.wav"

#images to be displayed
WELCOME_IMAGE = 'PicturesPi/welcome.jpg'
PHOTO_TAKEN_IMAGE = 'PicturesPi/photoistaken.jpg'
COUNT_DOWN_IMAGES = ['PicturesPi/timer-3-01.jpg', 'PicturesPi/timer-2-01.jpg', 'PicturesPi/timer-1-01.jpg']
CAPTURING_IMAGE = 'PicturesPi/capturing.jpg'
THANK_YOU_IMAGE = 'PicturesPi/thankyou.jpg'
TRY_AGAIN = "PicturesPi/somethingwrong.jpg"

DISPLAY_STATUS = ['welcome', 'timer1', 'timer2', 'timer3', 'taken', 'thankyou']
WHITE = (255,255,255)



#functions defined
def display_image(img):
    image = pygame.image.load(img)
    screen.fill(WHITE)
    screen.blit(image,(0,0))
    pygame.display.update() 

def check_enable():
    global enable_status
    global emergency_status
    
    if not enable_status and not emergency_status:
        print("system is enabled")
        status_led.on()
        enable_status = True
    else:
        print("system is disabled")
        status_led.off()
        enable_status = False
        emergency_status = False

def disable_process():
    global enable_status
    global sending_success
    print("guest book process is finished, welcome new vistor")
    enable_status = False
    sending_success = False
    status_led.off()
    countdown_led.off()
    display_image(WELCOME_IMAGE)

def squeeze_being_squeezed():
    print("I am squeezed!!")
    sleep(0.5)

def squeeze_take_photo():
    print("I am squeezed and will a take photo")
    main_process()
    

def cap_being_touched():
    print("I am being touched!!")
    sleep(0.5)

def cap_take_photo():
    print("I am being touched and will take a photo")
    main_process()

def emergency():
    global enable_status
    global emergency_status
    if enable_status and not emergency_status:
        print("fire---take a photo")
        emergency_status = True
        main_process()

def countdown_timer():
    for i in range(3):
        countdown_led.off()
        sleep(0.25)
        countdown_led.on()
        
        display_image(COUNT_DOWN_IMAGES[i])
        
        sleep(0.25)
    sleep(1)

def take_photo():
    countdown_timer()
    filename_1 = str(datetime.now().strftime('%d%m%Y'))
    filename_2 = str(datetime.now().strftime('%H%M%S'))
    filename = filename_1+"_"+filename_2+"_"+LOCATION
    
    display_image(CAPTURING_IMAGE)
    
    #photo_process = subprocess.call("fswebcam "+filename+".jpg", shell=True)
    photo_process = subprocess.Popen("fswebcam -r 1280x960 "+filename+".jpg", shell=True)
    photo_process.wait()
    print("process2: "+str(photo_process.returncode))
    print("Captured: "+filename)
    return {'process': photo_process.returncode, 'filename':filename}

def play_sound():
    mixer.music.play()
    while mixer.music.get_busy() == True:
        continue

def print_receipt(makername, qrpath):
    display_image(PHOTO_TAKEN_IMAGE)
    
    print_text_command = PIPSTAPRINT_TEXT +" "+makername
    print_qr_command = PIPSTAPRINT_QR +" "+qrpath
    print_text = subprocess.Popen(print_text_command, shell=True)
    print_text.wait()
    print_qr=  subprocess.Popen(print_qr_command, shell=True)
    print_qr.wait()
    
    sleep(1.0)
    display_image(THANK_YOU_IMAGE)
    sleep(1.5)

def send_file(filename):
    try:
        files = {'photo': open(filename, 'rb')}
        r = requests.post(URL, files=files)
        print(r.json())
        data = r.json()
        if data['success']:
            makername = data['name']
            qrpath = data['path']
            print(" name: "+makername+" path: "+qrpath)
            
            return {'success': True, 'makername': makername, 'path':qrpath}
        else:
            print("sending error, try again")
            return {'success': False, 'makername': None, 'path': None}
            
    #except FileNotFoundError:
    except IOError:
        print("File not found, try again")
        return {'success': False, 'makername': None, 'path': None}
    except:
        print("unexpected error, try again")
        return {'success': False, 'makername': None, 'path': None}

def somethingwrong():
    display_image(TRY_AGAIN)
    sleep(1.5)

def main_process():
    photoprocess = take_photo()
    if photoprocess['process'] == 0:
        global sending_success
        count_send_attemp = 0
        while not sending_success and count_send_attemp <= 3:
            filename = photoprocess['filename']+".jpg"
            sendingprocess = send_file(filename)
            sending_success = sendingprocess['success']
            count_send_attemp += 1
        
        if sending_success:
            play_sound()
            print_receipt(sendingprocess['makername'], sendingprocess['path'])
        else:
            #try again
            print("try again")
            somethingwrong()
        disable_process()
    else:
        #try again
        somethingwrong()
        print("try again")
        disable_process()
    sleep(1.5)



#squeez button type
squeeze_button = Button(4)

#enable  button. Enable all buttons to trigger the capturing process
enable_button = Button(5)
enable_button.hold_time = 1.5

#enable_status: 1press-->enable; 2press-->disable; hold-->trigger the capturing process when enabled
enable_status = False

#emergency status led: on-->activated; off-->deactivated
status_led = LED(18)
status_led.off()

#emergency_status: emergency status is enabled with the emergency
#emergency_status is enable (True) when enable_status is True
emergency_status = False

#countdown led
countdown_led = LED(17)
countdown_led.off()

#music
mixer.init()
mixer.music.load(MUSIC)

#image variables
capturing_image = ""
#sending_success is true when Success response from website is true. 
sending_success = False 

#code starts here
print ("Hello Maker Faire UK - Sqeeze button and Cap Touch")

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



#init to display on screen
pygame.init()
screen = pygame.display.set_mode((1280,960), 0,32)
display_image(WELCOME_IMAGE)

while True:
    enable_button.when_released = check_enable
    
    if enable_button.is_held:
        emergency()
    
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
            if current_touched & CAPPIN and enable_status:
                cap_take_photo()
            elif current_touched & CAPPIN:
                cap_being_touched()
            
            #print('{0} touched!'.format(i))
        # Next check if transitioned from touched to not touched.
        #if not current_touched & pin_bit and last_touched & pin_bit:
            #print('{0} released!'.format(i))
    # Update last state and wait a short period before repeating.
    last_touched = current_touched
    
    if enable_status:
        #squeeze_button check squeeze
        squeeze_button.when_pressed = squeeze_take_photo
    else:
        squeeze_button.when_pressed = squeeze_being_squeezed
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit();
    
    sleep(0.5)
