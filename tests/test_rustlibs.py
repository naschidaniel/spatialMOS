#!/usr/bin/env python
# coding: utf-8

"""Unittest for the rust module spatial_util"""

import unittest
import pathlib
import sys

# Rust Lib
import spatial_util

# spatialMOS python Scripts
py_spatialmos_path = pathlib.Path(__file__).parents[1].joinpath("py_spatialmos")
sys.path.insert(1, str(py_spatialmos_path))
get_suedtirol_data = __import__("get_suedtirol_data")


class TestRustModules(unittest.TestCase):

    def test_convert_measurements_ok(self):
        columns = list(get_suedtirol_data.SuedtirolData.parameters().keys())
        measurements = {
            '2021-01-01T00:00:00CET': {'SCODE': '82500WS', 'LAT': 46.6156, 'LONG': 11.4604, 'ALT': 2260, 'LT': 11, 'LF': 100.5},
            '2021-03-28T02:00:00CEST': {'SCODE': '82500WS', 'LAT': 46.6156, 'LONG': 11.4604, 'ALT': 6, 'LT': 17, 'LF': 60.5, 'WR': 360}}
        result = [
            ['2020-12-31 23:00:00', '82500WS', 46.6156, 11.4604,
                2260, 11, 100.5, None, None, None, None, None, None],
            ['2021-03-28 00:00:00', '82500WS', 46.6156, 11.4604,
                6, 17, 60.5, None, None, 360, None, None, None]]
        self.assertEqual(
            result, spatial_util.convert_measurements(measurements, columns))


if __name__ == '__main__':
    unittest.main(exit=False)