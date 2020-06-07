#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
"""The collection is needed for django commands."""

import logging
import os
import sys
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

django_development_ns = Collection("django")
django_development_ns.add_task(collectstatic)
django_development_ns.add_task(createsuperuser)
django_development_ns.add_task(generateSecretKey)
django_development_ns.add_task(loadexampledata)
django_development_ns.add_task(makemigrations)
django_development_ns.add_task(managepy)
django_development_ns.add_task(migrate)

django_production_ns = Collection("django")
django_production_ns.add_task(managepy)
django_production_ns.add_task(migrate)
django_production_ns.add_task(createsuperuser)
