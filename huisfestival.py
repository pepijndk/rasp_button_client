import ledpatterns as ls
import time
from time import sleep
import RPi.GPIO as GPIO
import servo_controller as sc
import feedback_led as fl
import datetime
from rpi_ws281x import *
from random import random

SMOKE_MACHINE_DURATION = 15

PIN_K1 = 6  # First button
PIN_K2 = 13  # Second button
PIN_K3 = 19  # Third button
PIN_K4 = 26  # Fourth button

GPIO.setmode(GPIO.BCM)


# moving dots
# comets
# random dots

GPIO.setup(PIN_K1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_K2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_K3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_K4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# how long to sleep when a song starts before activating smoke (in s)
SLEEP_UNTIL_SMOKE = 4
# after how long of no smoke it activates the smoke machine (in s)
SMOKE_INTERVAL = 3600
# after how long of now pattern there is a 50 50 chance to have a pattern
PATTERN_INTERVAL = 10
# sleep
SLEEP_DURATION = 0.2


# time since button is pressed
timer = 0
mode = 0

# reacting to control panel button pushes
smoke_active = False

# date when smoke machine was last activated
date_smoke = datetime.datetime.now()
date_pattern = datetime.datetime.now()


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
    global mode
    print("i", i)

    if i == PIN_K1:
        mode = 0
    if i == PIN_K2:
        mode = 1
        ls.setBrightness(ls.strip, 255)
    if i == PIN_K3:
        mode = 2
    if i == PIN_K4:
        activateSmoke()


GPIO.add_event_detect(PIN_K1, GPIO.FALLING, callback=registerPress)
GPIO.add_event_detect(PIN_K2, GPIO.FALLING, callback=registerPress)
GPIO.add_event_detect(PIN_K3, GPIO.FALLING, callback=registerPress)
GPIO.add_event_detect(PIN_K4, GPIO.FALLING, callback=registerPress)


def call():
    global mode
    global timer
    global date_pattern

    print("mode", mode, "timer", int(timer))

    if mode == 0:
        ls.clearStrip(ls.strip)
        ls.activatePixel(ls.strip, 0, Color(0, 255, 0))
        ls.activatePixel(ls.strip, 1, Color(0, 255, 0))
        ls.strip.show()

    if mode == 1:
        ls.setBrightness(ls.strip, 10)

        ls.strip.se

        print("mode 1")

        randomColor1 = ls.randomColor()
        randomColor2 = ls.randomColor()

        sc.activateSmokeMachine()

        ls.strobe(ls.strip, Color(255, 255, 255), iterations=100)
        ls.strobeColorToColor(ls.strip, Color(255, 255, 255), randomColor1)
        ls.strobeColorToColor(ls.strip, randomColor1, randomColor2)
        ls.strobe(ls.strip, randomColor2)

        sc.deactivateSmokeMachine()
        mode = 2
        ls.setBrightness(ls.strip, 255)
    elif mode == 2:
        time_diff_pattern = (datetime.datetime.now() -
                             date_pattern).total_seconds()
        if time_diff_pattern > PATTERN_INTERVAL:
            date_pattern = datetime.datetime.now()
            rand = random()

            if rand > 0.5 and rand < 0.7:
                ls.colorWipeBackandForth(ls.strip, ls.randomColor())
            elif rand > 0.7 and rand < 0.75:
                ls.colorWipeNoTailRainbow(ls.strip, 30, 1, 3)  # rainbow wipe
            elif rand > 0.75 and rand < 0.85:
                for p in range(3 + int(random() * 10)):
                    ls.colorWipeNoTail(ls.strip, ls.randomColor(), speed=4)
            elif rand > 0.85 and rand < 0.9:
                ls.colorWipeBackandForth(ls.strip, ls.randomColor(), tail=True)
            elif rand > 0.90 and rand < 0.93:
                ls.theaterChase(ls.strip, ls.randomColor())
            elif rand > 0.93 and rand < 0.95:
                ls.colorWipeNoTailRainbow(
                    ls.strip, 30, 1, 3, tail=True)  # rainbow wipe
                time.sleep(1)
                ls.colorWipeNoTail(ls.strip, Color(0, 0, 0))
            elif rand > 0.95 and rand < 0.99:
                ls.dots(ls.strip)
            elif rand > 0.99 and rand < 1:
                ls.strobeRainbow(ls.strip, iterations=300)


while True:
    call()

    # if not connected: try to reconnect
    # check if its time for smoke.
    # in here so it doesn't check every cycle, doesn't matter if not accurate
    time_diff = (datetime.datetime.now() - date_smoke).total_seconds()
    if time_diff > SMOKE_INTERVAL and mode > 0:  # if there has been no smoke in 10 minutes
        activateSmoke()

    # deactivate smoke if it has been on for a certain amount of time
    if smoke_active:
        time_diff = (datetime.datetime.now() - date_smoke).total_seconds()
        if time_diff > SMOKE_MACHINE_DURATION:  # if there has been no smoke in 10 minutes
            # deactivate smoke
            print("deactivating smoke")

            smoke_active = False
            sc.deactivateSmokeMachine()

    if timer > 10000:
        timer = 0

    timer = timer + SLEEP_DURATION
    sleep(SLEEP_DURATION)
