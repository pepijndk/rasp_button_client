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
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)


def colorWipeNoTail(strip, color, width=20, wait_ms=0, speed=3, inverted=False):
    """Wipe color across display a pixel at a time."""
    for i in range(int((strip.numPixels() + width) / speed)):
        pixel = i * speed

        for p in range(speed):
            activatePixel(strip, pixel + p, color, inverted=inverted)
            activatePixel(strip, pixel - width - p, 0, inverted=inverted)

            # strip.setPixelColor(pixel + p, color)
            # strip.setPixelColor(pixel - width - p, 0)

        strip.show()
        time.sleep(wait_ms/1000.0)

    clearStrip(strip)


def colorWipeBackandForth(strip, color, width=20, wait_ms=0, speed=3):
    colorWipeNoTail(strip, color, width=width, wait_ms=wait_ms, speed=speed)
    time.sleep(1)
    colorWipeNoTail(strip, color, width=width, wait_ms=wait_ms,
                    speed=speed, inverted=True)

    clearStrip(strip)


def colorWipeNoTailRainbow(strip, width=20, wait_ms=0, speed=3, inverted=False):
    """Wipe color across display a pixel at a time."""
    for i in range(int((strip.numPixels() + width) / speed)):
        pixel = i * speed

        for p in range(speed):
            activatePixel(strip, pixel + p, wheel(pixel & 255),
                          inverted=inverted)
            activatePixel(strip, pixel - width - p, 0, inverted=inverted)

        strip.show()
        time.sleep(wait_ms/1000.0)

    clearStrip(strip)


def strobe(strip, color, wait_ms=40, sections=5, iterations=50):
    """strobe"""

    size = int(LED_COUNT / sections)
    prev_prev_section = 0
    prev_section = 0

    for i in range(iterations):

        section = int(random() * (sections))

        for old in range(size):
            strip.setPixelColor(old + (prev_prev_section * size) - 1, 0)

        for new in range(size):
            strip.setPixelColor(new + (section * size) - 1, color)

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
            strip.setPixelColor(old + (prev_prev_section * size) - 1, 0)

        for new in range(size):
            strip.setPixelColor(new + (section * size) - 1, color)

        prev_prev_section = prev_section
        prev_section = section
        strip.show()
        time.sleep(wait_ms/1000.0)

    for i in range(strip.numPixels()):
        strip.setPixelColor(i, 0)


def dots(strip, wait_ms=100, iterations=300, width=5, newDotsPerCycle=1):

    brightness = {
        0: 0,
        1: 1,
        2: 2,
        3: 3,
        4: 5,
        5: 7,
        6: 10,
        7: 15,
        8: 20,
        9: 25,
        10: 30,
        11: 40,
        12: 50,
        13: 60,
        14: 70,
        15: 80,
        16: 90,
        17: 100,
        18: 120,
        19: 140,
        20: 180,
    }

    dots = dict()

    def colorDot(coord, level):
        for w in range(width):
            print("activating ", coord + w, level)
            activatePixel(strip, coord + w, Color(155, 0, 155))
            # activatePixel(strip, coord + w,Color(brightness[level], 0, brightness[level]))

    for i in range(iterations):
        if random() > 0.9:

            coord = int(2 + random() * (LED_BRIGHTNESS - 4))

            print("new dot made at", coord)
            dots[coord] = 20

        for key, value in dots.items():
            colorDot(key, value)

        time.sleep(wait_ms / 1000)

    clearStrip(strip)


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
            print("back and forth")

            dots(strip)

            colorWipeNoTailRainbow(strip, 20, 1, 3)  # rainbow wipe

            colorWipeBackandForth(strip, randomColor())
            colorWipeBackandForth(strip, randomColor())
            colorWipeBackandForth(strip, randomColor())
            print("strobe")
            strobe(strip, Color(255, 255, 255))  # white wipe
            strobeTransition(strip, Color(0, 255, 0))  # Blue wipe
            strobe(strip, Color(0, 255, 0))
            strobeTransition(strip, Color(255, 255, 0),
                             color1=Color(0, 255, 0))  # Blue wipe
            strobe(strip, Color(255, 255, 0))
            print('Color wipe animations.')
            colorWipeNoTail(strip, randomColor(), 20, 1, 3)  # random wipe
            colorWipeNoTail(strip, randomColor(), 20, 1, 3)  # random wipe
            colorWipeNoTail(strip, randomColor(), 20, 1, 3)  # random wipe
            colorWipeNoTail(strip, randomColor(), 20, 1, 3)  # random wipe

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0), 10)
