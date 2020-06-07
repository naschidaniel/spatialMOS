#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
"""This collection is used to execute commands for spatialMOS."""

import os
import sys
import logging
from invoke import task, Collection
import inv_base
import inv_logging
import inv_docker

@task
def get_available_data_suedtirol(c):
    """Resets postgres database and migrate django migrations."""
    inv_logging.task(get_available_data_suedtirol.__name__)
    cmd = ["py_get_available_data", "python", "./py_get_available_data/suedtirol.py", "-b", "2019-01-01", "-e", "2019-12-31"]
    str1 = ' '.join(cmd)
    print(str1)
    inv_docker.run(c, str1)
    inv_logging.success(get_available_data_suedtirol.__name__)

spatialmos_development_ns = Collection("spatialmos")
spatialmos_development_ns.add_task(get_available_data_suedtirol)

spatialmos_production_ns = Collection("spatialmos")
spatialmos_production_ns.add_task(get_available_data_suedtirol)