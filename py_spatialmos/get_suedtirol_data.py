#!/usr/bin/python
# -*- coding: utf-8 -*-
'''With this Python script data can be obtained from the South Tyrol Weather Service.'''

import logging
import os
import datetime
from pathlib import Path
from typing import Dict, List, Union
import requests
from .spatial_util import spatial_util
from .spatial_util.spatial_writer import SpatialWriter

class SuedtirolData:
    '''SuedtirolData Class'''

    # Data from the Open Data API Interface from - Wetter Provinz Bozen
    # http://daten.buergernetz.bz.it/de/dataset/misure-meteo-e-idrografiche
    # Licence: Creative Commons CC0 - http://opendefinition.org/okd/
    # Land Suedtirol - https://wetter.provinz.bz.it/
    # Information about the Metadata
    # http://daten.buergernetz.bz.it/de/dataset/misure-meteo-e-idrografiche

    @staticmethod
    def parameters() -> Dict[str, Dict[str, str]]:
        '''parameters and a unit which is encapsulated in the spatialmos format.'''
        return {'DATE': {'name': 'date', 'unit': '[UTC]'},
                'SCODE': {'name': 'name', 'unit': '[String]'},
                'LAT': {'name': 'lat', 'unit': '[angle Degree]'},
                'LONG': {'name': 'lon', 'unit': '[angle Degree]'},
                'ALT': {'name': 'alt', 'unit': '[m]'},
                'LT': {'name': 't', 'unit': '[Degree C]'},
                'LF': {'name': 'rf', 'unit': '[Percent]'},
                'WG.BOE': {'name': 'boe', 'unit': '[m/s]'},
                'WG': {'name': 'wg', 'unit': '[m/s]'},
                'WR': {'name': 'wr', 'unit': '[Degree]'},
                'N': {'name': 'regen', 'unit': '[mm/h]'},
                'GS': {'name': 'globalstrahlung', 'unit': '[W/m^2]'},
                'SD': {'name': 'sonne', 'unit': '[s]'}}

    @classmethod
    def request_data(cls, request_type: str, url='') -> dict:
        '''request_data loads the data from the API interface'''

        if request_type not in ['sensors', 'stations', 'timeseries']:
            raise RuntimeError(
                'The request_type \'%s\' ist not defined.' % request_type)

        if request_type == 'stations':
            url = 'http://dati.retecivica.bz.it/services/meteo/v1/stations'
        elif request_type == 'sensors':
            url = 'http://dati.retecivica.bz.it/services/meteo/v1/sensors'

        logging.info('Data is loaded from the api interface %s', url)
        data = requests.get(url)
        if data.status_code != 200:
            logging.error(
                'The response of the API \'%s\' does not match 200', url)
            return {}

        try:
            data_dict = data.json()
        except ValueError as ex:
            logging.error(
                'The loaded Data from the \'%s\' could not be converted into a json.',  url)
            logging.exception(ex)
            return {}

        if request_type == 'stations':
            return {station['properties']['SCODE']: station['properties'] for station in data_dict['features']}

        return data_dict


def suedtirol_spatial_converter(measurements: Dict[str, Dict[str, Union[str, float]]], filename: Path) -> None:
    '''convert suedtirol data and save it in spatialMOS CSV format'''
    try:
        columns = list(SuedtirolData.parameters().keys())
        measurements_write_lines: List[List] = spatial_util.convert_measurements(
            measurements, columns)
        if len(measurements_write_lines) != 0:
            with open(filename, mode='w', newline='') as target:
                logging.info(
                    'The suedtirol data will be written into the file \'%s\'', target)
                parameters = SuedtirolData.parameters()
                writer = SpatialWriter(parameters, target)

                # Convert data to spatialMOS CSV format
                station = measurements_write_lines[0][1]
                logging.info('%s data lines will be written for the station %s.', len(
                    measurements_write_lines), station)
                for entry in measurements_write_lines:
                    writer.append(entry)
    except ValueError as ex:
        logging.error(
            'The spatialmos CSV file \'%s\' could not be written.', filename)
        raise ex


def fetch_suedtirol_data(begindate: str, enddate: str) -> None:
    '''fetch_suedtirol_data from dati.retecivica.bz.it and store the original data json file. Additionally the converted data is saved in spatialMOS CSV Format.'''
    utcnow_str = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H_%M_%S')
    data_path = Path('./data/get_available_data/suedtirol/data')
    os.makedirs(data_path, exist_ok=True)

    stations = SuedtirolData.request_data('stations')
    sensors = SuedtirolData.request_data('sensors')

    if not stations or not sensors:
        logging.error(
            'The station or sensor data from the API interface is not available.')
        raise RuntimeError

    for sensor in sensors:
        if sensor['SCODE'] not in stations.keys():
            continue
        if 'SENSORS' in stations[sensor['SCODE']].keys():
            stations[sensor['SCODE']]['SENSORS'].append(sensor['TYPE'])
        else:
            stations[sensor['SCODE']]['SENSORS'] = [sensor['TYPE']]

    for station in stations.values():
        measurements: Dict = {}
        for sensor in station['SENSORS']:
            if not sensor in SuedtirolData.parameters().keys():
                continue
            url_values = f"http://daten.buergernetz.bz.it/services/meteo/v1/timeseries?station_code={station['SCODE']}&output_format=JSON&sensor_code={sensor}&date_from={begindate}0000&date_to={enddate}0000"
            timeseries = SuedtirolData.request_data('timeseries', url_values)
            for ts in timeseries:
                if not ':00:00' in ts['DATE']:
                    continue

                try:
                    measurements[ts['DATE']][sensor] = ts['VALUE']
                except KeyError:
                    measurements[ts['DATE']] = {
                        'SCODE': station['SCODE'],
                        'LAT': station['LAT'],
                        'LONG': station['LONG'],
                        'ALT': station['ALT'],
                        sensor: ts['VALUE']
                    }

        if len(list(measurements.keys())) == 0:
            logging.info(
                'No data relevant for spatialMOS are available for the station %s.', station['SCODE'])
            continue

        csv_filename = data_path.joinpath(
            f"suedtirol_{station['SCODE']}_{begindate}_{enddate}_{utcnow_str}.csv")
        suedtirol_spatial_converter(measurements, csv_filename)
