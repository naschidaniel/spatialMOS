#!/usr/bin/env python
# coding: utf-8

'''Unittest for the rust module get_data'''

import unittest
import pathlib
from py_spatialmos import spatial_util

test_avg_gribfile = pathlib.Path(__file__).parent.absolute().joinpath('./testdata/GFEE_20210416_0000_avg_f006.grb2')
test_spr_gribfile = pathlib.Path(__file__).parent.absolute().joinpath('./testdata/GFEE_20210416_0000_spr_f006.grb2')

test_subset = {'E': 20, 'W': 8, 'S': 45, 'N': 53}

test_info_file = {"parameter": "tmp_2m",
                  "modeltype": "avg",
                  "anal_date": "2021-04-16 00:00:00",
                  "valid_date": "2021-04-16 06:00:00",
                  "yday": 106,
                  "dayminute": 360,
                  "step": 6,
                  "latitude": [45.0, 45.5, 46.0, 46.5, 47.0, 47.5, 48.0, 48.5, 49.0, 49.5, 50.0, 50.5, 51.0, 51.5, 52.0, 52.5, 53.0],
                  "longitude": [8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0],
                #   "data": [[45, 8, 0.24, -1.427, 4.60001],
                #            [45, 8.5, 0.27, -1.309, 4.30002],
                #            [45, 9, 0.32, -1.139, 3.27002],
                #            [45, 9.5, 0.28, -1.273, 2.92001],
                #            [45, 10, 0.28, -1.273, 3.38],
                #            [45, 10.5, 0.2, -1.609, 3.95999],
                #            [45, 11, 0.12, -2.12, 4.48001],
                #            [45, 11.5, 0.1, -2.303, 4.84],
                #            [45, 12, 0.22, -1.514, 6.26001],
                #            [45, 12.5, 0.15, -1.897, 9.64999],
                #            [45, 13, 0.13, -2.04, 9.64001],
                #            [45, 13.5, 0.11, -2.207, 8.08002],
                #            [45, 14, 0.11, -2.207, 5.29001],
                #            [45, 14.5, 0.14, -1.966, 7.16],
                #            [45, 15, 0.19, -1.661, 1.79001],
                #            [45, 15.5, 0.19, -1.661, 1.05002],
                #            [45, 16, 0.17, -1.772, 2.17001],
                #            [45, 16.5, 0.15, -1.897, 2.99002],
                #            [45, 17, 0.17, -1.772, 3.01001],
                #            [45, 17.5, 0.14, -1.966, 3.24002]]
                  }
class TestSpatialUtil(unittest.TestCase):
    '''pytest for spatial_util'''

    def test_gribfile_to_json_ok(self):
        '''This test should return valid data from a *.grb2 file'''
        subset = {'E': 20, 'W': 8, 'S': 45, 'N': 53, 'resolution': 0.5}
        json_file = spatial_util.gribfile_to_json(test_avg_gribfile, test_spr_gribfile, 'tmp_2m', 'avg', subset)
        print(json_file)
        assert(False)
        #self.assertDictEqual(test_info_file, json_file)

if __name__ == '__main__':
    unittest.main(exit=False)
