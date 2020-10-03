# importeer de GPIO bibliotheek.
import RPi.GPIO as GPIO

#
# Constants
#

# GPIO pins
PIN_LED_RED = 27  # Red led
PIN_LED_BLUE = 22  # Red led
PIN_LED_GREEN = 17  # Red led


#
# Configuration
#

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_LED_RED, GPIO.OUT)
GPIO.setup(PIN_LED_BLUE, GPIO.OUT)
GPIO.setup(PIN_LED_GREEN, GPIO.OUT)


#
# Vars
#

# 0 = running script, 1 = listening but not connected, 2 = running and connected
status = 0

#
# Functions
#


def setStatus(status):
    GPIO.output(PIN_LED_RED, GPIO.LOW)
    GPIO.output(PIN_LED_GREEN, GPIO.LOW)
    GPIO.output(PIN_LED_BLUE, GPIO.LOW)
    if status == 0:
        GPIO.output(PIN_LED_BLUE, GPIO.HIGH)
    if status == 1:
        GPIO.output(PIN_LED_RED, GPIO.HIGH)
    if status == 2:
        #GPIO.output(PIN_LED_GREEN, GPIO.HIGH)

        # because green is not working in this led, activate blue again:
        GPIO.output(PIN_LED_BLUE, GPIO.HIGH)
