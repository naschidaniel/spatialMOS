#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''A script to combine data from get_lwd_data, get_suedtirol_data and get_zamg_data'''

import csv
import datetime
from pathlib import Path
from typing import Any, Dict
import spatial_rust_util
import logging

def combine_nwp_gamlss_climatology(gfse_file: Path, measurements_file: Path, target: Path):
    '''combine_nwp_climatology'''
    with open(gfse_file, mode='r', encoding='utf-8') as f:
        gfse_data = list(csv.reader(f, delimiter=';'))[2:]    

    with open(measurements_file, mode='r', encoding='utf-8') as f:
        measurements = list(csv.reader(f, delimiter=';'))[2:]   

    nwp_climatology = spatial_rust_util.combine_nwp_climatology(gfse_data, measurements)
    nwp_climatology = sorted(nwp_climatology, key=lambda x:x[0])
    logging.info("Write GAMLSS climatology to '%s'", target)
    with open(target, mode='w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(['yday', 'kfold', 'dayminute', 'alt', 'lon', 'lat', 'obs', 'mean', 'log_spread'])
        writer.writerows(nwp_climatology)

def combine_obs_gamlss_climatology(measurements_file: Path, target: Path):
    with open(measurements_file, mode='r', encoding='utf-8') as f:
        measurements = list(csv.reader(f, delimiter=';'))[2:]   

    measurements_gamlss = []
    for row in measurements:
        try:
            timestamp = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').timetuple()
        except ValueError:
            logging.error("The date '%s' could no be parsed", row[0])
            continue
        measurements_gamlss.append([timestamp.tm_yday, 1, 60 * timestamp.tm_hour, row[1], row[2], row[3], row[4]])

    with open(target, mode='w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["yday", "kfold", "dayminute", "alt", "lon", "lat", "obs"])
        writer.writerows(measurements_gamlss)

def run_combine_climatology(parser_dict: Dict[str, Any]):
    '''run_combine_data runs combine_data'''
    logging.info("GAMLSS climatology for paramaeter '%s' and observations will be created", parser_dict['parameter'])
    measurements_file = Path(f"./data/get_available_data/measurements/combined/all_measurements_{parser_dict['parameter']}.csv")
    target = Path(f"./data/spatialmos_climatology/gam/{parser_dict['parameter']}/{parser_dict['parameter']}_station_observations.csv")
    combine_obs_gamlss_climatology(measurements_file, target)
    
    steps = range(6, 192+1, 6)
    for step in steps:
        logging.info("GAMLSS climatology for paramaeter '%s' and step '%s' will be created", parser_dict['parameter'], f"{step:03}")
        gfse_file = Path(f"./data/get_available_data/interpolated_station_forecasts/{parser_dict['parameter']}/GFSE_f{step:03}.csv")
        target_file = Path(f"./data/spatialmos_climatology/gam/{parser_dict['parameter']}/climate_nwp/{parser_dict['parameter']}_{step:03}.csv")
        combine_nwp_gamlss_climatology(gfse_file, measurements_file, target_file)