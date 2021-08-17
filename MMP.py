import os
import time
import tkinter as tk
import requests
import locale
from tkinter import *



def get_time():
    return time.strftime("%H:%M:%S")


def get_buses():
    list_of_buses = []
    response = requests.get(
        f"https://transport.tallinn.ee/siri-stop-departures.php?stopid=881&time=")
    rows = response.text.split("\n")[2:-1]
    for i, row in enumerate(rows):
        if i < 3:
            data = row.split(",")
            time = int(data[5]) // 60
            string = "Vähem kui 1 minuti pärast"
            if time > 0:
                string = f"{time} minuti pärast"
            list_of_buses.append([data[1], data[4], string, data[0]])
    return list_of_buses[::-1]


def get_weather():
    city_name = "Tallinn, EE"
    API_key = "a32682b68c181bcc25cfae1aba449380"
    response = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_key}").json()

    temperature = str(round(response["main"]["temp"] - 273.15, 1))+"°C"
    feels_like = str(round(response["main"]["feels_like"] - 273.15, 1))+"°C"
    icon = response["weather"][0]["icon"]
    return temperature, feels_like, icon


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
            'caviar dreams', 50), bg='black', fg='white')
        number_frame.grid(row=8 - 2*i, column=0, rowspan=2, sticky="NEWS")
        number_frames.append(number_frame)

        terminus_frame = tk.Label(root, text=f"Terminus{i}", font=(
            'caviar dreams', 25), bg='black', fg='white', anchor="sw")
        terminus_frame.grid(row=8 - 2*i, column=1, columnspan=8, sticky="NEWS")
        terminus_frames.append(terminus_frame)

        time_frame = tk.Label(root, text=f"Time{i}", font=(
            'caviar dreams', 25), bg='black', fg='gray', anchor="nw")
        time_frame.grid(row=9 - 2*i, column=1, columnspan=8, sticky="NEWS")
        time_frames.append(time_frame)

    return number_frames, terminus_frames, time_frames


def create_weather_frames():
    weather_frames = []

    temp_frame = tk.Label(root, text=f"Temperature", font=(
        'caviar dreams', 100), bg='black', fg='white')
    temp_frame.grid(row=0, column=14, rowspan=2, columnspan=3, sticky="NS")
    weather_frames.append(temp_frame)

    feels_frame = tk.Label(root, text=f"Temperature", font=(
        'caviar dreams', 50), bg='black', fg='gray')
    feels_frame.grid(row=2, column=15, rowspan=1, columnspan=2, sticky="NE")
    weather_frames.append(feels_frame)

    return weather_frames


def update_weather(frames):
    weather_data = get_weather()
    for i in range(min(len(frames), len(weather_data))):
        frames[i].configure(text=weather_data[i])


def update_buses(number_frames, terminus_frames, time_frames):
    #buses = get_buses()
    buses = get_mock_buses()
    for i in range(3):
        if len(buses) > i:
            number_frames[i].configure(text=buses[i][0], fg="lime")
            if buses[i][3] == "trol":
                number_frames[i].configure(fg="blue")
            terminus_frames[i].configure(text=buses[i][1])
            time_frames[i].configure(text=buses[i][2])

        else:
            number_frames[i].configure(text="")
            terminus_frames[i].configure(text="")
            time_frames[i].configure(text="")


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Mirror')

    locale.setlocale(locale.LC_TIME, "et_ET")

    for i in range(16):
        root.columnconfigure(i, weight=1, uniform="col")
        if i < 10:
            root.rowconfigure(i, weight=1, uniform="row")

    current_time = ""
    last_updated = 0

    clock_frame = tk.Label(root, font=(
        'caviar dreams', 130), bg='black', fg='white', anchor="nw")
    clock_frame.grid(row=0, column=0, rowspan=2, columnspan=10, sticky="NEWS")
    date_frame = tk.Label(root, font=(
        'caviar dreams', 40), bg='black', fg='white', anchor="nw")
    date_frame.grid(row=2, column=0, rowspan=1, columnspan=10, sticky="NEWS")
    number_frames, terminus_frames, time_frames = create_bus_frames()
    weather_frames = create_weather_frames()

    while True:
        if current_time != (new_time := get_time()):
            current_time = new_time
            date = time.strftime("%A, %d. %B %Y")
            clock_frame.configure(text=current_time)
            date_frame.configure(text=date)
        if (current_time := time.time()) - last_updated > 10:
            last_updated = current_time
            print("update!")
            update_buses(number_frames, terminus_frames, time_frames)
            update_weather(weather_frames)
        root.attributes("-fullscreen", True)
        root.configure(background='black')
        root.update()
