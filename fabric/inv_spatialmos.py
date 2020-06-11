#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This collection is used to execute commands for spatialMOS."""

from invoke import task, Collection
import inv_logging
import inv_docker


@task
def archive_available_data(c, cmd):
    """The csv-files are created with the 7zip. The folder must be specified e.g. uibk."""
    inv_logging.task(archive_available_data.__name__)
    command = ["python", "./py_get_available_data/archive_available_data.py", "--folder", cmd]
    command = ' '.join(command)
    c.run(command)
    inv_logging.success(archive_available_data.__name__)


@task
def get_available_data_wetter_at(c):
    """Download data from wetter_at."""
    inv_logging.task(get_available_data_wetter_at.__name__)
    cmd = ["py_get_available_data", "python", "./py_get_available_data/wetter_at.py",
           "--beginndate", "2018-01-01", "--enddate", "2019-01-10"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(get_available_data_wetter_at.__name__)


@task
def get_available_data_suedtirol(c):
    """Download data from South Tyrol."""
    inv_logging.task(get_available_data_suedtirol.__name__)
    cmd = ["py_get_available_data", "python", "./py_get_available_data/suedtirol.py",
           "--beginndate", "2018-01-01", "--enddate", "2019-01-10"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(get_available_data_suedtirol.__name__)


@task
def get_available_data_uibk(c):
    """Download data from uibk."""
    inv_logging.task(get_available_data_uibk.__name__)
    cmd = ["py_get_available_data", "python",
           "./py_get_available_data/uibk.py"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(get_available_data_uibk.__name__)


@task
def get_available_data_zamg(c):
    """Download data from zamg webpage."""
    inv_logging.task(get_available_data_zamg.__name__)
    cmd = ["py_get_available_data", "python",
           "./py_get_available_data/zamg.py"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(get_available_data_zamg.__name__)


spatialmos_development_ns = Collection("spatialmos")
spatialmos_development_ns.add_task(archive_available_data)
spatialmos_development_ns.add_task(get_available_data_wetter_at)
spatialmos_development_ns.add_task(get_available_data_suedtirol)
spatialmos_development_ns.add_task(get_available_data_uibk)
spatialmos_development_ns.add_task(get_available_data_zamg)

spatialmos_production_ns = Collection("spatialmos")
spatialmos_production_ns.add_task(archive_available_data)
spatialmos_production_ns.add_task(get_available_data_wetter_at)
spatialmos_production_ns.add_task(get_available_data_suedtirol)
spatialmos_production_ns.add_task(get_available_data_uibk)
spatialmos_development_ns.add_task(get_available_data_zamg)
