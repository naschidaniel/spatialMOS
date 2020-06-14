#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This collection is used to execute commands for spatialMOS."""

from invoke import task, Collection
import inv_logging
import inv_docker


@task
def py_archive_get_available_data(c, cmd):
    """The csv-files are created with the 7zip. The folder must be specified e.g. uibk."""
    inv_logging.task(py_archive_get_available_data.__name__)
    command = ["python", "./py_get_available_data/archive_available_data.py", "--folder", cmd]
    command = ' '.join(command)
    c.run(command)
    inv_logging.success(py_archive_get_available_data.__name__)


@task
def py_get_available_data__gefs(c, cmd):
    """Download data gefs files."""
    inv_logging.task(py_get_available_data__gefs.__name__)
    cmd = ["py_get_available_data_gefs", "python", "./py_get_available_data/gefs.py", cmd]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_get_available_data__gefs.__name__)

@task
def py_get_available_data__suedtirol(c):
    """Download data from South Tyrol."""
    inv_logging.task(py_get_available_data__suedtirol.__name__)
    cmd = ["py_get_available_data", "python", "./py_get_available_data/suedtirol.py",
           "--beginndate", "2018-01-01", "--enddate", "2019-01-10"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_get_available_data__suedtirol.__name__)


@task
def py_get_available_data__uibk(c):
    """Download data from uibk."""
    inv_logging.task(py_get_available_data__uibk.__name__)
    cmd = ["py_get_available_data", "python", "./py_get_available_data/uibk.py"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_get_available_data__uibk.__name__)


@task
def py_get_available_data__wetter_at(c):
    """Download data from wetter_at."""
    inv_logging.task(py_get_available_data__wetter_at.__name__)
    cmd = ["py_get_available_data", "python", "./py_get_available_data/wetter_at.py",
           "--beginndate", "2018-01-01", "--enddate", "2019-01-10"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_get_available_data__wetter_at.__name__)


@task
def py_get_available_data__zamg(c):
    """Download data from zamg webpage."""
    inv_logging.task(py_get_available_data__zamg.__name__)
    cmd = ["py_get_available_data", "python", "./py_get_available_data/zamg.py"]
    cmd = ' '.join(cmd)
    inv_docker.run(c, cmd)
    inv_logging.success(py_get_available_data__zamg.__name__)


spatialmos_development_ns = Collection("spatialmos")
spatialmos_development_ns.add_task(py_archive_get_available_data)
spatialmos_development_ns.add_task(py_get_available_data__gefs)
spatialmos_development_ns.add_task(py_get_available_data__suedtirol)
spatialmos_development_ns.add_task(py_get_available_data__uibk)
spatialmos_development_ns.add_task(py_get_available_data__wetter_at)
spatialmos_development_ns.add_task(py_get_available_data__zamg)

spatialmos_production_ns = Collection("spatialmos")
spatialmos_production_ns.add_task(py_archive_get_available_data)
spatialmos_production_ns.add_task(py_get_available_data__gefs)
spatialmos_production_ns.add_task(py_get_available_data__suedtirol)
spatialmos_production_ns.add_task(py_get_available_data__uibk)
spatialmos_production_ns.add_task(py_get_available_data__wetter_at)
spatialmos_production_ns.add_task(py_get_available_data__zamg)
