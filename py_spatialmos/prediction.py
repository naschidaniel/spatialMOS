#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A script for generating surface forecasts based on GEFS predictions and GAMLSS climatologies."""

import os
import sys
import json
import csv
import logging
import datetime as dt
import numpy as np
import pandas as pd
import pytz
from scipy.interpolate import griddata
from py_middleware import logger_module
from py_middleware import spatial_parser
from py_middleware import plot_functions
from py_middleware import scandir



# Functions
def write_spatialmos_run_file(data_path_spool, anal_date_aware, spatialmos_run_status):
    """A function to create an Info File"""
    filename_spatialmos_run = os.path.join(data_path_spool, "{}_run.json".format(anal_date_aware.strftime("%Y%m%d")))
    with open(filename_spatialmos_run, "w") as f:
        json.dump(spatialmos_run_status, f)
        f.close()
    logging.info("The Info File '%s' for the spatialMOS run was written.", filename_spatialmos_run)

def write_spatialmos_run_file_failed(data_path_spool, anal_date_aware, spatialmos_run_status, step, reason):
    """A function to write missing spatialMOS data."""
    spatialmos_run_status[f"{step:03d}"] = {"status": "failed", "reason": reason, "step": f"{step:03d}"}
    write_spatialmos_run_file(data_path_spool, anal_date_aware, spatialmos_run_status)

def spatial_predictions(parser_dict):
    """The main function to create surface forecasts based on GEFS forecasts and GAMLSS climatologies."""

    # Create folder structure
    data_path_spool = f"./data/spool/{parser_dict['parameter']}/"
    if not os.path.exists(data_path_spool):
        os.makedirs(data_path_spool)

    with open("./data/get_available_data/gadm/spatial_alt_area.json") as f:
        alt_area = json.load(f)
        f.close()

    min_lon = alt_area["min_lon"]
    min_lat = alt_area["min_lat"]
    max_lon = alt_area["max_lon"]
    max_lat = alt_area["max_lat"]
    alt = pd.read_csv("./data/get_available_data/gadm/spatial_alt_area.csv", header=None)

    # Read preprocessed Info Files
    data_path = f"./data/get_available_data/gefs_pre_processed_forecast/{parser_dict['parameter']}/{parser_dict['date']}0000/"
    gribinfo_files = scandir.scandir(data_path, parameter=None, ending=".json")
    
    # A complete infofile about the status of the forecast
    spatialmos_run_status = dict()

    # Provide available NWP forecasts
    for json_info_filename in gribinfo_files:
        with open(json_info_filename) as json_file:
            gribfile_info = json.load(json_file)
            json_file.close()

        # Consider Timezone
        timezone = pytz.timezone("UTC")
        anal_date_aware = timezone.localize(dt.datetime.strptime(gribfile_info["anal_date_avg"], "%Y-%m-%d %H:%M"))
        valid_date_aware = timezone.localize(dt.datetime.strptime(gribfile_info["valid_date_avg"], "%Y-%m-%d %H:%M"))

        # Create required grids for NWP
        if parser_dict["resolution"] == 0.5:
            latlon_correction = 0.25
        else:
            latlon_correction = 0.5
        
        # Create meshgrid and add M + 1, N + 1
        # https://matplotlib.org/3.3.0/gallery/images_contours_and_fields/pcolormesh_grids.html
        # shading='auto'
        lons_plus_one = gribfile_info["lons"][-1] + parser_dict["resolution"]
        lats_plus_one = gribfile_info["lats"][-1] + parser_dict["resolution"]
        gribfile_info["lons"].append(lons_plus_one)
        gribfile_info["lats"].append(lats_plus_one)
        lons = [x - latlon_correction for x in gribfile_info["lons"]]
        lats = [x - latlon_correction for x in gribfile_info["lats"]]
        xx_nwp, yy_nwp = np.meshgrid(lons, lats)

        # Create required meshgrid for spatialMOS
        lons_spatialmos = np.linspace(min_lon, max_lon, alt.shape[1])
        lats_spatialmos = np.linspace(max_lat, min_lat, alt.shape[0])
        xx_spatialmos, yy_spatialmos = np.meshgrid(lons_spatialmos, lats_spatialmos)

        # Read in preprocessed NWP CSV file with the predictions
        nwp_df = pd.read_csv(gribfile_info["gribfile_data_filename"])

        # Interpolation of NWP forecasts
        mean_interpolation = griddata(nwp_df[["lon", "lat"]], nwp_df["mean"], (xx_spatialmos, yy_spatialmos), method="linear")
        log_spread_interpolation = griddata(nwp_df[["lon", "lat"]], nwp_df["log_spread"], (xx_spatialmos, yy_spatialmos), method="linear")
        mean_interpolation_spatial_area = np.ma.masked_where(np.isnan(alt), mean_interpolation)
        log_spread_interpolation_spatial_area = np.ma.masked_where(np.isnan(alt), log_spread_interpolation)

        climate_spatialmos_file = f"./data/spatialmos_climatology/gam/{parser_dict['parameter']}/climate_spatialmos/yday_{gribfile_info['yday']:03d}_dayminute_{gribfile_info['dayminute']}.csv"
        climate_spatialmos_nwp_file = f"./data/spatialmos_climatology/gam/{parser_dict['parameter']}/climate_spatialmos_nwp/yday_{gribfile_info['yday']:03d}_dayminute_{gribfile_info['dayminute']}_step_{gribfile_info['step']:03d}.csv"

        # Check if climatologies files are available
        if not os.path.exists(climate_spatialmos_file) or not os.path.exists(climate_spatialmos_nwp_file):
            logging.error("parameter: %9s | step: %03d | missing '%s' or '%s'", parser_dict["parameter"], gribfile_info["step"], climate_spatialmos_nwp_file, climate_spatialmos_file)
            # Write info file to spool directory
            write_spatialmos_run_file_failed(data_path_spool, anal_date_aware, spatialmos_run_status, gribfile_info["step"], "missing spatialMOS NWP or spatialMOS climatologies")
            continue

        # Read in GAMLSS climatologies
        climate_spatialmos = pd.read_csv(climate_spatialmos_file, header=0, index_col=0)
        climate_spatialmos_nwp = pd.read_csv(climate_spatialmos_nwp_file, header=0, index_col=0)

        # Set dytypes to float
        cols = climate_spatialmos.select_dtypes(exclude=["float"]).columns
        climate_spatialmos[cols] = climate_spatialmos[cols].apply(pd.to_numeric, downcast="float", errors="coerce")

        cols_nwp = climate_spatialmos_nwp.select_dtypes(exclude=["float"]).columns
        climate_spatialmos_nwp[cols_nwp] = climate_spatialmos_nwp[cols_nwp].apply(pd.to_numeric, downcast="float", errors="coerce")

        # Set index of climate dataframes to lat, lon
        climate_spatialmos = climate_spatialmos.set_index(["lat", "lon"])
        climate_spatialmos_nwp = climate_spatialmos_nwp.set_index(["lat", "lon"])

        spatial_alt_area = pd.read_csv("./data/get_available_data/gadm/spatial_alt_area_df.csv", header=0, index_col=0)
        cols_spatialmos = spatial_alt_area.select_dtypes(exclude=["float"]).columns
        spatial_alt_area[cols_spatialmos] = spatial_alt_area[cols_spatialmos].apply(pd.to_numeric, downcast="float", errors="coerce")
        spatial_alt_area = spatial_alt_area.set_index(["lat", "lon"])

        # Concate altitude and NWP und spatialMOS Dataframes to one big Dataframe
        spatialmos = pd.concat([spatial_alt_area, climate_spatialmos], axis=1, sort=True)
        spatialmos = pd.concat([spatialmos, climate_spatialmos_nwp], axis=1, sort=True)
        spatialmos = spatialmos.loc[:, ~spatialmos.columns.duplicated()]

        ## Reshape dataframe
        climate_fit = plot_functions.reshapearea(spatialmos["climate_fit"], alt)
        climate_sd = plot_functions.reshapearea(spatialmos["climate_sd"], alt)
        mean_fit = plot_functions.reshapearea(spatialmos["mean_fit"], alt)
        mean_sd = plot_functions.reshapearea(spatialmos["mean_sd"], alt)
        log_spread_fit = plot_functions.reshapearea(spatialmos["log_spread_fit"], alt)
        log_spread_sd = plot_functions.reshapearea(spatialmos["log_spread_sd"], alt)

        # Generate anomalies
        nwp_anom = (mean_interpolation_spatial_area.data - mean_fit) / mean_sd
        log_spread_nwp_anom = (log_spread_interpolation_spatial_area.data - log_spread_fit) / log_spread_sd

        # Check if spatialmos coefficients are available
        spatialmos_coef_file = f"./data/spatialmos_climatology/gam/{parser_dict['parameter']}/spatialmos_coef/spatialmos_coef_{parser_dict['parameter']}_{gribfile_info['step']:03d}.csv"
        if os.path.exists(spatialmos_coef_file):
            spatialmos_coef = pd.read_csv(spatialmos_coef_file, sep=";", quoting=csv.QUOTE_NONNUMERIC)
        else:
            logging.error("There are no spatialMOS coefficients for the parameter %s and step %s available. '%s'", parser_dict["parameter"], gribfile_info["step"], spatialmos_coef_file)
            # Write info file to spool directory
            write_spatialmos_run_file_failed(data_path_spool, anal_date_aware, spatialmos_run_status, gribfile_info["step"], "missing spatialMOS coefficients")
            continue

        # Generate spatialmos spatial predictions
        spatialmos_coef = spatialmos_coef.apply(pd.to_numeric)
        spatialmos_anom = spatialmos_coef["intercept"][0] + spatialmos_coef["mean_anom"][0] * nwp_anom
        spatialmos_mean = spatialmos_anom * climate_sd + climate_fit
        spatialmos_log_anom_spread = spatialmos_coef["intercept_log_spread"][0] + spatialmos_coef["log_spread_anom"][0] * log_spread_nwp_anom
        spatialmos_spread = np.exp(spatialmos_log_anom_spread) * climate_sd

        # Round predicted values
        spatialmos_mean = np.round(spatialmos_mean, decimals=2)
        spatialmos_spread = np.round(spatialmos_spread, decimals=5)

        # Create filename for the plots for NWP and spatialMOS forecast maps
        plot_filenames_nwp_mean = plot_functions.plot_forecast(parser_dict["parameter"], \
            xx_nwp, yy_nwp, np.load(gribfile_info["grb_avg_filename"]), gribfile_info, what="nwp_mean")
        plot_filenames_nwp_spread = plot_functions.plot_forecast(parser_dict["parameter"], \
            xx_nwp, yy_nwp, np.load(gribfile_info["grb_spr_filename"]), gribfile_info, what="nwp_spread")
        plot_filenames_spatialmos_mean = plot_functions.plot_forecast(parser_dict["parameter"], \
            xx_spatialmos, yy_spatialmos, spatialmos_mean, gribfile_info, what="spatialmos_mean")
        plot_filenames_spatialmos_spread = plot_functions.plot_forecast(parser_dict["parameter"], \
            xx_spatialmos, yy_spatialmos, spatialmos_spread, gribfile_info, what="spatialmos_spread")

        # Point Forecasts for North and South Tyrol without consideration of values outside the borders
        spatialmos_point = pd.DataFrame({"lat": yy_spatialmos.flatten().tolist(), "lon": xx_spatialmos.flatten().tolist(), "spatialmos_mean": spatialmos_mean.flatten().tolist(), "spatialmos_spread": spatialmos_spread.flatten().tolist()})
        spatialmos_point = spatialmos_point.dropna()
        spatialmos_point_dict = spatialmos_point.to_dict('records')
        
        # Exchange file for spatialMOS Run in JSON format. This file is imported into the database.
        filename_spatialmos_step = os.path.join(data_path_spool, "{}_step_{:03d}.json".format(anal_date_aware.strftime("%Y%m%d"), gribfile_info["step"]))
        prediction_json_file = {"SpatialMosRun":
                                    {
                                     "anal_date": anal_date_aware.strftime("%Y-%m-%d %H:%M:%S"),
                                     "parameter": parser_dict["parameter"]
                                    },
                                "SpatialMosStep":
                                    {"path_filename_SpatialMosStep": filename_spatialmos_step,
                                     "valid_date": valid_date_aware.strftime("%Y-%m-%d %H:%M:%S"),
                                     "step": gribfile_info["step"],
                                     "filename_nwp_mean_sm": plot_filenames_nwp_mean["filename_sm"],
                                     "filename_nwp_mean_md": plot_filenames_nwp_mean["filename_md"],
                                     "filename_nwp_mean_lg": plot_filenames_nwp_mean["filename_lg"],
                                     "filename_nwp_spread_sm": plot_filenames_nwp_spread["filename_sm"],
                                     "filename_nwp_spread_md": plot_filenames_nwp_spread["filename_md"],
                                     "filename_nwp_spread_lg": plot_filenames_nwp_spread["filename_lg"],
                                     "filename_spatialmos_mean_sm": plot_filenames_spatialmos_mean["filename_sm"],
                                     "filename_spatialmos_mean_md": plot_filenames_spatialmos_mean["filename_md"],
                                     "filename_spatialmos_mean_lg": plot_filenames_spatialmos_mean["filename_lg"],
                                     "filename_spatialmos_spread_sm": plot_filenames_spatialmos_spread["filename_sm"],
                                     "filename_spatialmos_spread_md": plot_filenames_spatialmos_spread["filename_md"],
                                     "filename_spatialmos_spread_lg": plot_filenames_spatialmos_spread["filename_lg"],
                                     "path_filename_nwp_mean_sm": plot_filenames_nwp_mean["path_filename_sm"],
                                     "path_filename_nwp_mean_md": plot_filenames_nwp_mean["path_filename_md"],
                                     "path_filename_nwp_mean_lg": plot_filenames_nwp_mean["path_filename_lg"],
                                     "path_filename_nwp_spread_sm": plot_filenames_nwp_spread["path_filename_sm"],
                                     "path_filename_nwp_spread_md": plot_filenames_nwp_spread["path_filename_md"],
                                     "path_filename_nwp_spread_lg": plot_filenames_nwp_spread["path_filename_lg"],
                                     "path_filename_spatialmos_mean_sm": plot_filenames_spatialmos_mean["path_filename_sm"],
                                     "path_filename_spatialmos_mean_md": plot_filenames_spatialmos_mean["path_filename_md"],
                                     "path_filename_spatialmos_mean_lg": plot_filenames_spatialmos_mean["path_filename_lg"],
                                     "path_filename_spatialmos_spread_sm": plot_filenames_spatialmos_spread["path_filename_sm"],
                                     "path_filename_spatialmos_spread_md": plot_filenames_spatialmos_spread["path_filename_md"],
                                     "path_filename_spatialmos_spread_lg": plot_filenames_spatialmos_spread["path_filename_lg"]
                                    },
                                "SpatialMosPoint": spatialmos_point_dict
                                }
        with open(filename_spatialmos_step, "w") as f:
            json.dump(prediction_json_file, f)
            f.close()

        # Write info file to spool directory
        spatialmos_run_status[f"{gribfile_info['step']:03d}"] = {"status": "ok", "prediction_json_file": filename_spatialmos_step, "step": f"{gribfile_info['step']:03d}"}
        write_spatialmos_run_file(data_path_spool, anal_date_aware, spatialmos_run_status)

        logging.info("parameter: %9s | anal_date: %s | valid_date: %s | step: %03d | %s", \
            prediction_json_file["SpatialMosRun"]["parameter"], prediction_json_file["SpatialMosRun"]["anal_date"], \
            prediction_json_file["SpatialMosStep"]["valid_date"], prediction_json_file["SpatialMosStep"]["step"], filename_spatialmos_step)


# Main
if __name__ == "__main__":
    STARTTIME = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    PARSER_DICT = spatial_parser.spatial_parser(parameter=True, name_parameter=["tmp_2m", "rh_2m", "wind_10m"], resolution=True, name_resolution=[0.5, 1], date=True)
    spatial_predictions(PARSER_DICT)
    logger_module.end_logging(STARTTIME)
