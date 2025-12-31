#!/usr/bin/env python
# Kaarslicht-style PWM buzzer using gpiozero
# Cross-platform: uses PWM on Pi, OutputDevice mock elsewhere

import random
import time
from gpiozero import PWMOutputDevice, OutputDevice, Device
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

# Use mock GPIO pins if not on Raspberry Pi
if not ON_PI:
    print("Not running on Raspberry Pi. Using Mock GPIO pins.")
    Device.pin_factory = MockFactory()

# Select appropriate device class
DeviceClass = PWMOutputDevice if ON_PI else OutputDevice

# GPIO16 (BCM numbering)
buzzer = DeviceClass(16)

def pulse_buzzer(duration, intensity=0.5):
    """Turn on the buzzer at a certain intensity for a short duration"""
    if ON_PI:
        buzzer.value = intensity  # PWM duty cycle
        time.sleep(duration)
        buzzer.value = 0
    else:
        # On non-Pi: just on/off
        buzzer.on()
        time.sleep(duration)
        buzzer.off()
    time.sleep(0.05)  # short pause between pulses

# Replicating original fixed sequence
pulse_buzzer(0.05)
time.sleep(1)

pulse_buzzer(0.1)
pulse_buzzer(0.1)
time.sleep(1)

pulse_buzzer(0.05)
pulse_buzzer(0.05)
pulse_buzzer(0.05)

# Optional: loop with random “candle flicker” effect
for _ in range(10):
    pulse_buzzer(random.uniform(0.03, 0.1), random.uniform(0.2, 0.8))

print("Done.")
