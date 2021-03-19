#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The Writer module for spatialMOS,"""

import csv
from typing import TextIO


class SpatialWriter:
    '''SpatialWriter for spatialMOS data'''

    def __init__(self, parameters: dict, target: TextIO) -> None:
        self.out = csv.writer(target, delimiter=";")
        self.out.writerow([parameters[parameter]['name'] for parameter in parameters])
        self.out.writerow([parameters[parameter]['unit'] for parameter in parameters])

    def append(self, row) -> None:
        '''append a new dataset'''
        self.out.writerow(row)
