#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from typing import List, Union
import numpy as np
import xarray as xr
from py_middleware import log_spread_calc

# Functions
def available_files(path_nwp_forecasts, avg_spr, available_steps, parameter):
    """A function to determine the available files."""
    nwp_gribfiles_available_steps: List[Union[bytes, str]] = []
    for dirpath, subdirs, files in os.walk(path_nwp_forecasts):
        for file in files:
            for step in available_steps:          
                if os.path.splitext(file)[1] not in ".grb2":
                    continue

                searchstring = None
                if avg_spr == "mean":
                    searchstring = "_avg_f{:03d}".format(step)
                elif avg_spr == "spread":
                    searchstring = "_spr_f{:03d}".format(step)

                if searchstring in file:
                    nwp_gribfiles_available_steps.append(os.path.join(dirpath, file))
                else:
                    continue

    if nwp_gribfiles_available_steps == []:
        logging.error("parameter: {:8} | available Files: {} | {} | {}".format(parameter, len(nwp_gribfiles_available_steps), avg_spr, path_nwp_forecasts))
        sys.exit(1)
    else:
        logging.info("parameter: {:8} | available Files: {} | {} | {}".format(parameter, len(nwp_gribfiles_available_steps), avg_spr, path_nwp_forecasts))

    return sorted(nwp_gribfiles_available_steps)


def nwp_gribfiles_avalibel_steps(parameter, date, resolution, available_steps):
    """A function which returns the available files as array"""
    path_nwp_forecasts = f"./data/get_available_data/gefs_avgspr_forecast_{resolution}/{parameter}/{date}0000/"
    return available_files(path_nwp_forecasts, "mean", available_steps, parameter), available_files(path_nwp_forecasts, "spread", available_steps, parameter)


def open_gribfile(file, parameter, avgspr, info=False):
    """A function to open gribfiles"""
    with xr.open_dataset(file, engine='cfgrib') as ds:
        if parameter == "tmp_2m" and avgspr == "avg":
            ds["mean"] = ds["t2m"] - 273.15 # Corrections of the values
        elif parameter == "tmp_2m" and avgspr == "spr":
            ds["spread"] = ds["t2m"]
        else:
            logging.error("The parameter '%s' cannot be unpacked from the xarray", parameter)
            sys.exit(1)

        # Dataset to pandas dataframe
        df = ds.to_dataframe()
                
        if avgspr == "spr":
            df["log_spread"] = log_spread_calc.log_spread(df["spread"]) 

        # Drop unused columns
        keep = set(df.columns) - (set(df.columns) - set(["mean", "log_spread"]))
        df = df[keep]

        # numpy array of predictions
        np_array = []
        if avgspr == "avg":
            np_array = ds["mean"].values
        elif avgspr == "spr":
            np_array = ds["spread"].values

        # Return values
        if not info:
            return df, np_array
        else:
            info_dict = {
                        "anal_date": ds.time.dt.strftime("%Y-%m-%d %H:%M").values.tolist(), 
                        "valid_date": ds.valid_time.dt.strftime("%Y-%m-%d %H:%M").values.tolist(), 
                        "step": int(ds.step.values / (3.6*10**12)),
                        "latitude": ds.latitude.values.tolist(), 
                        "longitude": ds.longitude.values.tolist(),
                        "dayminute": int(ds.valid_time.dt.hour.values * 60),
                        "yday": ds.valid_time.dt.dayofyear.values.tolist(),
                        }
            return df, np_array, info_dict
