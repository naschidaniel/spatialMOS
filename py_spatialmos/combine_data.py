#!/usr/bin/python
# -*- coding: utf-8 -*-
'''A script to combine data from get_lwd_data, get_suedtirol_data and get_zamg_data'''

import csv
from io import TextIOWrapper
import logging
import os
from pathlib import Path
from typing import Any, Dict, TextIO
from . import get_lwd_data
from . import get_suedtirol_data
from . import get_zamg_data
from .spatial_util import spatial_writer



def run_combine_data(parser_dict: Dict[str, Any]):
    '''run_combine_data runs combine_data'''
    target_path = Path("./data/get_available_data/measurements/")
    os.makedirs(target_path, exist_ok=True)
    targetfile = Path(target_path).joinpath(f"{parser_dict['folder']}_measurements.csv")
    with open(targetfile, mode='w') as target:
        if parser_dict['folder'] == 'lwd':
            parameters = get_lwd_data.LwdData.parameters()
        elif parser_dict['folder'] == 'suedtirol':
            parameters = get_suedtirol_data.SuedtirolData.parameters()
        elif parser_dict['folder'] == 'zamg':
            parameters = get_zamg_data.ZamgData.parameters()
        else:
            raise RuntimeError('The run_combine_data is for the folder \'%s\' is not implemented' % parser_dict['folder'])

        csv_files_path = Path(f"./data/get_available_data/{parser_dict['folder']}")
        combine_data(csv_files_path, parameters, target)

    for parameter in ['tmp_2m', 'rh_2m']:
        targetfile_parameter = Path(target_path).joinpath(f"{parser_dict['folder']}_measurements_{parameter}.csv")
        targetfile_stations = Path(target_path).joinpath(f"{parser_dict['folder']}_stations_{parameter}.csv")
        with open(targetfile_parameter, mode='w') as target_parameter, open(targetfile_stations, mode='w') as target_stations:
            data_for_spatialmos(targetfile, parameters, parameter, target_parameter, target_stations)

def combine_data(csv_files_path: Path, parameters: Dict[str, Dict[str, str]], target: TextIO):
    '''combine_data creates one csv file with all the data from one dataprovider'''
    parameters_keys = list(parameters.keys())
    parameters_units = [parameters[k]['unit'] for k in parameters]

    writer = spatial_writer.SpatialWriter(parameters, target)
    for csv_file in csv_files_path.glob('**/*.csv'):
        logging.info('The file %s is added to %s', csv_file, target)
        with open(csv_file) as f:
            data = list(csv.reader(f, delimiter=';'))
        if data[0] != parameters_keys and data[1] != parameters_units:
            raise RuntimeError(
                'The header in the file %s is not supported' % csv_file)
        writer.appendrows(data[2:])

def data_for_spatialmos(file: Path, parameters: Dict[str, Dict[str, str]], parameter: str, target_parameter: TextIO, target_stations: TextIO):
    '''get_station_locations extracts the station locations for a parameter'''
    header_parameter = {'date': {'name': 'date', 'unit': '[UTC]'},
                        'alt': {'name': 'alt', 'unit': '[m]'},
                        'lon': {'name': 'lon', 'unit': '[angle Degree]'},
                        'lat': {'name': 'lat', 'unit': '[angle Degree]'}}

    parameters_names = [parameters[k]['name'] for k in list(parameters.keys())]

    date_index = parameters_names.index('name')
    alt_index = parameters_names.index('alt')
    lon_index = parameters_names.index('lon')
    lat_index = parameters_names.index('lat')

    if parameter == 'tmp_2m':
        header_parameter.update({'t': {'name': 't', 'unit': '[Degree C]'}})
        value_index = parameters_names.index('t')
    elif parameter == 'rh_2m':
        header_parameter.update({'rf': {'name': 'rf', 'unit': '[Percent]'}})
        value_index = parameters_names.index('rf')

    with open(file) as f:
        data = list(csv.reader(f, delimiter=';'))

    writer_parameter = spatial_writer.SpatialWriter(header_parameter, target_parameter)
    station_locations = set()
    for row in data[2:]:
        writer_parameter.append([row[date_index], row[alt_index], row[lon_index], row[lat_index], row[value_index]])
        station_locations.add((row[lon_index], row[lat_index]))

    header_stations = {'lon': {'name': 'lon', 'unit': '[angle Degree]'},
                       'lat': {'name': 'lat', 'unit': '[angle Degree]'}}

    writer_stations = spatial_writer.SpatialWriter(header_stations, target_stations)
    writer_stations.appendrows(station_locations)
