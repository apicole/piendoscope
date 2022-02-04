#!/usr/bin/python3
##################################
# Endoscope Camera for Raspberry Pi
##################################

###Find which device 
###import evdev
###
###devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
###for device in devices:
###    print(device.fn, device.name, device.phys)
### >> /dev/input/event3 USB2.0 PC CAMERA: USB2.0 PC CAM usb-3f980000.usb-1.3/button
###
###Find which signal / button
###from evdev import InputDevice, categorize, ecodes
###dev = InputDevice('/dev/input/event3')
###print(dev)
###for event in dev.read_loop():
###    if event.type == ecodes.EV_KEY:
###        print(categorize(event))
### >> key event at 1643962822.987611, 212 (KEY_CAMERA), up/down

import time
from evdev import InputDevice, categorize, ecodes
import datetime as dt
import cv2
import os
import threading

_image=None
saveimg=False
output_folder = '/var/www/html/Webcam/'
if not os.path.exists(output_folder): os.makedirs(output_folder)
myloop = True
gwidth =480
gheight=320
font = cv2.FONT_HERSHEY_SIMPLEX

def buttonctrl():
    global saveimg
    while True: 
        dev3 = InputDevice('/dev/input/event3')
        for event in dev3.read_loop():
            if event.type == ecodes.EV_KEY:
                saveimg=True

def _quit():
    myloop = False
    cv2.destroyAllWindows()
    worker.join()
    print("App quittée par l'utilisateur")

def mouse_click(event,x,y,flags,param):
    """Used to save an image on double-click"""
    global saveimg
    # print (" Mouse is " + str(x) + " "  + str(y))
    #if event == cv2.EVENT_LBUTTONDBLCLK:
    #    _quit()
    if event == cv2.EVENT_LBUTTONDOWN:
        if ((x > (gwidth -35) ) and ( y < 35)):
            _quit()
        else:
            saveimg=True
    if event == cv2.EVENT_RBUTTONDOWN:
        _quit()

"""Print out a summary of the shortcut keys available during video runtime."""        
print("Raccourcis utiles:")
print("Esc - Quitte et ferme")
print("S - Sauvegarde une image")
print("Click - Sauvegarde une image")
print("Bouton- Sauvegarde une image")
print("Double-click - Quitte et ferme")

worker = threading.Thread(target=buttonctrl)
worker.start()
while myloop == True:
    try:
        cv2.namedWindow('Endoscope Image', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('Endoscope Image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        vidcap = cv2.VideoCapture(1)
        if not vidcap.isOpened():
            print("Cannot open camera")
            exit()
        ret, _image = vidcap.read()
        vidcap.release()
        cv2.setMouseCallback('Endoscope Image',mouse_click)
        key = cv2.waitKey(1) & 0xFF
        if key==27:  # Exit nicely if escape key is used
            _quit()
        if key == ord("s"):  # If s is chosen, save an image to file
            saveimg=True
        cv2.putText(_image,str(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),(10,30), font, .8,(255,255,255),2,cv2.LINE_AA)
        cv2.imshow('Endoscope Image', _image)
        if saveimg==True:
            saveimg=False
            fname = output_folder + "CameraEndoscope"+ dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.jpg'
            cv2.imwrite(fname, _image)
            cv2.putText(_image, 'Image sauvegardee!', (100,150),cv2.FONT_HERSHEY_SIMPLEX, .8, (255, 255, 255), 2)
            cv2.imshow('Endoscope Image', _image)
    except RuntimeError as e:
        if e.message == 'Too many retries':
            print("Too many retries error caught, continuing...")
            continue
        raise

cv2.destroyAllWindows()
