#!/usr/bin/python
# -*- coding: utf-8 -*-
"""With this Python script data can be obtained from the North Tirolian Avalanche Service."""

import logging
import logging.handlers
import os
import datetime
from pathlib import Path
from typing import TextIO
import requests

from spatial_logging import spatial_logging
from spatial_writer import Writer

spatial_logging.logging_init(Path(f"/log/{__file__}.log"))

class LwdData:
    '''Lwd_Data Class'''

    # Data from the Open Data Platform - Katalog Wetterstationsdaten Tirol
    # https://www.data.gv.at/katalog/dataset/bb43170b-30fb-48aa-893f-51c60d27056f
    # Licence: Creative Commons Namensnennung 4.0 International
    # Land Tirol - data.tirol.gv.at
    # Information about the METADATA
    # https://www.data.gv.at/katalog/api/3/action/package_show?id=bb43170b-30fb-48aa-893f-51c60d27056f

    @staticmethod
    def parameters() -> dict:
        '''parameters and a unit which is encapsulated in the spatialmos format.'''
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

    @classmethod
    def request_data(cls, target: TextIO) -> dict:
        '''request_data loads the data from the API interface'''
        data = requests.get(
            "https://wiski.tirol.gv.at/lawine/produkte/ogd.geojson")
        if data.status_code != 200:
            raise(RuntimeError(
                "The response of the API 'https://wiski.tirol.gv.at' does not match 200"))
        try:
            target.write(data.text)
            logging.info("A original data file '%s' was written.", str(target))
        except:
            raise(
                OSError(f"The API interface data could not be stored into {str(target)}."))
        return data.json()


class LwdSpatialConverter:
    '''LwdSpatialConverter for data conversion into spatialMOS format'''

    def __init__(self, request_data: dict, parameter: dict, target: TextIO) -> None:
        now_current_hour = datetime.datetime.now().replace(
            minute=0, second=0, microsecond=0)
        count_stations = 0
        count_stations_successfull = 0
        writer = Writer(parameter.keys(), target)
        for station in request_data["features"]:
            count_stations += 1
            append_data = station["properties"]
            append_data.update({"station": station["id"],
                                "alt": station["geometry"]["coordinates"][2],
                                "lon": station["geometry"]["coordinates"][0],
                                "lat": station["geometry"]["coordinates"][1],
                                })

            if "date" not in append_data:
                logging.warning(
                    "No date could be found in the data for the station '%s'.", append_data["name"])
                continue

            row = []
            for key in parameter:
                if key == "date":
                    date = datetime.datetime.strptime(
                        append_data["date"], "%Y-%m-%dT%H:%M:%S%z")
                    timedelta = (now_current_hour.timestamp() -
                                 date.timestamp()) / 60
                    if abs(timedelta) >= 15:
                        logging.warning(
                            "The received date '%s' for the station '%s' is too old and will not be saved.", date, append_data["name"])
                        break
                    else:
                        row.append(datetime.datetime.utcnow().replace(
                            minute=0, second=0, microsecond=0))
                        continue

                if key in append_data:
                    row.append(append_data[key])
                else:
                    row.append("")

            if len(row) != 0:
                logging.info("The received data for the date '%s' and the station '%s' are stored.",date, append_data["name"])
                writer.append(row)
                count_stations_successfull += 1

        if count_stations_successfull <= 50:
            logging.error("Only %s from %s stations are transmitted correctly", count_stations_successfull, count_stations)
        else:
            logging.info("%s from %s stations have been successfully saved.", count_stations_successfull, count_stations)


    @classmethod
    def convert(cls, request_data: dict, parameter: dict, target: TextIO):
        '''convert the data and save it in spatialMOS CSV format'''
        cls(request_data, parameter, target)


def fetch_lwd_data():
    """fetch_lwd_data from LWD Tirol and store the original data geojson file. Additionally the converted data is saved in spatialMOS CSV Format."""

    utcnow_str = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H_%M_%S")
    data_path = Path("./data/get_available_data/lwd/data")
    ogd_path = Path("./data/get_available_data/lwd/ogd")

    try:
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(ogd_path, exist_ok=True)
    except:
        raise OSError("The folders could not be created.")

    ogd_filename = ogd_path.joinpath(f"ogd_{utcnow_str}.geojson")
    try:
        with open(ogd_filename, mode="w") as target:
            request_data = LwdData.request_data(target)
    except:
        raise(
            OSError(f"The original data file '{ogd_filename}' could not be written."))


    parameters = LwdData.parameters()
    with open(data_path.joinpath(f"data_lwd_{utcnow_str}.csv"), "w", newline='') as target:
        LwdSpatialConverter.convert(request_data, parameters, target)


# Main
if __name__ == "__main__":
    try:
        STARTTIME = datetime.datetime.now()
        logging.info("The data lwd download has started.")
        fetch_lwd_data()
        DURATION = datetime.datetime.now() - STARTTIME
        logging.info(DURATION)
    except Exception as ex:
        logging.exception(ex)
        raise ex
