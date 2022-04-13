#!/usr/bin/env python3
# coding: utf-8

"""Unittest for the interpolate_gribfiles functions"""

import csv
import os
from pathlib import Path
import unittest
import tempfile
from py_spatialmos import interpolate_gribfiles
from py_spatialmos.spatial_util.spatial_writer import SpatialWriter
from . import test_spatial_util

PARAMETERS = {
    "anal_data": {"name": "anal_data", "unit": "[UTC]"},
    "valid_data": {"name": "valid_data", "unit": "[UTC]"},
    "yday": {"name": "yday", "unit": "[Integer]"},
    "dayminute": {"name": "dayminute", "unit": "[Integer]"},
    "step": {"name": "step", "unit": "[Integer]"},
    "lon": {"name": "lon", "unit": "[angle Degree]"},
    "lat": {"name": "lat", "unit": "[angle Degree]"},
    "spread": {"name": "spread", "unit": "[Degree C]"},
    "log_spread": {"name": "log_spread", "unit": "[Degree C]"},
    "mean": {"name": "mean", "unit": "[Degree C]"},
}

DATA_OK = [
    [
        "anal_data",
        "valid_data",
        "yday",
        "dayminute",
        "step",
        "lon",
        "lat",
        "spread",
        "log_spread",
        "mean",
    ],
    [
        "[UTC]",
        "[UTC]",
        "[Integer]",
        "[Integer]",
        "[Integer]",
        "[angle Degree]",
        "[angle Degree]",
        "[Degree C]",
        "[Degree C]",
        "[Degree C]",
    ],
    [
        "2021-04-16 00:00:00",
        "2021-04-16 06:00:00",
        "106",
        "360",
        "6",
        "15.0",
        "46.0",
        "0.14",
        "-1.97",
        "2.44",
    ],
    [
        "2021-04-16 00:00:00",
        "2021-04-16 06:00:00",
        "106",
        "360",
        "6",
        "15.5",
        "46.5",
        "0.14",
        "-1.97",
        "2.21",
    ],
    [
        "2021-04-16 00:00:00",
        "2021-04-16 06:00:00",
        "106",
        "360",
        "6",
        "16.3",
        "46.2",
        "0.13",
        "-2.04",
        "3.07",
    ],
]

STATION_LOCATIONS = [[15.0, 46.0], [15.5, 46.5], [16.3, 46.2]]

# pylint: disable=too-few-public-methods
class TestExitCodes(unittest.TestCase):
    """pytest for interpolate_gribfiles"""

    def test_interpolate_gribfiles(self):
        """test_interpolate_gribfiles tests the output of the interpolated gribdata"""
        gribdata = test_spatial_util.test_info_file
        fid, temp_source_file = tempfile.mkstemp(suffix=".csv")
        os.close(fid)
        target = Path(temp_source_file)
        with open(target, mode="w", newline="", encoding="utf-8") as f:
            csv_writer = SpatialWriter(PARAMETERS, f)
            interpolate_gribfiles.interpolate_gribfiles(
                gribdata, csv_writer, STATION_LOCATIONS
            )

        try:
            with open(target, "r", encoding="utf-8") as f:
                data = list(csv.reader(f, delimiter=";"))
            self.assertEqual(data, DATA_OK)

        finally:
            os.unlink(target)


if __name__ == "__main__":
    unittest.main(exit=False)
