#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The logging module for spatialMOS,"""

import logging
import logging.handlers
import pathlib
class spatial_logging:
    @classmethod
    def logging_init(cls, file: str):
        """logging_init the basic settings for logging"""
        logging_file = pathlib.Path(f"/log/{pathlib.Path(file).name}.log")
        try:
            logging_file.parents[0].mkdir(parents=True, exist_ok=True)
        except:
            logging.error("The log folder could not be created.")
            raise OSError

        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=logging.INFO,
            handlers=[logging.handlers.TimedRotatingFileHandler(filename=logging_file, when='midnight'), logging.StreamHandler()])
