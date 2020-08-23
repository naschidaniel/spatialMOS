#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""This collection is used to install spatialMOS."""

import os
import sys
import logging
import shutil
from invoke import task, Collection
import inv_base
import inv_logging
import inv_docker
import inv_docker
import inv_rsync


@task
def quickinstallation(c):
    """A task for quick installation of spatialMOS"""
    inv_logging.task(quickinstallation.__name__)
    folders(c)
    setenvironment(c, "development")
    inv_docker.rebuild(c)
    #inv_node.npm(c, "install")
    inv_django.migrate(c)
    inv_django.createsuperuser(c)
    #inv_django.loadexampledata(c)
    #inv_node.build(c)
    inv_django.collectstatic(c)
    inv_docker.serve(c)
    inv_logging.success(quickinstallation.__name__)


@task
def getdockercert(c):
    """A task to store the batch of docker certificates under ./fabric/cert"""
    inv_logging.task(getdockercert.__name__)
    settings = inv_base.read_settings("production")
    cert_path = settings["docker"]["DOCKER_CERT_PATH"]
    logging.info("The following path is used to store the certificates: %s", cert_path)
    if os.path.exists(cert_path):
        shutil.rmtree(cert_path)
        logging.info("The old certificates were deleted.")

    if not os.path.exists(cert_path):
        os.mkdir(cert_path)
        logging.info("The folder %s was created.", cert_path)

    inv_rsync.scp_get(c, "", settings["REMOTE_HOST"], "~/.docker/*", cert_path)
    inv_logging.success(getdockercert.__name__)


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


@task
def setenvironment(c, cmd):
    """The task writes the local environment variables for django and docker, for example: development"""
    inv_logging.task(setenvironment.__name__)
    inv_logging.cmd(cmd)

    settings = inv_base.read_settings(cmd)
    development_dir = os.getcwd()
    if cmd == "production":
        filename = ".env.production"
    else:
        filename = ".env"

    dict_env = {
        "django": os.path.join(development_dir, f"django/spatialmos/{filename}"),
        "docker": os.path.join(development_dir, f"{filename}")
    }
    
    # set the last commit msg
    settings["django"]["LASTCOMMIT"] = inv_base.generate_lastcommit(c, settings)

    for dict_env_key, dict_env_file in dict_env.items():
        try:
            with open(dict_env_file, "w") as f:
                for key, value in settings[dict_env_key].items():
                    f.write(f"{key}={value}\n")
                f.close()
            logging.info(f"The environment variable for '{dict_env_key}'' from the settings.json file was successfully written to the .env file.: '{dict_env_file}'")

        except:
            logging.error(
                f"It was not possible to write to the file: '{dict_env_file}'")
            sys.exit(1)

    inv_logging.success(setenvironment.__name__)
    return dict_env


#@task(pre=[check_upstream])
@task
def setproductionenvironment(c):
    """The task writes the environment variables on the server for django and docker. The created files are uploaded to the server and the required folders for spatialMOS are created."""
    inv_logging.task(setproductionenvironment.__name__)
    settings = inv_base.read_settings("production")

    dict_env = setenvironment(c, "production")
    remote_env = {
        "django": os.path.join(settings["docker"]["INSTALLFOLDER"], "django/spatialmos/.env"),
        "docker": os.path.join(settings["docker"]["INSTALLFOLDER"], ".env")
    }

    # set the last commit msg
    settings["django"]["LASTCOMMIT"] = inv_base.generate_lastcommit(c, settings)

    inv_rsync.scp_push(c, settings["REMOTE_USER"], settings["REMOTE_HOST"], dict_env["docker"], remote_env["docker"])
    inv_rsync.scp_push(c, settings["REMOTE_USER"], settings["REMOTE_HOST"], dict_env["django"], remote_env["django"])

    os.system(f"rm {dict_env['docker']}")
    logging.info(f"The environment '{dict_env['docker']}' variable was deleted.")
    os.system(f"rm {dict_env['django']}")
    logging.info(f"The environment '{dict_env['django']}' variable was deleted.")

    for folder in settings['initFolders']:
        folder = os.path.join(settings["docker"]["INSTALLFOLDER"], folder)
        inv_rsync.ssh(c, settings["REMOTE_USER"], settings["REMOTE_HOST"], f"mkdir -p {folder}")

    inv_logging.success(setproductionenvironment.__name__)



INSTALL_DEVELOPMENT_NS = Collection("install")
INSTALL_DEVELOPMENT_NS.add_task(folders)
INSTALL_DEVELOPMENT_NS.add_task(getdockercert)
INSTALL_DEVELOPMENT_NS.add_task(setenvironment)

INSTALL_PRODUCTION_NS = Collection("install")
INSTALL_PRODUCTION_NS.add_task(folders)
INSTALL_PRODUCTION_NS.add_task(setproductionenvironment)
