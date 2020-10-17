#!/usr/bin/env python
# coding: utf-8

"""A module for taking the logarithm of the spread."""

import numpy as np

def log_spread(spread):
    """A function which is used to calculate the log value of the spread."""
    log_spread = np.where(spread == 0., np.log(0.001), np.log(spread))
    return log_spread.round(3)
