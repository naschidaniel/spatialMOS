#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''With this Python script the predictions can be combined.'''

import logging
from pathlib import Path
import json
from typing import Dict, List

# Functions
def write_merged_predictions_file(data: Dict, outfile: Path):
    logging.info('Saving data in file \'%s\'', outfile)
    with open(outfile, mode='w', encoding='utf-8') as f:
        json.dump(data, f)
    logging.info('The file \'%s\' with the predictions was created', outfile)


def merge_predictions(parser_dict, data_path_media: Path, steps: List):
    '''combine_predictions'''
    predictions = {}
    data = {
            'anal_date': '',
            'parameter': parser_dict['parameter'],
            'unit': '',
            'dates_available': [],
            'steps_available': [],
            'steps_missing': []
            }
    for step in steps:
        file = data_path_media.joinpath(f"{parser_dict['date']}_step_{step}.json")
        logging.info('The file \'%s\' is processed.', file)
        if not file.exists():
            logging.warning('The file \'%s\' for the step \'%s\' is missing.', file, step)
            data['steps_missing'].append(step)
            continue
        else:
            data['steps_available'].append(step)

        with open(file) as f:
            d = json.load(f)
            data['anal_date'] = d['SpatialMosRun']['anal_date']
            data['unit'] = d['SpatialMosRun']['unit']
            data['dates_available'].append(d['SpatialMosStep']['valid_date'])
            for entry in d['SpatialMosPoint']:
                lat = entry['lat']
                lon = entry['lon']
                if lat not in predictions.keys():
                    predictions.setdefault(entry['lat'], {entry['lon']: {"spatialmos_mean": [entry['spatialmos_mean']], "spatialmos_spread": [entry['spatialmos_spread']]}})
                    continue
                if lon not in predictions[lat].keys():
                    predictions[lat][lon] = {"spatialmos_mean": [entry['spatialmos_mean']], "spatialmos_spread": [entry['spatialmos_spread']]}
                else:
                    predictions[lat][lon]['spatialmos_mean'].append(entry['spatialmos_mean'])
                    predictions[lat][lon]['spatialmos_spread'].append(entry['spatialmos_spread'])

    logging.info('The predictions has been merged.')
    data['predictions'] = predictions
    return data

def run_combine_predictions(parser_dict):
    '''run_combine_predictions combines the existing predictions'''
    steps = [f'{s:03d}' for s in range(6, 192+1, 6)]
    data_path_media = Path(f"./data/media/{parser_dict['parameter']}/")
    logging.info('The steps \'%s\' in the folder \'%s\' for \'%s\' and date \'%s\' will combined', steps, data_path_media, parser_dict['parameter'], parser_dict['date'])
    data = merge_predictions(parser_dict, data_path_media, steps)
    outfile = data_path_media.joinpath(f"{parser_dict['date']}_predictions.json")
    write_merged_predictions_file(data, outfile)

