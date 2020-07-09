#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A script to create the required data structure for further processing in R. The data tables required for gamlss in R are created individually for each parameter."""

import csv
import logging
import os
import sys
import threading
import dateutil
import numpy as np
import pandas as pd
from py_middleware import logger_module
from py_middleware import scandir
from py_middleware import spatial_parser


# Functions
def log_spread(spread):
    if spread == float(0):
        log_spread_val = np.log(0.001)
    else:
        log_spread_val = np.log(spread)
    return round(log_spread_val, 3)


def kfold(date, k):
    """A function to create a dict for cross-validation based on a date vector."""
    kfold = []
    for j in np.arange(1, k + 1):
        for i in np.arange(0, len(date) / k):
            kfold.append(j)
    kfold = kfold[0:len(date)]
    return dict(zip(date, kfold))


def combine_df_csvfiles(df, csvfiles_sorted, parameter, station_parameter):
    """"Multithreading worker function to create the climatologies."""
    df_grib = None
    for file in csvfiles_sorted:
        df_grib_new = pd.read_csv(file, sep=";", quoting=csv.QUOTE_NONNUMERIC)
        if df_grib is None:
            df_grib = df_grib_new
        else:
            df_grib = df_grib.append(df_grib_new)

    try:
        obstime_grib_no_tz = df_grib["validDate"].apply(
            lambda x: dateutil.parser.parse(x))  # obstimeformat is str("%Y-%m-%d %H:%M") no timezoneinfo
    except TypeError:
        logging.error("df_grib: {} | parameter: {} | Datum: {}".format(df_grib, parameter, df["datum"]))

    # Typenumwanldung für GAMLSS
    df_grib["utctimestamp"] = obstime_grib_no_tz.dt.tz_localize("UTC", ambiguous="NaT")
    df_grib.insert(0, "datum", df_grib["utctimestamp"].dt.strftime("%Y-%m-%d"))
    df_grib.insert(1, "yday", df_grib["utctimestamp"].dt.dayofyear)
    df_grib.insert(2, "hour", df_grib["utctimestamp"].dt.hour)
    df_grib.insert(3, "minute", df_grib["utctimestamp"].dt.minute)
    df_grib.insert(4, "dayminute", df_grib["utctimestamp"].dt.hour * 60 + df_grib["utctimestamp"].dt.minute)

    # Umwandlung in log(spread) wichtig, damit nur postive Werte simuliert werden
    log_spread_col = [log_spread(s) for s in df_grib["spread"]]
    df_grib.insert(15, "log_spread", log_spread_col)

    # TODO Typenumwandlung unnötig machen :)
    df["alt"] = df["alt"].astype(int)
    df_grib["alt"] = df_grib["alt"].astype(int)

    # Merge Dataframe von Messungen und Gribfiles
    df = pd.merge(df, df_grib, on=["datum", "yday", "minute", "dayminute", "hour", "alt", "lon", "lat", "station"])
    df[["datum", "analDate", "validDate", "station"]] = df[["datum", "analDate", "validDate", "station"]].astype(str)  # .astype("|S")
    df[["alt", "step", "yday", "hour", "minute", "dayminute"]] = df[["alt", "step", "yday", "hour", "minute", "dayminute"]].astype(int)
    df[["lon", "lat", station_parameter, "mean", "log_spread"]] = df[["lon", "lat", station_parameter, "mean", "log_spread"]].astype(float)

    # Save Format für R für alle Parameter
    stepstr = df["step"][0]
    df = df[["yday", "kfold", "dayminute", "alt", "lon", "lat", station_parameter, "mean", "log_spread"]]
    df.columns = ["yday", "kfold", "dayminute", "alt", "lon", "lat", "obs", "mean", "log_spread"]
    df.to_csv("./data/spatialmos_climatology/gam/{}/klima_nwp/{}_{:03d}.csv".format(parameter, parameter, stepstr), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
    logging.info("Thread mit Step {:03d} fertiggestellt".format(stepstr))
    return df

def create_gamlss_climatologies(parameter):
    """Main function to create climatologies for further processing."""

    data_path_csvfiles = os.path.join("./data/get_available_data/gefs_reforcast/interpolated_station_reforcasts/", parameter)

    # Assignment of the parameters and the designation of the parameters at the station.
    if parameter == "tmp_2m":
        station_parameter = "t"
    elif parameter == "rh_2m":
        station_parameter = "rf"
    elif parameter == "apcp_sfc":
        station_parameter = "regen"
    elif parameter == "wind_10m":
        station_parameter = "wg"

    # Erstellung Ordner für Klimatologien
    if not os.path.exists("./data/spatialmos_climatology/gam"):
        os.mkdir("./data/spatialmos_climatology/gam")
    if not os.path.exists("./data/spatialmos_climatology/gam/{}".format(parameter)):
        os.mkdir("./data/spatialmos_climatology/gam/{}".format(parameter))
    if not os.path.exists("./data/spatialmos_climatology/gam/{}/klima_nwp".format(parameter)):
        os.mkdir("./data/spatialmos_climatology/gam/{}/klima_nwp".format(parameter))

    # Read in interpolated reforcast
    csvfiles = scandir.scandir(data_path_csvfiles, parameter)

    # Generate Steps from CSV Filename
    step_ending = [s[-7:] for s in csvfiles]
    step_ending = list(dict.fromkeys(step_ending))

    csvfiles_sorted = []
    for files in step_ending:
        csvfiles_step = [s for s in csvfiles if files in s]
        csvfiles_sorted.append(csvfiles_step)

    station_observations_and_reforcasts = "./data/spatialmos_climatology/station_observations_and_reforcasts.h5"
    try:
        df_h5 = pd.read_hdf(f"{station_observations_and_reforcasts}", "table")
    except Exception as e:
        logging.error("The file %s could not be found. %s", station_observations_and_reforcasts, e)
        sys.exit(1)

    # Structure of the observation dataset
    df = df_h5[["datum", "yday", "hour", "minute", "dayminute", "alt", "lon", "lat", "station", station_parameter]]
    df = df[df["minute"] == 0]
    df = df.dropna(axis=0).reset_index(drop=True)

    # Prepare the dataset for cross-validation
    datum_series = df_h5["datum"].drop_duplicates(keep="first")
    datum_series = datum_series.to_list()
    kfold_dictonary = kfold(datum_series, k=10)
    kfold_entry = [int(kfold_dictonary[r]) for r in df["datum"]]
    df.insert(1, "kfold", kfold_entry)

    for i in np.arange(0, len(csvfiles_sorted), 1, int):
        thread = threading.Thread(target=combine_df_csvfiles, args=(df, csvfiles_sorted[i], parameter, station_parameter))
        thread.start()

    # Prepare the data record for further statistical processing
    df_save = df[["yday", "kfold", "dayminute", "alt", "lon", "lat", station_parameter]]
    df_save.columns = ["yday", "kfold", "dayminute", "alt", "lon", "lat", "obs"]
    df_save.to_csv(f"./data/spatialmos_climatology/gam/{parameter}/{parameter}_station_observations.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


# Main
if __name__ == "__main__":
    starttime = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    parser_dict = spatial_parser.spatial_parser(parameter=True, name_parameter=["tmp_2m", "rh_2m", "apcp_sfc", "wind_10m"])
    create_gamlss_climatologies(parser_dict["parameter"])
    logger_module.end_logging(starttime)
