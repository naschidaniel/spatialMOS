#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A module for calculate meteorological parameters"""

import numpy as np

# Functions
def spfh2rh(spfh_2m, pres_sfc, tmp_2m):
    """A function to calculate the relative humidity"""
    saturation_vapour_pressure = 6.112 * np.exp((17.67 * tmp_2m) / (tmp_2m + 243.5))
    vapour_pressure = spfh_2m * pres_sfc / (0.378 * spfh_2m + 0.622)
    relative_humidity = vapour_pressure / saturation_vapour_pressure

    relative_humidity[relative_humidity > 100] = 100.0
    relative_humidity[relative_humidity < 0] = 0.0
    return relative_humidity

def uv2wind(ugrd_10m, vgrd_10m):
    """A function to calculate the wind speed from the u and v component."""
    wind_speed_squared = ugrd_10m**2 + vgrd_10m**2
    wind_speed = np.sqrt(wind_speed_squared)
    return wind_speed
