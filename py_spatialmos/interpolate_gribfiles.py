#!/usr/bin/env python3
# coding: utf-8
''' With this Python script the downloaded gribfiles can be interpolated to station locations.'''

import csv
import json
import logging
import os
from pathlib import Path
import pathlib
from typing import Any, Dict
import spatial_rust_util
from .spatial_util.spatial_writer import SpatialWriter



def run_interpolate_gribfiles(parser_dict: Dict[str, Any]):
    '''run_interpolate_gribfiles is used to start the interpolation and create the folder structure'''

    gribfiles_path = Path(
        f"./data/get_available_data/gefs_avgspr_forecast_p05/{parser_dict['parameter']}")

    interpolated_data_path = Path(
        f"./data/get_available_data/interpolated_station_forecasts/{parser_dict['parameter']}")
    os.makedirs(interpolated_data_path, exist_ok=True)
    for file in interpolated_data_path.glob('*.csv'):
        os.unlink(file)

    station_locations = []
    for provider in ['lwd_stations', 'suedtirol_stations', 'zamg_stations']:
        station_files = pathlib.Path(f"./data/get_available_data/measurements/combined/").glob(f"{provider}_{parser_dict['parameter']}*.csv")
        for file in station_files:
            with open(file, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                next(reader) # skip header
                next(reader) # skip units
                for row in reader:
                    station_locations.append([float(row[0]), float(row[1])])
        if len(station_locations) <= 0:
            raise RuntimeError

    for step in [f'{s:03d}' for s in range(6, 192+1, 6)]:
        target = interpolated_data_path.joinpath(f"GFSE_f{step}.csv")
        gribfiles_json_path = sorted(gribfiles_path.glob(f'**/*{step}.json'))
        with open(target, mode='a', encoding='utf-8') as f:
            parameters = {'anal_data': {'name': 'anal_data', 'unit': '[UTC]'},
                'valid_data': {'name': 'valid_data', 'unit': '[UTC]'},
                'yday': {'name': 'yday', 'unit': '[Integer]'},
                'dayminute': {'name': 'dayminute', 'unit': '[Integer]'},
                'step': {'name': 'step', 'unit': '[Integer]'},
                'lon': {'name': 'lon', 'unit': '[angle Degree]'},
                'lat': {'name': 'lat', 'unit': '[angle Degree]'},
                'spread': {'name': 'spread', 'unit': '[Degree C]'},
                'log_spread': {'name': 'log_spread', 'unit': '[Degree C]'},
                'mean': {'name': 'mean', 'unit': '[Degree C]'}}

            if parser_dict['parameter'] == 'rh_2m':
                parameters['spread']['unit'] = '[Percent]'
                parameters['log_spread']['unit'] = '[Percent]'
                parameters['mean']['unit'] = '[Percent]'

            csv_writer = SpatialWriter(parameters, f)
            for json_file in gribfiles_json_path:
                logging.info('Interpolation \'%s\'', json_file)
                try:
                    with open(json_file, mode='r', encoding='utf-8') as f:
                        gribdata = json.load(f)
                except:
                    logging.error('Problems while loading the file \'%s\'', json_file)
                    continue
                interpolate_gribfiles(gribdata, csv_writer, station_locations)


def interpolate_gribfiles(gribdata: Dict[str, Any], csv_writer: SpatialWriter, station_locations: list[list[float]]):
    '''interpolate_gribfiles interpolates gribfiles to stations locations'''
    interpolated_data = spatial_rust_util.interpolate_gribdata(
        gribdata['latitude'], gribdata['longitude'], gribdata['values_avg'], gribdata['values_spr'], station_locations)
    for row in interpolated_data:
        # lon = row[0] lat = row[1] spr = row[2] log_spr = row[3] mean = row[4]
        csv_writer.append([gribdata['anal_date'], gribdata['valid_date'],
                           gribdata['yday'], gribdata['dayminute'], gribdata['step'], row[0], row[1], row[2], row[3], row[4]])
