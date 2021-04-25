#!/usr/bin/python
# -*- coding: utf-8 -*-
'''spatial_util functions'''

import logging
from typing import Dict, Union
import numpy as np
import sys
import xarray as xr
import spatial_rust_util


def convert_measurements(measurements: Dict[str, Dict[str, Union[str, float]]], columns: list[str]):
    '''convert_measurements wraps the spatial_rust_util.convert_measurements function'''
    return spatial_rust_util.convert_measurements(measurements, columns)

def log_spread(spread):
    '''A function which is used to calculate the log value of the spread.'''
    log_spread_val = np.where(spread == 0., np.log(0.001), np.log(spread))
    return log_spread_val.round(3)

def gribfile_to_json(file_avg, file_spr, parameter, modeltype, subset):
    '''A function to open gribfiles and write out a json file'''
    with xr.open_dataset(file_avg, engine='cfgrib') as ds_avg, xr.open_dataset(file_spr, engine='cfgrib') as ds_spr: 
        tgt_lat = np.arange(subset['S'], subset['N'] + subset['resolution'], subset['resolution'])
        tgt_lon = np.arange(subset['W'], subset['E'] + subset['resolution'], subset['resolution'])

        ds_avg = ds_avg.sel(latitude = tgt_lat, longitude = tgt_lon)
        ds_spr = ds_spr.sel(latitude = tgt_lat, longitude = tgt_lon)

        if parameter not in ['tmp_2m', 'pres_sfc', 'spfh_2m', 'rh_2m']:
            raise ValueError(
                'The parameter \'%s\' cannot be processed.', parameter)

        if parameter == 'tmp_2m':
            data_avg = ds_avg['t2m'] - 273.15 # Corrections of Kelvin to Celsius
            data_spr = ds_spr['t2m']
            data_avg = np.round(data_avg.values.tolist(), 2)
            data_spr = np.round(data_spr.values.tolist(), 2)
        elif parameter == 'pres_sfc': # Pa
            data_avg = ds_avg['sp']
            data_spr = ds_spr['sp']
        elif parameter == 'spfh_2m': # kg/kg
            data_avg = ds_avg['q']
            data_spr = ds_spr['q']
        elif parameter == 'rh_2m': # %
            data_avg = ds_avg['r2']
            data_spr = ds_spr['r2']

        return {
            'parameter': parameter,
            'modeltype': modeltype,
            'anal_date': ds_avg.time.dt.strftime('%Y-%m-%d %H:%M:%S').values.tolist(),
            'valid_date': ds_avg.valid_time.dt.strftime('%Y-%m-%d %H:%M:%S').values.tolist(),
            'yday': ds_avg.valid_time.dt.dayofyear.values.tolist(),
            'dayminute': int(ds_avg.valid_time.dt.hour.values * ds_avg.valid_time.dt.minute.values),
            'step': int(ds_avg.step.values / (3.6*10**12)),
            'latitude': ds_avg.latitude.values.tolist(),
            'longitude': ds_avg.longitude.values.tolist(),
            'data_avg': data_avg,
            'data_spr': data_spr,
        }
