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
import servo_controller as sc


# LED strip configuration:
LED_COUNT = 307      # Number of LED pixels.
LED_PIN = 18      # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
# True to invert the signal (when using NPN transistor level shift)
LED_INVERT = False
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# ideeen:
# paarse punten


def activatePixel(strip, pixel, color, inverted=False):
    if pixel > LED_COUNT or pixel < 0:
        return
    if not inverted:
        strip.setPixelColor(int(pixel), color)
    else:
        strip.setPixelColor((LED_COUNT - int(pixel)), color)


def clearStrip(strip, color=Color(0, 0, 0)):
    for i in range(strip.numPixels()):
        activatePixel(strip, i, color)
    strip.show()


# Define functions which animate LEDs in various ways.


def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        activatePixel(strip, i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)


def colorWipeNoTail(strip, color, width=20, wait_ms=0, speed=3, inverted=False, tail=False):
    """Wipe color across display a pixel at a time."""
    for i in range(int((strip.numPixels() + width) / speed)):
        pixel = i * speed

        for p in range(speed):

            activatePixel(strip, pixel + p, color, inverted=inverted)

            if tail == False:
                activatePixel(strip, pixel - width - p, 0, inverted=inverted)

            # strip.setPixelColor(pixel + p, color)
            # strip.setPixelColor(pixel - width - p, 0)

        strip.show()
        time.sleep(wait_ms/1000.0)

    if not tail:
        clearStrip(strip)


def colorWipeBackandForth(strip, color, width=20, wait_ms=0, speed=4, tail=False):
    if not tail:
        colorWipeNoTail(strip, color, width=width,
                        wait_ms=wait_ms, speed=speed)
    else:
        colorWipeNoTail(strip, color, width=width,
                        wait_ms=wait_ms, speed=speed, tail=True)
    time.sleep(0.6)
    colorWipeNoTail(strip, color, width=width, wait_ms=wait_ms,
                    speed=speed, inverted=True)

    clearStrip(strip)


def colorWipeNoTailRainbow(strip, width=20, wait_ms=0, speed=3, inverted=False, tail=False):
    """Wipe color across display a pixel at a time."""
    for i in range(int((strip.numPixels() + width) / speed)):
        pixel = i * speed

        for p in range(speed):
            activatePixel(strip, pixel + p, wheel(pixel & 255),
                          inverted=inverted)

            if not tail:
                activatePixel(strip, pixel - width - p,
                              Color(0, 0, 0), inverted=inverted)

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
            activatePixel(
                strip, old + (prev_prev_section * size) - 1, Color(0, 0, 0))

        for new in range(size):
            activatePixel(strip, new + (section * size) - 1, color)

        prev_prev_section = prev_section
        prev_section = section
        strip.show()
        time.sleep(wait_ms/1000.0)

    clearStrip(strip)


def strobeRainbow(strip, wait_ms=40, sections=5, iterations=150):
    """strobe"""

    size = int(LED_COUNT / sections)
    prev_prev_section = 0
    prev_section = 0

    for i in range(iterations):

        section = int(random() * (sections))

        for old in range(size):
            activatePixel(
                strip, old + (prev_prev_section * size) - 1, Color(0, 0, 0))

        for new in range(size):
            activatePixel(strip, new + (section * size) - 1, wheel(i & 255))

        prev_prev_section = prev_section
        prev_section = section
        strip.show()
        time.sleep(wait_ms/1000.0)

    clearStrip(strip)


def strobeTransition(strip, color2, color1=Color(255, 255, 255), wait_ms=40, sections=5, iterations=60, percentage_random=1):
    """strobe"""

    def getColor(i):
        # length transition period
        length_transition = int(0.4 * iterations)
        start_transition = int(iterations / 2) - int(length_transition / 2)
        color_num = (i - start_transition) / length_transition

        #
        if random() <= color_num:
            return color2
        else:
            return color1

    size = int(LED_COUNT / sections)
    prev_prev_section = 0
    prev_section = 0

    for i in range(iterations):

        color = getColor(i)

        section = int(random() * (sections))

        for old in range(size):
            activatePixel(
                strip, old + (prev_prev_section * size) - 1, Color(0, 0, 0))

        for new in range(size):
            activatePixel(strip, new + (section * size) - 1, color)

        prev_prev_section = prev_section
        prev_section = section
        strip.show()
        time.sleep(wait_ms/1000.0)

    for i in range(strip.numPixels()):
        activatePixel(strip, i, Color(0, 0, 0))


def dots(strip, wait_ms=100, iterations=1000, width=5, newDotsPerCycle=1):

    clearStrip(strip)

    chance = 0.9

    def brightness(level):
        return int(0.1 * (level ** 2))

    dots = dict()

    def colorDot(coord, level):

        for w in range(width):
            # print("activating ", coord + w, level)
            # activatePixel(strip, coord + w, Color(155, 0, 155))
            activatePixel(strip, coord + w,
                          Color(brightness(level), 0, brightness(level)))

    for i in range(iterations):
        if random() > chance:

            coord = int(2 + random() * (LED_COUNT - 4))

            dots[coord] = 50

        for key, value in dots.items():

            if value > 0:
                colorDot(key, value)
                dots[key] = value - 1

        time.sleep(wait_ms / 1000)

        strip.show()

        if chance == 0.9 and i > 0.8 * iterations:
            chance = 0.98

    clearStrip(strip)


def theaterChase(strip, color, wait_ms=50, iterations=30):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                activatePixel(strip, i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                activatePixel(strip, i+q, Color(0, 0, 0))


def theaterChaseWidth(strip, color, wait_ms=0, iterations=50, width=5):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for i in range(0, strip.numPixels(), 2*width):
            for p in range(width):
                activatePixel(strip, (i+j+p) & LED_COUNT, color)

        strip.show()
        time.sleep(wait_ms/1000.0)
        for i in range(strip.numPixels()):
            activatePixel(strip, i, Color(0, 0, 0))


def theaterChaseWidthRainbow(strip, wait_ms=0, iterations=80, width=5):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for i in range(0, strip.numPixels(), 2*width):
            for p in range(width):
                activatePixel(strip, i+j+p, wheel(i+j+p & 255))

        strip.show()
        time.sleep(wait_ms/1000.0)
        for i in range(strip.numPixels()):
            activatePixel(strip, i, Color(0, 0, 0))


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


def randomColor():
    # types:
    # type 1: 1 color (0.25)
    # type 2: primary + secundary (0.5)
    # type 3: primary + secundary + tertiary + 0.25 (0.5)

    rand_colors = [
        Color(255, 0, 0),
        Color(0, 255, 0),
        Color(0, 0, 255),

        Color(255, 255, 0),
        Color(0, 255, 255),
        Color(255, 0, 255),


        Color(255, 255, 20),
        Color(20, 255, 255),
        Color(255, 20, 255)
    ]

    return rand_colors[int(random() * (len(rand_colors) - 1))]


def strobeColorToColor(strip, color1, color2, wait_ms=40, sections=5, iterations=40, percentage_random=1):
    strobe(strip, color1, wait_ms=wait_ms,
           sections=sections, iterations=iterations)
    strobeTransition(strip,  color2, color1=color1, wait_ms=wait_ms, sections=sections,
                     iterations=iterations * 2, percentage_random=percentage_random)  # Blue wipe
    strobe(strip, color2, wait_ms=wait_ms,
           sections=sections, iterations=iterations)


strip = Adafruit_NeoPixel(
    LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

#
# Patterns
#


# def pattern_strobe(strip):
#     randomColor1 = ls.randomColor()
#     strobe(strip, Color(255, 255, 255), iterations=100)
#     strobeColorToColor(strip, Color(255, 255, 255),
#                        randomColor1, iterations=80)
#     strobe(strip, randomColor1)
