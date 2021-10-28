#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The logging module for spatialMOS,"""

import logging
import logging.handlers
import pathlib

def logging_init(file: str):
    """logging_init the basic settings for logging"""
    logging_file = pathlib.Path(f"./log/{file}")

    logging_file.parents[0].mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO,
        handlers=[logging.handlers.TimedRotatingFileHandler(filename=logging_file, when='midnight'), logging.StreamHandler()])
