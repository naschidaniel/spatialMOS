#!/usr/bin/python
# -*- coding: utf-8 -*-
"""With this Python script data can be obtained from the North Tirolian Avalanche Service."""

import os
import sys
import json
import logging
from datetime import datetime
import requests
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
    except:
        logging.error("The folders could not be created.")

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

    # Convert downloaded files to JSON and save it on local disk
    lwd_data = req_data.text
    now_str = datetime.now().strftime("%Y-%m-%dT%H_%M_%S")
    lwd_ogd_json = f"{data_path}/data/ogd_{now_str}.geojson"
    try:
        with open(lwd_ogd_json, mode="w") as f:
            f.write(lwd_data)
            f.close()
        logging.info("The file %s was written.", lwd_ogd_json)
    except:
        logging.error("The data could not be saved on the hdd.")
        sys.exit(1)

# Main
if __name__ == "__main__":
    STARTTIME = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    fetch_lwd_data()
    logger_module.end_logging(STARTTIME)
