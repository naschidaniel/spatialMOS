#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import csv
import logging
import json
import numpy as np
import pandas as pd
from py_middleware import logger_module
from py_middleware import spatial_parser
from py_middleware import gribfile_to_pandasdf
from py_middleware import log_spread_calc


# Functions
def gribfiles_to_pandasdataframe(parser_dict):
    """This function converts the gribfiles into a CSV-File and an a Json-Filefile."""
    
    # Create an array with for the available steps
    available_steps = np.arange(6, 193, 6, int)
    # Read in files for U and V Component of wind at 10 m hight
    if parser_dict["parameter"] == "wind_10m":
        nwp_gribfiles_available_u_mean_steps, nwp_gribfiles_avalibel_u_spread_steps = gribfile_to_pandasdf.nwp_gribfiles_avalibel_steps("ugrd_10m", parser_dict["date"], available_steps)
        nwp_gribfiles_avalibel_v_mean_steps, nwp_gribfiles_avalibel_v_spread_steps = gribfile_to_pandasdf.nwp_gribfiles_avalibel_steps("vgrd_10m", parser_dict["date"], available_steps)

        nwp_files = zip(nwp_gribfiles_available_u_mean_steps, nwp_gribfiles_avalibel_u_spread_steps, nwp_gribfiles_avalibel_v_mean_steps, nwp_gribfiles_avalibel_v_spread_steps)
        for u_mean_file, u_spread_file, v_mean_file, v_spread_file in nwp_files:
            # Create folder structure
            path_nwp_forecasts = f"./data/get_available_data/gefs_avgspr_forecast_p1/{parser_dict['parameter']}/{parser_dict['date']}0000/"
            if not os.path.exists(path_nwp_forecasts):
                os.makedirs(path_nwp_forecasts)

            u_mean, anal_date_u_mean, valid_date_u_mean = gribfile_to_pandasdf.open_gribfile(u_mean_file)
            u_spread, anal_date_u_spread, valid_date_u_spread = gribfile_to_pandasdf.open_gribfile(u_spread_file)
            v_mean, anal_date_v_mean, valid_date_v_mean = gribfile_to_pandasdf.open_gribfile(v_mean_file)
            v_spread, anal_date_v_spread, valid_date_v_spread = gribfile_to_pandasdf.open_gribfile(v_spread_file)

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
    nwp_gribfiles_avalibel_mean_steps, nwp_gribfiles_avalibel_spread_steps = gribfile_to_pandasdf.nwp_gribfiles_avalibel_steps(parser_dict["parameter"], parser_dict["date"], available_steps)

    for nwp_gribfiles_mean_step, nwp_gribfiles_spread_step in zip(nwp_gribfiles_avalibel_mean_steps, nwp_gribfiles_avalibel_spread_steps):
        grb_avg, anal_date_avg, valid_date_avg = gribfile_to_pandasdf.open_gribfile(nwp_gribfiles_mean_step)
        grb_spr, anal_date_spr, valid_date_spr = gribfile_to_pandasdf.open_gribfile(nwp_gribfiles_spread_step)
        yday = grb_avg.validDate.timetuple().tm_yday
        dayminute = grb_avg.validDate.timetuple().tm_hour * 60
        step = grb_avg.startStep

        # Create required grids for NWP
        lons = np.linspace(float(grb_avg["longitudeOfFirstGridPointInDegrees"]), float(grb_avg["longitudeOfLastGridPointInDegrees"]), int(grb_avg["Ni"]))
        lats = np.linspace(float(grb_avg["latitudeOfFirstGridPointInDegrees"]), float(grb_avg["latitudeOfLastGridPointInDegrees"]), int(grb_avg["Nj"]))

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

        prediction_df = pd.DataFrame(df, columns=["mean", "log_spread", "lon", "lat"])

        data_path = f"./data/get_available_data/gefs_pre_processed_forecast/{parser_dict['parameter']}/{parser_dict['date']}0000/"
        if not os.path.exists(data_path):
            os.makedirs(data_path)
            logging.info("The folder '%s' was created", data_path)
        json_info_filename = os.path.join(data_path, f"GFSE_{parser_dict['date']}_0000_f{step:03d}_gribfile_info.json")
        gribfile_data_filename = os.path.join(data_path, f"GFSE_{parser_dict['date']}_0000_f{step:03d}_gribfile_data.csv")
        grb_avg_filename = os.path.join(data_path, f"GFSE_{parser_dict['date']}_0000_f{step:03d}_gribfile_avg")
        grb_spr_filename = os.path.join(data_path, f"GFSE_{parser_dict['date']}_0000_f{step:03d}_gribfile_spz")

        prediction_df.to_csv(gribfile_data_filename, index=False, quoting=csv.QUOTE_NONNUMERIC)
        logging.info("The infofile '%s' was written.", gribfile_data_filename)
        
        np.save(grb_avg_filename, grb_avg.values - constant_offset)
        logging.info("The grb_avg file '%s' was written.", f"{grb_avg_filename}.npy")
        np.save(grb_spr_filename, grb_spr.values)
        logging.info("The grb_avg file '%s' was written.", f"{grb_spr_filename}.npy")
        
        gribfile_info = {
            "parameter": parser_dict["parameter"],
            "anal_date_avg": anal_date_avg,
            "valid_date_avg": valid_date_avg,
            "grb_avg_filename": f"{grb_avg_filename}.npy",
            "grb_spr_filename": f"{grb_spr_filename}.npy",
            "yday": yday,
            "dayminute": dayminute,
            "step": step,
            "lons": lons.tolist(),
            "lats": lats.tolist(),
            "gribfile_data_filename": gribfile_data_filename
        }

        with open(json_info_filename, "w") as f:
            json.dump(gribfile_info, f)
            f.close()
        logging.info("The infofile '%s' was written.", json_info_filename)

        logging.info("The forecast for the parameter %s was saved in CSV format and the infofile was created.", parser_dict["parameter"], )

# Main
if __name__ == "__main__":
    STARTTIME = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    PARSER_DICT = spatial_parser.spatial_parser(parameter=True, name_parameter=["tmp_2m", "rh_2m", "wind_10m"], date=True)
    gribfiles_to_pandasdataframe(PARSER_DICT)
    logger_module.end_logging(STARTTIME)
