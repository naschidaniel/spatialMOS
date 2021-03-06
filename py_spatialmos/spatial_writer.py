#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The Writer module for spatialMOS,"""

import csv
from typing import Iterable, TextIO

class Writer:
    '''Writer for spatialMOS data'''

    def __init__(self, header: Iterable[str], target: TextIO) -> None:
        self.out = csv.writer(target, delimiter=";")
        self.out.writerow(header)

    def append(self, row) -> None:
        '''append a new dataset'''
        self.out.writerow(row)