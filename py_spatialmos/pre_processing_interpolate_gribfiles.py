#!/usr/bin/env python
# coding: utf-8
''' With this Python script the downloaded gribfiles can be interpolated to station locations.'''

from datetime import datetime as dt
import json
import os
import pathlib
import spatial_rust_util
from .spatial_util.spatial_writer import SpatialWriter

PARAMETERS = {'year': {'name': 'year', 'unit': '[Integer]'},
              'yday': {'name': 'yday', 'unit': '[Integer]'},
              'step': {'name': 'step', 'unit': '[Integer]'},
              'lon': {'name': 'lon', 'unit': '[angle Degree]'},
              'lat': {'name': 'lat', 'unit': '[angle Degree]'},
              'alt': {'name': 'alt', 'unit': '[m]'},
              'mean': {'name': 'mean', 'unit': '[Degree C]'},
              'spread': {'name': 'mean', 'unit': '[Degree C]'}}


def run_interpolate_gribfiles(parser_dict):
    '''run_interpolate_gribfiles is used to start the interpolation to the stations locations'''

    station_locations = [[11.35, 47.25],
                         [11.38, 47.25],
                         [10.31, 46.98],
                         [11.75, 47.38]]

    gribfiles_path = pathlib.Path(
        f"./data/get_available_data/gefs_avgspr_forecast_p05/{parser_dict['parameter']}")

    interpolated_data_path = pathlib.Path(
        f"./data/get_available_data/interpolated_station_forecasts/{parser_dict['parameter']}")
    os.makedirs(interpolated_data_path, exist_ok=True)
    for file in interpolated_data_path.glob('*.csv'):
        os.unlink(file)

    for step in [f'{s:03d}' for s in range(6, 192+1, 6)]:
        targetfile_path = interpolated_data_path.joinpath(
            f"GFSE_f{step}.csv")
        with open(targetfile_path, mode='a') as f:
            csv_writer = SpatialWriter(PARAMETERS, f)

            for gribfile_json_path in sorted(gribfiles_path.glob(f'**/*{step}.json')):
                with open(gribfile_json_path) as f:
                    gribdata = json.load(f)
                valid_date_str = dt.strptime(
                    gribdata['anal_date'], '%Y-%m-%d %H:%M:%S')
                interpolated_data = spatial_rust_util.interpolate_gribdata(
                    gribdata['latitude'], gribdata['longitude'], gribdata['values_avg'], gribdata['values_spr'], station_locations)

                for row in interpolated_data:
                    csv_writer.append([valid_date_str.strftime(
                        '%Y'), gribdata['yday'], gribdata['step'], 'alt', row[0], row[1], row[2], row[3]])
