#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This collection is used to execute commands for spatialMOS."""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from invoke import task, Collection
import inv_base
import inv_logging
import inv_docker


@task
def spatialmos__init_topography(c):
    """Create shapefiles for spatialMOS"""
    inv_logging.task(spatialmos__init_topography.__name__)
    cmd = ["r_base", "Rscript", "./r_spatialmos/init_shapefiles.R"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)

    cmd = ['py_container', 'python', './run_script.py', '--script', 'pre_processing_topography']
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)

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

    inv_logging.success(spatialmos__init_topography.__name__)


@task
def py_spatialmos__archive_folder(c, folder):
    """The *.tar.gz are created with tar. The folder must be specified e.g. zamg."""
    inv_logging.task(py_spatialmos__archive_folder.__name__)
    cmd = ['py_container', 'python', './run_script.py', '--script', 'archive_folder', '--folder', folder]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_spatialmos__archive_folder.__name__, cmd)

@task
def py_spatialmos__untar_folder(c, folder):
    """The *.tar.gz untared with tar. The fileprefix must be specified e.g. zamg."""
    inv_logging.task(py_spatialmos__untar_folder.__name__)
    cmd = ['py_container', 'python', './run_script.py', '--script', 'untar_folder', '--folder', folder]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_spatialmos__untar_folder.__name__, cmd)


@task
def py_spatialmos_merge_statusfiles(c):
    """Merge statusfiles"""
    statusfiles_path = Path("./data/spool/statusfiles/")
    statusfiles = []
    for file in statusfiles_path.glob("*.json"):
        with (open(file, mode="r")) as f:
            status = json.load(f)
        statusfiles.append(status)

    merge_statusfile = Path("./data/media/statusfiles.json")
    with open(merge_statusfile, "w") as f:
        json.dump(statusfiles, f)
    logging.info("The merged status file %s has been written.", merge_statusfile)

    inv_base.write_statusfile_and_success_logging(py_spatialmos_merge_statusfiles.__name__, "")


@task
def py_spatialmos__get_gefs(c, date, resolution, modeltype, parameter):
    """Download data gefs files."""
    inv_logging.task(py_spatialmos__get_gefs.__name__)
    cmd = ["py_container", "python", "./run_script.py", "--script", "get_gefs_forecasts", "--date", date, "--resolution", resolution, "--modeltype", modeltype, "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_spatialmos__get_gefs.__name__, cmd)

@task
def py_spatialmos__get_gefs_forecasts(c, date, parameter):
    """Download and pre process the forecasts"""
    inv_logging.task(py_spatialmos__get_gefs_forecasts.__name__)

    if parameter == "wind_10m":
        get_gefs_parameter = ["ugrd_10m", "vgrd_10m"]        
    else:
        get_gefs_parameter = [parameter]

    for p in get_gefs_parameter:
        py_spatialmos__get_gefs(c, date=date, resolution="0.5", modeltype="avg", parameter=p)
        py_spatialmos__get_gefs(c, date=date, resolution="0.5", modeltype="spr", parameter=p)

    py_spatialmos__pre_processing_gribfiles(c, date=date, resolution="0.5", parameter=parameter)
    inv_logging.success(py_spatialmos__get_gefs_forecasts.__name__)

@task
def py_spatialmos__get_suedtirol(c, begindate, enddate):
    """Download data from South Tyrol."""
    inv_logging.task(py_spatialmos__get_suedtirol.__name__)
    cmd = ["py_container", "python", "./run_script.py", "--script", "get_suedtirol_data",
           "--begindate", begindate, "--enddate", enddate]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_spatialmos__get_suedtirol.__name__, cmd)


@task
def py_spatialmos__get_lwd(c):
    """Download data from lwd tirol"""
    inv_logging.task(py_spatialmos__get_lwd.__name__)
    cmd = ["py_container", "python", "./run_script.py", "--script", "get_lwd_data"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_spatialmos__get_lwd.__name__, cmd)


@task
def py_spatialmos__get_zamg(c):
    """Download data from zamg webpage."""
    inv_logging.task(py_spatialmos__get_zamg.__name__)
    cmd = ["py_container", "python", "./run_script.py", "--script", "get_zamg_data"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_spatialmos__get_zamg.__name__, cmd)


@task
def py_spatialmos__combine_data(c, folder):
    """Combine downloaded data for a folder."""
    inv_logging.task(py_spatialmos__combine_data.__name__)
    cmd = ["py_container", "python", "./run_script.py", "--script", "combine_data", "--folder", folder]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)

@task
def py_spatialmos__interpolate_gribfiles(c, parameter):
    """GEFS Reforecasts are bilinear interpolated at station locations."""
    inv_logging.task(py_spatialmos__interpolate_gribfiles.__name__)
    cmd = ['py_container', 'python', './run_script.py', '--script', 'interpolate_gribfiles', '--parameter', parameter]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_spatialmos__interpolate_gribfiles.__name__, cmd)


@task
def py_spatialmos__pre_processing_observations_and_reforecasts_to_stations(c):
    """Station Observations and GEFS Reforecasts are combined."""
    inv_logging.task(py_spatialmos__pre_processing_observations_and_reforecasts_to_stations.__name__)
    cmd = ["py_rdata", "python", "./py_spatialmos/pre_processing_station_observations_and_reforecasts.py"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_spatialmos__pre_processing_observations_and_reforecasts_to_stations.__name__, cmd)


@task
def py_spatialmos__pre_processing_gamlss_crch_climatologies(c, parameter):
    """Create climatologies for further processing in R with gamlss."""
    inv_logging.task(py_spatialmos__pre_processing_gamlss_crch_climatologies.__name__)
    cmd = ["py_rdata", "python", "./py_spatialmos/pre_processing_gamlss_crch_climatologies.py", "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_spatialmos__pre_processing_gamlss_crch_climatologies.__name__, cmd)


@task
def r_spatialmos__gamlss_crch_model(c, validation, parameter):
    """Create the required spatial climatologies."""
    inv_logging.task(r_spatialmos__gamlss_crch_model.__name__)
    cmd = ["r_base", "Rscript", "./r_spatialmos/gamlss_crch_model.R", "--validation", validation, "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(r_spatialmos__gamlss_crch_model.__name__)

@task
def r_spatialmos__spatial_climatologies_nwp(c,  begin, end, parameter):
    """Create daily climatologies for the NWP."""
    inv_logging.task(r_spatialmos__spatial_climatologies_nwp.__name__)
    cmd = ["r_base", "Rscript", "./r_spatialmos/spatial_climatologies_nwp.R",  "--begin", begin, "--end", end, "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(r_spatialmos__spatial_climatologies_nwp.__name__)

@task
def r_spatialmos__spatial_climatologies_obs(c, begin, end, parameter):
    """Create daily climatologies for the observations."""
    inv_logging.task(r_spatialmos__spatial_climatologies_obs.__name__)
    cmd = ["r_base", "Rscript", "./r_spatialmos/spatial_climatologies_observations.R", "--begin", begin, "--end", end, "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(r_spatialmos__spatial_climatologies_obs.__name__)

@task
def py_spatialmos__pre_processing_gribfiles(c, date, resolution, parameter):
    """Create the csv file and the jsonfile from the available gribfiles."""
    inv_logging.task(py_spatialmos__pre_processing_gribfiles.__name__)
    cmd = ["py_container", "python", "./run_script.py", "--script", "pre_processing_prediction", "--date", date, "--resolution", resolution, "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_spatialmos__pre_processing_gribfiles.__name__, cmd)

@task
def py_spatialmos__prediction(c, date, parameter):
    """Create the predictions and the spatialMOS plots."""
    inv_logging.task(py_spatialmos__prediction.__name__)
    cmd = ["py_container", "python", "./run_script.py", "--script", "prediction", "--date", date, "--resolution", "0.5", "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_base.write_statusfile_and_success_logging(py_spatialmos__prediction.__name__, cmd)


@task
def py_spatialmos__maturin_build(c):
    """Build the Rust libraries for Spatialmos"""
    inv_logging.task(py_spatialmos__maturin_build.__name__)
    user, group = inv_base.uid_gid(c)
    c.run("docker run --rm -v $(pwd):/io konstin2/maturin build --manylinux off")
    # TODO rm sudo
    c.run(f"sudo chown {user}:{group} -R target")
    c.run("mv ./target/wheels/*.whl ./container/py_container/")
    inv_logging.success(r_spatialmos__spatial_climatologies_obs.__name__)

SPATIALMOS_DEVELOPMENT_NS = Collection("spatialmos")
SPATIALMOS_DEVELOPMENT_NS.add_task(spatialmos__init_topography)
SPATIALMOS_DEVELOPMENT_NS.add_task(py_spatialmos__archive_folder)
SPATIALMOS_DEVELOPMENT_NS.add_task(py_spatialmos__untar_folder)
SPATIALMOS_DEVELOPMENT_NS.add_task(py_spatialmos__get_gefs)
SPATIALMOS_DEVELOPMENT_NS.add_task(py_spatialmos__get_gefs_forecasts)
SPATIALMOS_DEVELOPMENT_NS.add_task(py_spatialmos__get_suedtirol)
SPATIALMOS_DEVELOPMENT_NS.add_task(py_spatialmos__get_lwd)
SPATIALMOS_DEVELOPMENT_NS.add_task(py_spatialmos__get_zamg)
SPATIALMOS_DEVELOPMENT_NS.add_task(py_spatialmos__combine_data)
SPATIALMOS_DEVELOPMENT_NS.add_task(py_spatialmos__interpolate_gribfiles)
SPATIALMOS_DEVELOPMENT_NS.add_task(py_spatialmos_merge_statusfiles)
SPATIALMOS_DEVELOPMENT_NS.add_task(py_spatialmos__pre_processing_observations_and_reforecasts_to_stations)
SPATIALMOS_DEVELOPMENT_NS.add_task(py_spatialmos__pre_processing_gamlss_crch_climatologies)
SPATIALMOS_DEVELOPMENT_NS.add_task(py_spatialmos__pre_processing_gribfiles)
SPATIALMOS_DEVELOPMENT_NS.add_task(py_spatialmos__prediction)
SPATIALMOS_DEVELOPMENT_NS.add_task(py_spatialmos__maturin_build)
SPATIALMOS_DEVELOPMENT_NS.add_task(r_spatialmos__gamlss_crch_model)
SPATIALMOS_DEVELOPMENT_NS.add_task(r_spatialmos__spatial_climatologies_nwp)
SPATIALMOS_DEVELOPMENT_NS.add_task(r_spatialmos__spatial_climatologies_obs)



SPATIALMOS_PRODUCTION_NS = Collection("spatialmos")
SPATIALMOS_PRODUCTION_NS.add_task(py_spatialmos__archive_folder)
SPATIALMOS_PRODUCTION_NS.add_task(py_spatialmos__get_gefs)
SPATIALMOS_PRODUCTION_NS.add_task(py_spatialmos__get_lwd)
SPATIALMOS_PRODUCTION_NS.add_task(py_spatialmos__get_zamg)
SPATIALMOS_PRODUCTION_NS.add_task(py_spatialmos__pre_processing_gribfiles)
SPATIALMOS_PRODUCTION_NS.add_task(py_spatialmos__prediction)
