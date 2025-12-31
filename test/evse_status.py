#!/usr/bin/env python
# Cross-platform EVSE PWM reader
# Uses pigpio on Pi, mock reader elsewhere

import time
import random
import sys

# Detect if running on a Raspberry Pi
def is_raspberry_pi():
    try:
        with open("/proc/cpuinfo") as f:
            cpuinfo = f.read()
        return "BCM" in cpuinfo or "Raspberry Pi" in cpuinfo
    except FileNotFoundError:
        return False

ON_PI = is_raspberry_pi()

# EVSE states
EVSE_STATE_UNKNOWN   = 0
EVSE_STATE_INACTIVE  = 1
EVSE_STATE_CONNECTED = 2
EVSE_STATE_CHARGING  = 3
EVSE_STATE_ERROR     = 4
EVSE_MINLEVEL_STATE_CONNECTED = 8

def stateStr(state):
    return {
        EVSE_STATE_UNKNOWN: "Unknown",
        EVSE_STATE_INACTIVE: "Inactive",
        EVSE_STATE_CONNECTED: "Connected",
        EVSE_STATE_CHARGING: "Charging",
        EVSE_STATE_ERROR: "ERROR"
    }.get(state, "Unknown")

# --- Reader class ---
if ON_PI:
    import pigpio
    import RPi.GPIO as g

    class Reader:
        """Reads PWM from GPIO using pigpio"""
        def __init__(self, pi, gpio, weighting=0.0):
            self.pi = pi
            self.gpio = gpio
            self._new = 1.0 - weighting
            self._old = weighting
            self._high_tick = None
            self._period = None
            self._high = None
            self._cb = pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

        def _cbf(self, gpio, level, tick):
            if level == 1:
                if self._high_tick is not None:
                    t = pigpio.tickDiff(self._high_tick, tick)
                    self._period = (self._old * self._period + self._new * t) if self._period else t
                self._high_tick = tick
            elif level == 0:
                if self._high_tick is not None:
                    t = pigpio.tickDiff(self._high_tick, tick)
                    self._high = (self._old * self._high + self._new * t) if self._high else t

        def frequency(self):
            return 1000000.0 / self._period if self._period else 0.0

        def pulse_width(self):
            return self._high if self._high else 0.0

        def duty_cycle(self):
            return 100.0 * self._high / self._period if self._high and self._period else 0.0

        def cancel(self):
            self._cb.cancel()

else:
    # Mock reader for testing off Pi
    class Reader:
        """Generates fake PWM values for testing"""
        def __init__(self, pi=None, gpio=None, weighting=0.0):
            self._dc = 0
            self._inc = True

        def frequency(self):
            return 1000.0

        def pulse_width(self):
            return 500.0

        def duty_cycle(self):
            # simulate changing duty cycle between 0-100%
            if self._inc:
                self._dc += random.randint(0, 5)
                if self._dc >= 100: self._inc = False
            else:
                self._dc -= random.randint(0, 5)
                if self._dc <= 0: self._inc = True
            return self._dc

        def cancel(self):
            pass

# --- Main ---
if __name__ == "__main__":
    PWM_GPIO = 6
    RUN_TIME = 10.0  # seconds
    SAMPLE_TIME = 0.05
    debug = 1

    if ON_PI:
        g.setmode(g.BCM)
        g.setup(PWM_GPIO, g.IN, pull_up_down=g.PUD_UP)
        pi = pigpio.pi()
        reader_inst = Reader(pi, PWM_GPIO)
    else:
        print("Not on Pi: using mock reader")
        pi = None
        reader_inst = Reader()

    start = time.time()
    evse_state = EVSE_STATE_UNKNOWN
    evse_dcf_prev = None

    print(f"Starting EVSE reader, initial state {stateStr(evse_state)}")
    while (time.time() - start) < RUN_TIME:
        time.sleep(SAMPLE_TIME)
        dc = reader_inst.duty_cycle()
        evse_dcf = round(dc / 10)

        if evse_dcf_prev is None:
            evse_dcf_prev = evse_dcf
            continue

        # Very simple state logic for demo (full logic can be added like your original)
        if evse_dcf == evse_dcf_prev:
            if evse_dcf >= EVSE_MINLEVEL_STATE_CONNECTED:
                evse_state = EVSE_STATE_CONNECTED
            else:
                evse_state = EVSE_STATE_INACTIVE
        else:
            evse_state = EVSE_STATE_CHARGING

        evse_dcf_prev = evse_dcf
        if debug:
            print(f"dc={dc:.1f} dcf={evse_dcf} state={stateStr(evse_state)}")

    reader_inst.cancel()
    if ON_PI:
        pi.stop()
    print("Stopped EVSE reader")
