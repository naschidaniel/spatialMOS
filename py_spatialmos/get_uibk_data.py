#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This program is used to load data from the UIBK API interface."""

import json
import csv
import os
import time
import logging
from datetime import datetime, timedelta
import requests
import pandas as pd
from py_middleware import logger_module


# Functions
def rename_sensor_name(parameter):
    """The function is used to set the parameters to a uniform format."""
    sensor_dict = {"tl": "t", "tp": "tp", "rf": "rf", "ff": "wg",
                   "dd": "wr", "rr": "regen", "p": "ldstat", "so": "sonne"}
    if parameter in sensor_dict:
        name = sensor_dict[parameter]
    else:
        name = parameter
    return name


def fetch_uibk_data():
    """The data is stored as a csv file. Either 3 or 7 days will be returned."""

    # Provide folder structure.
    data_path = "./data/get_available_data/uibk"
    if not os.path.exists(f"{data_path}"):
        os.mkdir(f"{data_path}")

    data_path = os.path.join(data_path, "data")
    if not os.path.exists(f"{data_path}"):
        os.mkdir(f"{data_path}")

    # Loop over stations
    stations = ["innsbruck", "obergurgl", "ellboegen", "sattelberg"]
    for station in stations:
        df, startdate, enddate = download_api_data(data_path, station)
        df.to_csv(f"{data_path}/{startdate}_to_{enddate}_{station}.csv",
                  index=False, quoting=csv.QUOTE_NONNUMERIC)
        logging.info("| UIBK | {:18} | {} | {} ".format(
            station, startdate, enddate))
        time.sleep(5)

    # Information about parameters on a station
    parameters = [("Temperatur", "t", "[°C]"),
                  ("Taupunkt", "tp", "[°C]"),
                  ("Relative Luftfeuchte", "rf", "[%]"),
                  ("Windgeschwindigkeit", "wg", "[m/s]"),
                  ("Windrichtung", "wr", "[°]"),
                  ("Niederschlag", "regen", "[mm/h]"),
                  ("Stationsdruck", "ldstat", "[hPa]"),
                  ("Sonnenscheindauer", "sonne", "[min]"),
                  ]
    df_sensor = pd.DataFrame.from_records(
        parameters, columns=["Beschreibung", "Parameter", "Einheit"])
    df_sensor.to_csv(f"{data_path}/Parameter_Info_UIBK.csv",
                     index=False, quoting=csv.QUOTE_NONNUMERIC)

    # Info über die Stationen in stations.csv
    stations_info = [("11320", "Innsbruck Univ.", 578, 11.3841666666, 47.26),
                     # Winkelminuten lon=112303 lat=471536
                     ("11127", "Obergrugl", 1942, 11.02444, 46.8666666),
                     # Winkelminuten lon=110128 lat=465200
                     ("EllTir", "Ellboegen", 1070, 11.431111, 47.183611),
                     ("SattTir", "Sattelberg", 2115, 11.479167, 47.011111),
                     ]

    df_stations = pd.DataFrame.from_records(
        stations_info, columns=["station", "name", "alt", "lon", "lat"])

    df_stations.to_csv(f"{data_path}/stations_UIBK.csv",
                       index=False, quoting=csv.QUOTE_NONNUMERIC)


def download_api_data(data_path, station):
    """The function is used to load data from the UIBK WEATHER API service for a single station."""

    # Provide available data for the respective station
    url_station = "http://meteo145.uibk.ac.at/{}/3".format(station)
    req_station = requests.get(url_station)

    if req_station.status_code == 200:
        stations_json = f"{data_path}/{station}.json.tmp"
        with open(stations_json, mode="w") as f:
            f.write(req_station.text)
            f.close()
        with open(stations_json, "r") as f:
            data_stations = json.load(f)
        os.remove(stations_json)

        data_stations_pd = pd.DataFrame.from_dict(data_stations)
        obstime = [datetime(1970, 1, 1) + timedelta(milliseconds=ds)
                   for ds in data_stations_pd["datumsec"]]
        data_stations_pd.insert(0, "obstime", obstime)
        data_stations_pd.insert(1, "station", station)
        data_stations_pd = data_stations_pd.drop("datumsec", axis=1)

        labels_data_stations_pd = list(data_stations_pd)
        rename_label = []
        for label in labels_data_stations_pd:
            rename_label.append(rename_sensor_name(label))
        data_stations_pd.columns = rename_label

        beginndate = datetime.strftime(
            data_stations_pd["obstime"][0], "%Y-%m-%dT%H_%M")
        enddate = datetime.strftime(
            data_stations_pd["obstime"][len(data_stations_pd) - 1], "%Y-%m-%dT%H_%M")
        return (data_stations_pd, beginndate, enddate)
    else:
        logging.error(
            "The request for the URL '%s' returned the status code 404", url_station)


# Main
if __name__ == "__main__":
    starttime = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    fetch_uibk_data()
    logger_module.end_logging(starttime)
