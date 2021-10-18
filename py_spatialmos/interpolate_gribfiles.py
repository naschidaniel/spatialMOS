#!/usr/bin/env python
# coding: utf-8
''' With this Python script the downloaded gribfiles can be interpolated to station locations.'''

import json
import os
from pathlib import Path
from typing import Any, Dict
import spatial_rust_util
from .spatial_util.spatial_writer import SpatialWriter

PARAMETERS = {'anal_data': {'name': 'anal_data', 'unit': '[UTC]'},
              'valid_data': {'name': 'valid_data', 'unit': '[UTC]'},
              'yday': {'name': 'yday', 'unit': '[Integer]'},
              'step': {'name': 'step', 'unit': '[Integer]'},
              'lon': {'name': 'lon', 'unit': '[angle Degree]'},
              'lat': {'name': 'lat', 'unit': '[angle Degree]'},
              'spread': {'name': 'spread', 'unit': '[Degree C]'},
              'mean': {'name': 'mean', 'unit': '[Degree C]'}}


def run_interpolate_gribfiles(parser_dict: Dict[str, Any]):
    '''run_interpolate_gribfiles is used to start the interpolation and create the folder structure'''

    gribfiles_path = Path(
        f"./data/get_available_data/gefs_avgspr_forecast_p05/{parser_dict['parameter']}")

    interpolated_data_path = Path(
        f"./data/get_available_data/interpolated_station_forecasts/{parser_dict['parameter']}")
    os.makedirs(interpolated_data_path, exist_ok=True)
    for file in interpolated_data_path.glob('*.csv'):
        os.unlink(file)

    # TODO get a set of stations from lwd, suedtirol and zamg
    station_locations = [[11.35, 47.25],
                         [11.38, 47.25],
                         [10.31, 46.98],
                         [11.75, 47.38]]
    for step in [f'{s:03d}' for s in range(6, 192+1, 6)]:
        target = interpolated_data_path.joinpath(f"GFSE_f{step}.csv")
        gribfiles_json_path = sorted(gribfiles_path.glob(f'**/*{step}.json'))
        with open(target, mode='a', encoding='utf-8') as f:
            csv_writer = SpatialWriter(PARAMETERS, f)
            for json_file in gribfiles_json_path:
                with open(json_file, mode='r', encoding='utf-8') as f:
                    gribdata = json.load(f)
                interpolate_gribfiles(gribdata, csv_writer, station_locations)


def interpolate_gribfiles(gribdata: Dict[str, Any], csv_writer: SpatialWriter, station_locations: list[list[float]]):
    '''interpolate_gribfiles interpolates gribfiles to stations locations'''
    interpolated_data = spatial_rust_util.interpolate_gribdata(
        gribdata['latitude'], gribdata['longitude'], gribdata['values_avg'], gribdata['values_spr'], station_locations)
    for row in interpolated_data:
        csv_writer.append([gribdata['anal_date'], gribdata['valid_date'],
                           gribdata['yday'], gribdata['step'], row[0], row[1], row[2], row[3]])
