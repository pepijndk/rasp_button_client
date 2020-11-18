
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
PATTERN_INTERVAL = 20
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

    ls.tulips(ls.strip)
    ls.usa_3(ls.strip)
    ls.usa(ls.strip, iterations=100)
    ls.red(ls.strip)
    ls.usa(ls.strip, iterations=100)
    ls.red(ls.strip)
    ls.usa_2(ls.strip)

    if mode == 0:
        ls.clearStrip(ls.strip)
        ls.strip.show()

    if mode == 1:
        # cls.strip.se

        print("mode 1")

        randomColor1 = ls.randomColor()

        sc.activateSmokeMachine()

        ls.strobe(ls.strip, Color(255, 255, 255), iterations=100)
        ls.strobeColorToColor(ls.strip, Color(
            255, 255, 255), randomColor1, iterations=80)
        ls.strobe(ls.strip, randomColor1, iterations=60)

        sc.deactivateSmokeMachine()
        mode = 2
    elif mode == 2:

        time_diff_pattern = (datetime.datetime.now() -
                             date_pattern).total_seconds()
        if time_diff_pattern > PATTERN_INTERVAL:
            rand = random()

            if rand > 0.5 and rand < 0.65:
                ls.colorWipeBackandForth(ls.strip, ls.randomColor())
                ls.colorWipeBackandForth(ls.strip, ls.randomColor())
            elif rand > 0.65 and rand < 0.7:
                ls.theaterChaseWidth(
                    ls.strip, color=ls.randomColor(), width=int(random() * 40))
            elif rand > 0.75 and rand < 0.76:
                ls.theaterChaseWidthRainbow(ls.strip, width=int(random() * 40))
            elif rand > 0.76 and rand < 0.77:
                ls.colorWipeNoTailRainbow(ls.strip, 50, 1, 3)  # rainbow wipe
                time.sleep(1)
                ls.colorWipeNoTailRainbow(
                    ls.strip, 50, 1, 3, inverted=True)  # rainbow wipe
            elif rand > 0.77 and rand < 0.85:
                for p in range(3 + int(random() * 10)):
                    ls.colorWipeNoTail(ls.strip, ls.randomColor(), speed=6)
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
            date_pattern = datetime.datetime.now()


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
