#!/usr/bin/python
# -*- coding: utf-8 -*-
"""With this Python script data can be obtained from the South Tyrol Weather Service."""

import logging
import os
import datetime
from pathlib import Path
import requests
from typing import List, TextIO
import spatial_util
from py_middleware import spatial_parser
from py_middleware import logger_module

from spatial_logging import spatial_logging
from spatial_writer import Writer

spatial_logging.logging_init(Path(f"/log/{__file__}.log"))


class SuedtirolData:
    '''SuedtirolData Class'''

    # Data from the Open Data API Interface from - Wetter Provinz Bozen
    # http://daten.buergernetz.bz.it/de/dataset/misure-meteo-e-idrografiche
    # Licence: Creative Commons CC0 - http://opendefinition.org/okd/
    # Land Suedtirol - https://wetter.provinz.bz.it/
    # Information about the Metadata
    # http://daten.buergernetz.bz.it/de/dataset/misure-meteo-e-idrografiche

    @staticmethod
    def parameters() -> dict:
        '''parameters and a unit which is encapsulated in the spatialmos format.'''
        return {"DATE": {"name": "date", "unit": "[UTC]"},
                "SCODE": {"name": "name", "unit": "[str]"},
                "LAT": {"name": "lat", "unit": "[°]"},
                "LONG": {"name": "lon", "unit": "[°]"},
                "ALT": {"name": "alt", "unit": "[m]"},
                "LT": {"name": "t", "unit": "[°C]"},
                "LF": {"name": "rf", "unit": "[%]"},
                "WG.BOE": {"name": "boe", "unit": "[m/s]"},
                "WG": {"name": "wg", "unit": "[m/s]"},
                "WR": {"name": "wr", "unit": "[°]"},
                "N": {"name": "regen", "unit": "[mm/h]"},
                "GS": {"name": "globalstrahlung", "unit": "[W/m^2]"},
                "SD": {"name": "sonne", "unit": "[s]"}}

    @classmethod
    def request_data(cls, request_type: str, url = "") -> dict:
        '''request_data loads the data from the API interface'''

        if request_type not in ["sensors", "stations", "timeseries"]:
            raise(RuntimeError("The request_type '%s' ist not defined.", request_type))

        if request_type == "stations":
            url = "http://dati.retecivica.bz.it/services/meteo/v1/stations"
        elif request_type == "sensors":
            url = "http://dati.retecivica.bz.it/services/meteo/v1/sensors"

        data = requests.get(url)
        if data.status_code != 200:
            raise(RuntimeError("The response of the API '%s' does not match 200", url))

        try:
            data_dict = data.json()
        except:
            raise(RuntimeError("The loaded Data from the '%s' could not be converted into a json.", url))
       
        if request_type == "stations":
            return {station["properties"]["SCODE"]: station["properties"] for station in data_dict["features"]}
        else:
            return data_dict


class SuedtirolDataConverter:

    def __init__(self, measurements: List[List], target: TextIO) -> None:
        
        parameters = SuedtirolData.parameters()
        writer = Writer(parameters, target)

        # Convert data to spatialMOS CSV format
        for entry in measurements:
            writer.append(entry)

    @ classmethod
    def convert(cls, measurements, target: TextIO):
        '''convert the data and save it in spatialMOS CSV format'''    
        columns = list(SuedtirolData.parameters().keys())
        measurements = spatial_util.convert_measurements(measurements, columns)
        cls(measurements, target)


def fetch_suedtirol_data(begindate, enddate):
    '''fetch_suedtirol_data from dati.retecivica.bz.it and store the original data json file. Additionally the converted data is saved in spatialMOS CSV Format.'''

    utcnow_str = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H_%M_%S")
    data_path = Path("./data/get_available_data/suedtirol/data")

    try:
        os.makedirs(data_path, exist_ok=True)
    except:
        logging.error("The folders could not be created.")


    stations = SuedtirolData.request_data("stations")
    sensors = SuedtirolData.request_data("sensors")

    for sensor in sensors:
        if sensor["SCODE"] not in stations.keys():
            continue
        if "SENSORS" in stations[sensor["SCODE"]].keys():
            stations[sensor["SCODE"]]["SENSORS"].append(sensor['TYPE'])
        else:
            stations[sensor["SCODE"]]["SENSORS"] = [sensor['TYPE']]

    i = 0
    for station in stations.values():
        measurements = {}
        for sensor in station["SENSORS"]:
            if not sensor in SuedtirolData.parameters().keys():
                continue
            url_values = f"http://daten.buergernetz.bz.it/services/meteo/v1/timeseries?station_code={station['SCODE']}&output_format=JSON&sensor_code={sensor}&date_from={begindate}0000&date_to={enddate}0000"
            timeseries = SuedtirolData.request_data("timeseries", url_values)
            for ts in timeseries:
                if not ":00:00" in ts["DATE"]:
                    continue
                measurements[ts["DATE"]] = {
                    "NAME": station["SCODE"],
                    "LAT": station["LAT"],
                    "LONG": station["LONG"],
                    "ALT": station["ALT"],
                    sensor: ts['VALUE']
                } 

        filename = data_path.joinpath(f"station_{station['SCODE']}_{begindate}_{enddate}_{utcnow_str}.csv")
        try:
            with open(filename, mode="w") as target:
                SuedtirolDataConverter.convert(measurements, target)
        except:
            logging.error("The original data file '%s' could not be written.", filename)



# Main
if __name__ == "__main__":
    STARTTIME = logger_module.start_logging(
        "py_spatialmos", os.path.basename(__file__))
    PARSER_DICT = spatial_parser.spatial_parser(begindate=True, enddate=True)
    fetch_suedtirol_data(PARSER_DICT["begindate"], PARSER_DICT["enddate"])
    logger_module.end_logging(STARTTIME)
