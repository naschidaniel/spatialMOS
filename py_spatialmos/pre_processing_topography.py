#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A script to create a panda dataframe from the gadm grid files."""

import os
import json
import logging
import csv
from osgeo import gdal
from py_middleware import logger_module
from py_middleware import spatial_parser


# Functions
def spatial_predictions():
    """The main function for creating the required topography using gdal from grid data."""

    data_path = "./data/get_available_data/gadm/"
    spatial_alt_area = gdal.Open(os.path.join(data_path, "spatial_alt_area.grd"))
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

    alt_area_filename = os.path.join(data_path, "spatial_alt_area.json")
    
    alt_area_data = {
            "min_lon": min_lon,
            "min_lat": min_lat,
            "max_lon": max_lon,
            "max_lat": max_lat,
            "center_lon": center_lon,
            "center_lat": center_lat,
        }

    with open(alt_area_filename, "w") as f:
        json.dump(alt_area_data, f)
        f.close()

    alt_area_filename = os.path.join(data_path, "spatial_alt_area.csv")

    with open(alt_area_filename, "w") as f:
        writer = csv.writer(f)
        writer.writerows(alt)

    logging.info("The spatial_alt_area '%s' was written.", alt_area_filename)


# Main
if __name__ == "__main__":
    STARTTIME = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    spatial_predictions()
    logger_module.end_logging(STARTTIME)