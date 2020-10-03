#!/usr/bin/env python3
# rpi_ws281x library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

import time
from rpi_ws281x import *
import argparse
from random import random

# LED strip configuration:
LED_COUNT = 315      # Number of LED pixels.
LED_PIN = 18      # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
# True to invert the signal (when using NPN transistor level shift)
LED_INVERT = False
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)


def colorWipeNoTail(strip, color, width=20, wait_ms=0, speed=2):
    """Wipe color across display a pixel at a time."""
    for i in range(int((strip.numPixels() + width) / speed)):
        pixel = i * speed

        for p in range(speed):
            strip.setPixelColor(pixel + p, color)
            strip.setPixelColor(pixel - width - p, 0)

        strip.show()
        time.sleep(wait_ms/1000.0)

    sleep(1)

    for i in range(int((strip.numPixels() + width) / speed)):
        pixel = LED_COUNT - (i * speed)

        for p in range(speed):
            strip.setPixelColor(pixel + p, color)
            strip.setPixelColor(pixel + width - p, 0)

        strip.show()
        time.sleep(wait_ms/1000.0)


def strobe(strip, color, wait_ms=40, sections=5, iterations=50):
    """strobe"""

    size = int(LED_COUNT / sections)
    prev_prev_section = 0
    prev_section = 0

    for i in range(iterations):

        section = int(random() * (sections))

        for old in range(size):
            strip.setPixelColor(old + (prev_prev_section * size), 0)

        for new in range(size):
            strip.setPixelColor(new + (section * size), color)

        prev_prev_section = prev_section
        prev_section = section
        strip.show()
        time.sleep(wait_ms/1000.0)

    for i in range(strip.numPixels()):
        strip.setPixelColor(i, 0)


def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(
                i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)


def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true',
                        help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(
        LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        while True:
            print("strobe")
            strobe(strip, Color(255, 255, 255))  # white wipe
            strobe(strip, Color(0, 255, 0))  # Blue wipe
            print('Color wipe animations.')
            colorWipeNoTail(strip, Color((int(random() * 255), (int(random() * 255), (int(random() * 255)), 20, 0, 4)  # random wipe
            colorWipeNoTail(strip, Color((int(random() * 255), (int(random() * 255), (int(random() * 255)), 20, 0, 4)  # Red wipe
            colorWipeNoTail(strip, Color((int(random() * 255), (int(random() * 255), (int(random() * 255)), 20, 0, 4)  # Red wipe
            colorWipeNoTail(strip, Color((int(random() * 255), (int(random() * 255), (int(random() * 255)), 20, 0, 4)  # Red wipe
            colorWipeNoTail(strip, Color(255, 0, 0), 20, 0, 4)  # Red wipe
            colorWipeNoTail(strip, Color(0, 255, 0), 20, 0, 4)  # Blue wipe
            colorWipeNoTail(strip, Color(0, 0, 255), 20, 4)  # Green wipe
            print('Theater chase animations.')
            theaterChase(strip, Color(127, 127, 127))  # White theater chase
            theaterChase(strip, Color(127,   0,   0))  # Red theater chase
            theaterChase(strip, Color(0,   0, 127))  # Blue theater chase

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0), 10)
