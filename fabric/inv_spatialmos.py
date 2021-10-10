#!/usr/bin/python
# -*- coding: utf-8 -*-
'''This collection is used to execute commands for spatialMOS.'''

import os
import sys
import logging
import requests
from datetime import datetime

from invoke import task, Collection
from . import inv_base
from . import inv_logging
from . import inv_docker


@task
def init_topography(c):
    """Create shapefiles for spatialMOS"""
    inv_logging.task(init_topography.__name__)
    cmd = ["Rscript", "./r_spatialmos/init_shapefiles.R"]
    inv_docker.run_r_base(c, cmd)

    cmd = ['python', './run_script.py', '--script', 'pre_processing_topography']
    inv_docker.run_py_container(c, cmd)

    # Download Shapefile and unzip it
    if not os.path.exists("./data/get_available_data/gadm/gadm36_AUT_shp"):
        req_gadm36_zip_file = "https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_AUT_shp.zip"
        gadm36_zip_file = "./data/get_available_data/gadm/gadm36_AUT_shp.zip"
        req_shapefile = requests.get(req_gadm36_zip_file, stream=True)
        if req_shapefile.status_code == 200:
            with open(gadm36_zip_file, mode="wb") as f:
                for chunk in req_shapefile.iter_content(chunk_size=128):
                    f.write(chunk)
            logging.info("The shapefile '%s' has been downloaded.", req_gadm36_zip_file)
            c.run(f"unzip {gadm36_zip_file} -d ./data/get_available_data/gadm/gadm36_AUT_shp")
        else:
            logging.error("There was a problem with the download of the shapefile '%s'", req_gadm36_zip_file)
            sys.exit(1)

    inv_logging.success(init_topography.__name__)


@task
def py_archive_folder(c, folder):
    """The *.tar.gz are created with tar. The folder must be specified e.g. zamg."""
    inv_logging.task(py_archive_folder.__name__)
    cmd = ['./run_script.py', '--script', 'archive_folder', '--folder', folder]
    inv_docker.run_py_container(c, cmd)
    inv_logging.success(py_archive_folder.__name__)


@task
def py_archive_folder__gefs_avgspr_forecast_p05(c):
    """created a tar file from the folder gefs_avgspr_forecast_p05"""
    py_archive_folder(c, "gefs_avgspr_forecast_p05")
    inv_base.write_statusfile_and_success_logging(py_archive_folder__gefs_avgspr_forecast_p05.__name__)


@task
def py_archive_folder__lwd(c):
    """created a tar file from the folder lwd"""
    py_archive_folder(c, "lwd")
    inv_base.write_statusfile_and_success_logging(py_archive_folder__lwd.__name__)


@task
def py_archive_folder__zamg(c):
    """created a tar file from the folder lwd"""
    py_archive_folder(c, "zamg")
    inv_base.write_statusfile_and_success_logging(py_archive_folder__zamg.__name__)

@task
def py_untar_folder(c, folder):
    """The *.tar.gz untared with tar. The fileprefix must be specified e.g. zamg."""
    inv_logging.task(py_untar_folder.__name__)
    cmd = ['python', './run_script.py', '--script', 'untar_folder', '--folder', folder]
    inv_docker.run_py_container(c, cmd)
    inv_logging.success(py_untar_folder.__name__)


@task
def py_get_gefs(c, date, resolution, modeltype, parameter):
    """Download data gefs files."""
    inv_logging.task(py_get_gefs.__name__)
    cmd = ["python", "./run_script.py", "--script", "get_gefs_forecasts", "--date", date, "--resolution", resolution, "--modeltype", modeltype, "--parameter", parameter]
    inv_docker.run_py_container(c, cmd)
    inv_logging.success(py_get_gefs.__name__)


@task
def py_get_gefs_forecasts(c, date, parameter):
    """Download and pre process the forecasts"""
    inv_logging.task(py_get_gefs_forecasts.__name__)

    if parameter == 'wind_10m':
        get_gefs_parameter = ['ugrd_10m', 'vgrd_10m']     
    else:
        get_gefs_parameter = [parameter]

    for p in get_gefs_parameter:
        py_get_gefs(c, date=date, resolution="0.5", modeltype="avg", parameter=p)
        py_get_gefs(c, date=date, resolution="0.5", modeltype="spr", parameter=p)

    if parameter in ['rh_2m', 'tmp_2m']:
        py_pre_processing_gribfiles(c, date=date, resolution="0.5", parameter=parameter)
    inv_logging.success(py_get_gefs_forecasts.__name__)


@task
def py_get_gefs_forecasts__tmp_2m(c):
    """Download and pre process forcasts for tmp_2m"""
    inv_logging.task(py_get_gefs_forecasts__tmp_2m.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    py_get_gefs_forecasts(c, date, 'tmp_2m')
    inv_base.write_statusfile_and_success_logging(py_get_gefs_forecasts__tmp_2m.__name__)


@task
def py_get_gefs_forecasts__rh_2m(c):
    """Download and pre process forcasts for rh_2m"""
    inv_logging.task(py_get_gefs_forecasts__rh_2m.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    py_get_gefs_forecasts(c, date, 'rh_2m')
    inv_base.write_statusfile_and_success_logging(py_get_gefs_forecasts__rh_2m.__name__)


@task
def py_get_gefs_forecasts__wind_10m(c):
    """Download and pre process forcasts for wind_10m"""
    inv_logging.task(py_get_gefs_forecasts__wind_10m.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    py_get_gefs_forecasts(c, date, 'wind_10m')
    inv_base.write_statusfile_and_success_logging(py_get_gefs_forecasts__wind_10m.__name__)

@task
def py_get_suedtirol(c, begindate, enddate):
    """Download data from South Tyrol."""
    inv_logging.task(py_get_suedtirol.__name__)
    cmd = ["python", "./run_script.py", "--script", "get_suedtirol_data",
           "--begindate", begindate, "--enddate", enddate]
    inv_docker.run_py_container(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_get_suedtirol.__name__)


@task
def py_get_lwd(c):
    """Download data from lwd tirol"""
    inv_logging.task(py_get_lwd.__name__)
    cmd = ["python", "./run_script.py", "--script", "get_lwd_data"]
    inv_docker.run_py_container(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_get_lwd.__name__)


@task
def py_get_zamg(c):
    """Download data from zamg webpage."""
    inv_logging.task(py_get_zamg.__name__)
    cmd = ["python", "./run_script.py", "--script", "get_zamg_data"]
    inv_docker.run_py_container(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_get_zamg.__name__)


@task
def py_combine_data(c, folder):
    """Combine downloaded data for a folder."""
    inv_logging.task(py_combine_data.__name__)
    cmd = ["python", "./run_script.py", "--script", "combine_data", "--folder", folder]
    inv_docker.run_py_container(c, cmd)

@task
def py_interpolate_gribfiles(c, parameter):
    """GEFS Reforecasts are bilinear interpolated at station locations."""
    inv_logging.task(py_interpolate_gribfiles.__name__)
    cmd = ['python', './run_script.py', '--script', 'interpolate_gribfiles', '--parameter', parameter]
    inv_docker.run_py_container(c, cmd)
    inv_logging.success(py_interpolate_gribfiles.__name__)


@task
def py_pre_processing_gamlss_crch_climatologies(c, parameter):
    """Create climatologies for further processing in R with gamlss."""
    inv_logging.task(py_pre_processing_gamlss_crch_climatologies.__name__)
    cmd = ["python", "./py_spatialmos/pre_processing_gamlss_crch_climatologies.py", "--parameter", parameter]
    inv_docker.run_py_container(c, cmd)
    inv_logging.success(py_pre_processing_gamlss_crch_climatologies.__name__)


@task
def r_gamlss_crch_model(c, validation, parameter):
    """Create the required spatial climatologies."""
    inv_logging.task(r_gamlss_crch_model.__name__)
    cmd = ["Rscript", "./r_spatialmos/gamlss_crch_model.R", "--validation", validation, "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run_r_base(c, cmd)
    inv_logging.success(r_gamlss_crch_model.__name__)

@task
def r_spatial_climatologies_nwp(c,  begin, end, parameter):
    """Create daily climatologies for the NWP."""
    inv_logging.task(r_spatial_climatologies_nwp.__name__)
    cmd = ["Rscript", "./r_spatialmos/spatial_climatologies_nwp.R",  "--begin", begin, "--end", end, "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run_r_base(c, cmd)
    inv_logging.success(r_spatial_climatologies_nwp.__name__)

@task
def r_spatial_climatologies_obs(c, begin, end, parameter):
    """Create daily climatologies for the observations."""
    inv_logging.task(r_spatial_climatologies_obs.__name__)
    cmd = ["Rscript", "./r_spatialmos/spatial_climatologies_observations.R", "--begin", begin, "--end", end, "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run_r_base(c, cmd)
    inv_logging.success(r_spatial_climatologies_obs.__name__)

@task
def py_pre_processing_gribfiles(c, date, resolution, parameter):
    """Create the csv file and the jsonfile from the available gribfiles."""
    inv_logging.task(py_pre_processing_gribfiles.__name__)
    cmd = ["python", "./run_script.py", "--script", "pre_processing_prediction", "--date", date, "--resolution", resolution, "--parameter", parameter]
    inv_docker.run_py_container(c, cmd)
    inv_logging.success(py_pre_processing_gribfiles.__name__)

@task
def py_prediction__rh_2m(c):
    """Create the predictions and the spatialMOS plots for rh_2m."""
    inv_logging.task(py_prediction__rh_2m.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    cmd = ["python", "./run_script.py", "--script", "prediction", "--date", date, "--resolution", "0.5", "--parameter", "rh_2m"]
    inv_docker.run_py_container(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_prediction__rh_2m.__name__)

@task
def py_prediction__tmp_2m(c):
    """Create the predictions and the spatialMOS plots for tmp_2m."""
    inv_logging.task(py_prediction__tmp_2m.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    cmd = ["python", "./run_script.py", "--script", "prediction", "--date", date, "--resolution", "0.5", "--parameter", "tmp_2m"]
    inv_docker.run_py_container(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_prediction__tmp_2m.__name__)

SPATIALMOS_NS = Collection("spatialmos")
SPATIALMOS_NS.add_task(init_topography)
SPATIALMOS_NS.add_task(py_archive_folder__gefs_avgspr_forecast_p05)
SPATIALMOS_NS.add_task(py_archive_folder__lwd)
SPATIALMOS_NS.add_task(py_archive_folder__zamg)
SPATIALMOS_NS.add_task(py_untar_folder)
SPATIALMOS_NS.add_task(py_get_gefs_forecasts__rh_2m)
SPATIALMOS_NS.add_task(py_get_gefs_forecasts__tmp_2m)
SPATIALMOS_NS.add_task(py_get_gefs_forecasts__wind_10m)
SPATIALMOS_NS.add_task(py_get_suedtirol)
SPATIALMOS_NS.add_task(py_get_lwd)
SPATIALMOS_NS.add_task(py_get_zamg)
SPATIALMOS_NS.add_task(py_combine_data)
SPATIALMOS_NS.add_task(py_interpolate_gribfiles)
SPATIALMOS_NS.add_task(py_pre_processing_gamlss_crch_climatologies)
SPATIALMOS_NS.add_task(py_pre_processing_gribfiles)
SPATIALMOS_NS.add_task(py_prediction__tmp_2m)
SPATIALMOS_NS.add_task(py_prediction__rh_2m)
SPATIALMOS_NS.add_task(r_gamlss_crch_model)
SPATIALMOS_NS.add_task(r_spatial_climatologies_nwp)
SPATIALMOS_NS.add_task(r_spatial_climatologies_obs)
