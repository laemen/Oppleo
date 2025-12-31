#!/usr/bin/env python3
"""
Cross-platform LED pulse (candle light style) using gpiozero.
Uses real GPIO on Raspberry Pi, Mock pins elsewhere.
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

# --- LED Setup ---
led_pin = 16  # BCM numbering
led = PWMLED(led_pin)

def millis():
    return int(round(time.time() * 1000))

# --- Pulse parameters ---
pulse_value = 0
pulse_millis = millis()
pulse_up = True
pulse_duty_cycle = 1  # 1s / 100 steps = 10ms per step
pulse_min = 3
pulse_max = 98

print("Stop with CTRL + C")

try:
    while True:
        if millis() > (pulse_millis + ((pulse_duty_cycle * 1000) / 100)):
            # Reverse direction at edges
            if (pulse_up and pulse_value >= pulse_max) or (not pulse_up and pulse_value <= pulse_min):
                pulse_up = not pulse_up

            pulse_value = pulse_value + 1 if pulse_up else pulse_value - 1
            led.value = pulse_value / 100  # gpiozero PWMLED uses 0..1
            print(f"pulse_value = {pulse_value}")
            pulse_millis = millis()

        time.sleep(0.005)  # small delay to reduce CPU usage

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    led.off()
