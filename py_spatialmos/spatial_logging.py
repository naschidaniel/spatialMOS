#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The logging module for spatialMOS,"""

import logging
import logging.handlers
from pathlib import Path

class spatial_logging:
    @classmethod
    def logging_init(cls, logging_file: Path):
        """logging_init the basic settings for logging"""
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=logging.INFO,
            handlers=[logging.handlers.TimedRotatingFileHandler(filename=logging_file, when='midnight'), logging.StreamHandler()])
