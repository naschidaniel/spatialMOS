#!/usr/bin/env python3
# coding: utf-8
"""spatialMOS logging module for fabric."""

import logging
import logging.handlers
import time


def start_logging():
    """A function to start the logging."""
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
        handlers=[
            logging.handlers.TimedRotatingFileHandler(
                filename="log/fabric.log", when="midnight"
            ),
            logging.StreamHandler(),
        ],
    )

    logging.getLogger()
    logging.Formatter.converter = time.localtime
    logging.info("spatialMOS fabric logging module has started.")


def task(entry):
    """A logging message is created with the task name."""
    logging.info("The task %s has started.", entry)


def success(entry):
    """A function which returns the successful completion of the logging."""
    logging.info("The task %s has been successfully completed.", entry)
