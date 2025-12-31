#!/usr/bin/env python
# Cross-platform GPIO output for EVSE switch (LOW = enable charging)

from gpiozero import OutputDevice, Device
from gpiozero.pins.mock import MockFactory

# Detect if running on Raspberry Pi
def is_raspberry_pi():
    try:
        with open("/proc/cpuinfo") as f:
            cpuinfo = f.read()
        return "BCM" in cpuinfo or "Raspberry Pi" in cpuinfo
    except FileNotFoundError:
        return False

ON_PI = is_raspberry_pi()

# Use mock pins if not on a Pi
if not ON_PI:
    print("Not running on a Raspberry Pi. Using mock GPIO pins.")
    Device.pin_factory = MockFactory()

switch_pin = 5  # GPIO5 (BCM numbering)
switch = OutputDevice(switch_pin, active_high=True, initial_value=False)

# Setting the output LOW enables charging
switch.off()
print("Switch set LOW. Charging enabled.")

# Do NOT call cleanup; we want the pin to stay LOW
