# SPDX-FileCopyrightText: Copyright (c) 2022 Cedar Grove Maker Studios
#
# SPDX-License-Identifier: MIT
"""
`matrixportalr_failover.py`
================================================================================

Used after a fatal error to dim the display to keep the board cooler and flash
the NeoPixel for attention.

matrixportal_failover.py  2022-10-25 v1.1  Cedar Grove Studios

* Author(s): JG for Cedar Grove Maker Studios
"""

# imports__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/CedarGroveStudios/Failover"


import board
import time
import microcontroller
import neopixel
import digitalio
from adafruit_matrixportal.matrix import Matrix

DELAY = 20  # seconds

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True

matrix = Matrix(bit_depth=1)  # default is 2; maximum is 6
matrix.display.brightness = 0  # blank display during startup

print("matrixportal_failover: begin reset delay")
end_delay = time.monotonic() + DELAY
while time.monotonic() < end_delay:
    """Flash red LED during delay period."""
    time.sleep(0.5)
    led.value = not led.value

print("matrixportal_failover: resetting microcontroller")
microcontroller.reset()
