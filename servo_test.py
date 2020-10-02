#!/bin/python


 
# importeer de GPIO bibliotheek.
import RPi.GPIO as GPIO
# Importeer de time biblotheek voor tijdfuncties.
from time import sleep
import sys, argparse

parser = argparse.ArgumentParser(description='Short sample app')

parser.add_argument('servo', action="store", type=int)

args = parser.parse_args()

pin = 12
if args.servo == 2:
    pin = 16
if args.servo == 3:
    pin = 20
if args.servo == 4:
    pin = 21
 
# Zet de pinmode op Broadcom SOC.
GPIO.setmode(GPIO.BCM)
# Zet waarschuwingen uit.
GPIO.setwarnings(False)
 
# Zet de GPIO pin als uitgang.
GPIO.setup(pin, GPIO.OUT)
# Configureer de pin voor PWM met een frequentie van 50Hz.
p = GPIO.PWM(pin, 50)
# Start PWM op de GPIO pin met een duty-cycle van 6%
p.start(11)
 
try:
  while True:
      
    # 90 graden (links) standaard
    p.ChangeDutyCycle(11)
    sleep(4)  
      
    # 0 graden (neutraal)
    p.ChangeDutyCycle(8)
    sleep(1)
 


    
 
except KeyboardInterrupt:  
  # Stop PWM op GPIO.
  p.stop()

  GPIO.cleanup()
