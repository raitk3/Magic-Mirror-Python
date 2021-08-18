import os
import datetime
import time
import base64
import tkinter as tk
import requests
import locale
from tkinter import *

# LOCALE
LOCALE = "et_EE.utf8"

# FONT
FONT = 'Poppins'
BOLD_FONT = 'Poppins Bold'
# CLOCK
CLOCK_FONT_SIZE = 72
DATE_FONT_SIZE = 25

DEFAULT_FONT_COLOUR = "white"
DEFAULT_BACKGROUND_COLOUR = "black"
DEFAULT_ACCENT_COLOUR = "gray"

# TRANSPORT
BUS_NUMBER_SIZE = 30
BUS_LITTLE_FONT_SIZE = 15

# WEATHER
TEMP_SIZE = 30
FEELS_LIKE_SIZE = 15
WIND_SIZE = 18

# COLOURS
BUS_COLOUR = "#56C1A6"
TROLLEY_COLOUR = "#3466B1"


class BusController:
    def __init__(self, coords, root=None, rowspan=1, colspan=1):
        self.schedule = []
        self.root = root
        self.last_updated = None
        self.coords = coords
        self.rowspan = rowspan
        self.colspan = colspan
        self.number_frames = []
        self.terminus_frames = []
        self.time_frames = []

        self.create_bus_frames()

    def update_schedule(self):
        list_of_buses = []
        response = requests.get(
            f"https://transport.tallinn.ee/siri-stop-departures.php?stopid=881&time=0"
        )
        rows = response.text.split("\n")[2:-1]
        for i, row in enumerate(rows):
            if i < 3:
                data = row.split(",")
                bus_trol = data[0]
                line_number = data[1]
                eta = int(data[2])
                terminus = data[4]
                list_of_buses.append([line_number, terminus, eta, bus_trol])
            else:
                break
        self.schedule = list_of_buses

    def get_time_remaining_string(self, scheduled_time, current_time):
        time_remaining = (scheduled_time - current_time) // 60
        if time_remaining < 1:
            return "Vähem kui 1 minuti pärast"
        return f"{time_remaining} minuti pärast"

    def create_bus_frames(self):
        if self.root != None:
            for i in range(3):
                number_frame = tk.Label(self.root, text=f"Bus{i}", font=(
                    BOLD_FONT, BUS_NUMBER_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_FONT_COLOUR)
                number_frame.grid(
                    row=self.coords[0] + self.rowspan - 1 - 2*i, column=self.coords[1], rowspan=2, sticky="NEWS")
                self.number_frames.append(number_frame)

                terminus_frame = tk.Label(self.root, text=f"Terminus{i}", font=(
                    FONT, BUS_LITTLE_FONT_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_FONT_COLOUR, anchor="sw")
                terminus_frame.grid(row=self.coords[0] + self.rowspan - 1 - 2*i,
                                    column=self.coords[1]+1, columnspan=self.colspan - 1, sticky="NEWS")
                self.terminus_frames.append(terminus_frame)

                time_frame = tk.Label(self.root, text=f"Time{i}", font=(
                    FONT, BUS_LITTLE_FONT_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_ACCENT_COLOUR, anchor="nw")
                time_frame.grid(row=self.coords[0] + self.rowspan - 2*i,
                                column=self.coords[1]+1, columnspan=self.colspan - 1, sticky="NEWS")
                self.time_frames.append(time_frame)

    def update(self, timeController, force_update=False):
        updated = False
        if force_update or len(self.schedule) < 3 or self.last_updated == None or self.schedule[0][2] < timeController.current_time or timeController - self.last_updated > 300:
            self.last_updated = timeController.current_time
            try:
                self.update_schedule()
                updated = True
            except Exception:
                print("Failed to update!")
        if self.root != None:
            for i in range(3):
                row = 2-i
                if len(self.schedule) > i:
                    self.number_frames[row].configure(
                        text=self.schedule[i][0], fg=BUS_COLOUR)
                    if self.schedule[i][3] == "trol":
                        self.number_frames[row].configure(fg=TROLLEY_COLOUR)
                    self.terminus_frames[row].configure(
                        text=self.schedule[i][1])
                    self.time_frames[row].configure(
                        text=f"{self.get_time_remaining_string(self.schedule[i][2], timeController.time_in_seconds)} ({timeController.seconds_to_time(self.schedule[i][2])})"
                    )

                else:
                    self.number_frames[row].configure(text="")
                    self.terminus_frames[row].configure(text="")
                    self.time_frames[row].configure(text="")


class WeatherController:
    def __init__(self, coords, root=None):
        self.coords = coords
        self.root = root
        self.data = []
        self.widgets = []
        self.last_updated = None
        self.create_widgets()

    def update_data(self, timeController):
        city_name = "Tallinn, EE"
        API_key = "a32682b68c181bcc25cfae1aba449380"
        try:
            if self.last_updated == None or timeController.current_time - self.last_updated > 300:
                response = requests.get(
                    f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_key}"
                ).json()
                temperature = str(round(self.convert_K_to_C(
                    response["main"]["temp"]), 1))+"°C"
                feels_like = str(round(self.convert_K_to_C(
                    response["main"]["feels_like"]), 1))+"°C"
                weather_icon = response["weather"][0]["icon"]
                weather_icon = base64.encodebytes(requests.get(
                    f"http://openweathermap.org/img/wn/{weather_icon}.png", stream=True).raw.read())
                wind_direction = response["wind"]["deg"]
                wind_speed = response["wind"]["speed"]
                last_updated = timeController.current_time
                self.data = [temperature,
                             feels_like,
                             tk.PhotoImage(data=weather_icon),
                             wind_direction,
                             wind_speed]
        except Exception:
            print("Failed to update weather!")

    def convert_angle_to_dir(self, angle):
        sectors = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        angle_of_attack = (angle + 22.5) % 360
        return sectors[int(angle_of_attack // 45)]

    def convert_K_to_C(self, temperature_in_kelvin):
        return temperature_in_kelvin - 273.15

    def create_widgets(self):
        if self.root != None:
            temp_frame = tk.Label(self.root, text=f"Temperature", font=(
                FONT, TEMP_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_FONT_COLOUR, anchor="se")
            temp_frame.grid(
                row=self.coords[0]+1, column=self.coords[1]+1, columnspan=3, sticky="NEWS")
            self.widgets.append(temp_frame)

            feels_frame = tk.Label(self.root, text=f"Temperature", font=(
                FONT, FEELS_LIKE_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_ACCENT_COLOUR, anchor="ne")
            feels_frame.grid(
                row=self.coords[0]+2, column=self.coords[1]+2, columnspan=2, sticky="NEWS")
            self.widgets.append(feels_frame)

            icon_frame = tk.Label(
                self.root, text="Icon", bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_ACCENT_COLOUR, anchor="e")
            icon_frame.grid(row=self.coords[0]+1,
                            column=self.coords[1], sticky="NEWS")
            self.widgets.append(icon_frame)

            wind_direction_frame = tk.Label(
                self.root, text="Wind", bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_ACCENT_COLOUR,
                font=(FONT, WIND_SIZE), anchor="e")
            wind_direction_frame.grid(
                row=self.coords[0], column=self.coords[1]+2, columnspan=2, sticky="NEWS")
            self.widgets.append(wind_direction_frame)

            wind_speed_frame = tk.Label(
                self.root, text="Wind", bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_ACCENT_COLOUR,
                font=(FONT, WIND_SIZE), anchor="e")
            wind_speed_frame.grid(
                row=self.coords[0], column=self.coords[1]+1, columnspan=2, sticky="NEWS")
            self.widgets.append(wind_speed_frame)

    def update(self, timeController):
        self.update_data(timeController)
        if len(self.widgets) > 0:
            for i in range(min(len(self.widgets), len(self.data))):
                if i == 2:
                    if self.data[i] != "N/A":
                        self.widgets[i].configure(image=self.data[i])
                elif i == 3:
                    self.widgets[i].configure(
                        text=self.convert_angle_to_dir(self.data[i]))
                elif i == 4:
                    self.widgets[i].configure(
                        text=f"{round(self.data[i], 1)}m/s")
                else:
                    self.widgets[i].configure(text=self.data[i])


class TimeController:
    def __init__(self, coords, root=None, rowspan=1, colspan=1):
        self.coords = coords
        self.rowspan = rowspan
        self.colspan = colspan
        self.root = root
        self.current_time = None
        self.time_as_string = None
        self.time_in_seconds = None
        self.widget = None
        self.create_clock_widget()
        self.update()

    def update(self):
        self.current_time = time.time()
        self.time_as_string = time.strftime("%H:%M")

        now = datetime.datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        self.time_in_seconds = (now - midnight).seconds
        if self.widget != None:
            self.widget.configure(text=self.time_as_string)

    def seconds_to_time(self, seconds):
        hours = seconds // 3600
        minutes = int((seconds / 60) % 60)
        return f"{hours}:{minutes:0>2}"

    def create_clock_widget(self):
        if self.root != None:
            self.widget = tk.Label(self.root, font=(BOLD_FONT, CLOCK_FONT_SIZE),
                                   bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_FONT_COLOUR, anchor="nw")
            self.widget.grid(row=self.coords[0], column=self.coords[1],
                             rowspan=self.rowspan, columnspan=self.colspan, sticky="NEWS")


class DateController:
    def __init__(self, coords, root=None, rowspan=1, colspan=1):
        self.coords = coords
        self.rowspan = rowspan
        self.colspan = colspan
        self.root = root
        self.date = None
        self.widget = None
        self.create_date_frame()
        self.update()

    def update(self):
        self.date = time.strftime("%A, %d. %B %Y")
        if self.widget != None:
            self.widget.configure(text=self.date)

    def create_date_frame(self):
        if self.root != None:
            self.widget = tk.Label(self.root, font=(FONT, DATE_FONT_SIZE),
                                   bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_FONT_COLOUR, anchor="nw")
            self.widget.grid(row=self.coords[0]+1, column=self.coords[1],
                             rowspan=self.rowspan, columnspan=self.colspan, sticky="NEWS")


class Program:
    def __init__(self):
        locale.setlocale(locale.LC_TIME, LOCALE)

        self.root = tk.Tk()
        self.root.title('Mirror')
        self.root.attributes("-fullscreen", True)
        self.root.configure(background=DEFAULT_BACKGROUND_COLOUR)
        for i in range(16):
            self.root.columnconfigure(i, weight=1, uniform="col")
            if i < 10:
                self.root.rowconfigure(i, weight=1, uniform="row")

        # self.do_grid()

        self.timeController = TimeController(
            coords=(0, 0), root=self.root, rowspan=2, colspan=10)
        self.dateController = DateController(
            coords=(1, 0), root=self.root, rowspan=1, colspan=10)
        self.busController = BusController(
            coords=(5, 0), root=self.root, rowspan=6, colspan=8)
        self.weatherController = WeatherController(
            coords=(0, 12), root=self.root)

    def do_grid(self):
        for i in range(16):
            for j in range(10):
                tk.Label(self.root, relief="raised").grid(
                    row=j, column=i, sticky="NEWS")

    def mainloop(self):
        while True:
            self.timeController.update()
            self.dateController.update()
            self.busController.update(self.timeController, False)
            self.weatherController.update(self.timeController)
            self.root.update()


if __name__ == '__main__':
    Program().mainloop()
