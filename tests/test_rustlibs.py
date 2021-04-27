#!/usr/bin/env python
# coding: utf-8

"""Unittest for the rust module spatial_rust_util"""

import unittest
import spatial_rust_util
from py_spatialmos import get_suedtirol_data



class TestRustModules(unittest.TestCase):
    '''Test spatialMOS Rust library'''
    def test_convert_measurements_ok(self):
        '''This test ends without an error if the dictionary can be converted correctly.'''
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
            result, spatial_rust_util.convert_measurements(measurements, columns))

    def test_combine_data_ok(self):
        '''This test ends without an error if the data can be combined correctly.'''
        latitude = [45.0, 45.5, 46.0]
        longitude = [8.0, 8.5, 9.0]
        values_avg = [
            [4.600, 4.300, 3.270],
            [2.660, 4.830, 5.820],
            [-8.550, -0.610, -0.410],
        ]
        values_spr = [[0.24, 0.27, 0.32], [
            0.19, 0.18, 0.14], [0.87, 0.18, 0.15]]
        data = spatial_rust_util.combine_gribdata(
            latitude, longitude, values_avg, values_spr)

        combined_ok = [
            [45.0, 8.0, 0.24, -1.42, 4.6],
            [45.0, 8.5, 0.27, -1.30, 4.3],
            [45.0, 9.0, 0.32, -1.13, 3.27],
            [45.5, 8.0, 0.19, -1.66, 2.66],
            [45.5, 8.5, 0.18, -1.71, 4.83],
            [45.5, 9.0, 0.14, -1.96, 5.82],
            [46.0, 8.0, 0.87, -0.13, -8.55],
            [46.0, 8.5, 0.18, -1.71, -0.61],
            [46.0, 9.0, 0.15, -1.89, -0.41],
        ]
        self.assertEqual(combined_ok, data)

if __name__ == '__main__':
    unittest.main(exit=False)
