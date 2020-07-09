#!/usr/bin/python
# -*- coding: utf-8 -*-
"""With this Python script the existing data is combined and saved as csv file."""

import csv
import logging
import os
import datetime
import logging
import dateutil
import numpy as np
import pandas as pd
import pytz
import swifter
from py_middleware import logger_module


# Functions
def plausibility_check(df, parameter, lowerlimit, upperlimit):
    """A function for checking the plausibility (values in range) of meteorological data."""
    if any(df[parameter]) >= upperlimit:
        df.loc[(df[parameter] >= upperlimit), parameter] = -999

    if any(df[parameter]) <= lowerlimit:
        df.loc[(df[parameter] <= upperlimit), parameter] = -999

    return df

def combine_dataframes(data_path, columns):
    """A function to combine the data frames of North and South Tyrol."""
    data_files = []
    for filename in os.listdir(data_path):
        path = os.path.join(data_path, filename)
        if os.path.isdir(path):
            continue
        else:
            data_files.append(path)
    data_files = sorted(data_files, reverse=False)

    df = None
    i = 1
    for file in data_files:
        logging.info("CSV File {:2d} of {} is processed | File: {}".format(i, len(data_files), file))
        new_df = pd.read_csv(file, sep=";", quoting=csv.QUOTE_MINIMAL)
        new_df_columsn = new_df.columns
        for key in columns:
            if key in new_df_columsn:
                continue
            else:
                new_df[key] = np.NAN

        new_df = new_df[columns]

        if df is None:
            df = new_df
        else:
            df = pd.concat([df, new_df], axis=0, ignore_index=True)
        i += 1

    df = df.drop_duplicates(subset=None, keep="first", inplace=False)
    return df


def two_element_dict_from_pd_series(data_key, data_value):
    """A function to generate a directory from a Pandas Dataframe."""
    data_key = data_key.to_list()
    data_value = data_value.to_list()
    return dict(zip(data_key, data_value))


def spatialmos_dataframe():
    """A function to generate a dataframe of station observations and station predictions for further statistical processing."""
    stations_wetter_at = pd.read_csv("./data/get_available_data/wetter_at/stations.csv", delimiter=",", header=0)
    stations_wetter_at = stations_wetter_at.drop(["lon_winkelmin", "lat_winkelmin"], axis=1)
    stations_suedtirol = pd.read_csv("./data/get_available_data/suedtirol/stations.csv", delimiter=",", header=0)
    stations = pd.concat([stations_wetter_at, stations_suedtirol], axis=0)
    stations.to_csv("./data/spatialmos_climatology/stations.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)
    parameter_wetter_at = pd.read_csv("./data/get_available_data/wetter_at/Parameter_Info.csv", delimiter=",", header=0)
    parameter_suedtirol = pd.read_csv("./data/get_available_data/suedtirol/Parameter_Info.csv", delimiter=",", header=0)

    # Columns of Pandas Dataframe from all Stations
    columns_wetter_at = parameter_wetter_at["Parameter"].tolist()
    columns_suedtirol = parameter_suedtirol["Parameter"].tolist()
    columns = list(set(["obstime", "station"] + columns_wetter_at + columns_suedtirol))

    # stations from wetter_at
    data_path_wetter_at = str("./data/get_available_data/wetter_at/data")
    df_wetter_at = combine_dataframes(data_path_wetter_at, columns)

    # stations from suedtirol
    data_path_suedtirol = str("./data/get_available_data/suedtirol/data")
    df_suedtirol = combine_dataframes(data_path_suedtirol, columns)

    # Creating Timeinformations from the RAW Data
    local_tz = pytz.timezone("Europe/Vienna")
    df_wetter_at["timestamp"] = df_wetter_at["obstime"].swifter.apply(
        lambda x: dateutil.parser.parse(x).astimezone(local_tz))  # obstimeformat is str("%Y-%m-%d %H:%M") no timezoneinfo
    df_wetter_at["utctimestamp"] = df_wetter_at["timestamp"].dt.tz_convert("UTC")
    df_suedtirol["timestamp"] = df_suedtirol["obstime"].swifter.apply(
        lambda x: dateutil.parser.parse(x).astimezone(local_tz))  # obstimeformat is str("%Y-%m-%dT%H:%M:%S%Z")
    df_suedtirol["utctimestamp"] = df_suedtirol["timestamp"].dt.tz_convert("UTC")


    # Create a large dataset from station observations and reforcasts
    df_wetter_at["wg"] = df_wetter_at["wg"] * 0.277  # km/h in m/s
    df_wetter_at["wsg"] = df_wetter_at["wsg"] * 0.277
    df_suedtirol["sonne"] = 600 / df_suedtirol["sonne"] * 100  # sonnenscheindaur in s nach prozent

    df_wetter_at_test = df_wetter_at
    df_suedtirol_test = df_suedtirol
    df = pd.concat([df_wetter_at_test, df_suedtirol_test], axis=0, ignore_index=True)

    df = pd.concat([df_wetter_at, df_suedtirol], axis=0, ignore_index=True)

    # Check data for plausibility
    df = plausibility_check(df, "t", -50, 40)
    df = plausibility_check(df, "rf", 5, 100)
    df = plausibility_check(df, "wg", 0, 45)
    df = plausibility_check(df, "wsg", 0, 45)

    # Incorrect values are discarded
    df = df.replace(-999, np.NaN)
    df = df.drop_duplicates(keep="first")
    df = df.sort_values(by=["utctimestamp"])
    df = df.reset_index(drop=True)

    df.insert(0, "datum", df["utctimestamp"].dt.strftime("%Y-%m-%d"))
    df.insert(1, "yday", df["utctimestamp"].dt.dayofyear)
    df.insert(2, "hour", df["utctimestamp"].dt.hour)
    df.insert(3, "minute", df["utctimestamp"].dt.minute)
    df.insert(4, "dayminute", df["utctimestamp"].dt.hour * 60 + df["utctimestamp"].dt.minute)

    df = df.drop("utctimestamp", axis=1)
    df = df.drop("obstime", axis=1)
    df = df.drop("timestamp", axis=1)

    alt_dict = two_element_dict_from_pd_series(stations["station"], stations["alt"])
    alt_entry = [int(alt_dict[r]) for r in df["station"]]
    df.insert(5, "alt", alt_entry)
    logging.info("The altitude values were assigned.")

    lon_dict = two_element_dict_from_pd_series(stations["station"], stations["lon"])
    lon_entry = [float(lon_dict[r]) for r in df["station"]]
    df.insert(6, "lon", lon_entry)
    logging.info("The longitude values were assigned.")

    lat_dict = two_element_dict_from_pd_series(stations["station"], stations["lat"])
    lat_entry = [float(lat_dict[r]) for r in df["station"]]
    df.insert(7, "lat", lat_entry)
    logging.info("The latitude values were assigned.")

    df["station"] = df["station"].astype(str)
    df[["lon", "lat"]] = df[["lon", "lat"]].astype(float)
    df[["alt"]] = df[["alt"]].astype(int)

    h5filename = "./data/spatialmos_climatology/station_observations_and_reforcasts.h5"
    df.to_hdf(h5filename, "table", append=False, complevel=9, complib="zlib")
    logging.info("The data was saved in the h5 format under %s", h5filename)



# Main
if __name__ == "__main__":
    starttime = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    spatialmos_dataframe()
    logger_module.end_logging(starttime)
