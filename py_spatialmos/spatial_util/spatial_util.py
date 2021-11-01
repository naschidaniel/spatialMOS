#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''spatial_util functions'''

from typing import Dict, Union
import numpy as np
import xarray as xr
import spatial_rust_util


def convert_measurements(measurements: Dict[str, Dict[str, Union[str, float]]], columns: list[str]):
    '''convert_measurements wraps the spatial_rust_util.convert_measurements function'''
    return spatial_rust_util.convert_measurements(measurements, columns)


def gribfiles_to_json(file_avg, file_spr, parameter, subset):
    '''A function to open gribfiles and write out a json file'''
    with xr.open_dataset(file_avg, engine='cfgrib') as ds_avg, xr.open_dataset(file_spr, engine='cfgrib') as ds_spr:
        latitude = np.arange(subset['S'], subset['N'] + subset['resolution'], subset['resolution'])
        longitude = np.arange(subset['W'], subset['E'] + subset['resolution'], subset['resolution'])

        ds_avg = ds_avg.sel(latitude = latitude, longitude = longitude)
        ds_spr = ds_spr.sel(latitude = latitude, longitude = longitude)

        if parameter not in ['tmp_2m', 'pres_sfc', 'spfh_2m', 'rh_2m', 'ugrd_10m', 'vgrd_10m']:
            raise ValueError(
                'The parameter \'%s\' cannot be processed.' % parameter)

        if parameter == 'tmp_2m':
            values_avg = ds_avg['t2m'] - 273.15 # Corrections of Kelvin to Celsius
            values_spr = ds_spr['t2m']
            values_avg = np.round(values_avg.values.tolist(), 2)
            values_spr = np.round(values_spr.values.tolist(), 2)
        elif parameter == 'pres_sfc': # Pa
            values_avg = ds_avg['sp']
            values_spr = ds_spr['sp']
        elif parameter == 'spfh_2m': # kg/kg
            values_avg = ds_avg['q']
            values_spr = ds_spr['q']
        elif parameter == 'ugrd_10m': # m/s
            values_avg = ds_avg['u10']
            values_spr = ds_spr['u10']
            values_avg = np.round(values_avg.values.tolist(), 2)
            values_spr = np.round(values_spr.values.tolist(), 2)
        elif parameter == 'vgrd_10m': # m/s
            values_avg = ds_avg['v10']
            values_spr = ds_spr['v10']
            values_avg = np.round(values_avg.values.tolist(), 2)
            values_spr = np.round(values_spr.values.tolist(), 2)
        elif parameter == 'rh_2m': # %
            values_avg = ds_avg['r2']
            values_spr = ds_spr['r2']
            values_avg = np.round(values_avg.values.tolist(), 2)
            values_spr = np.round(values_spr.values.tolist(), 2)
        values_avg = [list(el) for el in values_avg]
        values_spr = [list(el) for el in values_spr]
        
        data = spatial_rust_util.combine_gribdata(list(latitude), list(longitude), values_avg, values_spr)
        return {
            'parameter': parameter,
            'anal_date': ds_avg.time.dt.strftime('%Y-%m-%d %H:%M:%S').values.tolist(),
            'valid_date': ds_avg.valid_time.dt.strftime('%Y-%m-%d %H:%M:%S').values.tolist(),
            'yday': ds_avg.valid_time.dt.dayofyear.values.tolist(),
            'dayminute': int(ds_avg.valid_time.dt.hour.values) * 60, # * ds_avg.valid_time.dt.minute.values),
            'step': int(ds_avg.step.values / (3.6*10**12)),
            'latitude': ds_avg.latitude.values.tolist(),
            'longitude': ds_avg.longitude.values.tolist(),
            'resolution': subset['resolution'],
            'values_avg': values_avg,
            'values_spr': values_spr,
            'data_columns': ['latitude', 'longitude', 'spread', 'log_spread', 'mean'],
            'data': data,
        }
