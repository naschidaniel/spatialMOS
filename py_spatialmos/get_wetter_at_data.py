#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This program is used to load data from the at-wetter.tk website."""

import csv
import os
import logging
import time
from datetime import datetime
import requests
import pandas as pd
from tqdm import tqdm
from py_middleware import spatial_parser
from py_middleware import logger_module


# Functions
def fetch_wetter_at_data(beginndate, enddate):
    """This function loads data from the API interface of at-wetter.tk website and saves it as csv files."""
    # Provide folder structure.
    data_path = "./data/get_available_data/wetter_at"
    if not os.path.exists(f"{data_path}"):
        os.mkdir(f"{data_path}")

    # Download from moses.tirol
    stationfile = f"{data_path}/stations.csv"
    if not os.path.exists(stationfile):
        req_stationsfile = requests.get("http://moses.tirol/required_files/wetter_at/stations.csv")
        if req_stationsfile.status_code == 200:
            with open(stationfile, mode="w") as f:
                f.write(req_stationsfile.text)
                f.close()

    parameter_info_file = f"{data_path}/Parameter_Info.csv"
    if not os.path.exists(parameter_info_file):
        req_parameter_info_file = requests.get("http://moses.tirol/required_files/wetter_at/Parameter_Info.csv")
        if req_parameter_info_file.status_code == 200:
            with open(parameter_info_file, mode="w") as f:
                f.write(req_parameter_info_file.text)
                f.close()

    stationinfo_all = pd.read_csv(stationfile, delimiter=",", header=0)
    parameter = ["t", "tp", "rf", "wr", "wg", "wsr",
                 "wsg", "regen", "ldred", "ldstat", "sonne"]

    data_path = f"{data_path}/data"
    if not os.path.exists(f"{data_path}"):
        os.mkdir(f"{data_path}")

    # beginndateformat, enddateformat and timedelta for URL
    startdate_time = datetime.strptime(beginndate, "%Y%m%d")
    enddate_time = datetime.strptime(enddate, "%Y%m%d")
    timedelta_time = enddate_time - startdate_time
    timedelta = timedelta_time.days

    # Fetch data from API
    with tqdm(total=stationinfo_all.shape[0], desc=f"Data download from API of the weather service at-wetter.tk | {beginndate} to {enddate} | |", leave=False) as pbar:
        for index, stationinfo in stationinfo_all.iterrows():
            time.sleep(10)
            csvfile = f"{data_path}/{beginndate}_{enddate}_{stationinfo['station']}.csv"
            if not os.path.exists(csvfile):
                df = None
                # Loop over parameters
                for p in parameter:
                    df = download_data_wetter_at(
                        data_path, stationinfo["station"], enddate, timedelta, parameter=p, df=df)
                pbar.set_description(
                    f"Download {stationinfo['station']} | from {beginndate} to {enddate} | ", refresh=False)
                df.to_csv(csvfile, sep=";", index=False,
                          quoting=csv.QUOTE_MINIMAL)
                logging.info(
                    "The data of for the station %s from %s to %s has been saved in the file %s.", stationinfo["station"], enddate, beginndate, csvfile)
            else:
                tqdm.write(
                    f"The data has already been saved in the file {csvfile}.")
                logging.warning(
                    "The data has already been saved in the file %s.", csvfile)
            pbar.update(1)


def download_data_wetter_at(data_path, station, beginndate, timeseries, parameter, df):
    """This function downloads data from the API interface and returns it as a panda dataframe."""
    url_parameter = f"http://at-wetter.tk/api/v1/station/{station}/{parameter}/{beginndate}/{timeseries}"
    req_parameter = requests.get(url_parameter)

    if req_parameter.status_code == 200:
        temporaryfile = "{}/tempfile.tmp".format(data_path)
        with open(temporaryfile, mode="w") as f:
            f.write(req_parameter.text)
            f.close()

        new_df = pd.read_csv(temporaryfile, delimiter=";", quotechar="'", header=None, names=[
                             "station", "name", "altdown", "datum", "uhr", parameter, "einheit", "downloaddate"])
        os.remove(temporaryfile)

        # Data manipulation
        new_df["obstime"] = new_df["datum"].astype(
            str) + " " + new_df["uhr"].astype(str)
        new_df["timestamp_datetime"] = pd.to_datetime(
            new_df["obstime"], format="%Y-%m-%d %H:%M")
        new_df = new_df.drop(columns=[
                             "name", "altdown", "datum", "uhr", "einheit", "downloaddate", "timestamp_datetime"])
        new_df = new_df[["obstime", "station", parameter]]

        # Set missing values to -999
        replace_value = new_df[parameter].astype(str).str.contains("null")
        if any(replace_value):
            new_df.loc[replace_value, parameter] = -999

        if df is None:
            df = new_df
        else:
            df = pd.concat([df, new_df[parameter]], axis=1)

        return df
    else:
        logging.error(
            "The request for the URL '%s' returned the status code 404", url_parameter)


# Main
if __name__ == "__main__":
    starttime = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    parser_dict = spatial_parser.spatial_parser(beginndate=True, enddate=True)
    fetch_wetter_at_data(parser_dict["beginndate"], parser_dict["enddate"])
    logger_module.end_logging(starttime)
