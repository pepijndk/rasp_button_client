#!/bin/python

import RPi.GPIO as GPIO
from time import sleep
import argparse

parser = argparse.ArgumentParser(description='Smoke time')
parser.add_argument('duration', action="store", type=str)
args = parser.parse_args()

print("smoke machine activated for ", args.duration, "seconds")

PIN_SMOKE = 25  # Pin for smoke

# Zet de pinmode op Broadcom SOC.
GPIO.setmode(GPIO.BCM)
# Zet waarschuwingen uit.
GPIO.setwarnings(False)

GPIO.setup(PIN_SMOKE, GPIO.OUT)
s = GPIO.PWM(PIN_SMOKE, 50)

s.start(9)
sleep(args.duration)
s.ChangeDutyCycle(11)
sleep(0.1)
s.stop()
sleep(0.1)
