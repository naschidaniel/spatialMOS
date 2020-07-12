#!/usr/bin/env python
# coding: utf-8

"""A module for taking the logarithm of the spread."""

import numpy as np

def log_spread(spread):
    if spread == float(0):
        log_spread_val = np.log(0.001)
    else:
        log_spread_val = np.log(spread)
    
    return round(log_spread_val, 3)