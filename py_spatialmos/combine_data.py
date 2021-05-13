#!/usr/bin/python
# -*- coding: utf-8 -*-
'''A script to combine data from get_lwd_data, get_suedtirol_data and get_zamg_data'''

import logging
from pathlib import Path
from typing import Any, Dict
from . import get_zamg_data
from . import get_lwd_data
import csv
import os
import sys


def run_combine_data(parser_dict: Dict[str, Any]):
    '''run_combine_data puts all the files together for spatialmos'''
    measurements_path = Path("./data/get_available_data/measurements/")
    os.makedirs(measurements_path, exist_ok=True)
    with open(Path(measurements_path).joinpath(f"{parser_dict['folder']}_measurements.csv"), mode='w') as target:
        if parser_dict['folder'] == 'lwd':
            parameters = get_lwd_data.LwdData.parameters()
            writer = get_lwd_data.SpatialWriter(parameters, target)
        elif parser_dict['folder'] == 'zamg':
            parameters = get_zamg_data.ZamgData.parameters()
            writer = get_zamg_data.SpatialWriter(parameters, target)
        parameters_keys = list(parameters.keys())
        parameters_units = [parameters[k]['unit'] for k in parameters]

        csv_files_path = Path(
            f"./data/get_available_data/{parser_dict['folder']}")
        for csv_file in csv_files_path.glob('**/*.csv'):
            logging.info('The file %s is added to %s', csv_file, target)
            with open(csv_file) as f:
                data = list(csv.reader(f, delimiter=';'))
            if data[0] != parameters_keys and data[1] != parameters_units:
                raise RuntimeError(
                    'The header in the file %s is not supported' % csv_file)

            writer.appendrows(data[2:])
