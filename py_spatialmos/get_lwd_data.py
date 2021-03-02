#!/usr/bin/python
# -*- coding: utf-8 -*-
"""With this Python script data can be obtained from the North Tirolian Avalanche Service."""

import csv
import logging
import logging.handlers
import os
import sys
import datetime
import json
from pathlib import Path
from typing import TextIO
import requests

# Initialize logging
logging.basicConfig(
    format='%(asctime)s\t%(process)d\t%(levelname)s\t%(message)s',
    level=logging.INFO,
    handlers=[logging.handlers.TimedRotatingFileHandler(filename=Path('/log/get_lwd_data.log'), when='midnight'), logging.StreamHandler()])


class Lwd_Data:

    # Data from the Open Data Platform - Katalog Wetterstationsdaten Tirol
    # https://www.data.gv.at/katalog/dataset/bb43170b-30fb-48aa-893f-51c60d27056f
    # Licence: Creative Commons Namensnennung 4.0 International
    # Land Tirol - data.tirol.gv.at
    # Information about the METADATA
    # https://www.data.gv.at/katalog/api/3/action/package_show?id=bb43170b-30fb-48aa-893f-51c60d27056f

    
    def __init__(self) -> None:
        pass

    @staticmethod
    def parameters():
        # Information about parameters on a station
        parameters = [("date", "date", ""),
                    ("name", "name", ""),
                    ("lat", "lat", "Deg"),
                    ("lon", "lon", "Deg"),
                    ("alt", "alt", "m"),
                    ("LD", "ldstat", "[hPa]"),
                    ("LT", "t", "[°C]"),
                    ("TD", "tp", "[°C]"),
                    ("RH", "rf", "[%]"),
                    ("WG_BOE", "boe", "[m/s]"),
                    ("WG", "wg", "[m/s]"),
                    ("WR", "wr", "[°]"),
                    ("OFT", "oft", "[°C]"),
                    ("GS_O", "globalstrahlung_oben", "[W/m^2]"),
                    ("GS_U", "globalstrahlung_unten", "[W/m^2]")]
        return dict((k, v) for k, v, u in parameters)

    @staticmethod
    def save_data(request_data, target):
        # Save original json files
        target.write(request_data.text)
        logging.info("A original data file '%s' was written.", target)
        
    @classmethod
    def get_data(cls, target):
        url_data = "https://wiski.tirol.gv.at/lawine/produkte/ogd.geojson"
        req_data = requests.get(url_data)
        if req_data.status_code != 200:
            raise(RuntimeError(
                "The response of the API 'https://wiski.tirol.gv.at' does not match 200"))
        cls.save_data(req_data, target)
        return req_data.json()


class Writer:
    def __init__(self, target: TextIO) -> None:
        self.out = csv.writer(target)
        self.out.writerow(["date", "name", "lat", "lon", "alt", "boe", "t", "wr", "ldstat",
                           "globalstrahlung_unten", "rf", "oft", "tp", "globalstrahlung_oben", "wg"])

    def append(self, row):
        self.out.writerow(row)


class Spatial_LWD_Writer:
    def __init__(self, request_data, parameter_dict, target: TextIO) -> None:
        utc_now = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        count_stations = 0
        count_stations_successfull = 0
        writer = Writer(target)
        for station in request_data["features"]:
            count_stations += 1
            append_data = station["properties"]
            append_data.update({"station": station["id"],
                                "alt": station["geometry"]["coordinates"][2],
                                "lon": station["geometry"]["coordinates"][0],
                                "lat": station["geometry"]["coordinates"][1],
                                })

            row = []
            for key in parameter_dict:
                if "date" not in append_data:
                    break

                if key == "date":
                    date = datetime.datetime.strptime(
                        append_data["date"], "%Y-%m-%dT%H:%M:%S%z").timetuple()
                    print(date)
                    date.timestamp()
                    timedelta = (utc_now.timestamp() - 123)
                    print(timedelta)
                    if abs(timedelta) >= 4000:
                        break
                        
                    else:
                        row.append(date.replace(
                            minute=0, second=0, microsecond=0))
                        continue

                if key in append_data:
                    row.append(append_data[key])
                else:
                    row.append("")

            if len(row) != 0:
                writer.append(row)
                count_stations_successfull += 1

        if (count_stations <= 50):
            raise(ValueError(
                f"Only {count_stations_successfull} from {count_stations} stations are transmitted correctly"))

    @classmethod
    def convert(cls, request_data, parameter_dict: dict, target):
        Spatial_LWD_Writer(request_data, parameter_dict, target)
        


# Functions
def fetch_lwd_data():
    """With this function data from LWD Tirol can be loaded. The data is saved in a geojson file."""

    utcnow_str = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H_%M_%S")
    data_path = Path("./data/get_available_data/lwd/data")
    orig_path = Path("./data/get_available_data/lwd/orig")

    try:
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(orig_path, exist_ok=True)
    except:
        logging.error("The folders could not be created.")

    ogd_filename = orig_path.joinpath(f"ogd_{utcnow_str}.geojson")
    # try:
    #     with open(ogd_filename, mode="w") as target:
    #         request_data = Lwd_Data.get_data(target)
    # except:
    #     raise(OSError(f"The original data file '{ogd_filename}' could not be written."))
    with open(orig_path.joinpath(f"ogd_2021-03-02T19_58_29.geojson")) as f:
        request_data = json.loads(f.read())
    
    parameters = Lwd_Data.parameters()
    with open(data_path.joinpath(f"data_lwd_{utcnow_str}.csv"), "w") as target:
        Spatial_LWD_Writer.convert(request_data, parameters, target)


# Main
if __name__ == "__main__":
    try:
        start = datetime.datetime.now()
        logging.info("The data lwd download has started.")
        fetch_lwd_data()
        duration = datetime.datetime.now() - start
        logging.info(duration)
    except Exception as ex:
        logging.exception(ex)
        raise(ex)

