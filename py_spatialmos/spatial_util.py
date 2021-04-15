#!/usr/bin/python
# -*- coding: utf-8 -*-
'''spatial_util functions'''

import spatial_rust_util

def convert_measurements(measurements, columns):
    '''convert_measurements wraps the spatial_rust_util.convert_measurements function'''
    return spatial_rust_util.convert_measurements(measurements, columns)
