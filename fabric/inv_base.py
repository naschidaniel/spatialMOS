#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""This base functions of the spatialMOS to project."""

import json
import sys
import os
import logging
from datetime import datetime

def manage_py(c, cmd):
    """The function executes the django manage.py command."""
    user, group = uid_gid(c)
    docker_compose(c, f"run -u {user}:{group} django python3 /www/site/manage.py {cmd}", pty=True)


def generate_lastcommit(c):
    """A function to create the last commit ID"""
    lastcommit = c.run("git rev-parse --short HEAD")
    lastcommit = lastcommit.stdout.strip()
    logging.info("Last commit number is %s", lastcommit)
    return lastcommit


def read_settings(what):
    """A function to read the settings file."""
    settings_file = os.path.join(os.path.join(
        os.getcwd(), "settings.json"))

    if what not in ["development", "production"]:
        logging.error(
            f"No settings could be found in the file {settings_file} for your input: {what}")
        sys.exit(1)

    if os.path.exists(settings_file):
        with open(settings_file) as f:
            settings = json.load(f)
    else:
        fabric_folder = os.path.join(os.getcwd(), "fabric")
        logging.error(
            f"There is no {settings_file} file available. Edit the settings.example.json file in the {fabric_folder} folder and save it in the main folder.")
        sys.exit(1)

    return settings[what]


def uid_gid(c):
    if c.config["collection"] == "production":
        uid = c.config["docker"]["USERID"]
        gid = c.config["docker"]["GROUPID"]
    else:
        uid = os.getuid()
        gid = os.getgid()
    return uid, gid


def docker_environment(c):
    """The function generates the docker environment variables."""
    settings = read_settings(c.config["collection"])
    docker_env_variables = settings["docker"]
    if c.config["collection"] in ["development"]:
        uid, gid = uid_gid(c)
        docker_env_variables["USERID"] = f"{uid}"
        docker_env_variables["GROUPID"] = f"{gid}"
    return docker_env_variables


def dockerdaemon(c, cmd, **kwargs):
    """A function to start the docker daemon."""
    command = ["docker"]
    command.append(cmd)
    return c.run(" ".join(command), env=docker_environment(c), **kwargs)


def docker_compose(c, cmd, **kwargs):
    """A function to start docker-compose."""
    command = ["docker-compose"]
    for config_file in c.docker_compose_files:
        command.append("-f")
        command.append(config_file)
    command.append(cmd)
    return c.run(" ".join(command), env=docker_environment(c), **kwargs)


def write_statusfile(taskname, cmd):
    """Write a statusfile for a successful run which can be imported into django"""
    timestr = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    status = {
        "taskname": taskname,
        "task_finished_time": timestr,
        "cmd": cmd
        }

    # Provide folder structure.
    data_path = "./data/spool/statusfiles"
    if not os.path.exists(f"{data_path}"):
        os.mkdir(f"{data_path}")
    statusfile = f"{data_path}/statusfile_{timestr}.json"

    try:
        with open(statusfile, "w") as f:
            json.dump(status, f)
            f.close()
        logging.info("The status file %s was written.", statusfile)
    except:
        logging.error("The infofile could not be written.")
        sys.exit(1)


def write_statusfile_and_success_logging(taskname, cmd):
    """Write statusfile and write out the final logging msg for the task"""
    write_statusfile (taskname, cmd)
    logging.info("The task '%s' with the command '%s' has run successfull.", taskname, cmd)
