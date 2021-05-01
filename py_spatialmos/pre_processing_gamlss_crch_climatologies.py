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
from . import spatial_parser
from py_middleware import log_spread_calc

# Functions
def kfold(date, k):
    """A function to create a dict for cross-validation based on a date vector."""
    kfold_value = []
    for j in np.arange(1, k + 1):
        for i in np.arange(0, len(date) / k):
            kfold_value.append(j)
    kfold_value = kfold_value[0:len(date)]
    return dict(zip(date, kfold_value))


def combine_df_csvfiles(df, csvfiles_sorted, parameter, station_parameter):
    """"Multithreading worker function to create the climatologies."""
    df_reforecasts = None
    for file in csvfiles_sorted:
        df_reforecasts_new = pd.read_csv(file, sep=";", quoting=csv.QUOTE_NONNUMERIC)
        if df_reforecasts is None:
            df_reforecasts = df_reforecasts_new
        else:
            df_reforecasts = df_reforecasts.append(df_reforecasts_new)

    try:
        obstime_grib_no_tz = df_reforecasts["validDate"].apply(lambda x: dateutil.parser.parse(x))  # obstimeformat is str("%Y-%m-%d %H:%M") no timezoneinfo
    except TypeError:
        logging.error("Typeerror in df_reforecasts: %s | parameter: %s | date: %s", df_reforecasts, parameter, df["datum"])

    # Datatable preperations for gamlss
    df_reforecasts["utctimestamp"] = obstime_grib_no_tz.dt.tz_localize("UTC", ambiguous="NaT")
    df_reforecasts.insert(0, "datum", df_reforecasts["utctimestamp"].dt.strftime("%Y-%m-%d"))
    df_reforecasts.insert(1, "yday", df_reforecasts["utctimestamp"].dt.dayofyear)
    df_reforecasts.insert(2, "hour", df_reforecasts["utctimestamp"].dt.hour)
    df_reforecasts.insert(3, "minute", df_reforecasts["utctimestamp"].dt.minute)
    df_reforecasts.insert(4, "dayminute", df_reforecasts["utctimestamp"].dt.hour * 60 + df_reforecasts["utctimestamp"].dt.minute)

    # conversion to log(spread) important, so that only positive values are simulated
    log_spread_col = [log_spread_calc.log_spread(s) for s in df_reforecasts["spread"]]
    df_reforecasts.insert(15, "log_spread", log_spread_col)

    # TODO make type conversion unnecessary
    df["alt"] = df["alt"].astype(int)
    df_reforecasts["alt"] = df_reforecasts["alt"].astype(int)

    # Merge Dataframe von Messungen und Gribfiles
    df = pd.merge(df, df_reforecasts, on=["datum", "yday", "minute", "dayminute", "hour", "alt", "lon", "lat", "station"])
    df[["datum", "analDate", "validDate", "station"]] = df[["datum", "analDate", "validDate", "station"]].astype(str)  # .astype("|S")
    df[["alt", "step", "yday", "hour", "minute", "dayminute"]] = df[["alt", "step", "yday", "hour", "minute", "dayminute"]].astype(int)
    df[["lon", "lat", station_parameter, "mean", "log_spread"]] = df[["lon", "lat", station_parameter, "mean", "log_spread"]].astype(float)

    # Save Format für R für alle Parameter
    stepstr = df["step"][0]
    df = df[["yday", "kfold", "dayminute", "alt", "lon", "lat", station_parameter, "mean", "log_spread"]]
    df.columns = ["yday", "kfold", "dayminute", "alt", "lon", "lat", "obs", "mean", "log_spread"]
    df.to_csv(f"./data/spatialmos_climatology/gam/{parameter}/climate_nwp/{parameter}_{stepstr:03d}.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
    logging.info("Finished Thread for Step %03d", stepstr)
    return df

def create_gamlss_climatologies(parameter):
    """Main function to create climatologies for further processing."""

    data_path_csvfiles = os.path.join("./data/get_available_data/gefs_reforecast/interpolated_station_reforecasts/", parameter)

    # Assignment of the parameters and the designation of the parameters at the station.
    station_parameter = None
    if parameter == "tmp_2m":
        station_parameter = "t"
    elif parameter == "rh_2m":
        station_parameter = "rf"
    elif parameter == "apcp_sfc":
        station_parameter = "regen"
    elif parameter == "wind_10m":
        station_parameter = "wg"

    # Provide folder structure
    if not os.path.exists("./data/spatialmos_climatology/gam"):
        os.mkdir("./data/spatialmos_climatology/gam")
    if not os.path.exists("./data/spatialmos_climatology/gam/{}".format(parameter)):
        os.mkdir("./data/spatialmos_climatology/gam/{}".format(parameter))
    if not os.path.exists("./data/spatialmos_climatology/gam/{}/climate_nwp".format(parameter)):
        os.mkdir("./data/spatialmos_climatology/gam/{}/climate_nwp".format(parameter))

    # Read in interpolated reforecast
    csvfiles = scandir.scandir(data_path_csvfiles, parameter)

    # Generate Steps from CSV Filename
    step_ending = [s[-7:] for s in csvfiles]
    step_ending = list(dict.fromkeys(step_ending))

    csvfiles_sorted = []
    for files in step_ending:
        csvfiles_step = [s for s in csvfiles if files in s]
        csvfiles_sorted.append(csvfiles_step)

    station_observations_and_reforecasts = "./data/spatialmos_climatology/station_observations_and_reforecasts.h5"
    try:
        df_h5 = pd.read_hdf(f"{station_observations_and_reforecasts}", "table")
    except Exception as e:
        logging.error("The file %s could not be found. %s", station_observations_and_reforecasts, e)
        sys.exit(1)

    # Structure of the observation dataset
    df = df_h5[["datum", "yday", "hour", "minute", "dayminute", "alt", "lon", "lat", "station", station_parameter]]
    df = df[df["minute"] == 0]
    df = df.dropna(axis=0).reset_index(drop=True)

    # Prepare the dataset for cross-validation
    date_series = df_h5["datum"].drop_duplicates(keep="first")
    date_series = date_series.to_list()
    kfold_dictonary = kfold(date_series, k=10)
    kfold_entry = [int(kfold_dictonary[r]) for r in df["datum"]]
    df.insert(1, "kfold", kfold_entry)

    for i in np.arange(0, len(csvfiles_sorted), 1, int):
        thread = threading.Thread(target=combine_df_csvfiles, args=(df, csvfiles_sorted[i], parameter, station_parameter))
        thread.start()

    # Prepare the data record for further statistical processing
    df_save = df[["yday", "kfold", "dayminute", "alt", "lon", "lat", station_parameter]]
    df_save.columns = ["yday", "kfold", "dayminute", "alt", "lon", "lat", "obs"]
    df_save.to_csv(f"./data/spatialmos_climatology/gam/{parameter}/{parameter}_station_observations.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)

    return None

# Main
if __name__ == "__main__":
    STARTTIME = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    argsinfo = {'parameter': True,
                'available_parameter': ["tmp_2m", "rh_2m", "apcp_sfc", "wind_10m"]
                }
    arguments = sys.argv[1:]
    PARSER_DICT = spatial_parser.spatial_parser(arguments, argsinfo)
    create_gamlss_climatologies(PARSER_DICT["parameter"])
    logger_module.end_logging(STARTTIME)
