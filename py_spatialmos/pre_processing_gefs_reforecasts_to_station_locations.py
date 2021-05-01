#!/usr/bin/python
# -*- coding: utf-8 -*-
"""With this Python script the GEFS Ensemble predictions can be interpolated bilinear to the station locations."""

import csv
from logging import error
import os
import sys
import time
import logging
from multiprocessing import Pool
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
from py_middleware import logger_module
from py_middleware import scandir
from . import spatial_parser
from py_middleware import meteorological_calc
from py_middleware import gribfile_to_pandasdf


# Functions
def status_gribfiles(cores, parameter, gribfiles_mean_spread):
    """A function for the calculation status to be processed."""
    logging.info("          available cores : %s", cores)
    logging.info("                parameter : %s", parameter)
    logging.info("    gribfiles to processed: %s", len(gribfiles_mean_spread))
    logging.info("            first gribfile: %s", gribfiles_mean_spread[0])
    logging.info("             last gribfile: %s", gribfiles_mean_spread[-1])

def filename_csv(parameter, df):
    """A function to generate the filename for the CSV-Files"""
    anal_date = pd.to_datetime(df["analDate"][0]).strftime("%Y%m%d%H")
    step = int(df["step"][0])
    
    path_interpolated_station_reforecasts = f"./data/get_available_data/gefs_reforecast/interpolated_station_reforecasts/{parameter}"
    if not os.path.exists(path_interpolated_station_reforecasts):
        os.makedirs(path_interpolated_station_reforecasts)
        
    return f"{path_interpolated_station_reforecasts}/GFSV2_{parameter}_{anal_date}_{step:03d}.csv"


def predictions_for_stations(gribfile, parameter):
    """A function to create a pandas dataframe for the GEFS Reforecasts for the respective stations."""
    df = pd.read_csv(gribfile, sep=";", quoting=csv.QUOTE_NONNUMERIC)
    df.columns = ["analDate", "validDate", "step", "station", "alt", "lon", "lat", f"mean_{parameter}", f"spread_{parameter}"]
    df.set_index("station")
    return df


def gefs_reforecasts_to_station_location(parameter, cores=8):
    """Main function of the program to interpolate GEFS Reforecasts on ward locations. Existing GEFS Reforecasts are interpolated. Data which is not included in the GEFS Reforecasts are calculated. The predictions are saved per model run and step in CSV-Format"""
    if parameter in ["tmp_2m", "pres_sfc", "spfh_2m", "apcp_sfc", "ugrd_10m", "vgrd_10m"]:
        data_path = "./data/get_available_data/gefs_reforecast/nwp/"
        gribfiles = scandir.scandir(data_path, parameter)

        if gribfiles == []:
            logging.error("There are no gribfiles for parameter {%s}", parameter)
            sys.exit(1)

        # Split gribfiles into mean and spread files
        gribfiles_mean = [s for s in gribfiles if "mean" in s]
        gribfiles_spread = [s for s in gribfiles if "sprd" in s]

        # group gribfiles by date
        gribfiles_mean_spread_parameter = []
        for mean_file in gribfiles_mean:
            spread_file = [s for s in gribfiles_spread if mean_file[-28:-18] in s]
            spread_file = spread_file[0]
            if spread_file is not None:
                gribfiles_mean_spread_parameter.append([mean_file, spread_file, parameter])

        status_gribfiles(cores, parameter, gribfiles_mean_spread_parameter)

        with Pool(cores) as p:
            p.map(interpolate_grib_files, gribfiles_mean_spread_parameter)

    elif parameter in ["rh_2m", "wind_10m"]:
        data_path_interpolated_gribfiles = "./data/get_available_data/gefs_reforecast/interpolated_station_reforecasts/"
        parameter_calc = []
        if parameter == "rh_2m":
            parameter_calc = ["spfh_2m", "pres_sfc", "tmp_2m"]
        elif parameter == "wind_10m":
            parameter_calc = ["ugrd_10m", "vgrd_10m"]

        data_path_spfh_2m = os.path.join(data_path_interpolated_gribfiles, parameter_calc[0])
        data_path_pres_sfc = os.path.join(data_path_interpolated_gribfiles, parameter_calc[1])

        csvfiles_file0 = scandir.scandir(data_path_spfh_2m, parameter_calc[0])
        csvfiles_file1 = scandir.scandir(data_path_pres_sfc, parameter_calc[1])
        csvfiles_file2 = []
        if parameter == "rh_2m":
            data_path_tmp_2m = os.path.join(data_path_interpolated_gribfiles, parameter_calc[2])
            csvfiles_file2 = scandir.scandir(data_path_tmp_2m, parameter_calc[2])

        # group gribfiles by date
        gribfiles_combined = []
        for file0_f in csvfiles_file0:
            file0_date = file0_f[-18:]
            file1_f = [s for s in csvfiles_file1 if file0_date in s]

            if parameter == 'rh_2m':
                file2_f = [s for s in csvfiles_file2 if file0_date in s]
                if file0_f != [] and file1_f != [] and file1_f != []:
                    gribfiles_combined.append([file0_f, file1_f[0], file2_f[0], parameter, parameter_calc])
            else:
                if file0_f != [] and file1_f != []:
                    gribfiles_combined.append([file0_f, file1_f[0], -999, parameter, parameter_calc])

        status_gribfiles(cores, parameter, gribfiles_combined)

        with Pool(cores) as p:
            p.map(calculate_parameter, gribfiles_combined)


def calculate_parameter(gribfiles_combined):
    """A function to calculate a parameter that is not available as direct model output."""
    parameter = gribfiles_combined[3]
    parameter_calc = gribfiles_combined[4]
    # TODO Index 0, 1, 2 with names replaced by parameter names
    file0_f = predictions_for_stations(gribfiles_combined[0], parameter_calc[0])
    file1_f = predictions_for_stations(gribfiles_combined[1], parameter_calc[1])

    data = file0_f.merge(file1_f)

    if parameter == "rh_2m":
        file2_f = predictions_for_stations(gribfiles_combined[2], parameter_calc[2])
        data = data.merge(file2_f)

    file_f = []
    for index, row in data.iterrows():
        parm0 = np.random.normal(row["mean_{}".format(parameter_calc[0])], row["spread_{}".format(parameter_calc[0])], 2500)
        parm1 = np.random.normal(row["mean_{}".format(parameter_calc[1])], row["spread_{}".format(parameter_calc[1])], 2500)
        mean_parameter = -999 # Set invalid value
        spread_parameter = -999 # Set invalid value

        if parameter == "rh_2m":
            parm2 = np.random.normal(row["mean_{}".format(parameter_calc[2])], row["spread_{}".format(parameter_calc[2])], 2500)
            parm = meteorological_calc.spfh2rh(parm0, parm1, parm2)
            mean_parameter = round(np.mean(parm), 0) # e.g.: 95%
            spread_parameter = round(np.std(parm), 1) # e.g.: 2.3%
        elif parameter == "wind_10m":
            parm = meteorological_calc.uv2wind(parm0, parm1)
            mean_parameter = round(np.mean(parm), 2) # e.g.: 10.51 m/s
            spread_parameter = round(np.std(parm), 2) # e.g.: 0.31 m/s

        file_f.append([row["analDate"], row["validDate"], row["step"], row["station"], row["alt"], row["lon"], row["lat"], mean_parameter, spread_parameter])

    file_f = pd.DataFrame(file_f, columns=["analDate", "validDate", "step", "station", "alt", "lon", "lat", "mean", "spread"])
    file_f.to_csv(filename_csv(parameter, file_f), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


def interpolate_grib_files(gribfiles_mean_spread_parameter):
    """A function to interpolate the gribfiles to station locations. The data is saved as individual CSV files for each prediction and each timestep."""
    # select parameter
    gribfiles_mean = gribfiles_mean_spread_parameter[0]
    gribfiles_spread = gribfiles_mean_spread_parameter[1]
    parameter = gribfiles_mean_spread_parameter[2]

    # Read Gribfiles
    last_step = False
    select_step = 0
    while not last_step:
        df_grb_avg, grb_avg, info, last_step = gribfile_to_pandasdf.open_gribfile(gribfiles_mean, parameter, "avg", select_step, info=True, last_step=False)
        df_grb_spr, grb_spr = gribfile_to_pandasdf.open_gribfile(gribfiles_spread, parameter, "spr", select_step)
        
        if len(df_grb_avg) != len(df_grb_spr):
            logging.error("There has been a error %s | anal_date: %s | valid_date: %s | step: %s", parameter, info["anal_date"], info["valid_date"], info["step"])
        else:
            # Combining Mean and Spread of Predictions
            prediction_df = pd.concat([df_grb_spr, df_grb_avg], axis=1, join='inner')        
            prediction_df = prediction_df.reset_index()

            # Station locations of South Tyrol and wetter_at
            stations_at_wetter = pd.read_csv("./data/get_available_data/wetter_at/stations.csv")
            stations_suedtirol = pd.read_csv("./data/get_available_data/suedtirol/stations.csv")
            stations = stations_at_wetter.append(stations_suedtirol, sort=False)

            entry_list = []
            for index, row in stations.iterrows():
                try:
                    entry_list.append([info["anal_date"], info["valid_date"], info["step"], row["station"], row["alt"], row["lon"], row["lat"],
                                        griddata(prediction_df[["longitude", "latitude"]], prediction_df["mean"], (row["lon"], row["lat"]), method="linear"),
                                        griddata(prediction_df[["longitude", "latitude"]], prediction_df["spread"], (row["lon"], row["lat"]), method="linear")])
                except Exception as e:
                    logging.error("The data points could not be interpolated. %s", e)

            df = pd.DataFrame(entry_list, columns=["analDate", "validDate", "step", "station", "alt", "lon", "lat", "mean", "spread"])
            # Store data as CSV files in the file system
            if parameter == "spfh_2m":
                df["mean"] = np.around(df["mean"].astype(np.double), 12)
                df["spread"] = np.around(df["spread"].astype(np.double), 12)
            else:
                df["mean"] = np.around(df["mean"].astype(np.double), 2)
                df["spread"] = np.around(df["spread"].astype(np.double), 2)

            df.to_csv(filename_csv(parameter, df), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)

        select_step = select_step + 1


# Main
if __name__ == "__main__":
    STARTTIME = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    argsinfo = {'parameter': True,
                'available_parameter': ["tmp_2m", "pres_sfc", "spfh_2m", "apcp_sfc", "rh_2m", "ugrd_10m", "vgrd_10m", "rh_2m", "wind_10m"]
                }
    arguments = sys.argv[1:]
    PARSER_DICT = spatial_parser.spatial_parser(arguments, argsinfo)
    gefs_reforecasts_to_station_location(PARSER_DICT["parameter"])
    logger_module.end_logging(STARTTIME)
