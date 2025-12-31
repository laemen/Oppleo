#!/usr/bin/env python3
"""
Cross-platform flickering LED using gpiozero.
Works on Raspberry Pi or desktop with Mock pins.
"""

import time
import random
from gpiozero import PWMLED, Device
from gpiozero.pins.mock import MockFactory

# --- Detect Raspberry Pi ---
def is_raspberry_pi():
    try:
        with open("/proc/cpuinfo") as f:
            cpuinfo = f.read()
        return "BCM" in cpuinfo or "Raspberry Pi" in cpuinfo
    except FileNotFoundError:
        return False

ON_PI = is_raspberry_pi()
if not ON_PI:
    print("Not running on Raspberry Pi. Using mock GPIO pins.")
    Device.pin_factory = MockFactory()

# --- LED Setup (BCM pins) ---
led_red = PWMLED(16)
led_green = PWMLED(12)
led_blue = PWMLED(13)

# Choose LED to flicker
led = led_red

# --- Helper functions ---
def brightness():
    """Return a random brightness value (0.05–1.0)"""
    return random.randint(5, 100) / 100

def flicker():
    """Return a short random delay for flicker effect"""
    return random.random() / 8

print("Stop -> CTRL + C")

try:
    while True:
        led.value = brightness()
        time.sleep(flicker())

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    led.off()
    print("Clean exit")
