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
ip = "192.168.0.114"


# PIN 18: OUTPUT, Script is running
# PIN 23: INPUT, Button input
# PIN 24: OUTPUT, Active is true

# PIN 12: OUTPUT, Servo 1
# PIN 16: OUTPUT, Servo 2
# PIN 20: OUTPUT, Servo 3
# PIN 21: OUTPUT, Servo 4

GPIO.setup(18, GPIO.OUT)
GPIO.setup(23, GPIO.IN)
GPIO.setup(24, GPIO.OUT)

# reacting to control panel button pushes
GPIO.setup(6, GPIO.OUT)  # k4 (lowest)
GPIO.setup(13, GPIO.OUT)  # k3 (3rd bttn)
GPIO.setup(19, GPIO.OUT)  # k2 (2nd bttn)
GPIO.setup(26, GPIO.OUT)  # k1 (highest button)

activated = False  # if the main button is pressed
mode = 2  # mode it is currently in
timer = 0

# Modes:
# 0 = party lights on
# 1 = party lights on & normal lights off
# 2 = party lights on & normal lights off & music on (everything)


def call():
    global mode
    global activated
    global timer

    print("call ", GPIO.input(23), "    state", state)

    # If it is in the process of deactivating
    if deactivating:
        print("not responding because in deactivation process")
        return

    # Button is clicked when everything is off
    if GPIO.input(23) and state == 0:
        print("activating")
        clientSocket.send("start".encode())
        sc.activate()
        state = 3

    elif not GPIO.input(23):
        if state != 0:
            print("deactivation noticed")
            sleep(2)  # prevent false positive
            deactivating = True

            while state > 0:
                if not GPIO.input(23):

                    if state == 3:
                        print("deactivating music")
                        # deactivate music first
                        clientSocket.send("stop".encode())
                    if state == 2:
                        print("deactivating stage 1")
                        sc.deactivate_stage_1()
                    if state == 1:
                        print("deactivating stage 2")
                        sc.deactivate_stage_2()
                    state = state - 1
                    if state != 0:
                        sleep(4)
                else:
                    print("canceling deactivation")
                    break

            deactivating = False


GPIO.output(24, GPIO.HIGH)
sc.deactivate()

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 65432

while clientSocket.connect_ex((ip, port)) != 0:
    print("waiting to connect")
    sleep(5)

connected = True
print("connected to server")
i = 0

try:
    while True:      # attempt to send and receive wave, otherwise reconnect
        message = "ping " + str(int(i / 100))
        if i % 100 == 0:
            try:
                clientSocket.send(message.encode())
            except socket.error:          # set connection status and recreate socket
                connected = False
                clientSocket = socket.socket()
                print("connection lost... reconnecting")
                while not connected:              # attempt to reconnect, otherwise sleep for 2 seconds
                    try:
                        clientSocket.connect((ip, port))
                        connected = True
                        print("re-connection successful")
                    except socket.error:
                        sleep(2)
        i = i + 1
        if i > 1000000:
            i = 0
        call()
        sleep(0.1)
finally:
    clientSocket.close()
    GPIO.cleanup()


# while True:
#    input_state = GPIO.input(23)
#    if input_state == True and active == False:
#        active = True
#        activate()
#    elif input_state == False and active == True:
#        sleep(0.1)
#        if input_state == False:
#            active = False
#            deactivate()
#    sleep(0.05)
