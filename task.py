#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""The fabricfile of the project."""

from fabric import inv_deploy
from invoke import Collection, Program
from fabric import inv_base
from fabric import inv_docker
from fabric import inv_logging
from fabric import inv_django
from fabric import inv_node
from fabric import inv_install
from fabric import inv_rsync
from fabric import inv_postgres
from fabric import inv_spatialmos

# Logging
inv_logging.start_logging()

# Namespace
MAIN_NS = Collection()

# Local Collection
LOCAL_NS = Collection("local")
LOCAL_NS.configure(inv_base.read_settings("development"))
LOCAL_NS.add_task(inv_docker.docker)
LOCAL_NS.add_collection(inv_install.INSTALL_DEVELOPMENT_NS)
LOCAL_NS.add_collection(inv_django.DJANGO_DEVELOPMENT_NS)
LOCAL_NS.add_collection(inv_docker.DOCKER_COMPOSE_DEVELOPMENT_NS)
LOCAL_NS.add_collection(inv_postgres.POSTGRESQL_DEVELOPMENT_NS)
LOCAL_NS.add_collection(inv_spatialmos.SPATIALMOS_DEVELOPMENT_NS)
LOCAL_NS.add_collection(inv_node.NODE_NS)
MAIN_NS.add_collection(LOCAL_NS)

# Production Collection
PRODUCTION_NS = Collection("production")
PRODUCTION_NS.configure(inv_base.read_settings("production"))
PRODUCTION_NS.add_collection(inv_rsync.RSYNC_NS)
PRODUCTION_NS.add_collection(inv_install.INSTALL_PRODUCTION_NS)
PRODUCTION_NS.add_collection(inv_docker.DOCKER_COMPOSE_PRODUCTION_NS)
PRODUCTION_NS.add_collection(inv_django.DJANGO_PRODUCTION_NS)
PRODUCTION_NS.add_task(inv_docker.docker)
PRODUCTION_NS.add_task(inv_deploy.deploy)
PRODUCTION_NS.add_collection(inv_spatialmos.SPATIALMOS_PRODUCTION_NS)
PRODUCTION_NS.add_collection(inv_postgres.POSTGRESQL_PRODUCTION_NS)
MAIN_NS.add_collection(PRODUCTION_NS)


# Program
PROGRAM = Program(namespace=MAIN_NS)
PROGRAM.run()
