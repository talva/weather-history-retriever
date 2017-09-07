# -*- coding: utf-8 -*-
import csv
import datetime
import json
import sys
import traceback
import urllib.request
from pathlib import Path

import settings


def get_url(day_location):
    day = '{:{dfmt}}'.format(day_location[0], dfmt='%Y-%m-%d')
    location = str(day_location[1][1]) + ',' + str(day_location[1][2])

    return """https://api.darksky.net/forecast/{ACCESS_TOKEN}/{location},{date}T23:59:59?units=si""".format(
        location=location, date=day, ACCESS_TOKEN=settings.DARKSKY_ACCESS_TOKEN)


def str_time(unix_time):
    if unix_time is None:
        return None
    else:
        return datetime.datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')


def readcsv(file_name):
    weather_file = Path(file_name)
    if weather_file.is_file():
        with open(weather_file, newline='') as f:
            return [row for row in csv.DictReader(f)]
    else:
        return []


def writecsv(file_name, header, weather_history):
    with open(file_name, 'w', newline='') as fp:
        writer = csv.DictWriter(fp, delimiter=',', fieldnames=header)
        writer.writeheader()
        writer.writerows(weather_history)


def get_existing_dates_and_locations(weather_history):
    existing_days_and_locations = set()
    for x in weather_history:
        daytime = datetime.datetime.strptime(x["time"], "%Y-%m-%d %H:%M:%S")
        day = daytime.date()
        location = (x["city"], float(x["latitude"]), float(x["longitude"]))
        existing_days_and_locations.add((day, location))
    return existing_days_and_locations


required_fields = [
    "time", "timezone", "latitude", "longitude", "summary", "sunriseTime", "sunsetTime",
    "precipIntensity", "precipIntensityMax", "precipIntensityMaxTime",
    "precipProbability", "precipType",
    "temperatureMin", "temperatureMinTime", "temperatureMax", "temperatureMaxTime",
    "apparentTemperatureMin", "apparentTemperatureMinTime", "apparentTemperatureMax",
    "apparentTemperatureMaxTime"
]


def get_expected_dates_and_locations(days_back, locations):
    end = datetime.datetime.today() - datetime.timedelta(days=1)
    start = end - datetime.timedelta(days=days_back)
    step = datetime.timedelta(days=1)
    expected_days_and_locations = set()
    while end > start:
        for l in locations:
            expected_days_and_locations.add((end.date(), l))
        end -= step
    return expected_days_and_locations


def get_weather_data(dates_and_locations):
    weather_history = []
    for day_location in dates_and_locations:
        url = get_url(day_location)
        print('getting data from {}'.format(url))
        try:
            raw_data = json.loads(urllib.request.urlopen(url).read())
            one_day_data = {key: value for key, value in raw_data["daily"]["data"][0].items() if key in required_fields}
            for required_field in required_fields:
                if required_field not in one_day_data:
                    one_day_data[required_field] = None

            daylight = str((datetime.datetime.fromtimestamp(one_day_data["sunsetTime"])) - (
                datetime.datetime.fromtimestamp(one_day_data["sunriseTime"])))
            one_day_data['daylight'] = daylight
            one_day_data['timezone'] = raw_data["timezone"]
            one_day_data['city'] = day_location[1][0]
            one_day_data['latitude'] = day_location[1][1]
            one_day_data['longitude'] = day_location[1][2]
            one_day_data['time'] = str_time(one_day_data['time'])
            one_day_data['sunriseTime'] = str_time(one_day_data['sunriseTime'])
            one_day_data['sunsetTime'] = str_time(one_day_data['sunsetTime'])
            one_day_data['temperatureMinTime'] = str_time(one_day_data['temperatureMinTime'])
            one_day_data['apparentTemperatureMinTime'] = str_time(one_day_data['apparentTemperatureMinTime'])
            one_day_data['apparentTemperatureMaxTime'] = str_time(one_day_data['apparentTemperatureMaxTime'])
            one_day_data['precipIntensityMaxTime'] = str_time(one_day_data['precipIntensityMaxTime'])
            one_day_data['temperatureMaxTime'] = str_time(one_day_data['temperatureMaxTime'])

            weather_history.append(one_day_data)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("Missing data in " + str(day_location))
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)

    return weather_history


existing_data = readcsv(settings.WEATHER_HISTORY_FILE)
existing_days_and_locations = get_existing_dates_and_locations(existing_data)
expected_days_and_locations = get_expected_dates_and_locations(settings.DAYS_BACK, settings.LOCATIONS)
missing_days_and_locations = expected_days_and_locations - existing_days_and_locations
missing_data = get_weather_data(missing_days_and_locations)
writecsv(settings.WEATHER_HISTORY_FILE, required_fields + ['daylight'] + ['city'], existing_data + missing_data)
