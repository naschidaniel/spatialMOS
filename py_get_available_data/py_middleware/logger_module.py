#!/usr/bin/env python
# coding: utf-8

"""A Logging Module for spatialMOS."""
import logging
import logging.config
import os
from datetime import datetime


def start_logging(folder, program, docker=True):
    """A function to initialize the logging module"""
    starttime = datetime.utcnow()

    logging_cfg_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.cfg')
    if docker:
        logfile = os.path.join('/log/', f"{folder}")
    else:
        logfile = os.path.join('./log/', f"{folder}")
    logfile = os.path.join(logfile, f"{program}_{datetime.now().strftime('%Y%m%d')}.log")
    logging.config.fileConfig(logging_cfg_file, \
        disable_existing_loggers=False, \
        defaults={'logfilename' : logfile})
    logging.getLogger()

    msg = 'STARTTIME | {}'.format(starttime.strftime("%Y-%m-%d %H:%M:%S"))
    logging.info("{s:{c}^{n}} ".format(s=msg, n=150, c='-'))
    return starttime

def end_logging(starttime):
    """A function to create an end logging message"""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    time_diff = datetime.utcnow() - starttime
    time_diff = time_diff.total_seconds()

    msg = 'ENDTIME | {} | TIMEDIFFERENCE | {:.1f} seconds'.format(now, time_diff)
    logging.info("{s:{c}^{n}} ".format(s=msg, n=150, c='-'))
