#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
"""This collection is used to test the functionality of DjangoVue before production."""

import os
import sys
import logging
from invoke import task
import inv_logging
import inv_base
import inv_install
import inv_django

@task
def starttest(c):
    """This function is used to start the production test environment"""
    inv_logging.task(starttest.__name__)
    static_folder = os.path.join(os.getcwd(), "django/static")
    try:
        shutil.rmtree(static_folder)
        logging.info(f"{static_folder} folder was deleted.")
    except:
        logging.error(f"{static_folder} could not be deleted.")

    inv_install.setenvironment(c, "test")
    inv_django.makemigrations(c)
    inv_django.migrate(c)
    inv_django.collectstatic(c)
    inv_base.docker_compose(c, f"up")
    inv_install.setenvironment(c, "development")
    inv_logging.success(starttest.__name__)
