#!/usr/bin/env python
#  -*- coding: utf-8 -*-
'''The fabricfile of the project.'''

from invoke import Collection, Program
from fabric import inv_base
from fabric import inv_docker
from fabric import inv_logging
from fabric import inv_node
from fabric import inv_rsync
from fabric import inv_spatialmos

# Logging
inv_logging.start_logging()

# Namespace
MAIN_NS = Collection()

# Local Collection
MAIN_NS = Collection('local')
MAIN_NS.configure(inv_base.read_settings())
MAIN_NS.add_task(inv_base.merge_statusfiles)
MAIN_NS.add_collection(inv_docker.DOCKER_NS)
MAIN_NS.add_collection(inv_spatialmos.SPATIALMOS_NS)
MAIN_NS.add_collection(inv_node.NODE_NS)
MAIN_NS.add_collection(inv_rsync.RSYNC_NS)

# Program
PROGRAM = Program(namespace=MAIN_NS)
PROGRAM.run()
