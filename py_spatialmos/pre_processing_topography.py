#!/usr/bin/python
# -*- coding: utf-8 -*-
'''A script to create a panda dataframe from the gadm grid files.'''

import os
import json
import logging
import csv
import pathlib
from osgeo import gdal


def run_preprocessing_topography():
    '''run_preprocessing_topography creates the required topography using gdal from grid data.'''

    data_path = pathlib.Path('./data/get_available_data/gadm/')
    spatial_alt_area = gdal.Open(data_path.joinpath('spatial_alt_area.grd'))
    alt = spatial_alt_area.ReadAsArray()
    width = spatial_alt_area.RasterXSize
    height = spatial_alt_area.RasterYSize
    geo_transform = spatial_alt_area.GetGeoTransform()

    min_lon = geo_transform[0]
    min_lat = geo_transform[3] + width * geo_transform[4] + height * geo_transform[5]
    max_lon = geo_transform[0] + width * geo_transform[1] + height * geo_transform[2]
    max_lat = geo_transform[3]
    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2

    alt_area_data = {
            'min_lon': min_lon,
            'min_lat': min_lat,
            'max_lon': max_lon,
            'max_lat': max_lat,
            'center_lon': center_lon,
            'center_lat': center_lat,
        }

    alt_area_filename = os.path.join(data_path, 'spatial_alt_area.json')
    with open(alt_area_filename, 'w') as f:
        json.dump(alt_area_data, f)

    with open(data_path.joinpath('spatial_alt_area.csv'), 'w') as f:
        writer = csv.writer(f)
        writer.writerows(alt)

    logging.info('The spatial_alt_area \'%s\' was written.', alt_area_filename)
