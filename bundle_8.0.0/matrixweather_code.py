# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
# Revised 2022-08-30 JG for Cedar Grove Maker Studios
#
# SPDX-License-Identifier: MIT
#
# matrixweather_code.py

"""
Matrix Weather for Matrix Portal
This project queries the Open Weather Maps site API to report a location's
current weather conditions using the MatrixPortal's 32x64 LED display.
"""
import time
import board
import supervisor
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix
from simpleio import map_range
import matrixweather_graphics  # pylint: disable=wrong-import-position

print("running matrixweather_code.py")

# Instantiate and blank display
matrix = Matrix(bit_depth=6)  # default is 2; maximum is 6
matrix.display.brightness = 0

# Reduce status neopixel brightness to help keep things cool on error exit
# TODO: reduce Matrix backlight brightness upon exit
supervisor.set_rgb_status_brightness(16)

# Force a restart upon error exit to keep things alive when the eventual
#   internet error happens
# supervisor.set_next_code_file(filename="code.py", reload_on_error=True)


UNITS = "imperial"  # can pick 'imperial' or 'metric' as part of URL query
# Use city, country code in ISO3166 format; e.g. "New York, US" or "London, GB"
LOCATION = "Seattle, WA, US"
# display settings
DISPLAY_BRIGHTNESS = 0.1  # 0.1 minimum; 1.0 maximum
DISPLAY_GAMMA = 1.0  # No adjustment = 1.0; can range from 0.0 to 2.0
SCROLL_DELAY = 0.1
SCROLL_HOLD_TIME = 0  # set this to hold each line before finishing scroll

# Set up network parameters and instantiate
#   Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("Error: WiFi secrets are kept in secrets.py")
    raise
# Set up from where we'll be fetching data
DATA_SOURCE = (
    "http://api.openweathermap.org/data/2.5/weather?q=" + LOCATION + "&units=" + UNITS
)
# You'll need to get a token from openweather.org, looks like 'b6907d289e10d714a6e88b30761fae22'
# it goes in your secrets.py file on a line such as:
# 'openweather_token' : 'your_big_humongous_gigantor_token',
DATA_SOURCE += "&appid=" + secrets["openweather_token"]
DATA_LOCATION = []

# instantiate buttons
button_down = DigitalInOut(board.BUTTON_DOWN)
button_down.switch_to_input(pull=Pull.UP)

button_up = DigitalInOut(board.BUTTON_UP)
button_up.switch_to_input(pull=Pull.UP)

# instantiate potentiometer
potentiometer = AnalogIn(board.A0)

# instantiate network connection
network = Network(status_neopixel=board.NEOPIXEL, debug=True)

# build display graphics and enable the display
gfx = matrixweather_graphics.MatrixWeatherGraphics(
    matrix.display,
    am_pm=True,
    units=UNITS,
    brightness=DISPLAY_BRIGHTNESS,
    gamma=DISPLAY_GAMMA,
)
matrix.display.brightness = 1
print(f"gfx display loaded:   gfx.brightness = {gfx.brightness}")

localtime_refresh = None
weather_refresh = None
scroll_refresh = None

while True:
    # only query the online time once per hour (and on first run)
    if (not localtime_refresh) or (time.monotonic() - localtime_refresh) > 3600:
        try:
            #print("Getting time from internet!")
            localtime_refresh = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue

    # only query the weather every 10 minutes (and on first run)
    if (not weather_refresh) or (time.monotonic() - weather_refresh) > 600:
        try:
            print(f"Getting weather for {LOCATION}")
            value = network.fetch_data(DATA_SOURCE, json_path=(DATA_LOCATION,))
            # print("Response is: ", value)
            gfx.display_weather(value)
            weather_refresh = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue

    # only scroll the description every SCROLL_DELAY seconds (and on first run)
    # also adjust brightness with up-down buttons during scrolling interval
    if (not scroll_refresh) or (time.monotonic() - scroll_refresh) > SCROLL_DELAY:
        gfx.scroll_description()
        scroll_refresh = time.monotonic()

        if not button_up.value:
            gfx.brightness = min(gfx.brightness + 0.01, 1.0)
            print(f"display brightness: {gfx.brightness:0.2f}")
        if not button_down.value:
            gfx.brightness = max(gfx.brightness - 0.01, 0.06)
            print(f"display brightness: {gfx.brightness:0.2f}")

        """gfx.brightness = map_range(potentiometer.value, 0, 54000, 0.04, 1.0)
        #print(potentiometer.value)
        print(f"display brightness: {gfx.brightness:0.2f}")"""
