#!/usr/bin/python
# -*- coding: utf-8 -*-
"""With this Python script the GEFS Enselble predictions can be interpolated bilinearly to the station locations."""

import csv
import os
import sys
import time
import logging
from multiprocessing import Pool
import numpy as np
import pandas as pd
import pygrib
from scipy.interpolate import griddata
from py_middleware import logger_module
from py_middleware import scandir
from py_middleware import spatial_parser


# Functions
def gefs_reforcasts_to_station_location(parameter, cores=8):
    """Main function of the program to interpolate GEFS Reforcasts on ward locations. Existing GEFS Reforcasts are interpolated. Data wich is not included in the GEFS Reforcasts are calculated. The predictions are saved per model run and step in CSV-Format"""
    if parameter in ["tmp_2m", "pres_sfc", "spfh_2m", "apcp_sfc", "ugrd_10m", "vgrd_10m"]:
        data_path = "./data/get_available_data/gefs_reforcast/nwp/"
        gribfiles = scandir.scandir(data_path, parameter)

        if gribfiles == []:
            logging.error("There are no gribfiles for parameter {%s}", parameter)
            sys.exit(1)

        # Split gribfiles into mean and spread files
        gribfiles_mean = [s for s in gribfiles if "mean" in s]
        gribfiles_spread = [s for s in gribfiles if "sprd" in s]

        # group gribfiles by date
        gribfiles_mean_spread = []
        for mean_f in gribfiles_mean:
            spread_f = [s for s in gribfiles_spread if mean_f[-28:-18] in s]
            spread_f = spread_f[0]
            if spread_f is not None:
                gribfiles_mean_spread.append([mean_f, spread_f, parameter])
        
        status_gribfiles(cores, parameter, gribfiles_mean_spread)

        with Pool(cores) as p:
            p.map(interpolate_grib_files, gribfiles_mean_spread)
    
    elif parameter in ["rh_2m", "wind_10m"]:
        data_path_interpolated_gribfiles = "./data/get_available_data/gefs_reforcast/interpolated_gribfiles/"
        parameter_calc = []
        if parameter == "rh_2m":
            parameter_calc = ["spfh_2m", "pres_sfc", "tmp_2m"]
        elif parameter == "wind_10m":
            parameter_calc = ["ugrd_10m", "vgrd_10m"]

        csvfiles_file0 = scandir.scandir(data_path_interpolated_gribfiles, parameter_calc[0])
        csvfiles_file1 = scandir.scandir(data_path_interpolated_gribfiles, parameter_calc[1])
        csvfiles_file2 = []

        if parameter == "rh_2m":
            csvfiles_file2 = scandir.scandir(data_path_interpolated_gribfiles, parameter_calc[2])
            if csvfiles_file0 == [] or csvfiles_file1 == [] or csvfiles_file2 == []:
                logging.error("There are no interpolated values in the folder %s available for parameter %s.", data_path_interpolated_gribfiles, parameter_calc)
                sys.exit(1)
        elif parameter == "wind_10m":
            if csvfiles_file0 == [] or csvfiles_file1 == []:
                logging.error("There are no interpolated values in the folder %s available for parameter %s.", data_path_interpolated_gribfiles, parameter_calc)
                sys.exit(1)


        # group gribfiles by date
        gribfiles_combined = []
        for file0_f in csvfiles_file1:
            file0_date = file0_f[-18:]
            file1_f = [s for s in csvfiles_file1 if file0_date in s]

            if parameter == 'rh_2m':
                file2_f = [s for s in csvfiles_file2 if file0_date in s]
                if file0_f != [] and file1_f != [] and file1_f != []:
                    gribfiles_combined.append([file0_f, file1_f[0], file2_f[0], parameter, parameter_calc])
                else:
                    pass
            else:
                if file0_f != [] and file1_f != []:
                    gribfiles_combined.append([file0_f, file1_f[0], -999, parameter, parameter_calc])
                else:
                    pass

        status_gribfiles(cores, parameter, gribfiles_combined)

        with Pool(cores) as p:
            p.map(calculate_parameter(gribfiles_combined), gribfiles_combined)


def status_gribfiles(cores, parameter, gribfiles_mean_spread):
    """A function for the calculation status to be processed."""
    logging.info("Cores für Parallelisierung: %s", cores)
    logging.info("                Parameter : %s", parameter)
    logging.info("    gribfiles to processed: %s", (len(gribfiles_mean_spread) * 43))
    logging.info("            first gribfile: %s", gribfiles_mean_spread[0])
    logging.info("             last gribfile: %s", gribfiles_mean_spread[-1])

def filename_csv(parameter, df):
    """A function to generate the filename for the CSV-Files"""
    analDate = pd.to_datetime(df["analDate"][0]).strftime("%Y%m%d%H")
    step = int(df["step"][0])
    
    path_interpolated_station_reforcasts = f"./data/get_available_data/gefs_reforcast/interpolated_station_reforcasts/{parameter}"
    if not os.path.exists(path_interpolated_station_reforcasts):
        os.makedirs(path_interpolated_station_reforcasts)
    
    return f"{path_interpolated_station_reforcasts}/GFSV2_{parameter}_{analDate}_{step:03d}.csv"

def spfh2rh(spfh_2m, pres_sfc, tmp_2m):
    """A function to calculate the relative humidity"""
    es = 6.112 * np.exp((17.67 * tmp_2m) / (tmp_2m + 243.5))
    e = spfh_2m * pres_sfc / (0.378 * spfh_2m + 0.622)
    rh = e / es

    rh[rh > 100] = 100.0
    rh[rh < 0] = 0.0
    return rh

def uv2wind(ugrd_10m, vgrd_10m):
    """A function to calculate the wind speed from the u and v component."""
    squarewind = ugrd_10m**2 + vgrd_10m**2
    windSpeed = np.sqrt(squarewind)
    return(windSpeed)

def predictions_for_stations(gribfile, parameter):
    """A function to create a pandas dataframe for the GEFS Reforcasts for the respective stations."""
    file_f = pd.read_csv(gribfile, sep=";", quoting=csv.QUOTE_NONNUMERIC)
    file_f.columns = ["analDate", "validDate", "step", "station", "alt", "lon", "lat", f"mean_{parameter}", f"spread_{parameter}"]
    file_f.set_index("station")
    return file_f

def calculate_parameter(gribfiles_combined):
    """A function to calculate a parameter that is not available as direct model output."""
    parameter = gribfiles_combined[3]
    parameter_calc = gribfiles_combined[4]
    

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
            parm = spfh2rh(parm0, parm1, parm2)
            mean_parameter = round(np.mean(parm), 0) # e.g.: 95%
            spread_parameter = round(np.std(parm), 1) # e.g.: 2.3%
        elif parameter == "wind_10m":
            parm = uv2wind(parm0, parm1)
            mean_parameter = round(np.mean(parm), 2) # e.g.: 10.51 m/s
            spread_parameter = round(np.std(parm), 2) # e.g.: 0.31 m/s

        file_f.append([row["analDate"], row["validDate"], row["step"], row["station"], row["alt"], row["lon"], row["lat"], mean_parameter, spread_parameter])

    file_f = pd.DataFrame(file_f, columns=["analDate", "validDate", "step", "station", "alt", "lon", "lat", "mean", "spread"])
    file_f.to_csv(filename_csv(parameter, file_f), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


def interpolate_grib_files(gribfiles_mean_spread_parameter):
    """A function to interpolate the gribfiles to station locations. The data is saved as individual CSV files for each prediction and each timestep."""
    # Read Gribfiles
    grbs_avg = pygrib.open(gribfiles_mean_spread_parameter[0])
    grbs_spr = pygrib.open(gribfiles_mean_spread_parameter[1])

    # select parameter
    parameter = gribfiles_mean_spread_parameter[2]
    intercept = 0
    grbs_select_name = None

    if parameter == "tmp_2m":
        grbs_select_name = "2 metre temperature"  # Kelvin
        intercept = 273.15  # from Kelvin to Celsius
    elif parameter == "pres_sfc":
        grbs_select_name = "Surface pressure"  # Pa
    elif parameter == "spfh_2m":
        grbs_select_name = "Specific humidity"  # kg/kg
    elif parameter == "apcp_sfc":
        grbs_select_name = "Total Precipitation"
    elif parameter == "ugrd_10m":
        grbs_select_name = "10 metre U wind component" #m s**-1
    elif parameter == "vgrd_10m":
        grbs_select_name = "10 metre V wind component" #m s**-1

    for grb_avg in grbs_avg.select(name=grbs_select_name):
        analDate = grb_avg.analDate.strftime("%Y-%m-%d %H:%M")
        validDate = grb_avg.validDate.strftime("%Y-%m-%d %H:%M")
        step = grb_avg.startStep

        try:
            # Combining Mean and Spread of Predictions
            grb_spr = grbs_spr.select(name=grbs_select_name, analDate=grb_avg.analDate, validDate=grb_avg.validDate, startStep=grb_avg.startStep)
            grb_spr = grb_spr[0]
        except ValueError as e:
            logging.error("There has been a error %s | analDate: %s | validDate: %s | step: %s | error: %s", grbs_select_name, grb_avg.analDate, grb_avg.validDate, grb_avg.startStep, e)
            continue
        
        # Scale to the grid of spatialMOS
        ## NWP
        latitude = np.linspace(float(grb_avg["latitudeOfFirstGridPointInDegrees"]),
                            float(grb_avg["latitudeOfLastGridPointInDegrees"]), int(grb_avg["Nj"]))
        longitude = np.linspace(float(grb_avg["longitudeOfFirstGridPointInDegrees"]),
                            float(grb_avg["longitudeOfLastGridPointInDegrees"]), int(grb_avg["Ni"]))

        nwp_df = []
        for lon in longitude:
            for lat in latitude:
                mean = grb_avg.data(lat1=lat, lon1=lon)
                if parameter == "spfh_2m":
                    mean = round(mean[0][0][0] - intercept, 12)
                else:
                    mean = round(mean[0][0][0] - intercept, 2)
                spread = grb_spr.data(lat1=lat, lon1=lon)
                spread = spread[0][0][0]
                nwp_df.append([mean, spread, lon, lat])

        nwp_df = pd.DataFrame(nwp_df, columns=["mean", "spread", "lon", "lat"])

        # Station locations of South Tyrol and wetter_at
        stations_at_wetter = pd.read_csv("./data/get_available_data/wetter_at/stations.csv")
        stations_suedtirol = pd.read_csv("./data/get_available_data/suedtirol/stations.csv")
        stations = stations_at_wetter.append(stations_suedtirol, sort=False)

        df_entry = []
        for index, row in stations.iterrows():
            try:
                df_entry.append([analDate, validDate, step, row["station"], row["alt"], row["lon"], row["lat"],
                                    griddata(nwp_df[["lon", "lat"]], nwp_df["mean"], (row["lon"], row["lat"]),
                                            method="linear"),
                                    griddata(nwp_df[["lon", "lat"]], nwp_df["spread"], (row["lon"], row["lat"]),
                                            method="linear")])
            except Exception as e:
                logging.error("The data points could not be interpolated. %s", e)

        df = pd.DataFrame(df_entry, columns=["analDate", "validDate", "step", "station", "alt", "lon", "lat", "mean", "spread"])

        # Store data as CSV files in the file system
        if parameter == "spfh_2m":
            df["mean"] = np.around(df["mean"].astype(np.double), 12)
            df["spread"] = np.around(df["spread"].astype(np.double), 12)
        else:
            df["mean"] = np.around(df["mean"].astype(np.double), 2)
            df["spread"] = np.around(df["spread"].astype(np.double), 2)

        df.to_csv(filename_csv(parameter, df), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)



# Main
if __name__ == "__main__":
    starttime = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    parser_dict = spatial_parser.spatial_parser(parameter=True, name_parameter=["tmp_2m", "pres_sfc", "spfh_2m", "apcp_sfc", "rh_2m", "ugrd_10m", "vgrd_10m", "rh_2m", "wind_10m"])
    gefs_reforcasts_to_station_location(parser_dict["parameter"])
    logger_module.end_logging(starttime)
