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
    with open(Path(target_path).joinpath(f"{parser_dict['folder']}_measurements.csv"), mode='w') as target:
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
