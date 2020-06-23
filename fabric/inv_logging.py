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


def task(task=None):
    """A logging message is created with the task name.
    """
    logging.info(f"The task {task} was started.")


def cmd(cmd=None):
    """A logging message is created with the additional command.
    """
    if cmd is not None and cmd != "":
        logging.info(f"The following command was entered: {cmd}")
    else:
        logging.info(f"The program was successfully completed.")


def success(task=None):
    """A function which returns the successful completion of the logging.
    """
    if task is not None and task != "":
        logging.info(f"The task {task} was successfully completed.")
    else:
        logging.info(f"The program was successfully completed.")
