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


PIN_MAIN_BUTTON = 23
PIN_LED_RED = 24
SMOKE_MACHINE_DURATION = 8
HOLD_DURATION = 1.5


# how long to sleep when a song starts before activating smoke (in s)
SLEEP_UNTIL_SMOKE = 4
# after how long of no smoke it activates the smoke machine (in s)
SMOKE_INTERVAL = 300


# other
IP_ADDRESS = "192.168.0.61"
PORT = 65432
SLEEP_DURATION = 0.1
TULIPS_CHANCE = 0.15

GPIO.setmode(GPIO.BCM)


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.settimeout(5)


# PIN 18: INPUT, Button input
# PIN 24: OUTPUT, Active is true

# PIN 12: OUTPUT, Servo 1
# PIN 16: OUTPUT, Servo 2
# PIN 20: OUTPUT, Servo 3
# PIN 21: OUTPUT, Servo 4


GPIO.setup(PIN_MAIN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(24, GPIO.OUT)


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

last_clicked = 0

connected = False
start_time = 0
# time since button is pressed
timer = 0

smoke_active = False

# date when smoke machine was last activated
date_smoke = datetime.datetime.now()


def activateSmoke():
    global smoke_active
    global date_smoke

    date_smoke = datetime.datetime.now()
    smoke_active = True
    sc.activateSmokeMachine()

    # # workaround for bug
    # sleep(0.1)
    # sc.deactivateSmokeMachine()
    # sc.activateSmokeMachine()


def registerPress(i):
    global last_clicked

    print("btn clicked ", i)
    sleep(0.1)
    if GPIO.input(i) or last_clicked == i:
        print("false press, returning", i)
        return

    print("valid press", i)
    last_clicked = i

    sleep(HOLD_DURATION)
    if GPIO.input(i):
        print("long press", i)
        long_press(i)

    else:
        print("short press", i)
        short_press(i)


def short_press(i):
    global activated_lights_party
    global activated_lights_gr
    global activated_music
    global activated_music
    global connected

    if i == PIN_K1:
        activated_lights_party = True
    if i == PIN_K2:
        activated_lights_gr = True
    if i == PIN_K3:
        activated_smoke = True
    if i == PIN_K4:
        if not activated_music:
            sc.deactivate()
            if connected:
                sendToServer(stop)
        else:
            sc.activate()
            # smoke machine
            ls.strobeColorToColor(ls.strip, Color(
                255, 255, 255), randomColor1, iterations=100)

    activate_remote()
    last_clicked = 0


def long_press(i):
    if i == PIN_K1:
        activated_lights_party = False
    if i == PIN_K2:
        activated_lights_gr = False
    if i == PIN_K3:
        activated_smoke = False
    if i == PIN_K4:

    activate_remote()
    last_clicked = 0


def activate_remote():
    if activated_lights_gr:
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
    global activated_music
    global connected

    print("activated:", GPIO.input(PIN_MAIN_BUTTON), " connected: ", connected)

    # Button is clicked when everything is off
    if GPIO.input(PIN_MAIN_BUTTON) and activated_music == False:
        print("activating")
        activated_music = True

        if random() < TULIPS_CHANCE:  # TULIPS_CHANCE:  # small chance tulips
            sendToServer("start tulips")
            sc.activate()
            sleep(0.2)
            for i in range(30):
                sc.activate_normal_lights()
                ls.tulips(ls.strip, iterations=10)
                sc.deactivate_normal_lights()
                ls.tulips(ls.strip, iterations=10)

        else:  # normal start
            sendToServer("start")
            sc.activate()
            for i in range(7):
                ls.colorWipeNoTail(ls.strip, ls.randomColor(), speed=8)

            random_color = ls.randomColor()
            ls.colorWipeNoTail(ls.strip, random_color, speed=8, tail=True)
            time.sleep(0.3)
            # smoke machine
            ls.strobeColorToColor(
                ls.strip, random_color, ls.randomColor(), iterations=80)  # reset back to 100

    elif activated_lights_gr:
        if activated_music and random() < 0.0006:
            ls.random_pattern()
        elif random() < 0.0003:
            ls.random_pattern()

    elif not GPIO.input(PIN_MAIN_BUTTON) and activated_music == True:
        print("deactivation noticed")
        sleep(3)  # prevent false positive

        if not GPIO.input(PIN_MAIN_BUTTON):
            sendToServer("stop")
            activate_remote()


# start of script
sc.deactivate()
# sc.deactivateSmokeMachine()
sleep(2)


try:
    clientSocket.connect((IP_ADDRESS, PORT))
    connected = True
    fl.setStatus(2)
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
            fl.setStatus(1)
            clientSocket = socket.socket()
            print("message could not be sent... attempting reconnect")
            try:  # try to connect
                clientSocket.connect((IP_ADDRESS, PORT))
                connected = True
                fl.setStatus(2)
                print("re-connection successful")
            except socket.error:
                print("connection could not be made, continuing without connection'")

        # check if its time for smoke.
        # in here so it doesn't check every cycle, doesn't matter if not accurate
        time_diff = (datetime.datetime.now() - date_smoke).total_seconds()
        print("time diff", time_diff)
        if time_diff > SMOKE_INTERVAL and activated:  # if there has been no smoke in 10 minutes
            activateSmoke()

    # deactivate smoke if it has been on for a certain amount of time
    if smoke_active:
        time_diff = (datetime.datetime.now() - date_smoke).total_seconds()
        print("time diff2", time_diff)
        if time_diff > SMOKE_MACHINE_DURATION:  # if there has been no smoke in x minutes
            # deactivate smoke
            print("deactivating smoke")

            smoke_active = False
            sc.deactivateSmokeMachine()

    if timer > 10000:
        timer = 0

    timer = timer + SLEEP_DURATION
    sleep(SLEEP_DURATION)
