# SPDX-FileCopyrightText: Copyright (c) 2022 Cedar Grove Maker Studios
#
# SPDX-License-Identifier: MIT
"""
`matrixweather_failover.py`
================================================================================

Used after a fatal error to dim the display to keep the board cooler and flash
the NeoPixel for attention.

matrixweather_failover.py  2022-08-31 v1.0  Cedar Grove Studios

* Author(s): JG for Cedar Grove Maker Studios
"""

# imports__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/CedarGroveStudios/MatrixWeather"


import board
import neopixel
import time

import board
import digitalio
import time
from adafruit_matrixportal.matrix import Matrix

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True

matrix = Matrix(bit_depth=1)  # default is 2; maximum is 6
matrix.display.brightness = 0  # blank display during startup

while True:
    """Flash red LED forever."""
    time.sleep(1)
    led.value = not led.value
