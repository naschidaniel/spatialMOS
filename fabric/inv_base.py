#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""This base functions of the spatialMOS to project."""

import json
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from invoke import task
from . import inv_logging

@task
def merge_statusfiles(c):
    """Merge statusfiles"""
    statusfiles_path = Path("./data/spool/statusfiles/")
    statusfiles = []
    for file in sorted(statusfiles_path.glob("*.json")):
        logging.info("The file %s will be added to the systemstatus file.", file)
        with (open(file, mode="r")) as f:
            status = json.load(f)
            status['failed'] = datetime.now() > datetime.strptime(status['taskMaxAgeTime'], '%Y-%m-%dT%H:%M:%S')
        statusfiles.append(status)

    settings = read_settings()
    systemchecks_done = sorted([c["taskName"] for c in statusfiles])
    systemchecks_available = [check for check in sorted(settings["systemChecks"].keys()) if check != merge_statusfiles.__name__]
    systemchecks_missing = [check for check in systemchecks_available if check not in systemchecks_done]

    if len(systemchecks_missing) == 0:
        status_complete = True
        logging.info("All available checks from the 'settings.json' file are checked.")
    else:
        status_complete = False
        for check in systemchecks_missing:
            logging.error("The check '%s' is missing", check)

    settings = read_settings()
    status = {
        "taskName": merge_statusfiles.__name__,
        "taskFinishedTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "taskMaxAgeTime": (datetime.now() + timedelta(minutes=int(settings['systemChecks'][merge_statusfiles.__name__]))).strftime("%Y-%m-%dT%H:%M:%S"),
        "maxAge": int(settings['systemChecks'][merge_statusfiles.__name__]),
        "complete": status_complete,
        "failed": False,
        }
    statusfiles.append(status)
    statusfiles = sorted(statusfiles, key=lambda x: x['taskName'], reverse=False)


    merge_statusfile = Path("./data/media/systemstatus.json")
    with open(merge_statusfile, 'w', encoding='utf-8') as f:
        json.dump(statusfiles, f)
    logging.info("The merged status file %s has been written.", merge_statusfile)
    inv_logging.success(merge_statusfiles.__name__)


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

    settings = read_settings()
    max_age = 60
    if taskname in settings["systemChecks"].keys():
        max_age = int(settings["systemChecks"][taskname])

    status = {
        "taskName": taskname,
        "taskFinishedTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "taskMaxAgeTime": (datetime.now() + timedelta(minutes=max_age)).strftime("%Y-%m-%dT%H:%M:%S"),
        "maxAge": max_age,
        }

    # Provide folder structure.
    data_path = Path("./data/spool/statusfiles")
    os.makedirs(data_path, exist_ok=True)

    statusfile = data_path.joinpath(f"{taskname}.json")

    try:
        with open(statusfile, "w") as f:
            json.dump(status, f)
        logging.info("The status file %s has been written.", statusfile)
    except OSError:
        logging.error("The infofile could not be written.")
    logging.info("The task '%s' has run successfull.", taskname)
