#!/bin/python


import RPi.GPIO as GPIO
import sys
import argparse

from time import sleep


# PIN 12: OUTPUT, Servo 1
# PIN 16: OUTPUT, Servo 2
# PIN 20: OUTPUT, Servo 3
# PIN 21: OUTPUT, Servo 4


# Zet de pinmode op Broadcom SOC.
GPIO.setmode(GPIO.BCM)
# Zet waarschuwingen uit.
GPIO.setwarnings(False)

GPIO.setup(12, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)


def activate_servo(num):  # Hier de pins veranderen als er ooit een kapot gaat.
    gpio_pin = 12
    if num == 2:
        gpio_pin = 16
    if num == 3:
        gpio_pin = 20
    if num == 4:
        gpio_pin = 21

    p = GPIO.PWM(gpio_pin, 50)
    p.start(9)
    sleep(0.2)
    p.ChangeDutyCycle(11)
    sleep(0.2)
    p.stop()

# stages: (correspond with modes in button_detect)
# 0 = party lights on
# 1 = party lights on & normal lights off


def activate_stage_0():  # party lampen aan
    activate_servo(3)


def activate_stage_1():  # gr lampen uit
    activate_servo(2)


def deactivate_stage_1():  # gr lampen weer aan
    activate_servo(1)


def deactivate_stage_0():  # party lampen uit
    activate_servo(4)


def activate():  # Eerst gr lampen uit dan lampen+ledstrips aan
    activate_stage_0()
    sleep(0.5)
    activate_stage_1()


def deactivate():
    deactivate_stage_0()
    sleep(0.5)
    deactivate_stage_1()
