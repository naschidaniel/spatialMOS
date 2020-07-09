#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This collection is used to execute commands for spatialMOS."""

from invoke import task, Collection
import inv_logging
import inv_docker


@task
def py_spatialmos__archive_available_data(c, cmd):
    """The csv-files are created with the 7zip. The folder must be specified e.g. uibk."""
    inv_logging.task(py_spatialmos__archive_available_data.__name__)
    command = ["python", "./py_spatialmos/archive_available_data.py", "--folder", cmd]
    command = ' '.join(command)
    c.run(command)
    inv_logging.success(py_spatialmos__archive_available_data.__name__)


@task
def py_spatialmos__get_gefs(c, cmd):
    """Download data gefs files."""
    inv_logging.task(py_spatialmos__get_gefs.__name__)
    cmd = ["py_get_gefs", "python", "./py_spatialmos/get_gefs_forcasts.py", cmd]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__get_gefs.__name__)

@task
def py_spatialmos__get_suedtirol(c, begindate, enddate):
    """Download data from South Tyrol."""
    inv_logging.task(py_spatialmos__get_suedtirol.__name__)
    cmd = ["py_get", "python", "./py_spatialmos/get_suedtirol_data.py",
           "--beginndate", begindate, "--enddate", enddate]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__get_suedtirol.__name__)


@task
def py_spatialmos__get_uibk(c):
    """Download data from uibk."""
    inv_logging.task(py_spatialmos__get_uibk.__name__)
    cmd = ["py_get", "python", "./py_spatialmos/get_uibk_data.py"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__get_uibk.__name__)


@task
def py_spatialmos__get_wetter_at(c, begindate, enddate):
    """Download data from wetter_at."""
    inv_logging.task(py_spatialmos__get_wetter_at.__name__)
    cmd = ["py_get", "python", "./py_spatialmos/get_wetter_at_data.py",
           "--beginndate", begindate, "--enddate", enddate]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__get_wetter_at.__name__)


@task
def py_spatialmos__get_zamg(c):
    """Download data from zamg webpage."""
    inv_logging.task(py_spatialmos__get_zamg.__name__)
    cmd = ["py_get", "python", "./py_spatialmos/get_zamg_data.py"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__get_zamg.__name__)

@task
def py_spatialmos__pre_proccessing_reforcasts(c, parameter):
    """GEFS Reforcasts are bilinearly interpolated at station locations."""
    inv_logging.task(py_spatialmos__pre_proccessing_reforcasts.__name__)
    cmd = ["py_pre_processing_gefs", "python", "./py_spatialmos/pre_processing_gefs_reforcasts_to_station_locations.py", "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__pre_proccessing_reforcasts.__name__)


@task
def py_spatialmos__pre_proccessing_observations_and_reforcasts_to_stations(c):
    """Station Observations and GEFS Reforcasts are combined."""
    inv_logging.task(py_spatialmos__pre_proccessing_observations_and_reforcasts_to_stations.__name__)
    cmd = ["py_pre_processing_gefs", "python", "./py_spatialmos/pre_processing_station_observations_and_reforcasts.py"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__pre_proccessing_observations_and_reforcasts_to_stations.__name__)

@task
def py_spatialmos__pre_processing_gamlss_crch_climatologies(c, parameter):
    """Create climatologies for further processing in R with gamlss."""
    inv_logging.task(py_spatialmos__pre_processing_gamlss_crch_climatologies.__name__)
    cmd = ["py_pre_processing_gefs", "python", "./py_spatialmos/pre_processing_gamlss_crch_climatologies.py", "--parameter", parameter]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_spatialmos__pre_processing_gamlss_crch_climatologies.__name__)

@task
def r_spatialmos__gam_init_shapefiles(c):
    """Create shapefiles for spatialMOS"""
    inv_logging.task(r_spatialmos__gam_init_shapefiles.__name__)
    cmd = ["r_spatialmos_climatology", "Rscript", "./r_spatialmos/init_shapefiles.R"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(r_spatialmos__gam_init_shapefiles.__name__)

@task
def r_spatialmos__gamlss_crch_model(c):
    """Create the required spatial climatologies."""
    inv_logging.task(r_spatialmos__gamlss_crch_model.__name__)
    cmd = ["r_spatialmos_climatology", "Rscript", "./r_spatialmos/gamlss_crch_model.R"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(r_spatialmos__gamlss_crch_model.__name__)

@task
def r_spatialmos__spatial_climatologies_nwp(c, parameter, beginn, end):
    """Create daily climatologies."""
    inv_logging.task(r_spatialmos__spatial_climatologies_nwp.__name__)
    cmd = ["r_spatialmos_climatology", "Rscript", "./r_spatialmos/spatial_climatologies_nwp.R", "--parameter", parameter, "--beginn", beginn, "--end", end]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(r_spatialmos__spatial_climatologies_nwp.__name__)

@task
def r_spatialmos__spatial_climatologies_obs(c, parameter, beginn, end):
    """Create daily climatologies."""
    inv_logging.task(r_spatialmos__spatial_climatologies_obs.__name__)
    cmd = ["r_spatialmos_climatology", "Rscript", "./r_spatialmos/spatial_climatologies_obs.R", "--parameter", parameter, "--beginn", beginn, "--end", end]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(r_spatialmos__spatial_climatologies_obs.__name__)

spatialmos_development_ns = Collection("spatialmos")
spatialmos_development_ns.add_task(py_spatialmos__archive_available_data)
spatialmos_development_ns.add_task(py_spatialmos__get_gefs)
spatialmos_development_ns.add_task(py_spatialmos__get_suedtirol)
spatialmos_development_ns.add_task(py_spatialmos__get_uibk)
spatialmos_development_ns.add_task(py_spatialmos__get_wetter_at)
spatialmos_development_ns.add_task(py_spatialmos__get_zamg)
spatialmos_development_ns.add_task(py_spatialmos__pre_proccessing_reforcasts)
spatialmos_development_ns.add_task(py_spatialmos__pre_proccessing_observations_and_reforcasts_to_stations)
spatialmos_development_ns.add_task(py_spatialmos__pre_processing_gamlss_crch_climatologies)
spatialmos_development_ns.add_task(r_spatialmos__gam_init_shapefiles)
spatialmos_development_ns.add_task(r_spatialmos__gamlss_crch_model)
spatialmos_development_ns.add_task(r_spatialmos__spatial_climatologies_nwp)
spatialmos_development_ns.add_task(r_spatialmos__spatial_climatologies_obs)


spatialmos_production_ns = Collection("spatialmos")
spatialmos_production_ns.add_task(py_spatialmos__archive_available_data)
spatialmos_production_ns.add_task(py_spatialmos__get_gefs)
spatialmos_production_ns.add_task(py_spatialmos__get_uibk)
spatialmos_production_ns.add_task(py_spatialmos__get_zamg)
