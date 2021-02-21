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
SLEEP_DURATION = 0.1
TULIPS_CHANCE = 0.1

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

# Modes:
# 0 = party lights on
# 1 = party lights on & normal lights off
# 2 = party lights on & normal lights off & music on (everything)

activated_music = False  # if the main button is pressed
activated_smoke = False
activated_lights_gr = True
activated_lights_party = False
activated_lights_party_before_activation = False

last_clicked = 0

connected = False
start_time = 0
# time since button is pressed
timer = 0

# date when smoke machine was last activated
date_smoke = datetime.datetime.now()


# wie trekt een spies vars
spies_mode = False


def registerPress(i):
    global last_clicked
    global spies_mode

    print("btn clicked ", i)
    sleep(0.11)
    if GPIO.input(i) or last_clicked == i:
        print("false press, returning", i)
        return

    if i == PIN_K4 and spies_mode:
        ls.random_spies_setup(ls.strip)
        return

    print("valid press", i)
    last_clicked = i

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
        if (rand < TULIPS_CHANCE):
            sendToServer("stop")
        return

    sleep(HOLD_DURATION)
    if not GPIO.input(i):
        print("long press", i)
        long_press(i)

    else:
        print("short press", i)
        short_press(i)


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
                  cwd='/home/pi/Documents/escalatieknop')

            if activated_lights_party:
                ls.strobeColorToColor(ls.strip, ls.randomColor(),
                                      ls.randomColor(), iterations=120)

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
        if not spies_mode and not activated_music:
            spies_mode = True
            ls.theaterChaseWidthRainbow(ls.strip, iterations=20, width=10)
            ls.random_spies_setup(ls.strip)

    last_clicked = 0


def activate_remote():
    global activated_lights_party
    global activated_lights_gr
    global activated_music

    print("party: " + str(activated_lights_party) +
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


def sendToServer(command):
    global clientSocket
    global connected

    if connected:
        try:
            clientSocket.send(command.encode())
        except socket.error:
            print("Message could not be sent")
            connected = False


def call():
    global timer
    global connected
    global tulips
    global activated_lights_party
    global activated_lights_gr
    global activated_music
    global activated_smoke
    global connected
    global date_smoke
    global spies_mode
    global activated_lights_party_before_activation

    print("activated:", GPIO.input(PIN_MAIN_BUTTON),
          " connected: ", connected, "smoke", activated_smoke)

    # Button is clicked when everything is off
    if GPIO.input(PIN_MAIN_BUTTON) and activated_music == False:
        print("activating")

        activated_music = True
        activated_lights_gr = False
        activated_lights_party = True
        activate_remote()
        date_smoke = datetime.datetime.now()

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
                  cwd='/home/pi/Documents/escalatieknop')

            for i in range(7):
                ls.colorWipeNoTail(ls.strip, ls.randomColor(), speed=7)

            random_color = ls.randomColor()
            ls.colorWipeNoTail(ls.strip, random_color, speed=8, tail=True)
            time.sleep(1)
            ls.strobeColorToColor(
                ls.strip, random_color, ls.randomColor(), iterations=80)  # reset back to 100

    if not GPIO.input(PIN_MAIN_BUTTON) and activated_music == True:
        print("deactivation noticed")
        sleep(3)  # prevent false positive

        if not GPIO.input(PIN_MAIN_BUTTON):
            sendToServer("stop")
            ls.clearStrip(ls.strip)
            activated_lights_gr = True
            activated_lights_party = False
            activate_remote()
            activated_music = False


# start of script
ls.clearStrip(ls.strip)
sc.deactivate()
ls.sleep(2)


try:
    clientSocket.connect((IP_ADDRESS, PORT))
    connected = True
    print("connection successful")
except socket.error:
    print("connection could not be established")


while True:
    call()

    # if not connected: try to reconnect
    if int(timer) % 10 == 0:
        timer = timer + 1
        print("attempting to send message")
        message = "ping"
        try:
            clientSocket.send(message.encode())
            print("message sent")
        except socket.error:          # set connection status and recreate socket
            connected = False
            print("message could not be sent... attempting reconnect")
            try:  # try to connect
                clientSocket.connect((IP_ADDRESS, PORT))
                connected = True
                print("re-connection successful")
            except socket.error:
                print("connection could not be made, continuing without connection'")

        # check if its time for smoke.
        # in here so it doesn't check every cycle, doesn't matter if not accurate
        time_diff = (datetime.datetime.now() - date_smoke).total_seconds()
        print("time diff", time_diff)
        # if there has been no smoke in 10 minutes
        if time_diff > SMOKE_INTERVAL and activated_smoke and activated_lights_party:
            print("activating smoke aut")
            Popen(['python3', 'smoke.py', '10'],
                  cwd='/home/pi/Documents/escalatieknop')
            date_smoke = datetime.datetime.now()

        if activated_lights_party and not activated_lights_gr:
            if random() < 0.05:  # *10 if ledstrip works again
                ls.random_pattern()
        elif activated_lights_party:
            if random() < 0.02:
                ls.random_pattern()

    if timer > 10000:
        timer = 0

    timer = timer + SLEEP_DURATION
    sleep(SLEEP_DURATION)
