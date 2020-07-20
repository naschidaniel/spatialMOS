#!/usr/bin/python
# -*- coding: utf-8 -*-
""" A script for generating surface forecasts based on GEFS predictions and GAMLSS climatologies."""

import os
import json
import csv
import logging
import pytz
import numpy as np
import pandas as pd
from osgeo import gdal
from scipy.interpolate import griddata
from py_middleware import logger_module
from py_middleware import spatial_parser
from py_middleware import spatial_predictions as pf
from py_middleware import log_spread_calc

# Import Basemap
os.environ["PROJ_LIB"] = "/usr/share/proj"
from mpl_toolkits.basemap import Basemap

# Functions
def spatial_predictions(parser_dict):
    """The main function to create surface forecasts based on GEFS forecasts and GAMLSS climatologies."""

    # Create folder structure
    data_path_spool = "./spool/{}/samos/".format(parser_dict["parameter"])
    if not os.path.exists(data_path_spool):
        os.makedirs(data_path_spool)

    # Create an array with for the available steps
    available_steps = np.arange(6, 193, 6, int)

    spatial_alt_area = gdal.Open("./data/get_available_data/gadm/spatial_alt_area.grd")
    alt = spatial_alt_area.ReadAsArray()
    width = spatial_alt_area.RasterXSize
    height = spatial_alt_area.RasterYSize
    geo_transform = spatial_alt_area.GetGeoTransform()
    min_lon = geo_transform[0]
    min_lat = geo_transform[3] + width * geo_transform[4] + height * geo_transform[5]
    max_lon = geo_transform[0] + width * geo_transform[1] + height * geo_transform[2]
    max_lat = geo_transform[3]
    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2

    # BASEMAPS for GEFS predictions and spatialMOS
    m_nwp = Basemap(llcrnrlon=9, urcrnrlon=18, llcrnrlat=46, urcrnrlat=50, resolution="c", ellps="WGS84")
    m_samos = Basemap(llcrnrlon=10, urcrnrlon=13, llcrnrlat=min_lat, urcrnrlat=48, ellps="WGS84", lat_0=center_lat, lon_0=center_lon)

    # Read in files for U and V Component of wind at 10 m hight
    if parser_dict["parameter"] == "wind_10m":
        nwp_gribfiles_available_u_mean_steps, nwp_gribfiles_avalibel_u_spread_steps = pf.nwp_gribfiles_avalibel_steps("ugrd_10m", parser_dict["date"], available_steps)
        nwp_gribfiles_avalibel_v_mean_steps, nwp_gribfiles_avalibel_v_spread_steps = pf.nwp_gribfiles_avalibel_steps("vgrd_10m", parser_dict["date"], available_steps)

        nwp_files = zip(nwp_gribfiles_available_u_mean_steps, nwp_gribfiles_avalibel_u_spread_steps, nwp_gribfiles_avalibel_v_mean_steps, nwp_gribfiles_avalibel_v_spread_steps)
        for u_mean_file, u_spread_file, v_mean_file, v_spread_file in nwp_files:
            # Create folder structure
            path_nwp_forecasts = f"./data/get_available_data/gefs_forecast/{parser_dict['parameter']}/{parser_dict['date']}0000/"
            if not os.path.exists(path_nwp_forecasts):
                os.makedirs(path_nwp_forecasts)

            u_mean, anal_date_u_mean, valid_date_u_mean = pf.open_gribfile(u_mean_file)
            u_spread, anal_date_u_spread, valid_date_u_spread = pf.open_gribfile(u_spread_file)
            v_mean, anal_date_v_mean, valid_date_v_mean = pf.open_gribfile(v_mean_file)
            v_spread, anal_date_v_spread, valid_date_v_spread = pf.open_gribfile(v_spread_file)

            wind_10m = pd.DataFrame()
            wind_10m_spread = pd.DataFrame()
            wind_10m["values"] = np.sqrt(u_mean["values"] ** 2 + v_mean["values"] ** 2)
            wind_10m_spread["values"] = np.sqrt(u_spread["values"] ** 2 + v_spread["values"] ** 2)

            wind_mean_file = u_mean_file[u_mean_file.rfind("/")+1:]
            wind_spread_file = u_spread_file[u_spread_file.rfind("/")+1:]

            wind_10m_mean = wind_10m.tostring()
            wind_10m_spread = wind_10m_spread.tostring()

            file_mean = os.path.join(path_nwp_forecasts, wind_mean_file)
            file_spread = os.path.join(path_nwp_forecasts, wind_spread_file)

            grbout_mean = open(file_mean, "wb")
            grbout_mean.write(wind_10m_mean)
            grbout_mean.close()

            grbout_spread = open(file_spread, "wb")
            grbout_spread.write(wind_10m_spread)
            grbout_spread.close()

    # Provide available NWP forecasts
    nwp_gribfiles_avalibel_mean_steps, nwp_gribfiles_avalibel_spread_steps = pf.nwp_gribfiles_avalibel_steps(parser_dict["parameter"], parser_dict["date"], available_steps)

    for nwp_gribfiles_mean_step, nwp_gribfiles_spread_step in zip(nwp_gribfiles_avalibel_mean_steps, nwp_gribfiles_avalibel_spread_steps):
        grb_avg, anal_date_avg, valid_date_avg = pf.open_gribfile(nwp_gribfiles_mean_step)
        grb_spr, anal_date_spr, valid_date_spr = pf.open_gribfile(nwp_gribfiles_spread_step)
        yday = grb_avg.validDate.timetuple().tm_yday
        dayminute = grb_avg.validDate.timetuple().tm_hour * 60
        step = grb_avg.startStep

        # Create required grids for NWP
        lons = np.linspace(float(grb_avg["longitudeOfFirstGridPointInDegrees"]), float(grb_avg["longitudeOfLastGridPointInDegrees"]), int(grb_avg["Ni"]))
        lats = np.linspace(float(grb_avg["latitudeOfFirstGridPointInDegrees"]), float(grb_avg["latitudeOfLastGridPointInDegrees"]), int(grb_avg["Nj"]))
        xx_nwp, yy_nwp = m_nwp(*np.meshgrid(lons - 0.5, lats - 0.5))

        # Create required meshgrid for spatialMOS
        lons_linespace = np.linspace(min_lon, max_lon, alt.shape[1])
        lats_linespace = np.linspace(max_lat, min_lat, alt.shape[0])

        xx_samos, yy_samos = m_samos(*np.meshgrid(lons_linespace, lats_linespace))

        # Corrections of the values
        if parser_dict["parameter"] == "tmp_2m":
            constant_offset = 273.15
        else:
            constant_offset = 0

        df = []
        for lon in lons:
            for lat in lats:
                mean = grb_avg.data(lat1=lat, lon1=lon)
                mean = round(mean[0][0][0] - constant_offset, 2)
                spread = grb_spr.data(lat1=lat, lon1=lon)
                log_spread = log_spread_calc.log_spread(spread[0][0][0])
                df.append([mean, log_spread, lon, lat])

        nwp_df = pd.DataFrame(df, columns=["mean", "log_spread", "lon", "lat"])

        # Interpolation of NWP forecasts
        mean_interpolation = griddata(nwp_df[["lon", "lat"]], nwp_df["mean"], (xx_samos, yy_samos), method="linear")
        log_spread_interpolation = griddata(nwp_df[["lon", "lat"]], nwp_df["log_spread"], (xx_samos, yy_samos), method="linear")
        mean_interpolation_spatial_area = np.ma.masked_where(np.isnan(alt), mean_interpolation)
        log_spread_interpolation_spatial_area = np.ma.masked_where(np.isnan(alt), log_spread_interpolation)

        climate_samos_file = f"./data/spatialmos_climatology/gam/{parser_dict['parameter']}/climate_samos/yday_{yday:03d}_dayminute_{dayminute}.feather"
        climate_samos_nwp_file = f"./data/spatialmos_climatology/gam/{parser_dict['parameter']}/climate_samos_nwp/yday_{yday:03d}_dayminute_{dayminute}_step_{step:03d}.feather"

        # Check if climatologies files are available
        if not os.path.exists(climate_samos_file) or not os.path.exists(climate_samos_nwp_file):
            logging.error("parameter: %9s | step: %03d | missing '%s' or '%s'", parser_dict["parameter"], step, climate_samos_nwp_file, climate_samos_file)
            continue

        # Read in GAMLSS climatologies
        climate_samos = pd.read_feather(climate_samos_file)
        climate_samos_nwp = pd.read_feather(climate_samos_nwp_file)

        # Set dytypes to float
        cols = climate_samos.select_dtypes(exclude=["float"]).columns
        climate_samos[cols] = climate_samos[cols].apply(pd.to_numeric, downcast="float", errors="coerce")

        cols_nwp = climate_samos_nwp.select_dtypes(exclude=["float"]).columns
        climate_samos_nwp[cols_nwp] = climate_samos_nwp[cols_nwp].apply(pd.to_numeric, downcast="float", errors="coerce")

        # Set index of climate dataframes to lat, lon
        climate_samos = climate_samos.set_index(["lat", "lon"])
        climate_samos_nwp = climate_samos_nwp.set_index(["lat", "lon"])

        spatial_alt_area = pd.read_feather("./data/get_available_data/gadm/spatial_alt_area_df.feather")
        cols_samos = spatial_alt_area.select_dtypes(exclude=["float"]).columns
        spatial_alt_area[cols_samos] = spatial_alt_area[cols_samos].apply(pd.to_numeric, downcast="float", errors="coerce")
        spatial_alt_area = spatial_alt_area.set_index(["lat", "lon"])

        # Concate altitude and NWP und spatialMOS Dataframes to one big Dataframe
        samos = pd.concat([spatial_alt_area, climate_samos], axis=1, sort=True)
        samos = pd.concat([samos, climate_samos_nwp], axis=1, sort=True)
        samos = samos.loc[:, ~samos.columns.duplicated()]

        ## Reshape dataframe
        climate_fit = pf.reshapearea(samos["climate_fit"], alt)
        climate_sd = pf.reshapearea(samos["climate_sd"], alt)
        mean_fit = pf.reshapearea(samos["mean_fit"], alt)
        mean_sd = pf.reshapearea(samos["mean_sd"], alt)
        log_spread_fit = pf.reshapearea(samos["log_spread_fit"], alt)
        log_spread_sd = pf.reshapearea(samos["log_spread_sd"], alt)

        # Generate anomalies
        nwp_anom = (mean_interpolation_spatial_area.data - mean_fit) / mean_sd
        log_spread_nwp_anom = (log_spread_interpolation_spatial_area.data - log_spread_fit) / log_spread_sd

        # Check if samos coefficients are available
        samos_coef_file = f"./data/spatialmos_climatology/gam/{parser_dict['parameter']}/samos_coef/samos_coef_{parser_dict['parameter']}_{step:03d}.csv"
        if os.path.exists(samos_coef_file):
            samos_coef = pd.read_csv(samos_coef_file, sep=";", quoting=csv.QUOTE_NONNUMERIC)
        else:
            logging.error("There are no spatialMOS coefficients for the parameter %s and step %s available. '%s'", parser_dict["parameter"], step, samos_coef_file)
            continue

        # Generate samos spatial predictions
        samos_coef = samos_coef.apply(pd.to_numeric)
        samos_anom = samos_coef["intercept"][0] + samos_coef["mean_anom"][0] * nwp_anom
        samos_pred = samos_anom * climate_sd + climate_fit
        samos_log_anom_spread = samos_coef["intercept_log_spread"][0] + samos_coef["log_spread_anom"][0] * log_spread_nwp_anom
        samos_pred_spread = np.exp(samos_log_anom_spread) * climate_sd

        # Round predicted values
        samos_pred = np.round(samos_pred, decimals=2)
        samos_pred_spread = np.round(samos_pred_spread, decimals=5)

        # Create filename for the plots for NWP and spatialMOS forecast maps
        figname_nwp = pf.plot_forecast(parser_dict["parameter"], m_nwp, xx_nwp, yy_nwp, grb_avg.values - constant_offset, anal_date_avg, valid_date_avg, grb_avg.analDate, step, what="nwp_mean")
        figname_nwp_sd = pf.plot_forecast(parser_dict["parameter"], m_nwp, xx_nwp, yy_nwp, grb_spr.values, anal_date_avg, valid_date_avg, grb_avg.analDate, step, what="nwp_spread")
        figname_samos = pf.plot_forecast(parser_dict["parameter"], m_samos, xx_samos, yy_samos, samos_pred, anal_date_avg, valid_date_avg, grb_avg.analDate, step, what="samos_mean")
        figname_samos_sd = pf.plot_forecast(parser_dict["parameter"], m_samos, xx_samos, yy_samos, samos_pred_spread, anal_date_avg, valid_date_avg, grb_avg.analDate, step, what="samos_spread")

        timezone = pytz.timezone("UTC")
        anal_date_aware = timezone.localize(grb_avg.analDate)
        valid_date_aware = timezone.localize(grb_avg.validDate)

        # TODO adaptations to the django models
        prediction_json_file = {"Modellauf": {"analDate": anal_date_aware.strftime("%Y-%m-%d %H:%M"), "parameter": parser_dict["parameter"]}, \
                                "VorhersageStep": {"validDate": valid_date_aware.strftime("%Y-%m-%d %H:%M"), "step": step, "fig_nwp": figname_nwp, "fig_nwp_sd": figname_nwp_sd, "fig_samos": figname_samos, "fig_samos_sd": figname_samos_sd}, \
                                "points": {"lat": yy_samos.flatten().tolist(), "lon": xx_samos.flatten().tolist(), "samos_mean": samos_pred.flatten().tolist(), "samos_spread": samos_pred_spread.flatten().tolist()}}

        prediction_filename = os.path.join(data_path_spool, "{}_step_{:03d}.json".format(anal_date_aware.strftime("%Y%m%d%H%M"), step))
        with open(prediction_filename, "w") as f:
            json.dump(prediction_json_file, f)
            f.close()

        logging.info("parameter: %9s | analDate: %s | validDate: %s | step: %03d | %s", \
            prediction_json_file["Modellauf"]["parameter"], prediction_json_file["Modellauf"]["analDate"], \
            prediction_json_file["VorhersageStep"]["validDate"], prediction_json_file["VorhersageStep"]["step"], prediction_filename)



# Main
if __name__ == "__main__":
    STARTTIME = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    PARSER_DICT = spatial_parser.spatial_parser(parameter=True, name_parameter=["tmp_2m", "rh_2m", "wind_10m"], date=True)
    spatial_predictions(PARSER_DICT)
    logger_module.end_logging(STARTTIME)
