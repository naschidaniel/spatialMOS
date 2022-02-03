#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''A script to combine data from get_lwd_data, get_suedtirol_data and get_zamg_data'''

import csv
from pathlib import Path
from typing import Any, Dict
import spatial_rust_util

def combine_nwp_climatology(gfse_file: Path, measurements_file: Path, target: Path):
    '''combine_nwp_climatology'''
    with open(gfse_file, mode='r', encoding='utf-8') as f:
        gfse_data = list(csv.reader(f, delimiter=';'))[2:]    

    with open(measurements_file, mode='r', encoding='utf-8') as f:
        measurements = list(csv.reader(f, delimiter=';'))[2:]   

    nwp_climatology = spatial_rust_util.combine_nwp_climatology(gfse_data, measurements)
    nwp_climatology = sorted(nwp_climatology, key=lambda x:x[0])
    with open(target, mode='w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(['yday', 'kfold', 'dayminute', 'alt', 'lon', 'lat', 'obs', 'mean', 'log_spread'])
        writer.writerows(nwp_climatology)

def run_combine_climatology(parser_dict: Dict[str, Any]):
    '''run_combine_data runs combine_data'''
    measurements_file = Path(f"./data/get_available_data/measurements/combined/all_measurements_{parser_dict['parameter']}_2019-12-31_2022-02-02.csv")
    steps = range(6, 192+1, 6)
    for step in steps:
        gfse_file = Path(f"./data/get_available_data/interpolated_station_forecasts/{parser_dict['parameter']}/GFSE_f{step:03}.csv")
        target_file = Path("./rudi.csv")
        combine_nwp_climatology(gfse_file, measurements_file, target_file)
        if step == 6:
            break

    # with open('GFSE_f006.csv', mode='w', encoding='utf-8') as f:
    #     writer = csv.writer(f, delimiter=";")
    #     writer.writerows(gfse_data[0:5000])

    # rudi = Path("./data/get_available_data/measurements/combined/all_measurements_tmp_2m_2019-12-31_2022-02-02.csv")
    # with open(rudi, mode='r', encoding='utf-8') as f:
    #     gfse_data = list(csv.reader(f, delimiter=';'))
    

    # with open('all_measurements_tmp_2m.csv', mode='w', encoding='utf-8') as f:
    #     writer = csv.writer(f, delimiter=";")
    #     found = False
    #     i = 0
    #     for row in gfse_data:
    #         if row [0] == "2020-08-12 00:00:00":
    #             found = True

    #         if not found:
    #             continue

    #         writer.writerow(row)
    #         i += 1
    #         if i == 10000:
    #             break

