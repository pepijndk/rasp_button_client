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

GPIO.setmode(GPIO.BCM)
ip = "192.168.0.61"

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 65432


# PIN 18: INPUT, Button input
# PIN 24: OUTPUT, Active is true

# PIN 12: OUTPUT, Servo 1
# PIN 16: OUTPUT, Servo 2
# PIN 20: OUTPUT, Servo 3
# PIN 21: OUTPUT, Servo 4

GPIO.setup(18, GPIO.IN)
GPIO.setup(24, GPIO.OUT)

# reacting to control panel button pushes
GPIO.setup(6, GPIO.OUT)  # k4 (lowest)
GPIO.setup(13, GPIO.OUT)  # k3 (3rd bttn)
GPIO.setup(19, GPIO.OUT)  # k2 (2nd bttn)
GPIO.setup(26, GPIO.OUT)  # k1 (highest button)

activated = False  # if the main button is pressed
mode = 2  # mode it is currently in
connected = False

timer_since_on = 0
timer_since_mode_switch = 0

# Modes:
# 0 = party lights on
# 1 = party lights on & normal lights off
# 2 = party lights on & normal lights off & music on (everything)


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
    sleep(0.1)


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
