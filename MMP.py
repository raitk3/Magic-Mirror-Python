import os
import datetime
import time
import base64
import tkinter as tk
import requests
import locale

import urllib

from tkinter import *

# LOCALE
LOCALE = "et_EE.utf8"

# FONT
FONT = 'Poppins'
BOLD_FONT = 'Poppins Semibold'
# CLOCK
CLOCK_FONT_SIZE = 144
DATE_FONT_SIZE = 40

DEFAULT_FONT_COLOUR = "white"
DEFAULT_BACKGROUND_COLOUR = "black"
DEFAULT_ACCENT_COLOUR = "gray"

# TRANSPORT
BUS_NUMBER_SIZE = 60
BUS_LITTLE_FONT_SIZE = 28

# WEATHER
TEMP_SIZE = 60
FEELS_LIKE_SIZE = 30
WIND_SIZE = 36

# COLOURS
BUS_COLOUR = "#56C1A6"
TROLLEY_COLOUR = "#3466B1"


class BusController:
    def __init__(self, coords, stop_id, stop_name, root=None, rowspan=1, colspan=1):
        self.schedule = []
        self.root = root
        self.last_updated = None
        self.coords = coords
        self.rowspan = rowspan
        self.colspan = colspan
        self.number_frames = []
        self.terminus_frames = []
        self.time_frames = []
        self.stop_id = stop_id
        self.stop_name = stop_name

        self.create_bus_frames()

    def update_schedule(self, timeController, force_update):
        if \
                force_update \
                or len(self.schedule) < 3 \
                or self.schedule[0][2] < timeController.time_in_seconds \
                or self.last_updated == None \
                or timeController.current_time - self.last_updated > 300:
            list_of_buses = []
            response = requests.get(
                f"https://transport.tallinn.ee/siri-stop-departures.php?stopid={self.stop_id}&time=0"
            )
            rows = response.text.split("\n")[2:-1]
            for i, row in enumerate(rows):
                if i < 3:
                    data = row.split(",")
                    bus_trol = data[0]
                    line_number = data[1]
                    eta = int(data[2])
                    terminus = data[4]
                    list_of_buses.append(
                        [line_number, terminus, eta, bus_trol])
                else:
                    break
            self.schedule = list_of_buses

    def update_schedule_risti(self, timeController, force_update, stop_id):
        if \
                force_update \
                or len(self.schedule) == 0 \
                or self.schedule[0][2] < timeController.time_in_seconds \
                or self.last_updated == None \
                or timeController.current_time - self.last_updated > 60:
            # 25470,5700337-1
            # 25469,5700338-1
            schedule = []
            trips = {}
            routes = {}
            list_of_buses = []
            time_atm = timeController.time_in_seconds
            with open("stop_times.txt") as f:
                for line in f.readlines():
                    line_data = line.split(",")
                    if line_data[3] == stop_id:
                        schedule.append([line_data[0], line_data[2]])
            schedule.sort(key=lambda el: el[1])
            with open("trips.txt") as f:
                for trip in f.readlines():
                    trip_data = trip.split(",")
                    if trip_data[2] in [el[0] for el in schedule]:
                        trips[trip_data[2]] = [trip_data[0], trip_data[3]]
            with open("routes.txt") as f:
                for route in f.readlines():
                    route_data = route.split(",")
                    if route_data[0] in [trips[el][0] for el in trips]:
                        routes[route_data[0]] = route_data[2:4]
            # with ZipFile("data.zip", "r") as zf:
            #    zf.printdir()
            actual_schedule = []
            for el in schedule:
                line_time = timeController.time_to_seconds(el[1])
                time_left = (
                    line_time - timeController.time_in_seconds) % (24*60*60)
                trip = trips[el[0]]
                line_number = routes[trips[el[0]][0]][0]
                line_terminus = trips[el[0]][1]
                actual_schedule.append(
                    [line_number, line_terminus, line_time, "white"])
            actual_schedule.sort(key=lambda x: (
                x[2] - timeController.time_in_seconds) % (24*60*60))
            #print(*actual_schedule, sep="\n")
            list_of_buses = actual_schedule[0:3]
            cut_list_of_buses = [el for el in list_of_buses if (el[2] - time_atm) % (24*60*60) < (2 * 60 * 60)]
            #print()
            print(*list_of_buses, sep="\n")
            self.schedule = cut_list_of_buses

    def get_time_remaining_string(self, scheduled_time, current_time):
        time_remaining = ((scheduled_time - current_time) % (24 * 60 * 60))
        hours = time_remaining // 3600
        minutes = (time_remaining // 60) % 60
        if minutes < 1:
            return "Vähem kui 1 minuti pärast"
        if minutes == 0:
            return f"{hours} tunni pärast."
        if hours > 0:
            return f"{hours} tunni ja {minutes} minuti pärast"
        return f"{minutes} minuti pärast"

    def create_bus_frames(self):
        if self.root != None:
            name_frame = tk.Label(self.root,
            text=self.stop_name,
            font=(BOLD_FONT, WIND_SIZE),
            bg=DEFAULT_BACKGROUND_COLOUR,
            fg=DEFAULT_FONT_COLOUR,
            anchor="w")
            name_frame.grid(row=self.coords[0], column=self.coords[1], columnspan=self.colspan, sticky="NESW")
            for i in range(3):
                number_frame = tk.Label(self.root, text=f"Bus{i}", font=(
                    BOLD_FONT, BUS_NUMBER_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_FONT_COLOUR)
                number_frame.grid(
                    row=self.coords[0] + self.rowspan - 1 - 2*i, column=self.coords[1], columnspan=2, rowspan=2, sticky="NEWS")
                self.number_frames.append(number_frame)

                terminus_frame = tk.Label(self.root, text=f"Terminus{i}", font=(
                    FONT, BUS_LITTLE_FONT_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_FONT_COLOUR, anchor="sw")
                terminus_frame.grid(row=self.coords[0] - 1 + self.rowspan - 2*i,
                                    column=self.coords[1]+2, columnspan=self.colspan - 2, sticky="NEWS")
                self.terminus_frames.append(terminus_frame)

                time_frame = tk.Label(self.root, text=f"Time{i}", font=(
                    FONT, BUS_LITTLE_FONT_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_ACCENT_COLOUR, anchor="nw")
                time_frame.grid(row=self.coords[0] + self.rowspan - 2*i,
                                column=self.coords[1]+2, columnspan=self.colspan - 2, sticky="NEWS")
                self.time_frames.append(time_frame)

    def update(self, timeController, force_update=False):
        updated = False
        try:
            if self.stop_name[0:5] == "Risti" and self.stop_id in ["25469", "25470"]:
                self.update_schedule_risti(timeController, force_update, self.stop_id)
            else:
                self.update_schedule(timeController, force_update)
            self.last_updated = timeController.current_time
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
                    elif self.schedule[i][3] == "white":
                        self.number_frames[row].configure(
                            fg=DEFAULT_FONT_COLOUR)

                    self.terminus_frames[row].configure(
                        text=self.schedule[i][1])
                    self.time_frames[row].configure(
                        #text=f"{self.get_time_remaining_string(self.schedule[i][2], timeController.time_in_seconds)} ({timeController.seconds_to_time(self.schedule[i][2])})"
                        text=f"{self.get_time_remaining_string(self.schedule[i][2], timeController.time_in_seconds)}"
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
                self.last_updated = timeController.current_time
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
            temp_frame = tk.Label(self.root, text=f"", font=(
                FONT, TEMP_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_FONT_COLOUR, anchor="se")
            temp_frame.grid(
                row=self.coords[0]+1, column=self.coords[1]+1, columnspan=3, sticky="NEWS")
            self.widgets.append(temp_frame)

            feels_frame = tk.Label(self.root, text=f"", font=(
                FONT, FEELS_LIKE_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_ACCENT_COLOUR, anchor="ne")
            feels_frame.grid(
                row=self.coords[0]+2, column=self.coords[1]+2, columnspan=2, sticky="NEWS")
            self.widgets.append(feels_frame)

            icon_frame = tk.Label(
                self.root, text="", bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_ACCENT_COLOUR, anchor="e")
            icon_frame.grid(row=self.coords[0]+1,
                            column=self.coords[1], sticky="NEWS")
            self.widgets.append(icon_frame)

            wind_direction_frame = tk.Label(
                self.root, text="", bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_ACCENT_COLOUR,
                font=(FONT, WIND_SIZE), anchor="s")
            wind_direction_frame.grid(
                row=self.coords[0], column=self.coords[1]+3, columnspan=1, sticky="NEWS")
            self.widgets.append(wind_direction_frame)

            wind_speed_frame = tk.Label(
                self.root, text="", bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_ACCENT_COLOUR,
                font=(FONT, WIND_SIZE), anchor="se")
            wind_speed_frame.grid(
                row=self.coords[0], column=self.coords[1], columnspan=3, sticky="NEWS")
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

    def time_to_seconds(self, time_given):
        elements = [int(el) for el in time_given.split(":")]
        return elements[0] * 3600 + elements[1] * 60 + elements[2]

    def create_clock_widget(self):
        if self.root != None:
            self.widget = tk.Label(self.root, font=(BOLD_FONT, CLOCK_FONT_SIZE),
                                   bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_FONT_COLOUR, anchor="w")
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
            coords=(0, 0), root=self.root, rowspan=2, colspan=6)
        self.dateController = DateController(
            coords=(1, 0), root=self.root, rowspan=1, colspan=9)
        self.busController_1 = BusController(
            coords=(3, 0), stop_id="25469", stop_name="Risti (-> Haapsalu)", root=self.root, rowspan=6, colspan=8)
        self.busController_2 = BusController(
            coords=(3, 8), stop_id="25470", stop_name="Risti (-> Tallinn)", root=self.root, rowspan=6, colspan=8)
        
        #self.busController_1 = BusController(
        #    coords=(3, 0), stop_id="881", stop_name="Keemia", root=self.root, rowspan=6, colspan=8)
        #self.busController_2 = BusController(
        #    coords=(3, 8), stop_id="888", stop_name="Tehnikaülikool", root=self.root, rowspan=6, colspan=8)
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
            self.busController_1.update(self.timeController, False)
            self.busController_2.update(self.timeController, False)
            self.weatherController.update(self.timeController)
            self.root.update()


if __name__ == '__main__':
    Program().mainloop()
