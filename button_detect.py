import RPi.GPIO as GPIO
import time
from time import sleep
import sys
import os
import threading
from subprocess import call, Popen
import subprocess
import servo_controller as sc
import feedback_led as fl
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


# how long to sleep when a song starts before activating smoke (in s)
SLEEP_UNTIL_SMOKE = 4
# after how long of no smoke it activates the smoke machine (in s)
SMOKE_INTERVAL = 300


# other
IP_ADDRESS = "192.168.0.61"
PORT = 65432
SLEEP_DURATION = 0.1
TULIPS_CHANCE = 0.1

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

activated = False  # if the main button is pressed
mode = 2  # mode it is currently in
connected = False
start_time = 0
# time since button is pressed
timer = 0

faking = False

smoke_active = False

# counts down from 30 when k-button is clicked, mode back to 2 if at 0
timer_since_mode_switch = 0

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
    global timer_since_mode_switch
    global activated
    global mode
    global faking

    print("btn clicked ", i)
    sleep(0.15)
    if GPIO.input(i):
        print("false press, returning", i)
        return

    print("valid press", i)

    # differentiate between if activated is true.
    # if it is not activated it will set itself to that mode for 30 seconds
    #   if false:                   if true:
    #   k1 =   k4 set mode to 0          next song
    #   k2 =   k3 set mode to 1          <--
    #   k3 =   k2 set mode to 2          <--
    #   k4 =   k1 reset to normal        (smoke machine) // extra

    if not activated:
        timer_since_mode_switch = 30
        if i == PIN_K1:
            mode = 0
        if i == PIN_K2:
            mode = 1
        if i == PIN_K3:
            mode = 2
        if i == PIN_K4:
            sc.deactivateSmokeMachine()
            sc.deactivate()
            sendToServer("stop")
            sleep(2)
            sc.deactivate()

    elif activated:
        if i == PIN_K1:
            if mode == 2 and connected:  # if the music was on, turn it off
                sendToServer("stop")

            # make sure lights are in mode 0
            sc.activate_normal_lights()
            sc.activate_party_lights()

            mode = 0

        if i == PIN_K2:
            if mode == 2 and connected:  # if the music was on, turn it off
                sendToServer("stop")

            sc.activate()

            mode = 1

        if i == PIN_K3:
            sendToServer("start")

            # make sure lights are in mode 2
            sc.activate()

            mode = 2

        if i == PIN_K4:  # smoke and strobe
            print("activating smoke machine")
            # activateSmoke()

            ls.strobe(ls.strip, Color(255, 255, 255), iterations=100)
            ls.strobeColorToColor(ls.strip, Color(
                255, 255, 255), randomColor1, iterations=80)
            ls.strobe(ls.strip, randomColor1, iterations=60)


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
            fl.setStatus(1)
            connected = False


def call():
    global mode
    global activated
    global timer
    global connected
    global faking

    print("activated:", GPIO.input(PIN_MAIN_BUTTON),
          " mode:", mode, " connected: ", connected)

    # Modes:
    # 0 = party lights on
    # 1 = party lights on & normal lights off
    # 2 = party lights on & normal lights off & music on (everything)

    # Button is clicked when everything is off
    if GPIO.input(PIN_MAIN_BUTTON) and activated == False:
        print("activating")
        activated = True

        if mode == 0:
            sc.activate_party_lights()
        elif mode == 1:
            sc.activate()
        elif mode == 2:
            if random() < TULIPS_CHANCE:  # TULIPS_CHANCE:  # small chance tulips
                sendToServer("start tulips")
                sc.activate_party_lights()
                sc.deactivate_normal_lights()
                sleep(0.2)
                for i in range(30):
                    sc.activate_normal_lights()
                    ls.tulips(ls.strip, iterations=10)
                    sc.deactivate_normal_lights()
                    ls.tulips(ls.strip, iterations=10)

            else:  # normal start
                sendToServer("start")
                sc.activate()
                for i in range(6):
                    ls.colorWipeNoTail(ls.strip, ls.randomColor(), speed=8)

                random_color = ls.randomColor()
                ls.colorWipeNoTail(ls.strip, random_color, speed=8, tail=True)
                time.sleep(0.3)
                activateSmoke()
                ls.strobeColorToColor(
                    ls.strip, random_color, ls.randomColor(), iterations=80)  # reset back to 100
                sc.deactivateSmokeMachine()

    elif GPIO.input(PIN_MAIN_BUTTON) and activated:
        if random() < 0.0003:
            print("random pattern")
            ls.random_pattern()

    elif not GPIO.input(PIN_MAIN_BUTTON) and activated == True and not faking:
        print("deactivation noticed")
        sleep(3)  # prevent false positive

        if not GPIO.input(PIN_MAIN_BUTTON):
            sc.deactivate()
            activated = False

            sendToServer("stop")


# start of script
sc.deactivate()
# sc.deactivateSmokeMachine()
fl.setStatus(0)
sleep(2)


try:
    clientSocket.connect((IP_ADDRESS, PORT))
    connected = True
    fl.setStatus(2)
    print("connection successful")
except socket.error:
    print("connection could not be established")
    fl.setStatus(1)


while True:
    call()

    if timer_since_mode_switch > 0:
        timer_since_mode_switch = timer_since_mode_switch - SLEEP_DURATION
        if timer_since_mode_switch <= 0:
            mode = 2

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
