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
# import message_server_pythonversion as server

#
# Constants
#

# GPIO pins
PIN_K1 = 6  # First button
PIN_K2 = 13  # Second button
PIN_K3 = 19  # Third button
PIN_K4 = 26  # Fourth button


PIN_MAIN_BUTTON = 18
PIN_LED_RED = 24
SMOKE_MACHINE_DURATION = 15


# how long to sleep when a song starts before activating smoke (in s)
SLEEP_UNTIL_SMOKE = 4
# after how long of no smoke it activates the smoke machine (in s)
SMOKE_INTERVAL = 60


# other
IP_ADDRESS = "192.168.0.61"
PORT = 65432
SLEEP_DURATION = 0.1

GPIO.setmode(GPIO.BCM)


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


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
    
    # workaround for bug
    sleep(0.1)
    sc.deactivateSmokeMachine()
    sc.activateSmokeMachine()


def registerPress(i):
    global timer_since_mode_switch
    global activated
    global mode

    print("btn clicked ", i)

    # differentiate between if activated is true.
    # if it is not activated it will set itself to that mode for 30 seconds
    #   if false:                   if true:
    #   k1 = set mode to 2          next song
    #   k2 = set mode to 1          <--
    #   k3 = set mode to 0          <--
    #   k4 = reset to normal        (smoke machine) // extra

    if not activated:
        timer_since_mode_switch = 30
        if i == PIN_K1:
            mode = 2
        if i == PIN_K2:
            mode = 1
        if i == PIN_K3:
            mode = 0
        if i == PIN_K4:
            sc.deactivate()

    elif activated:
        if i == PIN_K1:
            if mode == 2:  # if music was playing, play next song
                print("next song")
                message = "next"
                clientSocket.send(message.encode())
                sleep(4)
                activateSmoke()
            else:
                print("start")
                message = "start"
                clientSocket.send(message.encode())

        if i == PIN_K2:
            if mode == 2:  # if the music was on, turn it off
                print("turn music off'")
                message = "stop"
                clientSocket.send(message.encode())

            # make sure lights are in mode 1
            sc.activate()

        if i == PIN_K3:
            if mode == 2:  # if the music was on, turn it off
                print("turn music off'")
                message = "stop"
                clientSocket.send(message.encode())

            # make sure lights are in mode 0
            sc.activate_stage_0()
            sleep(0.5)
            sc.deactivate_stage_1()

        if i == PIN_K4:
            print("activating smoke machine")
            activateSmoke()


GPIO.add_event_detect(PIN_K1, GPIO.FALLING, callback=registerPress)
GPIO.add_event_detect(PIN_K2, GPIO.FALLING, callback=registerPress)
GPIO.add_event_detect(PIN_K3, GPIO.FALLING, callback=registerPress)
GPIO.add_event_detect(PIN_K4, GPIO.FALLING, callback=registerPress)


def call():
    global mode
    global activated
    global timer
    global connected
    global clientSocket

    print("call", GPIO.input(18), "mode", mode, "connected", connected)

    # Button is clicked when everything is off
    if GPIO.input(18) and activated == False:
        print("activating")
        activated = True

        if mode == 0:
            sc.activate_stage_0()
        elif mode == 1:
            sc.activate()
        elif mode == 2:
            if connected:
                message = "start"
                clientSocket.send(message.encode())
            sc.activate()
            activateSmoke()

    elif not GPIO.input(18) and activated == True:
        print("deactivation noticed")
        sleep(3)  # prevent false positive

        if not GPIO.input(18):
            sc.deactivate()
            activated = False
            print("sending message to server to stop music")


# start of script
sc.deactivate()

try:
    clientSocket.connect((IP_ADDRESS, PORT))
    connected = True
    print("connection successful")
except socket.error:
    print("connection could not be established")


while True:
    call()

    if timer_since_mode_switch > 0:
        timer_since_mode_switch = timer_since_mode_switch - SLEEP_DURATION
        if timer_since_mode_switch <= 0:
            mode = 2

    # if not connected: try to reconnect
    if timer % 10 == 0:
        print("attempting to send message")
        message = "ping"
        try:
            clientSocket.send(message.encode())
        except socket.error:          # set connection status and recreate socket
            connected = False
            clientSocket = socket.socket()
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
        if time_diff > 3600:  # if there has been no smoke in 10 minutes
            activateSmoke()

    # deactivate smoke if it has been on for a certain amount of time
    if smoke_active:
        time_diff = (datetime.datetime.now() - date_smoke).total_seconds()
        print("time diff2", time_diff)
        if time_diff > SMOKE_MACHINE_DURATION:  # if there has been no smoke in 10 minutes
            # deactivate smoke
            print("deactivating smoke")

            smoke_active = False
            sc.deactivateSmokeMachine()

    timer = timer + SLEEP_DURATION
    sleep(SLEEP_DURATION)


# GPIO.output(24, GPIO.HIGH)
# sc.deactivate()


# while clientSocket.connect_ex((ip, port)) != 0:
#     print("waiting to connect")
#     sleep(5)

# connected = True
# print("connected to server")
# i = 0

# # try:
# #     while True:      # attempt to send and receive wave, otherwise reconnect
# #         message = "ping " + str(int(i / 100))
# #         if i % 100 == 0:
# #             try:
# #                 clientSocket.send(message.encode())
# #             except socket.error:          # set connection status and recreate socket
# #                 connected = False
# #                 clientSocket = socket.socket()
# #                 print("connection lost... reconnecting")
# #                 while not connected:              # attempt to reconnect, otherwise sleep for 2 seconds
# #                     try:
# #                         clientSocket.connect((ip, port))
# #                         connected = True
# #                         print("re-connection successful")
# #                     except socket.error:
# #                         sleep(2)
# #         i = i + 1
# #         if i > 1000000:
# #             i = 0
# #         call()
# #         sleep(0.1)
# # finally:
# #     clientSocket.close()
# #     GPIO.cleanup()
