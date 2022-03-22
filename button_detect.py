from distutils.log import Log
import RPi.GPIO as GPIO
import time
from time import sleep
import sys
import os
import threading
from subprocess import call, Popen
import subprocess
import servo_controller as sc
import socket
import datetime
import ledpatterns as ls
from random import random
# import message_server_pythonversion as server

#
# Constants
#

# GPIO pins
PIN_K1 = 26  # 6  # First button
PIN_K2 = 19  # 13  # Second button
PIN_K3 = 13  # 19  # Third button
PIN_K4 = 6  # 26  # Fourth button


PIN_MAIN_BUTTON = 24
SMOKE_MACHINE_DURATION = 9
HOLD_DURATION = 1.5


# after how long of no smoke it activates the smoke machine (in s)
SMOKE_INTERVAL = 100


# other
IP_ADDRESS = "192.168.0.60"
PORT = 65432
SLEEP_DURATION = 10
TULIPS_CHANCE = 0.05

GPIO.setmode(GPIO.BCM)

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.settimeout(5)


# PIN 18: INPUT, Button input

# PIN 12: OUTPUT, Servo 1
# PIN 16: OUTPUT, Servo 2
# PIN 20: OUTPUT, Servo 3
# PIN 21: OUTPUT, Servo 4


GPIO.setup(PIN_MAIN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


# reacting to control panel button pushes
GPIO.setup(PIN_K1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_K2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_K3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_K4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_MAIN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

activated_music = False  # if the main button is pressed
activated_smoke = False
activated_lights_gr = True
activated_lights_party = False
activated_lights_party_before_activation = False

last_clicked = 0
add_player_clickable = True

connected = False
start_time = 0
# time since button is pressed
timer = 0
call_running = False

# date when smoke machine was last activated
date_smoke = datetime.datetime.now()


# wie trekt een spies vars
spies_mode = False


def registerPress(i):
    global last_clicked
    global spies_mode
    global add_player_clickable
    global call_running


    try:
        # log("btn clicked " + str(i))

        # main button
        if i == PIN_MAIN_BUTTON:
            sleep(0.02)
            if GPIO.input(PIN_MAIN_BUTTON) and activated_music == False and not call_running:
                call_running = True
                log("main button pressed", communicate=True)
                call()
            return

        sleep(0.2)
        if GPIO.input(i) or last_clicked == i:
            log("false press, returning" + str(i))
            return


        if i == PIN_K4 and spies_mode:
            if not add_player_clickable:
                return
            add_player_clickable = False
            ls.random_spies_setup(ls.strip)
            sleep(0.3)
            add_player_clickable = True
            return

        log("valid press " + str(i), communicate=True)
        last_clicked = i

        # activate random spies game
        if i == PIN_K1 and spies_mode:
            rand = random()
            flicker = 5
            if (rand < 0.5 * TULIPS_CHANCE):
                flicker = 20
                ls.random_spies_activate(ls.strip, tulips=True)
                sendToServer("start tulips")
            else:
                ls.random_spies_activate(ls.strip)

            for i in range(flicker):
                sc.activate_normal_lights()
                sleep(1)
                sc.deactivate_normal_lights()
                sleep(1)
            sc.activate_normal_lights()
            ls.clearStrip(ls.strip)
            spies_mode = False
            sendToServer("stop")
            last_clicked = 0
            return

        sleep(HOLD_DURATION)
        if not GPIO.input(i):
            log("long press" + str(i), communicate=True)
            long_press(i)

        else:
            log("short press" + str(i), communicate=True)
            short_press(i)
    except Exception as e:
        log("ERROR - register button press", communicate=True)
        log(str(e), communicate=True)



def short_press(i):
    global activated_lights_party
    global activated_lights_party_before_activation
    global activated_lights_gr
    global activated_music
    global activated_smoke
    global connected
    global last_clicked
    global spies_mode
    global date_smoke

    if i == PIN_K1:
        activated_lights_party = True
        if not activated_music:
            activated_lights_party_before_activation = True
        activate_remote()
    if i == PIN_K2:
        activated_lights_gr = True
        activate_remote()
    if i == PIN_K3:
        activated_smoke = True
        date_smoke = datetime.datetime.now()
        ls.clearStrip(ls.strip, ls.Color(0, 200, 0))
        time.sleep(3)
        ls.clearStrip(ls.strip)

    if i == PIN_K4:
        if spies_mode:
            ls.random_spies_setup(ls.strip)
        else:
            Popen(['python3', 'smoke.py', '15'],
                  cwd='/home/pi/rasp_button_client')

            if activated_lights_party:
                ls.strobeColorToColor(ls.strip, ls.randomColor(),
                                      ls.randomColor(), iterations=200)


    last_clicked = 0


def long_press(i):
    global activated_lights_party
    global activated_lights_party_before_activation
    global activated_lights_gr
    global activated_music
    global activated_smoke
    global last_clicked
    global spies_mode

    if i == PIN_K1:
        activated_lights_party = False
        activate_remote()
    if i == PIN_K2:
        ls.clearStrip(ls.strip)
        activated_lights_gr = False
        activate_remote()
        if not activated_music:
            activated_lights_party_before_activation = False
    if i == PIN_K3:
        activated_smoke = False
        ls.clearStrip(ls.strip, ls.Color(200, 0, 0))
        time.sleep(3)
        ls.clearStrip(ls.strip)
    if i == PIN_K4:
        if not spies_mode:
            spies_mode = True
            ls.random_spies_setup(ls.strip)

    last_clicked = 0


def activate_remote():
    global activated_lights_party
    global activated_lights_gr
    global activated_music

    log("party: " + str(activated_lights_party) +
          " gr: " + str(activated_lights_gr))

    if activated_lights_party:
        sc.activate_party_lights()
    else:
        sc.deactivate_party_lights()

    sleep(0.5)

    if activated_lights_gr:
        sc.activate_normal_lights()
    else:
        sc.deactivate_normal_lights()


GPIO.add_event_detect(PIN_K1, GPIO.FALLING, callback=registerPress)
GPIO.add_event_detect(PIN_K2, GPIO.FALLING, callback=registerPress)
GPIO.add_event_detect(PIN_K3, GPIO.FALLING, callback=registerPress)
GPIO.add_event_detect(PIN_K4, GPIO.FALLING, callback=registerPress)
GPIO.add_event_detect(PIN_MAIN_BUTTON, GPIO.RISING, callback=registerPress)

def log(message, communicate=False):
    print(message)
    if communicate:
        sendToServer(message)

def sendToServer(command):
    global clientSocket
    global connected

    if connected:
        try:
            clientSocket.send(command.encode())
        except socket.error:
            log("Message could not be sent")
            connected = False


def call():
    global timer
    global connected
    global activated_lights_party
    global activated_lights_gr
    global activated_music
    global activated_smoke
    global connected
    global date_smoke
    global spies_mode
    global activated_lights_party_before_activation
    global call_running

    print("call called")
    try:
        # Button is clicked when music is off
        if GPIO.input(PIN_MAIN_BUTTON) and activated_music == False:
            log("activating music", communicate=True)

            if not connected:
                log("error - not connected")
                for i in range(3):
                    ls.clearStrip(ls.strip, ls.Color(255, 0, 0))
                    ls.sleep(0.2)
                    ls.clearStrip(ls.strip)
                    ls.sleep(0.2)   
                ls.clearStrip(ls.strip)
                sleep(20)
                call()
                return



            if random() < TULIPS_CHANCE:  # TULIPS_CHANCE:  # small chance tulips
                sendToServer("start tulips")
                sleep(0.2)
                for i in range(30):
                    sc.activate_normal_lights()
                    ls.tulips(ls.strip, iterations=10)
                    sc.deactivate_normal_lights()
                    ls.tulips(ls.strip, iterations=10)
                ls.clearStrip(ls.strip)

            else:  # normal start
                sendToServer("start")

                Popen(['python3', 'smoke.py', '15'],
                    cwd='/home/pi/rasp_button_client')

                activated_music = True
                activated_lights_gr = False
                activated_lights_party = True
                activate_remote()
                date_smoke = datetime.datetime.now()

                for i in range(2):  # weer 6 na ledstrip fix
                    ls.colorWipeNoTail(ls.strip, ls.randomColor(), speed=10)

                random_color = ls.randomColor()
                ls.colorWipeNoTail(ls.strip, random_color, speed=8, tail=True)
                time.sleep(1)
                ls.strobeColorToColor(
                    ls.strip, random_color, ls.randomColor(), iterations=80)  # reset back to 100

            call() # call again
        
        # music running
        elif GPIO.input(PIN_MAIN_BUTTON) and activated_music == True:
            log("music running")

            # if activated_lights_party and not spies_mode and random() < 0.05:
            #     ls.random_pattern()


            sleep(1)
            call()
        
        # deactivate
        else:
            log("deactivating from call", communicate=True)
            sendToServer("stop")
            ls.clearStrip(ls.strip)
            activated_lights_gr = True
            activated_lights_party = False
            activated_music = False
            activate_remote()
            call_running = False
    except Exception as e:
        log("ERROR - call method", communicate=True)
        log(str(e), communicate=True)
        call()

def attempt_reconnect(flash_red=False):
    global connected

    try:
        clientSocket.connect((IP_ADDRESS, PORT))
        connected = True
        log("connection successful")  

    except socket.error:
        log("connection could not be established")

        # flash red if lights are enabled

        if flash_red:
            for i in range(3):
                ls.clearStrip(ls.strip, ls.Color(255, 0, 0))
                ls.sleep(0.2)
                ls.clearStrip(ls.strip)
                ls.sleep(0.2)

    if connected and flash_red:
        # flash green 
        for i in range(3):
            ls.clearStrip(ls.strip, ls.Color(0, 255, 0))
            ls.sleep(0.2)
            ls.clearStrip(ls.strip)
            ls.sleep(0.2)    
    
    ls.clearStrip(ls.strip)


# start of script
ls.clearStrip(ls.strip, ls.Color(255, 255, 0))
sleep(2)

attempt_reconnect(flash_red=True)


while True:
    try:
        log("activated:" + str(activated_music) + " main button: " + str(GPIO.input(PIN_MAIN_BUTTON)) + " smoke " + str(activated_smoke), communicate=True)

        if not GPIO.input(PIN_MAIN_BUTTON) and activated_music == True:
            sleep(1)
            if not GPIO.input(PIN_MAIN_BUTTON) and activated_music == True:
                log("deactivating from loop", communicate=True)
                sendToServer("stop")
                ls.clearStrip(ls.strip)
                activated_lights_gr = True
                activated_lights_party = False
                activated_music = False
                activate_remote()
                call_running = False

        # if not connected: try to reconnect
        timer = timer + 1
        # log("attempting to send message")
        message = "ping"
        try:
            clientSocket.send(message.encode())
            # log("message sent" )
        except socket.error: # set connection status and recreate socket
            connected = False
            log("message could not be sent... attempting reconnect")

            attempt_reconnect()

        # check if its time for smoke.
        # in here so it doesn't check every cycle, doesn't matter if not accurate
        time_diff = (datetime.datetime.now() - date_smoke).total_seconds()
        # if there has been no smoke in x minutes
        if time_diff > SMOKE_INTERVAL and activated_smoke and activated_lights_party:
            log("activating smoke - interval", communicate=True)
            Popen(['python3', 'smoke.py', '15'],
                cwd='/home/pi/rasp_button_client')
            date_smoke = datetime.datetime.now()

        

        if not activated_music and not activated_lights_party and not spies_mode:
            ls.clearStrip(ls.strip)

        # Random pattern

        if activated_lights_party and not spies_mode and random() < 0.1:#0.05:
                ls.random_pattern()

        if timer > 10000:
            timer = 0

        timer = timer + SLEEP_DURATION
        sleep(SLEEP_DURATION)
    except Exception as e: 
        log("ERROR - Main loop", communicate=True)
        log(str(e), communicate=True)


