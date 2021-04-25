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
        data = [[2.39, 2.10, 2.05, 2.71, 3.21, 3.23,
                2.86, 2.83, 3.10, 3.41, 3.65, 3.73,
                3.50, 3.42, 3.42, 3.22, 3.12, 3.18,
                3.15, 3.09, 3.27, 3.37, 3.61, 4.10,
                4.49],
                [2.76, 2.61, 2.06, 2.15, 2.79, 3.06,
                 3.38, 3.37, 3.23, 3.43, 3.67, 3.91,
                 3.90, 3.94, 3.65, 3.56, 3.57, 3.41,
                 3.31, 3.35, 3.56, 3.59, 3.70, 4.00,
                 4.25]]
        latitude = [45.0, 45.5]
        longitude = [8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5,
                     14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0]
        result = spatial_rust_util.combine_data(data, latitude, longitude)
        print(result)
        assert False

if __name__ == '__main__':
    unittest.main(exit=False)
