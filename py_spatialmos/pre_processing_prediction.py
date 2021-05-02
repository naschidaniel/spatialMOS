#!/usr/bin/env python
# coding: utf-8
''' With this Python script gribfiles can be converted into json files.'''

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict
from . import spatial_util


def combine_gribfiles(parser_dict: Dict[str, Any]):
    '''combine_gribfiles combines the previously downloaded gribfiles from the datafolder into one json file'''
    subset ={'W': 15, 'E': 20, 'S': 45, 'N': 53, 'resolution': 0.5}

    data_path = Path(f"./data/get_available_data/gefs_pre_processed_forecast/{parser_dict['parameter']}/{parser_dict['date']}0000")
    os.makedirs(data_path, exist_ok=True)

    if parser_dict['resolution'] == 0.5:
        folder = 'gefs_avgspr_forecast_p05'
    else:
        folder = 'gefs_avgspr_forecast_p1'

    gribfiles_path = Path(f"./data/get_available_data/{folder}/{parser_dict['parameter']}/{parser_dict['date']}0000/")
    spr_files = sorted(gribfiles_path.glob('*spr*.grb2'))
    for avg_gribfile in sorted(gribfiles_path.glob('*avg*.grb2')):
        logging.info('')
        step = f'{avg_gribfile.name[-9:-5]}'
        for spr_gribfile in spr_files:
            if spr_gribfile.match(f'*{step}*'):
                json_file = data_path.joinpath(f"./GFSE_{parser_dict['date']}_0000_{step}.json")
                with open(Path(json_file), 'w') as f:
                    json.dump(spatial_util.gribfiles_to_json(avg_gribfile, spr_gribfile, 'tmp_2m', subset), f)
