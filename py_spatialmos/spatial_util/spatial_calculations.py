#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
'''spatial_calculations is used to do some calculations for spatialMOS.'''

import numpy as np

def log_spread(spread):
    '''A function which is used to calculate the log value of the spread.'''
    log_spread_val = np.where(spread == 0., np.log(0.001), np.log(spread))
    return log_spread_val.round(3)