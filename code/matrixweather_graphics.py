# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
# Revised 2022-08-30 JG for Cedar Grove Maker Studios
#
# SPDX-License-Identifier: MIT
#
# matrixweather_graphics.py


import displayio
import terminalio
from adafruit_display_text.label import Label
import adafruit_imageload
from cedargrove_palettefader import PaletteFader

# Color list for labels
LABEL_COLORS_REF = [
    0xFFFF00,  # yellow; temperature
    0x0066FF,  # blue; description
    0x00FFFF,  # cyan; humidity
    0xFF00FF,  # purple; wind
]

cwd = ("/" + __file__).rsplit("/", 1)[0]  # the current working directory

DISPLAY_FONT = terminalio.FONT
ICON_SPRITESHEET = cwd + "/weather-icons.bmp"
ICON_SPRITE_WIDTH = 16
ICON_SPRITE_HEIGHT = 16


class MatrixWeatherGraphics(displayio.Group):
    """Creates the Matrix Weather Station display layout, filling the text
    labels and initializing the weather graphic icon."""

    def __init__(
        self,
        display,
        *,
        am_pm=True,
        units="imperial",
        brightness=1.0,
        gamma=1.0,
    ):
        super().__init__()
        self.am_pm = am_pm
        print(f"Measurement units set to {units}")
        if units == "metric":
            self.celsius = True
            self.meters_speed = True
        else:
            self.celsius = False
            self.meters_speed = False

        # A list of named compass directions for use with wind speed
        self._compass = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

        # Define initial display parameters
        self.display = display
        display.rotation = 270
        self._disp_brightness = brightness
        self._disp_gamma = gamma
        self._disp_center = (display.width // 2, display.height // 2)

        self.label_colors = PaletteFader(
            LABEL_COLORS_REF, self._disp_brightness, gamma=1.0,
            normalize=False
        )

        # Load an image and create a modifible palette for brightness control
        splash, splash_palette_ref = adafruit_imageload.load(
            "background_sun_clouds.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette
        )
        # Adjust palette colors in proportion to brightness setting
        splash_normal = PaletteFader(
            splash_palette_ref, self._disp_brightness, gamma=0.65, normalize=True
        )
        splash_sprite = displayio.TileGrid(splash, pixel_shader=splash_normal.palette)

        splash_group = displayio.Group()
        splash_group.append(splash_sprite)
        display.show(splash_group)

        self.primary_group = displayio.Group()
        self.primary_group.append(self)
        self._icon_group = displayio.Group()
        self.append(self._icon_group)
        self._fg_group = displayio.Group()
        self.append(self._fg_group)

        # Load the icon sprite sheet and create a reference palette for brightness control
        icons, self.icons_ref_palette = adafruit_imageload.load(
            ICON_SPRITESHEET, bitmap=displayio.Bitmap, palette=displayio.Palette
        )
        self.icons_ref_palette.make_transparent(0)

        # Instantiate icon palette normalizer object and adjust
        self.icon_normal = PaletteFader(
            self.icons_ref_palette, self._disp_brightness, gamma=1.0, normalize=True
        )
        self._icon_sprite = displayio.TileGrid(
            icons,
            pixel_shader=self.icon_normal.palette,
            tile_width=ICON_SPRITE_WIDTH,
            tile_height=ICON_SPRITE_HEIGHT,
        )

        # Place a blank icon on-screen
        self._icon_sprite.x = self._disp_center[0] - 8
        self._icon_sprite.y = 12
        self.set_icon(None)

        # Define the text labels. Add an attribute for the reference color to each.
        self.temperature_text = Label(DISPLAY_FONT)
        self.temperature_text.anchor_point = (0.5, 0.5)
        self.temperature_text.anchored_position = (self._disp_center[0], 4)
        self.temperature_text.color = self.label_colors.palette[0]
        self._fg_group.append(self.temperature_text)

        self.description_text = Label(DISPLAY_FONT)
        self.description_text.anchor_point = (0.5, 0.5)
        self.description_text.anchored_position = (self.display.width, 55)
        self.description_text.color = self.label_colors.palette[1]
        self._fg_group.append(self.description_text)

        self.humidity_text = Label(DISPLAY_FONT)
        self.humidity_text.anchor_point = (0.5, 0.5)
        self.humidity_text.anchored_position = (self._disp_center[0], 45)
        self.humidity_text.color = self.label_colors.palette[2]
        self._fg_group.append(self.humidity_text)

        self.wind_text = Label(DISPLAY_FONT)
        self.wind_text.anchor_point = (0.5, 0.5)
        self.wind_text.anchored_position = (self._disp_center[0], 34)
        self.wind_text.color = self.label_colors.palette[3]
        self._fg_group.append(self.wind_text)

        # Adjust relative brightness of all display objects
        self.brightness = self._disp_brightness

    def scroll_description(self):
        """Starting at the right-most position on the display, scroll the
        description text one pixel position to the left. Wrap the text after it
        fully disappears. Non-blocking method."""
        self._text_width = self.description_text.bounding_box[2]
        self.description_text.x = self.description_text.x - 1
        if self.description_text.x < 0 - self._text_width:
            self.description_text.x = self.display.width

    def display_weather(self, weather):
        """Parse the weather information from the JSON data. Checks for the
        existence of each data element.

        :param dict weather: The retrieved weather JSON dictionary.
        """
        try:
            # Get the code for the weather icon
            self.set_icon(weather["weather"][0]["icon"])
        except:
            pass

        try:
            # Get the temperature and apply a measurement unit code
            temperature = weather["main"]["temp"]
            print(f"Temperature: {temperature:.0f}°")
            if self.celsius:
                self.temperature_text.text = f"{temperature:.1f}° C"
            else:
                self.temperature_text.text = f"{temperature:.0f}° F"
        except:
            self.temperature_text.text = "--"

        try:
            # Get the long weather description; "Overcast clouds"
            description = weather["weather"][0]["description"]
            description = description[0].upper() + description[1:]
            print(f"Description: {description}")
            self.description_text.text = description
        except:
            self.description_text.text = "--"

        try:
            # Get the relative humidity
            humidity = weather["main"]["humidity"]
            print(f"Humidity: {humidity:.0f}% RH")
            self.humidity_text.text = f"{humidity:.0f}%"
        except:
            self.humidity_text.text = "--"

        try:
            # Get the wind direction and determine compass text
            wind_direction = weather["wind"]["deg"]
            wind_dir = self._compass[int(((wind_direction + 22.5) % 360) / 45)]
        except:
            wind_dir = "--"

        try:
            # Get the wind speed and merge with direction compass text
            wind = weather["wind"]["speed"]
            if wind_dir != "--":
                self.wind_text.text = f"{wind_dir} {wind:.0f}"
                if self.meters_speed:
                    print(f"Wind: {wind} m/s, {wind_direction}° ({wind_dir})")
                else:
                    print(f"Wind: {wind} MPH, {wind_direction}° ({wind_dir})")
            else:
                print("No wind")
                self.wind_text.text = "--"
        except:
            self.wind_text.text = "--"

        self.display.show(self.primary_group)

    def set_icon(self, icon_name):
        """Use icon_name to get the position of the sprite and update
        the current icon. Format is always 2 numbers followed by 'd' or 'n' as
        the 3rd character.

        :param str icon_name: The icon name returned by openweathermap
        """

        icon_map = ("01", "02", "03", "04", "09", "10", "11", "13", "50")

        print("Set icon to", icon_name)
        if self._icon_group:
            self._icon_group.pop()
        if icon_name is not None:
            row = None
            for index, icon in enumerate(icon_map):
                if icon == icon_name[0:2]:
                    row = index
                    break
            column = 0
            if icon_name[2] == "n":
                column = 1
            if row is not None:
                self._icon_sprite[0] = (row * 2) + column
                self._icon_group.append(self._icon_sprite)

    @property
    def brightness(self):
        return self._disp_brightness

    @brightness.setter
    def brightness(self, new_brightness=1.0):
        """Adjust brightness of all display objects; text colors and weather icon.

        :param float new_brightness: The new brightness value.
        """
        if self._disp_brightness != new_brightness:
            self._disp_brightness = new_brightness

            # Adjust brightness of colors in displayio text group
            self.label_colors.brightness = self._disp_brightness
            for i in range(len(self._fg_group)):
                self._fg_group[i]._palette[1] = self.label_colors.palette[i]

            # Adjust the icon palette brightness and refresh it
            self.icon_normal.brightness = self._disp_brightness
            self._icon_sprite.pixel_shader = self.icon_normal.palette
