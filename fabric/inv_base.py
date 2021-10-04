#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""This base functions of the spatialMOS to project."""

import json
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta


def read_settings():
    """A function to read the settings file."""
    settings_file = Path(os.getcwd()).joinpath("settings.json")

    if os.path.exists(settings_file):
        with open(settings_file) as f:
            settings = json.load(f)
    else:
        raise RuntimeError(
            f"There is no {settings_file} file available. Edit the settings.example.json file from the ./fabric folder and save it in the main folder.")

    return settings


def uid_gid(c):
    uid = os.getuid()
    gid = os.getgid()
    return uid, gid

def docker_environment(c):
    """The function generates the docker environment variables."""
    settings = read_settings()
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


def write_statusfile_and_success_logging(taskname, cmd):
    """Write statusfile and write out the final logging msg for the task"""
    cmd_args_dict = {}
    i = 1
    cmd_args = cmd.split(" ")
    for arg in cmd_args:
        if "--" in arg:
            cmd_args_dict[arg[2:]] = cmd_args[i]
        i += 1

    check_name = taskname
    display_name_website = ""
    for key, value in cmd_args_dict.items():
        if key == "date":
            continue
        check_name = f"{check_name}__{value}"
        display_name_website = f"{display_name_website} {value}"

    check_name = check_name.replace(".", "_")
    settings = read_settings()

    max_age = 60
    if check_name in settings["systemChecks"].keys():
        max_age = int(settings["systemChecks"][check_name])

    if display_name_website == "":
        display_name_website = taskname

    status = {
        "taskName": taskname,
        "taskFinishedTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "taskMaxAgeTime": (datetime.now() + timedelta(minutes=max_age)).strftime("%Y-%m-%dT%H:%M:%S"),
        "failed": datetime.now() >= (datetime.now() + timedelta(minutes=max_age)),
        "cmd": cmd,
        "cmdArgs": cmd_args_dict,
        "checkName": check_name,
        "displayNameWebsite": display_name_website,
        }

    # Provide folder structure.
    data_path = Path("./data/spool/statusfiles")
    os.makedirs(data_path, exist_ok=True)

    statusfile = data_path.joinpath(f"{check_name}.json")

    try:
        with open(statusfile, "w") as f:
            json.dump(status, f)
        logging.info("The status file %s has been written.", statusfile)
    except OSError:
        logging.error("The infofile could not be written.")
    logging.info("The task '%s' with the command '%s' has run successfull.", taskname, cmd)
