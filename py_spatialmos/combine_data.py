#!/usr/bin/python
# -*- coding: utf-8 -*-
'''A script to combine data from get_lwd_data, get_suedtirol_data and get_zamg_data'''

import csv
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, TextIO
from . import get_lwd_data
from . import get_suedtirol_data
from . import get_zamg_data
from .spatial_util import spatial_writer



def run_combine_data(parser_dict: Dict[str, Any]):
    '''run_combine_data runs combine_data'''
    target_path = Path("./data/get_available_data/measurements/")
    os.makedirs(target_path, exist_ok=True)
    targetfile = Path(target_path).joinpath(f"{parser_dict['folder']}_measurements.csv")
    parameters = select_parameters(parser_dict['folder'])
    with open(targetfile, mode='w', newline='') as target:
        csv_files_path = Path(f"./data/get_available_data/{parser_dict['folder']}")
        combine_data(csv_files_path, parameters, target)

def run_data_for_spatialmos(parser_dict: Dict[str, Any]):
    '''run_data_for_spatialmos combins the data for spatialmos'''
    target_path = Path("./data/get_available_data/measurements/")
    measurements_file = Path(target_path).joinpath(f"{parser_dict['folder']}_measurements.csv")
    parameters = select_parameters(parser_dict['folder'])
    for parameter in ['tmp_2m', 'rh_2m']:
        with open(measurements_file) as f:
            data = list(csv.reader(f, delimiter=';'))
        if len(data) <= 3:
            logging.warning("There is no data so the csv file \'%s\' will be skiped.", measurements_file)
            continue

        targetfile_parameter = Path(target_path).joinpath(f"{parser_dict['folder']}_measurements_{parameter}.csv")
        targetfile_stations = Path(target_path).joinpath(f"{parser_dict['folder']}_stations_{parameter}.csv")
        with open(targetfile_parameter, mode='w', newline='') as target_parameter, open(targetfile_stations, mode='w', newline='') as target_stations:
            data_for_spatialmos(data, parameters, parameter, target_parameter, target_stations)

def select_parameters(folder: str) -> Dict[str, Dict[str, str]]:
    '''select_parameters selects the parameters from the folder name'''
    if folder == 'lwd':
        parameters = get_lwd_data.LwdData.parameters()
    elif folder == 'suedtirol':
        parameters = get_suedtirol_data.SuedtirolData.parameters()
    elif folder == 'zamg':
        parameters = get_zamg_data.ZamgData.parameters()
    else:
        raise RuntimeError('The run_combine_data is for the folder \'%s\' is not implemented' % folder)
    return parameters

def combine_data(csv_files_path: Path, parameters: Dict[str, Dict[str, str]], target: TextIO):
    '''combine_data creates one csv file with all the data from one dataprovider'''
    parameters_keys =  [parameters[k]['name'] for k in parameters]
    parameters_units = [parameters[k]['unit'] for k in parameters]

    writer = spatial_writer.SpatialWriter(parameters, target)
    for csv_file in sorted(csv_files_path.glob('**/*.csv')):
        logging.info('The file %s is added to %s', csv_file, target)
        with open(csv_file) as f:
            data = list(csv.reader(f, delimiter=';'))

        if len(data) <= 3:
            logging.warning("There is no data so the csv file \'%s\' will be skiped.", csv_file)
            continue

        if data[0] != parameters_keys and data[1] != parameters_units:
            logging.error("Header Keys expected: %s", parameters_keys)
            logging.error("Header Keys     File: %s", data[0])
            logging.error("Header Units Expected: %s", parameters_units)
            logging.error("Header Units     File: %s", data[1])
            raise RuntimeError(
                'The header in the file %s is not supported' % csv_file)
        writer.appendrows(data[2:])

def data_for_spatialmos(data: List[List[str]], parameters: Dict[str, Dict[str, str]], parameter: str, target_parameter: TextIO, target_stations: TextIO):
    '''get_station_locations extracts the station locations for a parameter'''

    # Only select stations for the region of North- and Southtirol
    spatialmos_subset: Dict[str, float] = {'W': 10., 'E': 12., 'S': 46., 'N': 48.}

    header_parameter = {'date': {'name': 'date', 'unit': '[UTC]'},
                        'alt': {'name': 'alt', 'unit': '[m]'},
                        'lon': {'name': 'lon', 'unit': '[angle Degree]'},
                        'lat': {'name': 'lat', 'unit': '[angle Degree]'}}

    parameters_names = [parameters[k]['name'] for k in list(parameters.keys())]

    date_index = parameters_names.index('date')
    alt_index = parameters_names.index('alt')
    lon_index = parameters_names.index('lon')
    lat_index = parameters_names.index('lat')

    if parameter == 'tmp_2m':
        header_parameter.update({'t': {'name': 't', 'unit': '[Degree C]'}})
        value_index = parameters_names.index('t')
    elif parameter == 'rh_2m':
        header_parameter.update({'rf': {'name': 'rf', 'unit': '[Percent]'}})
        value_index = parameters_names.index('rf')

    writer_parameter = spatial_writer.SpatialWriter(header_parameter, target_parameter)
    station_locations = set()
    for row in data[2:]:
        if row[value_index] == '':
            continue

        try:
            lon = round(float(row[lon_index]), 3)
            lat = round(float(row[lat_index]), 3)
        except ValueError:
            logging.error("Could not convert string %s, %s to float", row[lon_index], row[lat_index])
            continue

        if not (spatialmos_subset['W'] <= lon <= spatialmos_subset['E']) and (spatialmos_subset['S'] <= lat <= spatialmos_subset['N']):
            continue

        try:
            writer_parameter.append([row[date_index], row[alt_index], str(lon), str(lat), row[value_index]])
            station_locations.add((str(lon), str(lat)))
        except IndexError:
            logging.error("The columns read in the file are of unequal length.")

    header_stations = {'lon': {'name': 'lon', 'unit': '[angle Degree]'},
                    'lat': {'name': 'lat', 'unit': '[angle Degree]'}}

    writer_stations = spatial_writer.SpatialWriter(header_stations, target_stations)
    writer_stations.appendrows(sorted(station_locations))
