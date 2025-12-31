#!/usr/bin/env python
# Candle-flicker buzzer cross-platform
# Uses PWM on Raspberry Pi, OutputDevice mock elsewhere

import time
import random
from gpiozero import PWMOutputDevice, OutputDevice
from gpiozero import Device
from gpiozero.pins.mock import MockFactory

# Detect if running on Raspberry Pi
def is_raspberry_pi():
    try:
        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read()
        return "BCM" in cpuinfo or "Raspberry Pi" in cpuinfo
    except FileNotFoundError:
        return False

ON_PI = is_raspberry_pi()

# Setup GPIO
if not ON_PI:
    print("Not on Raspberry Pi, using mock GPIO pins.")
    Device.pin_factory = MockFactory()

# Select appropriate device class
DeviceClass = PWMOutputDevice if ON_PI else OutputDevice

# GPIO23 (BCM numbering)
buzzer = DeviceClass(23)

def flicker_pulse():
    """Random flicker pulse for buzzer"""
    if ON_PI:
        # PWM: random duty cycle
        intensity = random.uniform(0.2, 0.8)
        duration = random.uniform(0.03, 0.12)
        buzzer.value = intensity
        time.sleep(duration)
        buzzer.value = 0
    else:
        # Mock or non-PWM: just on/off
        buzzer.on()
        time.sleep(random.uniform(0.03, 0.12))
        buzzer.off()
    time.sleep(random.uniform(0.05, 0.15))

try:
    print("Starting candle-flicker buzzer. Press Ctrl+C to stop.")
    while True:
        flicker_pulse()
except KeyboardInterrupt:
    buzzer.off()
    print("\nStopped.")
