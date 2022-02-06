#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''A script to combine measurements for spatialmos'''

import csv
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, TextIO
from . import get_lwd_data
from . import get_suedtirol_data
from . import get_zamg_data
from .spatial_util import spatial_writer


def run_data_for_spatialmos():
    '''run_data_for_spatialmos combins the data for spatialmos'''
    for provider in ['lwd', 'suedtirol', 'zamg']:
        if provider == 'lwd':
            parameters = get_lwd_data.LwdData.parameters()
        elif provider == 'suedtirol':
            parameters = get_suedtirol_data.SuedtirolData.parameters()
        elif provider == 'zamg':
            parameters = get_zamg_data.ZamgData.parameters()
        else:
            raise RuntimeError(f'There is not data for \'{provider}\' available')
        for parameter in ['tmp_2m', 'rh_2m']:
            logging.info('\'%s\' Measurements for the parameter \'%s\' will be combined', provider, parameter)
            data = []
            for measurements_file in Path('./data/get_available_data/measurements').glob(f"{provider}_measurements_all_*.csv"):
                logging.info("Rading %s", measurements_file)
                with open(measurements_file, mode='r', encoding='utf-8') as f:
                    data_new = list(csv.reader(f, delimiter=';'))
                if len(data_new) <= 3:
                    logging.warning("There is no data so the csv file \'%s\' will be skiped.", measurements_file)
                    continue
                data = data + data_new[2:]
            data = sorted(data[2:], key=lambda x:x[0])
            start_date = data[0][0][0:10]
            end_date = data[-1][0][0:10]

            target_path = Path("./data/get_available_data/measurements/combined")
            os.makedirs(target_path, exist_ok=True)

            targetfile_parameter = Path(target_path).joinpath(f"{provider}_measurements_{parameter}_{start_date}_{end_date}.csv")
            targetfile_stations = Path(target_path).joinpath(f"{provider}_stations_{parameter}_{start_date}_{end_date}.csv")
            with open(targetfile_parameter, mode='w', newline='', encoding='utf-8') as target_parameter, open(targetfile_stations, mode='w', newline='', encoding='utf-8') as target_stations:
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
        raise RuntimeError(f'The run_combine_data is for the folder \'{folder}\' is not implemented')
    return parameters

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
    for row in data:
        if row[value_index] == '':
            continue

        try:
            lon = round(float(row[lon_index]), 3)
            lat = round(float(row[lat_index]), 3)
        except ValueError:
            logging.error("Could not convert string %s, %s to float", row[lon_index], row[lat_index])
            continue

        if not spatialmos_subset['W'] <= lon <= spatialmos_subset['E']:
            continue

        if not spatialmos_subset['S'] <= lat <= spatialmos_subset['N']:
            continue

        if lat > 47.0 and float(row[alt_index]) <= 400:
            logging.error("The altitude \'%s\' for the point '%s, %s' is probably wrong", row[alt_index], row[lon_index], row[lat_index])
            continue

        try:
            if parameter == 'tmp_2m':
                value = round(float(row[value_index]), 1)
                if not -45 <= value <= +45:
                    logging.warning('tmp_2m value \'%s\' \'%s\' out of range',row[0], value)
                    continue
            if parameter == 'rh_2m':
                value = round(float(row[value_index]), 0)
                if not 0 <= value <= 100:
                    logging.warning('rh_2m value \'%s\' \'%s\' out of range',row[0], value)
                    continue
        except ValueError:
            logging.error("Could not convert string %s to float", row[value_index])
            continue

        try:
            writer_parameter.append([row[date_index], row[alt_index], str(lon), str(lat), value])
            station_locations.add((str(lon), str(lat)))
        except IndexError:
            logging.error("The columns read in the file are of unequal length.")

    header_stations = {'lon': {'name': 'lon', 'unit': '[angle Degree]'},
                    'lat': {'name': 'lat', 'unit': '[angle Degree]'}}

    writer_stations = spatial_writer.SpatialWriter(header_stations, target_stations)
    writer_stations.appendrows(sorted(station_locations))

def run_combine_all_provider():
    '''run_combine_all_provider combines all measurements'''
    for parameter in ['rh_2m', 'tmp_2m']:
        data = []
        for provider in ['lwd', 'suedtirol', 'zamg']:
            measurements_files = Path("./data/get_available_data/measurements/combined/").glob(f"{provider}_measurements_{parameter}_*.csv")
            for measurements_file in measurements_files:
                logging.info("Reading %s", measurements_file)
                with open(measurements_file, mode='r', newline='', encoding='utf-8') as f:
                    data_new = list(csv.reader(f, delimiter=';'))
                    header = data_new[0:2]
                    data = data + data_new[2:]

        data = sorted(data[2:], key=lambda x:x[0])
        data = header + data
        measurements_file_all = Path(f"./data/get_available_data/measurements/combined/all_measurements_{parameter}.csv")
        logging.info("Writing all measurements to %s", measurements_file_all)
        with open(measurements_file_all, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerows(data)
