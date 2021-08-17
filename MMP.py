import os
import datetime
import time
import tkinter as tk
import requests
import locale
from tkinter import *

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

# COLOURS
BUS_COLOUR = "lime"
TROLLEY_COLOUR = "blue"

def do_grid():
    for i in range(16):
        for j in range(10):
            tk.Label(root, relief="raised").grid(row=j, column=i, sticky="NEWS")

def get_time():
    current_time = time.time()
    time_as_string = time.strftime("%H:%M:%S")

    # Some hack to get todays time in seconds
    now = datetime.datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seconds = (now - midnight).seconds
    return time.strftime("%H:%M:%S"), time.time(), seconds


def convert_K_to_C(temperature_in_kelvin):
    return temperature_in_kelvin - 273.15


def get_time_remaining_string(scheduled_time, current_time):
    time_remaining = (scheduled_time - current_time) // 60
    if time_remaining < 1:
        return "Vähem kui 1 minuti pärast"
    return f"{time_remaining} minuti pärast"


def get_buses():
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
    return list_of_buses


def get_weather():
    city_name = "Tallinn, EE"
    API_key = "a32682b68c181bcc25cfae1aba449380"
    try:
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_key}"
        ).json()

        temperature = str(round(convert_K_to_C(
            response["main"]["temp"]), 1))+"°C"
        feels_like = str(round(convert_K_to_C(
            response["main"]["feels_like"]), 1))+"°C"
        icon = response["weather"][0]["icon"]
        return temperature, feels_like, icon
    except Exception:
        return "N/A", "N/A", "N/A"


def get_mock_buses():
    return [
        ["3", "Kaubamaja", "8 minuti pärast", "trol"],
        ["11", "Kivisilla", "3 minuti pärast", "bus"],
        ["3", "Kaubamaja", "Vähem kui 1 minuti pärast", "trol"]
    ]


def create_bus_frames():
    number_frames = []
    terminus_frames = []
    time_frames = []

    for i in range(3):
        number_frame = tk.Label(root, text=f"Bus{i}", font=(
            'caviar dreams', BUS_NUMBER_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_FONT_COLOUR)
        number_frame.grid(row=8 - 2*i, column=0, rowspan=2, sticky="NEWS")
        number_frames.append(number_frame)

        terminus_frame = tk.Label(root, text=f"Terminus{i}", font=(
            'caviar dreams', BUS_LITTLE_FONT_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_FONT_COLOUR, anchor="sw")
        terminus_frame.grid(row=8 - 2*i, column=1, columnspan=8, sticky="NEWS")
        terminus_frames.append(terminus_frame)

        time_frame = tk.Label(root, text=f"Time{i}", font=(
            'caviar dreams', BUS_LITTLE_FONT_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_ACCENT_COLOUR, anchor="nw")
        time_frame.grid(row=9 - 2*i, column=1, columnspan=8, sticky="NEWS")
        time_frames.append(time_frame)

    return number_frames, terminus_frames, time_frames


def create_weather_frames():
    weather_frames = []

    temp_frame = tk.Label(root, text=f"Temperature", font=(
        'caviar dreams', TEMP_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_FONT_COLOUR, anchor="se")
    temp_frame.grid(row=0, column=14, rowspan=2, columnspan=3, sticky="NEWS")
    weather_frames.append(temp_frame)

    feels_frame = tk.Label(root, text=f"Temperature", font=(
        'caviar dreams', FEELS_LIKE_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_ACCENT_COLOUR, anchor="ne")
    feels_frame.grid(row=2, column=15, rowspan=1, columnspan=2, sticky="NEWS")
    weather_frames.append(feels_frame)

    return weather_frames


def update_weather(frames):
    weather_data = get_weather()
    for i in range(min(len(frames), len(weather_data))):
        frames[i].configure(text=weather_data[i])


def update_buses(buses, number_frames, terminus_frames, time_frames, force_update):
    _, _, current_time = get_time()
    updated = False

    if force_update or len(buses) < 3 or buses[0][2] < current_time:
        try:
            buses = get_buses()
            updated = True
        except Exception:
            print("Failed to update!")
    #buses = get_mock_buses()
    for i in range(3):
        row = 2-i
        if len(buses) > i:
            number_frames[row].configure(text=buses[-i][0], fg=BUS_COLOUR)
            if buses[i][3] == "trol":
                number_frames[row].configure(fg=TROLLEY_COLOUR)
            terminus_frames[row].configure(text=buses[i][1])
            time_frames[row].configure(
                text=get_time_remaining_string(buses[i][2], current_time))

        else:
            number_frames[row].configure(text="")
            terminus_frames[row].configure(text="")
            time_frames[row].configure(text="")
    return buses, updated


def create_clock_and_date_frames():
    clock_frame = tk.Label(root, font=(
        'caviar dreams', CLOCK_FONT_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_FONT_COLOUR, anchor="nw")
    clock_frame.grid(row=0, column=0, rowspan=2, columnspan=10, sticky="NEWS")
    date_frame = tk.Label(root, font=(
        'caviar dreams', DATE_FONT_SIZE), bg=DEFAULT_BACKGROUND_COLOUR, fg=DEFAULT_FONT_COLOUR, anchor="nw")
    date_frame.grid(row=2, column=0, rowspan=1, columnspan=10, sticky="NEWS")
    return clock_frame, date_frame


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Mirror')

    #locale.setlocale(locale.LC_TIME, "et_ET")

    for i in range(16):
        root.columnconfigure(i, weight=1, uniform="col")
        if i < 10:
            root.rowconfigure(i, weight=1, uniform="row")

    current_time = ""
    do_grid()
    current_bus_schedule = []
    last_updated = 0
    clock_frame, date_frame = create_clock_and_date_frames()
    number_frames, terminus_frames, time_frames = create_bus_frames()
    weather_frames = create_weather_frames()

    while True:
        time_as_string, time_as_time, _ = get_time()
        if current_time != time_as_string:
            current_time = time_as_string
            date = time.strftime("%A, %d. %B %Y")
            clock_frame.configure(text=current_time)
            date_frame.configure(text=date)
            force_update = time_as_time - last_updated > 300
            current_bus_schedule, updated = update_buses(
                current_bus_schedule, number_frames, terminus_frames, time_frames, force_update)
            if updated:
                last_updated = time_as_time
                # Might as well update weather as well...
                update_weather(weather_frames)
        root.attributes("-fullscreen", True)
        root.configure(background=DEFAULT_BACKGROUND_COLOUR)
        root.update()
