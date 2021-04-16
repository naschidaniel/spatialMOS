#!/usr/bin/python
# -*- coding: utf-8 -*-
'''spatial_util functions'''

from typing import Dict, Union
import spatial_rust_util

def convert_measurements(measurements: Dict[str, Dict[str, Union[str, float]]], columns: list[str]):
    '''convert_measurements wraps the spatial_rust_util.convert_measurements function'''
    return spatial_rust_util.convert_measurements(measurements, columns)
