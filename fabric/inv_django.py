#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""The collection is needed for django commands."""

import logging
from invoke import task, Collection
import inv_base
import inv_logging
import inv_docker

@task
def collectstatic(c):
    """This task is used to collect the static files"""
    inv_logging.task(collectstatic.__name__)
    inv_base.manage_py(c, "collectstatic -v 0 --no-input")
    inv_logging.success(collectstatic.__name__)


@task
def createsuperuser(c):
    """The task is used to create a superuser."""
    inv_logging.task(createsuperuser.__name__)
    logging.info("Enter the user for the Django backend.")
    inv_docker.stop(c)
    inv_base.manage_py(c, "createsuperuser")
    inv_logging.success(createsuperuser.__name__)


@task
def loadexampledata(c):
    """This task is used to load the sample data into the database"""
    inv_logging.task(loadexampledata.__name__)
    inv_base.manage_py(c, "loaddata db.json")
    inv_logging.success(loadexampledata.__name__)


@task
def managepy(c, cmd):
    """The task executes the django manage.py command, for example: collectstatic"""
    inv_logging.task(managepy.__name__)
    inv_base.manage_py(c, cmd)
    inv_logging.success(managepy.__name__)


@task
def makemigrations(c):
    """This task is used to create magrations"""
    inv_logging.task(makemigrations.__name__)
    inv_base.manage_py(c, "makemigrations")
    inv_logging.success(makemigrations.__name__)


@task
def migrate(c):
    """This task is used to load migrations into the database"""
    inv_logging.task(migrate.__name__)
    inv_docker.stop(c)
    inv_base.manage_py(c, "migrate")
    inv_logging.success(migrate.__name__)


@task
def generateSecretKey(c):
    """This task creates a new Secret Key for the fabric/settings.json file."""
    inv_logging.task(generateSecretKey.__name__)
    inv_base.manage_py(c, "shell -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'")
    inv_logging.success(generateSecretKey.__name__)

DJANGO_DEVELOPMENT_NS = Collection("django")
DJANGO_DEVELOPMENT_NS.add_task(collectstatic)
DJANGO_DEVELOPMENT_NS.add_task(createsuperuser)
DJANGO_DEVELOPMENT_NS.add_task(generateSecretKey)
DJANGO_DEVELOPMENT_NS.add_task(loadexampledata)
DJANGO_DEVELOPMENT_NS.add_task(makemigrations)
DJANGO_DEVELOPMENT_NS.add_task(managepy)
DJANGO_DEVELOPMENT_NS.add_task(migrate)

DJANGO_PRODUCTION_NS = Collection("django")
DJANGO_PRODUCTION_NS.add_task(managepy)
DJANGO_PRODUCTION_NS.add_task(migrate)
DJANGO_PRODUCTION_NS.add_task(createsuperuser)
