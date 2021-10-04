#!/usr/bin/env python
# coding: utf-8
"""spatialMOS logging module for fabric."""

import logging
import logging.handlers
import time


def start_logging():
    """A function to start the logging.
    """
    logging.basicConfig(
    format='%(asctime)s\t%(process)d\t%(levelname)s\t%(message)s',
    level=logging.INFO,
    handlers=[
        logging.handlers.TimedRotatingFileHandler(
            filename='log/fabric.log', when='midnight'),
        logging.StreamHandler()])

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
