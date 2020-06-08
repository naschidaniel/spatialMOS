#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
"""The fabricfile of the project."""

import os
import logging
import sys
from invoke import task, Collection, Program

sys.path.insert(0, os.getcwd())
from fabric import inv_base
from fabric import inv_docker
from fabric import inv_logging
from fabric import inv_django
from fabric import inv_node
from fabric import inv_install
from fabric import inv_test
from fabric import inv_rsync
from fabric import inv_postgres
from fabric import inv_spatialmos
from fabric import inv_test

# Logging
inv_logging.start_logging()


# Namespace
MAIN_NS = Collection()


# Local Collection
local_ns = Collection("local")
local_ns.configure(inv_base.read_settings("development"))
local_ns.add_task(inv_docker.docker)
local_ns.add_collection(inv_install.install_ns)
local_ns.add_collection(inv_django.django_development_ns)
local_ns.add_collection(inv_docker.docker_compose_development_ns)
local_ns.add_collection(inv_postgres.postgresql_development_ns)
local_ns.add_collection(inv_spatialmos.spatialmos_development_ns)
local_ns.add_collection(inv_node.node_ns)
MAIN_NS.add_collection(local_ns)

# Testing Collection
test_ns = Collection("test")
test_ns.configure(inv_base.read_settings("test"))
test_ns.add_task(inv_test.starttest)
test_ns.add_task(inv_docker.stop)
MAIN_NS.add_collection(test_ns)

# Production Collection
production_ns = Collection("production")
production_ns.configure(inv_base.read_settings("production"))
production_ns.add_collection(inv_rsync.rsync_ns)
production_ns.add_task(inv_install.setproductionenvironment)
production_ns.add_collection(inv_docker.docker_compose_production_ns)
production_ns.add_collection(inv_django.django_production_ns)
production_ns.add_task(inv_docker.docker)
production_ns.add_collection(inv_postgres.postgresql_production_ns)
MAIN_NS.add_collection(production_ns)


# Program
PROGRAM = Program(namespace=MAIN_NS)
PROGRAM.run()
