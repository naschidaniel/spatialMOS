#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
'''The fabricfile of the project.'''

from invoke import Collection, Program
from fabric import inv_docker
from fabric import inv_logging
from fabric import inv_node
from fabric import inv_rsync
from fabric import inv_spatialmos
from fabric import util

# Logging
inv_logging.start_logging()

# Namespace
MAIN_NS = Collection()

# Local Collection
MAIN_NS.configure(util.read_settings())
MAIN_NS.add_collection(inv_docker.DOCKER_NS)
MAIN_NS.add_collection(inv_node.NODE_NS)
MAIN_NS.add_collection(inv_rsync.RSYNC_NS)

MAIN_NS.add_task(inv_spatialmos.init_topography)
MAIN_NS.add_task(inv_spatialmos.archive_folder__gefs_avgspr_forecast_p05)
MAIN_NS.add_task(inv_spatialmos.archive_folder__lwd)
MAIN_NS.add_task(inv_spatialmos.archive_folder__zamg)
MAIN_NS.add_task(inv_spatialmos.combine_data)
MAIN_NS.add_task(inv_spatialmos.combine_predictions__rh_2m)
MAIN_NS.add_task(inv_spatialmos.combine_predictions__tmp_2m)
MAIN_NS.add_task(inv_spatialmos.deploy)
MAIN_NS.add_task(inv_spatialmos.untar_folder)
MAIN_NS.add_task(inv_spatialmos.get_gefs_forecasts__rh_2m_avg)
MAIN_NS.add_task(inv_spatialmos.get_gefs_forecasts__rh_2m_spr)
MAIN_NS.add_task(inv_spatialmos.get_gefs_forecasts__tmp_2m_avg)
MAIN_NS.add_task(inv_spatialmos.get_gefs_forecasts__tmp_2m_spr)
MAIN_NS.add_task(inv_spatialmos.get_gefs_forecasts__ugrd_10m_avg)
MAIN_NS.add_task(inv_spatialmos.get_gefs_forecasts__ugrd_10m_spr)
MAIN_NS.add_task(inv_spatialmos.get_gefs_forecasts__vgrd_10m_avg)
MAIN_NS.add_task(inv_spatialmos.get_gefs_forecasts__vgrd_10m_spr)
MAIN_NS.add_task(inv_spatialmos.get_suedtirol)
MAIN_NS.add_task(inv_spatialmos.get_lwd)
MAIN_NS.add_task(inv_spatialmos.get_zamg)
MAIN_NS.add_task(inv_spatialmos.install)
MAIN_NS.add_task(inv_spatialmos.interpolate_gribfiles)
MAIN_NS.add_task(inv_spatialmos.merge_statusfiles)
MAIN_NS.add_task(inv_spatialmos.pre_processing_gamlss_crch_climatologies)
MAIN_NS.add_task(inv_spatialmos.pre_processing_gribfiles__rh_2m)
MAIN_NS.add_task(inv_spatialmos.pre_processing_gribfiles__tmp_2m)
MAIN_NS.add_task(inv_spatialmos.pre_processing_gribfiles__ugrd_10m)
MAIN_NS.add_task(inv_spatialmos.pre_processing_gribfiles__vgrd_10m)
MAIN_NS.add_task(inv_spatialmos.prediction__tmp_2m)
MAIN_NS.add_task(inv_spatialmos.prediction__rh_2m)
MAIN_NS.add_task(inv_spatialmos.r_gamlss_crch_model)
MAIN_NS.add_task(inv_spatialmos.r_spatial_climatologies_nwp)
MAIN_NS.add_task(inv_spatialmos.r_spatial_climatologies_obs)
MAIN_NS.add_task(inv_spatialmos.remove_old_climatologies)

# Program
PROGRAM = Program(namespace=MAIN_NS)
PROGRAM.run()
