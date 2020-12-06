#!/bin/python
from subprocess import Popen
import os

Popen(['python3', 'smoke.py', '4'])
for i in range(50):
    print("test")
    sleep(0.1)
