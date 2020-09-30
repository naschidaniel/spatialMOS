#!/usr/bin/python
# -*- coding: utf-8 -*-
"""With this Python script data can be obtained from the North Tirolian Avalanche Service."""

import csv
import logging
import os
import sys
import requests
import pandas as pd
from py_middleware import logger_module


# Functions
def fetch_lwd_data():
    """With this function data from LWD Tirol can be loaded. The data is saved in CSV file format."""
    data_path = "./data/get_available_data/suedtirol"
    if not os.path.exists(f"{data_path}"):
        os.mkdir(f"{data_path}")

    if not os.path.exists(f"{data_path}/data/"):
        os.mkdir(f"{data_path}/data/")

    # Data from the Open Data Platform - Katalog Wetterstationsdaten Tirol
    # https://www.data.gv.at/katalog/dataset/bb43170b-30fb-48aa-893f-51c60d27056f
    # Licence: Creative Commons Namensnennung 4.0 International
    # Land Tirol - data.tirol.gv.at
    # Information about the METADATA
    # https://www.data.gv.at/katalog/api/3/action/package_show?id=bb43170b-30fb-48aa-893f-51c60d27056f

    url_data = "https://wiski.tirol.gv.at/lawine/produkte/ogd.geojson"
    req_data = requests.get(url_data)

    if req_data.status_code != 200:
        logging.error(
            "The response of the API 'https://wiski.tirol.gv.at' does not match 200")
        sys.exit(1)

    # Convert downloaded files to JSON
    lwd_data = req_data.json()

    # Loop over stations
    df_stations = pd.DataFrame(
        columns=["station", "name", "alt", "lon", "lat"])
    for station in lwd_data["features"]:
        df_stations.append({"station": station["id"],
                            "name": station["properties"],
                            "alt": station["geometry"]["coordinates"][2],
                            "lon": station["geometry"]["coordinates"][0],
                            "lat": station["geometry"]["coordinates"][1],
                            },
                           ignore_index=True)

    # Save station information in stations_*.csv
    df_stations.to_csv(f"{data_path}/stations_LWD.csv",
                       index=False, quoting=csv.QUOTE_NONNUMERIC)

    # Information about parameters on a station
    parameters = [("Luftdruck (LD)", "ldstat", "[hPa]"),
                  ("Lufttemperatur (LT)", "t", "[°C]"),
                  ("Taupunkt (TD)", "tp", "[°C]"),
                  ("Luftfeuchtigkeit (RH)", "rf", "[%]"),
                  ("Windgeschwindigkeit (WG_BOE)", "boe", "[m/s]"),
                  ("Windgeschwindigkeit (WG)", "wg", "[m/s]"),
                  ("Windrichtung (WR)", "wr", "[°]"),
                  ("Oberflächentemperatur (OFT)", "oft", "[°C]"),
                  ("Globalstrahlung Oben (GS_O)",
                   "globalstrahlung_oben", "[W/m^2]"),
                  ("Globalstrahlung Unten (GS_U)",
                   "globalstrahlung_unten", "[W/m^2]"),
                  ]
    # Save information about the installed sensors in Parameter_Info_LWD.csv
    df_sensor = pd.DataFrame.from_records(
        parameters, columns=["Beschreibung", "Parameter", "Einheit"])
    df_sensor.to_csv(f"{data_path}/Parameter_Info_LWD.csv",
                     index=False, quoting=csv.QUOTE_NONNUMERIC)
# Main
if __name__ == "__main__":
    STARTTIME = logger_module.start_logging(
        "py_spatialmos", os.path.basename(__file__))
    fetch_lwd_data()
    logger_module.end_logging(STARTTIME)
