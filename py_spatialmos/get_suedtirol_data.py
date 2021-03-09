#!/usr/bin/python
# -*- coding: utf-8 -*-
"""With this Python script data can be obtained from the South Tyrol Weather Service."""

import csv
import json
import logging
import os
import datetime
from pathlib import Path
import dateutil
import requests
import pandas as pd
from tqdm import tqdm
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
        return {"date": {"name": "date", "unit": "[UTC]"},
                "name": {"name": "name", "unit": "[str]"},
                "lat": {"name": "lat", "unit": "[°]"},
                "lon": {"name": "lon", "unit": "[°]"},
                "alt": {"name": "alt", "unit": "[m]"},
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
            return {station["properties"]["SCODE"]: station["properties"]
                        for station in data_dict["features"]}
        elif request_type == "sensors":
            return data_dict
        elif request_type == "timeseries":
            return data.json()


class SuedtirolDataConverter:

    def __init__(self) -> None:
        uedtirolData.request_data(request_type="stations")
        # Convert data to spatialMOS CSV format

        station_features = []
        station_properties = [d["properties"] for d in station_features]
        station_data = pd.json_normalize(station_properties)
        station_data = station_data.drop(
            ["NAME_E", "NAME_I", "NAME_L"], axis=1)
        station_data.columns = ["station", "name", "alt", "lon", "lat"]
        station_data["lon"] = round(station_data["lon"], ndigits=2)
        station_data["lat"] = round(station_data["lat"], ndigits=2)
        station_data.to_csv("{}/stations.csv".format(data_path),
                            index=False, quoting=csv.QUOTE_NONNUMERIC)

        # Provide available sensors for the respective station
        stations_sensor_json = "{}/stations_sensor.json.tmp".format(
            data_path)
        with open(stations_sensor_json, mode="w") as f:
            f.write(req_sensor.text)
            f.close()
        with open(stations_sensor_json, "r") as f:
            data_stations_sensor = json.load(f)
        os.remove(stations_sensor_json)

        sensor_data = pd.json_normalize(data_stations_sensor)
        sensor_data_info = sensor_data[["DESC_D", "TYPE", "UNIT"]]
        sensor_data_info = sensor_data_info.drop_duplicates(keep="first")
        sensor_data_info.columns = ["Beschreibung", "Parameter", "Einheit"]
        for index, row in sensor_data_info.iterrows():
            row["Parameter"] = rename_sensor_name(row["Parameter"])
        sensor_data_info.to_csv(
            "{}/Parameter_Info.csv".format(data_path), index=False, quoting=csv.QUOTE_NONNUMERIC)

        station_sensor_dict = {}
        for index, row in sensor_data.iterrows():
            if row["SCODE"] in station_sensor_dict:
                station_sensor_dict[row["SCODE"]].append(row["TYPE"])
            else:
                station_sensor_dict[row["SCODE"]] = [row["TYPE"]]

        # Discard duplicates from sensor list
        result = {}
        for key, value in station_sensor_dict.items():
            value = list(dict.fromkeys(value))
            result[key] = value
        station_sensor_dict = result

        for index, row in station_data.iterrows():
            df = None
            for sensor in station_sensor_dict[str(row["station"])]:
                url_values = "http://daten.buergernetz.bz.it/services/meteo/v1/timeseries?station_code={}&output_format=JSON&" \
                    "sensor_code={}&date_from={begindate}0000&date_to={}0000".format(
                        str(row["station"]), str(sensor), begindate, enddate)
                req_values = requests.get(url_values)

                if req_values.status_code == 200:
                    tmp_data_file = f"{data_path}/data/value.json.tmp"
                    with open(tmp_data_file, mode="w") as f:
                        f.write(req_values.text)
                        f.close()
                    if os.path.exists(tmp_data_file):
                        with open(tmp_data_file, "r") as f:
                            data_stations_value = json.load(f)
                        os.remove(tmp_data_file)

                        new_df = pd.json_normalize(data_stations_value)

                        # check if Data exists
                        if new_df.empty:
                            logging.warning(
                                "The station contains no data and was skipped.")
                            continue

                        new_df.columns = ["obstime",
                                          rename_sensor_name(sensor)]
                        new_df = new_df.set_index("obstime")

                        if df is None:
                            df = new_df
                            df.insert(0, "station", row["station"])
                        else:
                            df = df.join(new_df)
                    else:
                        logging.error(
                            "The template file was not created correctly. URL: %s", url_values)
                else:
                    logging.info(
                        "The values could not be downloaded. URL: %s", url_values)

            if df is None:
                tqdm.write(
                    f"No data for the date range {begindate} to {enddate} are available for station {str(row['station'])}.")
            else:
                tzinfos = {"CET": dateutil.tz.gettz(
                    "Europe/Vienna"), "CEST": dateutil.tz.gettz("Europe/Vienna")}
                start_date_df = dateutil.parser.parse(
                    df.index[-1], tzinfos=tzinfos)
                start_date_df = datetime.strftime(
                    start_date_df, "%Y-%m-%d")

                end_date_df = dateutil.parser.parse(
                    df.index[0], tzinfos=tzinfos)
                end_date_df = datetime.strftime(
                    end_date_df, "%Y-%m-%d")

                df.to_csv("{}/data/{}_{}_{}.csv".format(data_path, start_date_df, end_date_df, str(
                    row["station"])), sep=";", index=True, quoting=csv.QUOTE_MINIMAL)
                logging.info("The data of the station %s for the time range from %s to %s has been saved successfully.",
                             row["station"], start_date_df, end_date_df)


def fetch_suedtirol_data(begindate, enddate):
    '''fetch_suedtirol_data from dati.retecivica.bz.it and store the original data json file. Additionally the converted data is saved in spatialMOS CSV Format.'''

    utcnow_str = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H_%M_%S")
    data_path = Path("./data/get_available_data/suedtirol/data")
    ogd_path = Path("./data/get_available_data/suedtirol/ogd")

    try:
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(ogd_path, exist_ok=True)
    except:
        logging.error("The folders could not be created.")

    stations = SuedtirolData.request_data("stations")
    sensors = SuedtirolData.request_data("sensors")

    i = 0
    for sensor in sensors:
        if not sensor['TYPE'] in SuedtirolData.parameters().keys():
            continue
        url_values = f"http://daten.buergernetz.bz.it/services/meteo/v1/timeseries?station_code={sensor['SCODE']}&output_format=JSON&sensor_code={sensor['TYPE']}&date_from={begindate}0000&date_to={enddate}0000"
        timeseries = SuedtirolData.request_data("timeseries", url_values)
        print(timeseries)
        if i == 5:
            break
        i += 1        



    ogd_filename = ogd_path.joinpath(f"sensors_{utcnow_str}.json")
    try:
        with open(ogd_filename, mode="w") as target:
            SuedtirolDataConverter
    except:
        logging.error(
            "The original data file '%s' could not be written.", ogd_filename)


# Main
if __name__ == "__main__":
    STARTTIME = logger_module.start_logging(
        "py_spatialmos", os.path.basename(__file__))
    PARSER_DICT = spatial_parser.spatial_parser(begindate=True, enddate=True)
    fetch_suedtirol_data(PARSER_DICT["begindate"], PARSER_DICT["enddate"])
    logger_module.end_logging(STARTTIME)
