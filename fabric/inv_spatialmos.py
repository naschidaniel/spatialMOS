#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''This collection is used to execute commands for spatialMOS.'''

import os
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
import requests
from invoke import task
from . import inv_logging
from . import inv_docker
from . import inv_node
from . import inv_rsync
from . import util


def archive_folder(c, folder):
    '''The *.tar.gz are created with tar. The folder must be specified e.g. zamg.'''
    inv_logging.task(archive_folder.__name__)
    cmd = ['python', './run_script.py', '--script', 'archive_folder', '--folder', folder]
    inv_docker.run_py_container(c, cmd)


@task
def archive_folder__gefs_avgspr_forecast_p05(c):
    '''created a tar file from the folder gefs_avgspr_forecast_p05'''
    archive_folder(c, 'gefs_avgspr_forecast_p05')
    util.write_statusfile_and_success_logging(archive_folder__gefs_avgspr_forecast_p05.__name__)


@task
def archive_folder__lwd(c):
    '''created a tar file from the folder lwd'''
    archive_folder(c, 'lwd')
    util.write_statusfile_and_success_logging(archive_folder__lwd.__name__)


@task
def archive_folder__zamg(c):
    '''created a tar file from the folder lwd'''
    archive_folder(c, 'zamg')
    util.write_statusfile_and_success_logging(archive_folder__zamg.__name__)


@task
def combine_data(c, folder):
    '''Combine downloaded data for a folder.'''
    inv_logging.task(combine_data.__name__)
    cmd = ['python', './run_script.py', '--script', 'combine_data', '--folder', folder]
    inv_docker.run_py_container(c, cmd)


@task
def deploy(c):
    '''Everything you need to deploy'''
    inv_logging.task(deploy.__name__)
    util.check_upstream(c)
    inv_node.build(c)
    inv_rsync.push(c, 'sourcefiles')
    inv_rsync.push(c, 'staticfiles')
    inv_logging.success(deploy.__name__)


@task
def get_gefs(c, date, resolution, modeltype, parameter):
    '''Download data gefs files.'''
    inv_logging.task(get_gefs.__name__)
    cmd = ['python', './run_script.py', '--script', 'get_gefs_forecasts', '--date', date, '--resolution', resolution, '--modeltype', modeltype, '--parameter', parameter]
    inv_docker.run_py_container(c, cmd)
    inv_logging.success(get_gefs.__name__)


@task
def get_gefs_forecasts__tmp_2m_avg(c):
    '''Download and pre process forcasts for tmp_2m'''
    inv_logging.task(get_gefs_forecasts__tmp_2m_avg.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    get_gefs(c, date=date, resolution='0.5', modeltype='avg', parameter='tmp_2m')
    util.write_statusfile_and_success_logging(get_gefs_forecasts__tmp_2m_avg.__name__)


@task
def get_gefs_forecasts__tmp_2m_spr(c):
    '''Download and pre process forcasts for tmp_2m'''
    inv_logging.task(get_gefs_forecasts__tmp_2m_spr.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    get_gefs(c, date=date, resolution='0.5', modeltype='spr', parameter='tmp_2m')
    util.write_statusfile_and_success_logging(get_gefs_forecasts__tmp_2m_spr.__name__)


@task
def get_gefs_forecasts__rh_2m_avg(c):
    '''Download and pre process forcasts for rh_2m'''
    inv_logging.task(get_gefs_forecasts__rh_2m_avg.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    get_gefs(c, date=date, resolution='0.5', modeltype='avg', parameter='rh_2m')
    util.write_statusfile_and_success_logging(get_gefs_forecasts__rh_2m_avg.__name__)


@task
def get_gefs_forecasts__rh_2m_spr(c):
    '''Download and pre process forcasts for rh_2m spr'''
    inv_logging.task(get_gefs_forecasts__rh_2m_spr.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    get_gefs(c, date=date, resolution='0.5', modeltype='spr', parameter='rh_2m')
    util.write_statusfile_and_success_logging(get_gefs_forecasts__rh_2m_spr.__name__)


@task
def get_gefs_forecasts__ugrd_10m_avg(c):
    '''Download and pre process forcasts for ugrd_10 avg'''
    inv_logging.task(get_gefs_forecasts__ugrd_10m_avg.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    get_gefs(c, date=date, resolution='0.5', modeltype='avg', parameter='ugrd_10m')
    util.write_statusfile_and_success_logging(get_gefs_forecasts__ugrd_10m_avg.__name__)


@task
def get_gefs_forecasts__ugrd_10m_spr(c):
    '''Download and pre process forcasts for ugrd_10 spr'''
    inv_logging.task(get_gefs_forecasts__ugrd_10m_spr.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    get_gefs(c, date=date, resolution='0.5', modeltype='spr', parameter='ugrd_10m')
    util.write_statusfile_and_success_logging(get_gefs_forecasts__ugrd_10m_spr.__name__)


@task
def get_gefs_forecasts__vgrd_10m_avg(c):
    '''Download and pre process forcasts for wind_10m avg'''
    inv_logging.task(get_gefs_forecasts__vgrd_10m_avg.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    get_gefs(c, date=date, resolution='0.5', modeltype='avg', parameter='vgrd_10m')
    util.write_statusfile_and_success_logging(get_gefs_forecasts__vgrd_10m_avg.__name__)


@task
def get_gefs_forecasts__vgrd_10m_spr(c):
    '''Download and pre process forcasts for wind_10m spr'''
    inv_logging.task(get_gefs_forecasts__vgrd_10m_spr.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    get_gefs(c, date=date, resolution='0.5', modeltype='spr', parameter='vgrd_10m')
    util.write_statusfile_and_success_logging(get_gefs_forecasts__vgrd_10m_spr.__name__)


@task
def pre_processing_gribfiles__tmp_2m(c):
    '''combine tmp_2m gribfiles for predictions'''
    inv_logging.task(pre_processing_gribfiles__tmp_2m.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    pre_processing_gribfiles(c, date=date, resolution='0.5', parameter='tmp_2m')
    util.write_statusfile_and_success_logging(pre_processing_gribfiles__tmp_2m.__name__)


@task
def pre_processing_gribfiles__rh_2m(c):
    '''combine rh_2m gribfiles for predictions'''
    inv_logging.task(pre_processing_gribfiles__rh_2m.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    pre_processing_gribfiles(c, date=date, resolution='0.5', parameter='rh_2m')
    util.write_statusfile_and_success_logging(pre_processing_gribfiles__rh_2m.__name__)


@task
def pre_processing_gamlss_crch_climatologies(c, parameter):
    '''Create climatologies for further processing in R with gamlss.'''
    inv_logging.task(pre_processing_gamlss_crch_climatologies.__name__)
    cmd = ['python', './spatialmos/pre_processing_gamlss_crch_climatologies.py', '--parameter', parameter]
    inv_docker.run_py_container(c, cmd)
    inv_logging.success(pre_processing_gamlss_crch_climatologies.__name__)


@task
def pre_processing_gribfiles(c, date, resolution, parameter):
    '''Create the csv file and the jsonfile from the available gribfiles.'''
    inv_logging.task(pre_processing_gribfiles.__name__)
    cmd = ['python', './run_script.py', '--script', 'pre_processing_prediction', '--date', date, '--resolution', resolution, '--parameter', parameter]
    inv_docker.run_py_container(c, cmd)
    inv_logging.success(pre_processing_gribfiles.__name__)


@task
def prediction__rh_2m(c):
    '''Create the predictions and the spatialMOS plots for rh_2m.'''
    inv_logging.task(prediction__rh_2m.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    cmd = ['python', './run_script.py', '--script', 'prediction', '--date', date, '--resolution', '0.5', '--parameter', 'rh_2m']
    inv_docker.run_py_container(c, cmd)
    util.write_statusfile_and_success_logging(prediction__rh_2m.__name__)


@task
def prediction__tmp_2m(c):
    '''Create the predictions and the spatialMOS plots for tmp_2m.'''
    inv_logging.task(prediction__tmp_2m.__name__)
    date = datetime.now().strftime('%Y-%m-%d')
    cmd = ['python', './run_script.py', '--script', 'prediction', '--date', date, '--resolution', '0.5', '--parameter', 'tmp_2m']
    inv_docker.run_py_container(c, cmd)
    util.write_statusfile_and_success_logging(prediction__tmp_2m.__name__)


@task
def get_suedtirol(c, begindate, enddate):
    '''Download data from South Tyrol.'''
    inv_logging.task(get_suedtirol.__name__)
    cmd = ['python', './run_script.py', '--script', 'get_suedtirol_data',
           '--begindate', begindate, '--enddate', enddate]
    inv_docker.run_py_container(c, cmd)
    util.write_statusfile_and_success_logging(get_suedtirol.__name__)


@task
def get_lwd(c):
    '''Download data from lwd tirol'''
    inv_logging.task(get_lwd.__name__)
    cmd = ['python', './run_script.py', '--script', 'get_lwd_data']
    inv_docker.run_py_container(c, cmd)
    util.write_statusfile_and_success_logging(get_lwd.__name__)


@task
def get_zamg(c):
    '''Download data from zamg webpage.'''
    inv_logging.task(get_zamg.__name__)
    cmd = ['python', './run_script.py', '--script', 'get_zamg_data']
    inv_docker.run_py_container(c, cmd)
    util.write_statusfile_and_success_logging(get_zamg.__name__)


@task
def init_topography(c):
    '''Create shapefiles for spatialMOS'''
    inv_logging.task(init_topography.__name__)
    cmd = ['Rscript', './r_spatialmos/init_shapefiles.R']
    inv_docker.run_r_base(c, cmd)

    cmd = ['python', './run_script.py', '--script', 'pre_processing_topography']
    inv_docker.run_py_container(c, cmd)

    # Download Shapefile and unzip it
    if not os.path.exists('./data/get_available_data/gadm/gadm36_AUT_shp'):
        req_gadm36_zip_file = 'https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_AUT_shp.zip'
        gadm36_zip_file = './data/get_available_data/gadm/gadm36_AUT_shp.zip'
        req_shapefile = requests.get(req_gadm36_zip_file, stream=True)
        if req_shapefile.status_code == 200:
            with open(gadm36_zip_file, mode='wb') as f:
                for chunk in req_shapefile.iter_content(chunk_size=128):
                    f.write(chunk)
            logging.info('The shapefile \'%s\' has been downloaded.', req_gadm36_zip_file)
            c.run(f'unzip {gadm36_zip_file} -d ./data/get_available_data/gadm/gadm36_AUT_shp')
        else:
            raise RuntimeError(f'There was a problem with the download of the shapefile \'{req_gadm36_zip_file}\'')

    inv_logging.success(init_topography.__name__)


@task
def install(c):
    '''A task for quick installation of spatialMOS'''
    inv_logging.task(install.__name__)
    util.create_folders(c)
    inv_docker.rebuild(c)
    inv_node.yarn(c, '')
    inv_node.build(c)
    inv_logging.success(install.__name__)


@task
def interpolate_gribfiles(c, parameter):
    '''GEFS Reforecasts are bilinear interpolated at station locations.'''
    inv_logging.task(interpolate_gribfiles.__name__)
    cmd = ['python', './run_script.py', '--script', 'interpolate_gribfiles', '--parameter', parameter]
    inv_docker.run_py_container(c, cmd)
    inv_logging.success(interpolate_gribfiles.__name__)


@task
def merge_statusfiles(c): # pylint: disable=W0613
    '''Merge statusfiles'''
    statusfiles_path = Path('./data/spool/statusfiles/')
    statusfiles = []
    for file in sorted(statusfiles_path.glob('*.json')):
        logging.info('The file %s will be added to the systemstatus file.', file)
        with (open(file, mode='r', encoding='UTF-8')) as f:
            status = json.load(f)
            status['failed'] = datetime.now() > datetime.strptime(status['taskMaxAgeTime'], '%Y-%m-%dT%H:%M:%S')
        statusfiles.append(status)

    settings = util.read_settings()
    systemchecks_done = sorted([c['taskName'] for c in statusfiles])
    systemchecks_available = [check for check in sorted(settings['systemChecks'].keys()) if check != merge_statusfiles.__name__]
    systemchecks_missing = [check for check in systemchecks_available if check not in systemchecks_done]

    if len(systemchecks_missing) == 0:
        status_complete = True
        logging.info('All available checks from the \'settings.json\' file are checked.')
    else:
        status_complete = False
        for check in systemchecks_missing:
            logging.error('The check \'%s\' is missing', check)

    status = {
        'taskName': merge_statusfiles.__name__,
        'taskFinishedTime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'taskMaxAgeTime': (datetime.now() + timedelta(minutes=int(settings['systemChecks'][merge_statusfiles.__name__]))).strftime('%Y-%m-%dT%H:%M:%S'),
        'maxAge': int(settings['systemChecks'][merge_statusfiles.__name__]),
        'complete': status_complete,
        'failed': False,
        }
    statusfiles.append(status)
    statusfiles = sorted(statusfiles, key=lambda x: x['taskName'], reverse=False)

    merge_statusfile = Path('./data/media/systemstatus.json')
    with open(merge_statusfile, 'w', encoding='utf-8') as f:
        json.dump(statusfiles, f)
    logging.info('The merged status file %s has been written.', merge_statusfile)
    inv_logging.success(merge_statusfiles.__name__)


@task
def r_gamlss_crch_model(c, validation, parameter):
    '''Create the required spatial climatologies.'''
    inv_logging.task(r_gamlss_crch_model.__name__)
    cmd = ['Rscript', './r_spatialmos/gamlss_crch_model.R', '--validation', validation, '--parameter', parameter]
    cmd = ' '.join(cmd)
    inv_docker.run_r_base(c, cmd)
    inv_logging.success(r_gamlss_crch_model.__name__)


@task
def r_spatial_climatologies_nwp(c,  begin, end, parameter):
    '''Create daily climatologies for the NWP.'''
    inv_logging.task(r_spatial_climatologies_nwp.__name__)
    cmd = ['Rscript', './r_spatialmos/spatial_climatologies_nwp.R',  '--begin', begin, '--end', end, '--parameter', parameter]
    cmd = ' '.join(cmd)
    inv_docker.run_r_base(c, cmd)
    inv_logging.success(r_spatial_climatologies_nwp.__name__)


@task
def r_spatial_climatologies_obs(c, begin, end, parameter):
    '''Create daily climatologies for the observations.'''
    inv_logging.task(r_spatial_climatologies_obs.__name__)
    cmd = ['Rscript', './r_spatialmos/spatial_climatologies_observations.R', '--begin', begin, '--end', end, '--parameter', parameter]
    cmd = ' '.join(cmd)
    inv_docker.run_r_base(c, cmd)
    inv_logging.success(r_spatial_climatologies_obs.__name__)


@task
def untar_folder(c, folder):
    '''The *.tar.gz untared with tar. The fileprefix must be specified e.g. zamg.'''
    inv_logging.task(untar_folder.__name__)
    cmd = ['python', './run_script.py', '--script', 'untar_folder', '--folder', folder]
    inv_docker.run_py_container(c, cmd)
    inv_logging.success(untar_folder.__name__)
