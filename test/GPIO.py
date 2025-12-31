#!/usr/bin/env python3
"""
Cross-platform GPIO info script
Prints pin modes, levels, and functions, using RPi.GPIO if available,
otherwise using a mock.
"""

import sys

try:
    import RPi.GPIO as GPIO
    ON_PI = True
except (ImportError, RuntimeError):
    print("RPi.GPIO not available. Using mock GPIO.")
    ON_PI = False

    # --- Mock GPIO constants ---
    class MockGPIO:
        BCM = 11
        BOARD = 10

        IN = 0
        OUT = 1
        I2C = 2
        SPI = 3
        HARD_PWM = 4
        SERIAL = 5
        UNKNOWN = -1

        LOW = 0
        HIGH = 1

        PUD_DOWN = 0
        PUD_UP = 1

        RISING = 0
        FALLING = 1
        BOTH = 2

        RPI_INFO = {'Mock': True}
        RPI_REVISION = 0
        VERSION = 'mock'

        _pin_modes = {}

        @staticmethod
        def gpio_function(pin):
            # Return previously set mode, default IN
            return MockGPIO._pin_modes.get(pin, MockGPIO.IN)

        @staticmethod
        def setup(pin, mode, pull_up_down=None, initial=None):
            MockGPIO._pin_modes[pin] = mode

    GPIO = MockGPIO

# --- Print GPIO constants ---
print(f"GPIO.BCM: {GPIO.BCM}")
print(f"GPIO.BOARD: {GPIO.BOARD}")
print(f"GPIO.IN: {GPIO.IN}")
print(f"GPIO.OUT: {GPIO.OUT}")
print(f"GPIO.I2C: {GPIO.I2C}")
print(f"GPIO.SPI: {GPIO.SPI}")
print(f"GPIO.HARD_PWM: {GPIO.HARD_PWM}")
print(f"GPIO.SERIAL: {GPIO.SERIAL}")
print(f"GPIO.UNKNOWN: {GPIO.UNKNOWN}")
print(f"GPIO.LOW: {GPIO.LOW}")
print(f"GPIO.HIGH: {GPIO.HIGH}")
print(f"GPIO.PUD_DOWN: {GPIO.PUD_DOWN}")
print(f"GPIO.PUD_UP: {GPIO.PUD_UP}")
print(f"GPIO.RISING: {GPIO.RISING}")
print(f"GPIO.FALLING: {GPIO.FALLING}")
print(f"GPIO.BOTH: {GPIO.BOTH}")
print(f"GPIO.RPI_INFO: {GPIO.RPI_INFO}")
print(f"GPIO.RPI_REVISION: {GPIO.RPI_REVISION}")
print(f"GPIO.VERSION: {GPIO.VERSION}")

gpio_functions = {
    GPIO.IN: 'Input',
    GPIO.OUT: 'Output',
    GPIO.I2C: 'I2C',
    GPIO.SPI: 'SPI',
    GPIO.HARD_PWM: 'HARD_PWM',
    GPIO.SERIAL: 'Serial',
    GPIO.UNKNOWN: 'Unknown'
}

print("\nGPIO.gpio_function values:")
for key, val in gpio_functions.items():
    print(f" {key}: {val}")

print("\nCurrent GPIO pin config:")
gpio_pins = range(0, 40)
for gpio_pin in gpio_pins:
    print(f" GPIO {gpio_pin} is an {gpio_functions.get(GPIO.gpio_function(gpio_pin), 'Unknown')}")

print("Done!")
