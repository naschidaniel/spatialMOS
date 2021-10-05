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




def write_statusfile_and_success_logging(taskname):
    """Write statusfile and write out the final logging msg for the task"""

    check_name = taskname
    settings = read_settings()

    max_age = 60
    if check_name in settings["systemChecks"].keys():
        max_age = int(settings["systemChecks"][check_name])

    status = {
        "taskName": taskname,
        "taskFinishedTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "taskMaxAgeTime": (datetime.now() + timedelta(minutes=max_age)).strftime("%Y-%m-%dT%H:%M:%S"),
        "failed": datetime.now() >= (datetime.now() + timedelta(minutes=max_age)),
        "checkName": check_name,
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
    logging.info("The task '%s' has run successfull.", taskname)
