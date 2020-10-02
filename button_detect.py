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
# import message_server_pythonversion as server

#
# Constants
#

# GPIO pins
PIN_K1 = 26  # First button
PIN_K2 = 19  # Second button
PIN_K3 = 13  # Third button
PIN_K4 = 6  # Fourth button

PIN_MAIN_BUTTON = 18
PIN_LED_RED = 24

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


activated = False  # if the main button is pressed
mode = 2  # mode it is currently in
connected = False


# time since button is pressed
timer_since_on = 0

# counts down from 30 when k-button is clicked, mode back to 2 if at 0
timer_since_mode_switch = 0

# Modes:
# 0 = party lights on
# 1 = party lights on & normal lights off
# 2 = party lights on & normal lights off & music on (everything)


def registerPress(i):
    print("btn clicked ", i)

    # differentiate between if activated is true.
    # if it is not activated it will set itself to that mode for 30 seconds
    #   if false:                   if true:
    #   k1 = set mode to 2          (next song) // extra feature
    #   k2 = set mode to 1          <--
    #   k3 = set mode to 0          <--
    #   k4 = reset to normal        (smoke machine) // extra

    if not activated and i != PIN_K4:
        timer_since_mode_switch = 30
        if i = PIN_K1:
            mode = 2
        if i = PIN_K2:
            mode = 1
        if i = PIN_K3:
            mode = 0

    elif activated:
        if i = PIN_K1:
            if mode == 2:  # if music was playing, play next song
                print("next song")  # todo
        if i = PIN_K2:
            if mode == 2:  # if the music was on, turn it off
                print("turn music off'")  # todo

            # make sure lights are in mode 1
            sc.activate_stage_0()
            sc.activate_stage_1()

        if i = PIN_K3:
            if mode == 2:  # if the music was on, turn it off
                print("turn music off'")  # todo

            # make sure lights are in mode 0
            sc.activate_stage_0()
            sc.deactivate_stage_1()

        if i = PIN_K4:
            print("activating smoke machine")


GPIO.add_event_detect(PIN_K1, GPIO.FALLING, callback=registerPress)
GPIO.add_event_detect(PIN_K2, GPIO.FALLING, callback=registerPress)
GPIO.add_event_detect(PIN_K3, GPIO.FALLING, callback=registerPress)
GPIO.add_event_detect(PIN_K4, GPIO.FALLING, callback=registerPress)


def call():
    global mode
    global activated
    global timer
    global connected

    print("call ", GPIO.input(18))

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
                print("sending message to server to start music")
            sc.activate()

    elif not GPIO.input(18) and activated == True:
        print("deactivation noticed")
        sleep(3)  # prevent false positive

        if not GPIO.input(18):
            sc.deactivate()
            activated = False
            print("sending message to server to stop music")


while True:
    call()

    if timer_since_mode_switch > 0:
        timer_since_mode_switch = timer_since_mode_switch - step_size
        if timer_since_mode_switch = < 0:
            mode = 2

    sleep(step_size)


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
