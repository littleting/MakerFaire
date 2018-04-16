from gpiozero import Button
from time import sleep
import subprocess
from datetime import datetime

button = Button(2)
makerfaire_location = "uk"

#Toggle button state. Default is False --> deactivated.
toggle_state = False

while True:
    button.wait_for_press()
    print('your pushed me')
    filename_1 = str(datetime.now().strftime('%d%m%Y'))
    filename_2 = str(datetime.now().strftime('%H%M%S'))
    filename = filename_1+"_"+filename_2+"_"+makerfaire_location
    #photo_process = subprocess.call("fswebcam "+filename+".jpg", shell=True)
    photo_process = subprocess.Popen("fswebcam -r 1280x960 "+filename+".jpg", shell=True)
    photo_process.wait()
    print("Captured: "+filename)
    sleep(1)