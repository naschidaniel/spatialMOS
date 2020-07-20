#!/usr/bin/env python
# coding: utf-8
"""spatialMOS logging module for fabric."""

import logging
import logging.config
import os
import time
from datetime import datetime


def start_logging():
    """A function to start the logging.
    """
    logging_folder = os.path.join(os.getcwd(), "log/fabric")
    if not os.path.exists(os.path.join(os.getcwd(), "log")):
        os.mkdir(os.path.join(os.getcwd(), "log"))

    if not os.path.exists(logging_folder):
        os.mkdir(logging_folder)

    logging_cfg_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.cfg")

    logfile = os.path.join(
        logging_folder, f"logfile-{datetime.now().strftime('%Y-%m-%d')}.log")
    logging.config.fileConfig(logging_cfg_file,
                              disable_existing_loggers=False,
                              defaults={"logfilename": logfile})
    logging.getLogger()
    logging.Formatter.converter = time.localtime
    logging.info("spatialMOS fabric logging module was started.")


def task(entry=None):
    """A logging message is created with the task name.
    """
    logging.info("The task %s was started.", entry)


def cmd(entry=None):
    """A logging message is created with the additional command.
    """
    logging.info("The following command was entered: %s", entry)

def error(entry=None):
    """A function which returns the error for wrong entries."""
    logging.error("Your entry %s was incorrect. Please read the Readme.md", entry)

def success(entry=None):
    """A function which returns the successful completion of the logging.
    """
    if entry is not None and entry != "":
        logging.info("The task %s was successfully completed.", entry)
    else:
        logging.info("The program was successfully completed.")
