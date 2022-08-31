# SPDX-FileCopyrightText: Copyright (c) 2022 Cedar Grove Maker Studios
#
# SPDX-License-Identifier: MIT
"""
`code.py`
================================================================================

A "jumping-off" code.py for the MatrixWeather project.
code.py  2022-08-30 v1.0  Cedar Grove Studios

* Author(s): JG for Cedar Grove Maker Studios
"""

# imports__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/CedarGroveStudios/MatrixWeather"


# Uncomment the following to test the palettefader module
# import palettefader_simpletest

# Uncomment the following to display the snowman
# import snowman_code

"""Set FAILOVER to True to fail to a dimmed display and flashing NeoPixel;
False to fail normally with error reporting via the REPL."""
FAILOVER = True

while True and FAILOVER:
    """Attempt to start the primary code module. Upon failure, dim the display
    to keep the board cooler and flash the LED for attention."""

    try:
        import matrixweather_code
    except Exception as e:
        import board
        import digitalio
        import time
        from adafruit_matrixportal.matrix import Matrix

        led = digitalio.DigitalInOut(board.LED)
        led.direction = digitalio.Direction.OUTPUT
        led.value = True

        matrix = Matrix(bit_depth=2)  # default is 2; maximum is 6
        matrix.display.brightness = 0  # blank display during startup

        print(f"FAIL: matrixweather_code.py: {e}  time.monotonic: {time.monotonic()}")

        while True:
            """Flash red LED forever."""
            time.sleep(1)
            led.value = not led.value

else:
    import matrixweather_code
