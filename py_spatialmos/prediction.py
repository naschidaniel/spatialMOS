#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A script for generating surface forecasts based on GEFS predictions and GAMLSS climatologies."""

import os
import json
import csv
import logging
import datetime as dt
import numpy as np
import pandas as pd
import pytz
from scipy.interpolate import griddata
os.environ["PROJ_LIB"] = "/usr/share/proj" # Environment Variable for basemap
from mpl_toolkits.basemap import Basemap
from py_middleware import logger_module
from py_middleware import spatial_parser
from py_middleware import plot_functions
from py_middleware import scandir



# Functions
def spatial_predictions(parser_dict):
    """The main function to create surface forecasts based on GEFS forecasts and GAMLSS climatologies."""

    # Create folder structure
    data_path_spool = "./data/spool/{}/samos/".format(parser_dict["parameter"])
    if not os.path.exists(data_path_spool):
        os.makedirs(data_path_spool)

    with open("./data/get_available_data/gadm/spatial_alt_area.json") as f:
        alt_area = json.load(f)
        f.close()

    min_lon = alt_area["min_lon"]
    min_lat = alt_area["min_lat"]
    max_lon = alt_area["max_lon"]
    max_lat = alt_area["max_lat"]
    center_lon = alt_area["center_lon"]
    center_lat = alt_area["center_lat"]
    alt = pd.read_csv("./data/get_available_data/gadm/spatial_alt_area.csv", header=None)

    # BASEMAPS for GEFS predictions and spatialMOS
    m_nwp = Basemap(llcrnrlon=9, urcrnrlon=18, llcrnrlat=46, urcrnrlat=50, resolution="c", ellps="WGS84")
    m_samos = Basemap(llcrnrlon=10, urcrnrlon=13, llcrnrlat=min_lat, urcrnrlat=48, ellps="WGS84", lat_0=center_lat, lon_0=center_lon)

    # Read preprocessed Info Files
    data_path = f"./data/get_available_data/gefs_pre_processed_forecast/{parser_dict['parameter']}/{parser_dict['date']}0000/"
    gribinfo_files = scandir.scandir(data_path, parameter=None, ending=".json")

    # Provide available NWP forecasts
    for json_info_filename in gribinfo_files:
        with open(json_info_filename) as json_file:
            gribfile_info = json.load(json_file)
            json_file.close()

        # Create required grids for NWP
        lons = [x - 0.5 for x in gribfile_info["lons"]]
        lats = [x - 0.5 for x in gribfile_info["lats"]]
        xx_nwp, yy_nwp = m_nwp(*np.meshgrid(lons, lats))

        # Create required meshgrid for spatialMOS
        lons_samos = np.linspace(min_lon, max_lon, alt.shape[1])
        lats_samos = np.linspace(max_lat, min_lat, alt.shape[0])
        xx_samos, yy_samos = m_samos(*np.meshgrid(lons_samos, lats_samos))

        # Read in preprocessed NWP CSV file with the predictions
        nwp_df = pd.read_csv(gribfile_info["gribfile_data_filename"])

        # Interpolation of NWP forecasts
        mean_interpolation = griddata(nwp_df[["lon", "lat"]], nwp_df["mean"], (xx_samos, yy_samos), method="linear")
        log_spread_interpolation = griddata(nwp_df[["lon", "lat"]], nwp_df["log_spread"], (xx_samos, yy_samos), method="linear")
        mean_interpolation_spatial_area = np.ma.masked_where(np.isnan(alt), mean_interpolation)
        log_spread_interpolation_spatial_area = np.ma.masked_where(np.isnan(alt), log_spread_interpolation)

        climate_samos_file = f"./data/spatialmos_climatology/gam/{parser_dict['parameter']}/climate_samos/yday_{gribfile_info['yday']:03d}_dayminute_{gribfile_info['dayminute']}.csv"
        climate_samos_nwp_file = f"./data/spatialmos_climatology/gam/{parser_dict['parameter']}/climate_samos_nwp/yday_{gribfile_info['yday']:03d}_dayminute_{gribfile_info['dayminute']}_step_{gribfile_info['step']:03d}.csv"

        # Check if climatologies files are available
        if not os.path.exists(climate_samos_file) or not os.path.exists(climate_samos_nwp_file):
            logging.error("parameter: %9s | step: %03d | missing '%s' or '%s'", parser_dict["parameter"], gribfile_info["step"], climate_samos_nwp_file, climate_samos_file)
            continue

        # Read in GAMLSS climatologies
        climate_samos = pd.read_csv(climate_samos_file, header=0, index_col=0)
        climate_samos_nwp = pd.read_csv(climate_samos_nwp_file, header=0, index_col=0)

        # Set dytypes to float
        cols = climate_samos.select_dtypes(exclude=["float"]).columns
        climate_samos[cols] = climate_samos[cols].apply(pd.to_numeric, downcast="float", errors="coerce")

        cols_nwp = climate_samos_nwp.select_dtypes(exclude=["float"]).columns
        climate_samos_nwp[cols_nwp] = climate_samos_nwp[cols_nwp].apply(pd.to_numeric, downcast="float", errors="coerce")

        # Set index of climate dataframes to lat, lon
        climate_samos = climate_samos.set_index(["lat", "lon"])
        climate_samos_nwp = climate_samos_nwp.set_index(["lat", "lon"])

        spatial_alt_area = pd.read_csv("./data/get_available_data/gadm/spatial_alt_area_df.csv", header=0, index_col=0)
        cols_samos = spatial_alt_area.select_dtypes(exclude=["float"]).columns
        spatial_alt_area[cols_samos] = spatial_alt_area[cols_samos].apply(pd.to_numeric, downcast="float", errors="coerce")
        spatial_alt_area = spatial_alt_area.set_index(["lat", "lon"])

        # Concate altitude and NWP und spatialMOS Dataframes to one big Dataframe
        samos = pd.concat([spatial_alt_area, climate_samos], axis=1, sort=True)
        samos = pd.concat([samos, climate_samos_nwp], axis=1, sort=True)
        samos = samos.loc[:, ~samos.columns.duplicated()]

        ## Reshape dataframe
        climate_fit = plot_functions.reshapearea(samos["climate_fit"], alt)
        climate_sd = plot_functions.reshapearea(samos["climate_sd"], alt)
        mean_fit = plot_functions.reshapearea(samos["mean_fit"], alt)
        mean_sd = plot_functions.reshapearea(samos["mean_sd"], alt)
        log_spread_fit = plot_functions.reshapearea(samos["log_spread_fit"], alt)
        log_spread_sd = plot_functions.reshapearea(samos["log_spread_sd"], alt)

        # Generate anomalies
        nwp_anom = (mean_interpolation_spatial_area.data - mean_fit) / mean_sd
        log_spread_nwp_anom = (log_spread_interpolation_spatial_area.data - log_spread_fit) / log_spread_sd

        # Check if samos coefficients are available
        samos_coef_file = f"./data/spatialmos_climatology/gam/{parser_dict['parameter']}/samos_coef/samos_coef_{parser_dict['parameter']}_{gribfile_info['step']:03d}.csv"
        if os.path.exists(samos_coef_file):
            samos_coef = pd.read_csv(samos_coef_file, sep=";", quoting=csv.QUOTE_NONNUMERIC)
        else:
            logging.error("There are no spatialMOS coefficients for the parameter %s and step %s available. '%s'", parser_dict["parameter"], gribfile_info["step"], samos_coef_file)
            continue

        # Generate samos spatial predictions
        samos_coef = samos_coef.apply(pd.to_numeric)
        samos_anom = samos_coef["intercept"][0] + samos_coef["mean_anom"][0] * nwp_anom
        samos_mean = samos_anom * climate_sd + climate_fit
        samos_log_anom_spread = samos_coef["intercept_log_spread"][0] + samos_coef["log_spread_anom"][0] * log_spread_nwp_anom
        samos_spread = np.exp(samos_log_anom_spread) * climate_sd

        # Round predicted values
        samos_mean = np.round(samos_mean, decimals=2)
        samos_spread = np.round(samos_spread, decimals=5)

        # Create filename for the plots for NWP and spatialMOS forecast maps
        path_filename_nwp_mean, filename_nwp_mean = plot_functions.plot_forecast(parser_dict["parameter"], m_nwp, xx_nwp, yy_nwp, \
            np.load(gribfile_info["grb_avg_filename"]), gribfile_info["anal_date_avg"], gribfile_info["valid_date_avg"], gribfile_info["step"], what="nwp_mean")
        path_filename_nwp_spread, filename_nwp_spread = plot_functions.plot_forecast(parser_dict["parameter"], m_nwp, xx_nwp, yy_nwp, \
            np.load(gribfile_info["grb_spr_filename"]), gribfile_info["anal_date_avg"], gribfile_info["valid_date_avg"], gribfile_info["step"], what="nwp_spread")
        path_filename_samos_mean, filename_samos_mean = plot_functions.plot_forecast(parser_dict["parameter"], m_samos, xx_samos, yy_samos, \
            samos_mean, gribfile_info["anal_date_avg"], gribfile_info["valid_date_avg"], gribfile_info["step"], what="samos_mean")
        path_filename_samos_spread, filename_samos_spread = plot_functions.plot_forecast(parser_dict["parameter"], m_samos, xx_samos, yy_samos, \
            samos_spread, gribfile_info["anal_date_avg"], gribfile_info["valid_date_avg"], gribfile_info["step"], what="samos_spread")

        # Consider Timezone
        timezone = pytz.timezone("UTC")
        anal_date_aware = timezone.localize(dt.datetime.strptime(gribfile_info["anal_date_avg"], "%Y-%m-%d %H:%M"))
        valid_date_aware = timezone.localize(dt.datetime.strptime(gribfile_info["anal_date_avg"], "%Y-%m-%d %H:%M"))

        # TODO adaptations to the django models
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
                                    "filename_nwp_mean": filename_nwp_mean,
                                    "path_filename_nwp_mean": path_filename_nwp_mean,
                                    "filename_nwp_spread": filename_nwp_spread, 
                                    "path_filename_nwp_spread": path_filename_nwp_spread,
                                    "filename_samos_mean": filename_samos_mean, 
                                    "path_filename_samos_mean": path_filename_samos_mean,
                                    "filename_samos_spread": filename_samos_spread,
                                    "path_filename_samos_spread": path_filename_samos_spread
                                    },
                                "SpatialMosPoint": 
                                    {
                                    "lat": yy_samos.flatten().tolist(), 
                                    "lon": xx_samos.flatten().tolist(), 
                                    "samos_mean": samos_mean.flatten().tolist(),
                                    "samos_spread": samos_spread.flatten().tolist()
                                    }
                                }

        with open(filename_spatialmos_step, "w") as f:
            json.dump(prediction_json_file, f)
            f.close()

        logging.info("parameter: %9s | anal_date: %s | valid_date: %s | step: %03d | %s", \
            prediction_json_file["SpatialMosRun"]["parameter"], prediction_json_file["SpatialMosRun"]["anal_date"], \
            prediction_json_file["SpatialMosStep"]["valid_date"], prediction_json_file["SpatialMosStep"]["step"], filename_spatialmos_step)



# Main
if __name__ == "__main__":
    STARTTIME = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    PARSER_DICT = spatial_parser.spatial_parser(parameter=True, name_parameter=["tmp_2m", "rh_2m", "wind_10m"], date=True)
    spatial_predictions(PARSER_DICT)
    logger_module.end_logging(STARTTIME)
