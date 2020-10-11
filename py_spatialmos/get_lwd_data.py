#!/usr/bin/python
# -*- coding: utf-8 -*-
"""With this Python script data can be obtained from the North Tirolian Avalanche Service."""

import csv
import logging
import os
import sys
from datetime import datetime
import requests
import pandas as pd
from py_middleware import logger_module


# Functions
def fetch_lwd_data():
    """With this function data from LWD Tirol can be loaded. The data is saved in a geojson file."""
    data_path = "./data/get_available_data/lwd"
    try:
        if not os.path.exists(f"{data_path}"):
            os.mkdir(f"{data_path}")

        if not os.path.exists(f"{data_path}/data/"):
            os.mkdir(f"{data_path}/data/")

        if not os.path.exists(f"{data_path}/orig/"):
            os.mkdir(f"{data_path}/orig/")
    except:
        logging.error("The folders could not be created.")

    # String for Filenames
    utcnow_str = datetime.utcnow().strftime("%Y-%m-%dT%H_%M_%S_+0000")
    
    # Information about parameters on a station
    parameters = [("LD", "ldstat", "[hPa]"),
                  ("LT", "t", "[°C]"),
                  ("TD", "tp", "[°C]"),
                  ("RH", "rf", "[%]"),
                  ("WG_BOE", "boe", "[m/s]"),
                  ("WG", "wg", "[m/s]"),
                  ("WR", "wr", "[°]"),
                  ("OFT", "oft", "[°C]"),
                  ("GS_O",
                   "globalstrahlung_oben", "[W/m^2]"),
                  ("GS_U",
                   "globalstrahlung_unten", "[W/m^2]"),
                  ]
    # Create a dict from parameters     
    parameter_dict = dict((k, v) for k, v, u in parameters)

    # Data from the Open Data Platform - Katalog Wetterstationsdaten Tirol
    # https://www.data.gv.at/katalog/dataset/bb43170b-30fb-48aa-893f-51c60d27056f
    # Licence: Creative Commons Namensnennung 4.0 International
    # Land Tirol - data.tirol.gv.at
    # Information about the METADATA
    # https://www.data.gv.at/katalog/api/3/action/package_show?id=bb43170b-30fb-48aa-893f-51c60d27056f

    url_data = "https://wiski.tirol.gv.at/lawine/produkte/ogd.geojson"
    req_data = requests.get(url_data)

    if req_data.status_code != 200:
        logging.error("The response of the API 'https://wiski.tirol.gv.at' does not match 200")
        sys.exit(1)

    # Save original json files
    ogd_filename = f"{data_path}/orig/ogd_{utcnow_str}.geojson"

    try:
        with open(ogd_filename, mode="w") as f:
            f.write(req_data.text)
            f.close()
            logging.info("A original data file '%s' was written.", ogd_filename)
    except:
        logging.error("The original data file '%s' could not be written.", ogd_filename)
        sys.exit(1)

    # Convert downloaded files to JSON
    lwd_data = req_data.json()

    # Loop over stations
    df_data = pd.DataFrame()
    for station in lwd_data["features"]:
        append_data = station["properties"]
        append_data.update({"station": station["id"],
                            "alt": station["geometry"]["coordinates"][2],
                            "lon": station["geometry"]["coordinates"][0],
                            "lat": station["geometry"]["coordinates"][1],
                            })
        df_data = df_data.append(append_data, ignore_index=True)

    keep = set(df_data.columns) - (set(df_data.columns) - set(parameter_dict.keys()))
    new_order = ["date", "name", "lat", "lon", "alt"]
    new_order.extend(list(keep))
    df_data["date"] = pd.to_datetime(df_data["date"], utc=True)
    df_data = df_data[new_order]
    df_data = df_data.rename(columns = parameter_dict)

    csv_filename = f"{data_path}/data/data_lwd_{utcnow_str}.csv"
    try:
        df_data.to_csv(csv_filename, index=False, quoting=csv.QUOTE_NONNUMERIC)
        logging.info("The datafile file '%s' was written.", csv_filename)
    except:
        logging.error("The datafile file '%s' could not be written.", csv_filename)
        sys.exit(1)


# Main
if __name__ == "__main__":
    STARTTIME = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    fetch_lwd_data()
    logger_module.end_logging(STARTTIME)
