#!/usr/bin/env python
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
MAIN_NS = Collection('local')
MAIN_NS.configure(util.read_settings())
MAIN_NS.add_collection(inv_docker.DOCKER_NS)
MAIN_NS.add_collection(inv_spatialmos.SPATIALMOS_NS)
MAIN_NS.add_collection(inv_node.NODE_NS)
MAIN_NS.add_collection(inv_rsync.RSYNC_NS)

# Program
PROGRAM = Program(namespace=MAIN_NS)
PROGRAM.run()
