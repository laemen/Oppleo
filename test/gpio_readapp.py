#!/usr/bin/env python3
"""
Read all GPIO pins (cross-platform)
Uses pigpio on Raspberry Pi, mock values elsewhere
"""

import sys
import time
import random

# Detect if running on Raspberry Pi
def is_raspberry_pi():
    try:
        with open("/proc/cpuinfo") as f:
            cpuinfo = f.read()
        return "BCM" in cpuinfo or "Raspberry Pi" in cpuinfo
    except FileNotFoundError:
        return False

ON_PI = is_raspberry_pi()

if ON_PI:
    import pigpio
else:
    print("Not on a Raspberry Pi. Using mock GPIO values.")

# --- GPIO Setup ---
MODES = ["IN", "OUT", "ALT5", "ALT4", "ALT0", "ALT1", "ALT2", "ALT3"]

HEADER = ('3.3v', '5v', 2, '5v', 3, 'GND', 4, 14, 'GND', 15, 17, 18, 27, 'GND', 22, 23,
          '3.3v', 24, 10, 'GND', 9, 25, 11, 8, 'GND', 7, 0, 1, 5, 'GND', 6, 12, 13, 'GND',
          19, 16, 26, 20, 'GND', 21)
GPIOPINS = 40

FUNCTION = {
    'Pull': ('High',) * 28,
    'ALT0': ('SDA0','SCL0','SDA1','SCL1','GPCLK0','GPCLK1','GPCLK2','SPI0_CE1_N','SPI0_CE0_N',
             'SPI0_MISO','SPI0_MOSI','SPI0_SCLK','PWM0','PWM1','TXD0','RXD0','FL0','FL1','PCM_CLK',
             'PCM_FS','PCM_DIN','PCM_DOUT','SD0_CLK','SD0_XMD','SD0_DATO','SD0_DAT1','SD0_DAT2','SD0_DAT3'),
    # other ALT modes omitted for brevity
}

# --- Pin state function ---
def pin_state(g, pi_obj=None):
    if ON_PI:
        mode = pi_obj.get_mode(g)
        value = pi_obj.read(g)
    else:
        # Mock: random HIGH/LOW, mode randomly IN/OUT
        mode = random.choice([0, 1])
        value = random.choice([0, 1])
    mode_name = MODES[mode] if mode < len(MODES) else "UNKNOWN"
    name = f"GPIO{g}" if ON_PI or mode < 2 else FUNCTION.get(MODES[mode], ("?",))[g]
    return name, mode_name, value

# --- Main ---
if ON_PI:
    pi = pigpio.pi(sys.argv[1] if len(sys.argv) > 1 else None)
    if not pi.connected:
        sys.exit(1)
    rev = pi.get_hardware_revision()
    if rev < 16:
        GPIOPINS = 26
else:
    pi = None

# --- Print GPIO table ---
print('+-----+------------+------+---+----++----+---+------+-----------+-----+')
print('| BCM |    Name    | Mode | V |  Board   | V | Mode | Name      | BCM |')
print('+-----+------------+------+---+----++----+---+------+-----------+-----+')

for h in range(1, GPIOPINS, 2):
    # odd pin
    hh = HEADER[h-1]
    if isinstance(hh, int):
        state = pin_state(hh, pi)
        print(f'|{hh:4} | {state[0]:<10} | {state[1]:<4} | {state[2]} |{h:3} ', end='|| ')
    else:
        print(f'|     |  {hh:<18}   | {h:2} ', end=' || ')
    # even pin
    hh = HEADER[h]
    if isinstance(hh, int):
        state = pin_state(hh, pi)
        print(f'{h+1:2} | {state[2]:<2}| {state[1]:<5}| {state[0]:<10}|{hh:4} |')
    else:
        print(f'{h+1:2} |             {hh:<9}|     |')

print('+-----+------------+------+---+----++----+---+------+-----------+-----+')
print('| BCM |    Name    | Mode | V |  Board   | V | Mode | Name      | BCM |')
print('+-----+------------+------+---+----++----+---+------+-----------+-----+')
