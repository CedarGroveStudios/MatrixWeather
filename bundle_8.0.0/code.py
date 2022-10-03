# SPDX-FileCopyrightText: Copyright (c) 2022 Cedar Grove Maker Studios
#
# SPDX-License-Identifier: MIT
"""
`code.py`
================================================================================

A "jumping-off" code.py for the MatrixWeather project.
code.py  2022-08-31 v1.0  Cedar Grove Studios

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
    """Attempt to start the primary code module. Upon failure, execute the
    failover module."""

    try:
        import matrixweather_code
    except Exception as e:
        import time
        print(f"matrixweather failover: --{e}--  at time.monotonic: {time.monotonic()}")
        import matrixportal_failover
else:
    import matrixweather_code
