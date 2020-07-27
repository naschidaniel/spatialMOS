#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A script to create a panda dataframe from the gadm grid files."""

import os
import json
import logging
import csv
import requests
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

    gadm36_AUT_shp = "./data/get_available_data/gadm/gadm36_AUT_shp"
    if not os.path.exists(gadm36_AUT_shp):
        gadm36_zip_file = "https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_AUT_shp.zip"
        req_shapefile = requests.get(gadm36_zip_file, stream=True)
        if req_shapefile.status_code == 200:
            with open("./data/get_available_data/gadm/gadm36_AUT_shp.zip", mode="wb") as f:
                for chunk in req_shapefile.iter_content(chunk_size=128):
                    f.write(chunk)
            logging.info("The shapefile '%s' has been downloaded.", gadm36_zip_file)
        else:
            logging.error("There was a problem with the download of the shapefile '%s'", gadm36_zip_file)



# Main
if __name__ == "__main__":
    STARTTIME = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    spatial_predictions()
    logger_module.end_logging(STARTTIME)