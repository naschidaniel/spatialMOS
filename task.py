#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""The fabricfile of the project."""

from invoke import Collection, Program
from fabric import inv_deploy
from fabric import inv_base
from fabric import inv_docker
from fabric import inv_logging
from fabric import inv_node
from fabric import inv_install
from fabric import inv_rsync
from fabric import inv_spatialmos

# Logging
inv_logging.start_logging()

# Namespace
MAIN_NS = Collection()

# Local Collection
MAIN_NS = Collection("local")
MAIN_NS.configure(inv_base.read_settings())
MAIN_NS.add_task(inv_docker.docker)
MAIN_NS.add_collection(inv_install.INSTALL_DEVELOPMENT_NS)
MAIN_NS.add_collection(inv_docker.DOCKER_COMPOSE_DEVELOPMENT_NS)
MAIN_NS.add_collection(inv_spatialmos.SPATIALMOS_DEVELOPMENT_NS)
MAIN_NS.add_collection(inv_node.NODE_NS)
MAIN_NS.add_collection(inv_rsync.RSYNC_NS)
MAIN_NS.add_task(inv_deploy.deploy)
MAIN_NS.add_task(inv_deploy.push_climatologies)

# Program
PROGRAM = Program(namespace=MAIN_NS)
PROGRAM.run()
