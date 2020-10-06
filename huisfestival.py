import ledpatterns as ls
import time
from time import sleep
import RPi.GPIO as GPIO
import servo_controller as sc
import datetime
from rpi_ws281x import *

SMOKE_MACHINE_DURATION = 15

PIN_K1 = 6  # First button
PIN_K2 = 13  # Second button
PIN_K3 = 19  # Third button
PIN_K4 = 26  # Fourth button

GPIO.setmode(GPIO.BCM)

GPIO.setup(PIN_K1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_K2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_K3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_K4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# how long to sleep when a song starts before activating smoke (in s)
SLEEP_UNTIL_SMOKE = 4
# after how long of no smoke it activates the smoke machine (in s)
SMOKE_INTERVAL = 3600
# sleep
SLEEP_DURATION = 0.1


# time since button is pressed
timer = 0
mode = 1

# reacting to control panel button pushes
smoke_active = False

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
    global mode

    if i == PIN_K1:
        mode = 0
    if i == PIN_K2:
        mode = 1
    if i == PIN_K3:
        mode = 3
    if i == PIN_K4:
        activateSmoke()


def call():
    global mode
    global timer

    if mode == 0:
        ls.activatePixel(ls.strip, 0, Color(0, 255, 0))
        ls.activatePixel(ls.strip, 1, Color(0, 255, 0))
        ls.activatePixel(ls.strip, 2, Color(0, 255, 0))

    if mode == 1:

        randomColor1 = randomColor()
        randomColor2 = randomColor()

        sc.activateSmokeMachine()

        ls.strobe(ls.strip, Color(255, 255, 255), iterations=100)
        ls.strobeColorToColor(ls.strip, Color(255, 255, 255), randomColor1)
        ls.strobeColorToColor(ls.strip, randomColor1, randomColor2)
        ls.strobe(ls.strip, randomColor2)

        sc.deactivateSmokeMachine()
        mode = 2
    elif mode == 2:
        rand = random()

        if rand > 0.5 and rand < 0.7:
            colorWipeBackandForth(ls.strip, randomColor())
        elif rand > 0.7 and rand < 0.75:
            colorWipeNoTailRainbow(ls.strip, 30, 1, 3)  # rainbow wipe
        elif rand > 0.75 and rand < 0.85:
            for p in range(3 + int(random() * 10)):
                colorWipeNoTail(ls.strip, randomColor(), speed=4)
        elif rand > 0.85 and rand < 0.9:
            colorWipeBackandForth(ls.strip, randomColor(), tail=True)
        elif rand > 0.90 and rand < 0.93:
            theaterChase(ls.strip, randomColor())
        elif rand > 0.93 and rand < 0.95:
            colorWipeNoTailRainbow(
                ls.strip, 30, 1, 3, tail=True)  # rainbow wipe
            sleep(1)
            colorWipeNoTail(ls.strip, Color(0, 0, 0))
        elif rand > 0.95 and rand < 0.99:
            dots(ls.strip, )
        elif rand > 0.99 and rand < 1:
            strobeRainbow(ls.strip, iterations=300)


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
