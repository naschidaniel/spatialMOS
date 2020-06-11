#!/usr/bin/python
# -*- coding: utf-8 -*-
"""With this Python script data can be obtained from the South Tyrol Weather Service."""

import csv
import json
import logging
import os
import time
from datetime import datetime
import dateutil
import requests
import pandas as pd
from tqdm import tqdm
from py_middleware import spatial_parser


# Functions
def rename_sensor_name(parameter):
    """The function is used to set the parameters to a uniform format."""
    sensor_dict = {"LT": "t", "LF": "rf", "WR": "wr", "WG": "wg", "WG.BOE": "wsg",
                   "N": "regen", "LD.RED": "ldred", "GS": "globalstrahlung", "SD": "sonne"}
    if parameter in sensor_dict:
        name = sensor_dict[parameter]
    else:
        name = parameter
    return name


def fetch_suedirol_data(beginndate, enddate):
    """The function is used to load data from the South Tyrolean weather service. The data is stored as a csv file."""

    # Provide folder structure.
    data_path = "/get_available_data/suedtirol"
    if not os.path.exists(f"{data_path}"):
        os.mkdir(f"{data_path}")

    if not os.path.exists(f"{data_path}/data/"):
        os.mkdir(f"{data_path}/data/")

    # Station network of the South Tyrolean weather service
    url_stations = "http://dati.retecivica.bz.it/services/meteo/v1/stations"
    req_stations = requests.get(url_stations)

    # Parameters of the current sensors installed on the measuring station
    url_sensor = "http://dati.retecivica.bz.it/services/meteo/v1/sensors"
    req_sensor = requests.get(url_sensor)

    if req_stations.status_code == 200 and req_sensor.status_code == 200:
        stations_json = "{}/stations.json.tmp".format(data_path)
        with open(stations_json, mode="w") as f:
            f.write(req_stations.text)
            f.close()
        with open(stations_json, "r") as f:
            data_stations = json.load(f)
        os.remove(stations_json)

        # Convert data to spatialMOS CSV format
        station_features = data_stations["features"]
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
        stations_sensor_json = "{}/stations_sensor.json.tmp".format(data_path)
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

        with tqdm(total=station_data.shape[0], desc=f"Data download from API of the weather service Province of Bolzano. | {beginndate} to {enddate} |", leave=False) as pbar:
            for index, row in station_data.iterrows():
                df = None
                for sensor in station_sensor_dict[str(row["station"])]:
                    url_values = "http://daten.buergernetz.bz.it/services/meteo/v1/timeseries?station_code={}&output_format=JSON&" \
                        "sensor_code={}&date_from={}0000&date_to={}0000".format(
                            str(row["station"]), str(sensor), beginndate, enddate)
                    req_values = requests.get(url_values)

                    if req_values.status_code == 200:
                        tmp_data_file = f"{data_path}/data/value.json.tmp"
                        with open(tmp_data_file, mode="w") as f:
                            f.write(req_values.text)
                            f.close()

                        with open(tmp_data_file, "r") as f:
                            data_stations_value = json.load(f)
                        os.remove(tmp_data_file)

                        new_df = pd.json_normalize(data_stations_value)
                        new_df.columns = ["obstime",
                                          rename_sensor_name(sensor)]
                        new_df = new_df.set_index("obstime")

                        if df is None:
                            df = new_df
                            df.insert(0, "station", row["station"])
                        else:
                            df = df.join(new_df)
                    else:
                        logging.info("The values could not be downloaded.")

                if df is None:
                    tqdm.write(
                        f"No data for the date range {beginndate} to {enddate} are available for station {str(row['station'])}.")
                else:
                    tzinfos = {"CET": dateutil.tz.gettz(
                        "Europe/Vienna"), "CEST": dateutil.tz.gettz("Europe/Vienna")}
                    start_date_df = dateutil.parser.parse(
                        df.index[-1], tzinfos=tzinfos)
                    start_date_df = datetime.strftime(
                        start_date_df, "%Y-%m-%d")

                    end_date_df = dateutil.parser.parse(
                        df.index[0], tzinfos=tzinfos)
                    end_date_df = datetime.strftime(end_date_df, "%Y-%m-%d")

                    df.to_csv("{}/data/{}_{}_{}.csv".format(data_path, start_date_df, end_date_df,
                                                            str(row["station"])), sep=";", index=True, quoting=csv.QUOTE_MINIMAL)
                pbar.update(1)
    else:
        logging.error(
            "Error while Downloading Station File from http://dati.retecivica.bz.it")


# Main
if __name__ == "__main__":
    start = time.time()
    parser_dict = spatial_parser.spatial_parser(beginndate=True, enddate=True)
    fetch_suedirol_data(parser_dict["beginndate"], parser_dict["enddate"])
    end = time.time()
    time_diff = (end - start) / 60
    logging.info(
        "The download process took {0:.2f} minutes.".format(time_diff))
