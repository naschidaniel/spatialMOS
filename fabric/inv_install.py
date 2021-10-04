#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""This collection is used to install spatialMOS."""

import os
import sys
import logging
from invoke import task, Collection
from . import inv_base
from . import inv_logging
from . import inv_docker
from . import inv_node


@task
def quickinstallation(c):
    """A task for quick installation of spatialMOS"""
    inv_logging.task(quickinstallation.__name__)
    folders(c)
    inv_docker.rebuild(c)
    inv_node.npm(c, "")
    inv_node.build(c)
    inv_logging.success(quickinstallation.__name__)


@task
def folders(c):
    """This task is used to create the folder structure"""
    inv_logging.task(folders.__name__)
    for folder in c.config["initFolders"]:
        folder = os.path.join(os.getcwd(), folder)

        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
                logging.info("The folder %s has been created.", folder)
            except:
                logging.error("The folder %s could not be created.", folder)
                sys.exit(1)
        else:
            logging.warning("The folder %s already exists.", folder)

    inv_logging.success(folders.__name__)




INSTALL_DEVELOPMENT_NS = Collection("install")
INSTALL_DEVELOPMENT_NS.add_task(folders)
INSTALL_DEVELOPMENT_NS.add_task(quickinstallation)
