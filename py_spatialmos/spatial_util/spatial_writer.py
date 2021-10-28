#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The Writer module for spatialMOS,"""

import csv
from typing import List, TextIO

class SpatialWriter:
    '''SpatialWriter for spatialMOS data'''

    def __init__(self, parameters: dict, target: TextIO) -> None:
        self.out = csv.writer(target, delimiter=";")
        self.out.writerow([parameters[parameter]['name'] for parameter in parameters])
        self.out.writerow([parameters[parameter]['unit'] for parameter in parameters])

    def append(self, row: List[str]) -> None:
        '''append a new dataset'''
        self.out.writerow(row)

    def appendrows(self, rows: List[List[str]]) -> None:
        '''append multiple lines to a dataset'''
        self.out.writerows(rows)
