#!/usr/bin/env python
# coding: utf-8

'''Unittest for the spatial_util functions'''

from argparse import Namespace
import unittest
import pathlib
from py_spatialmos import spatial_util
from py_spatialmos import spatial_parser

# Convert Grib Files
test_avg_gribfile = pathlib.Path(__file__).parent.absolute().joinpath(
    './testdata/GFEE_20210416_0000_avg_f006.grb2')
test_spr_gribfile = pathlib.Path(__file__).parent.absolute().joinpath(
    './testdata/GFEE_20210416_0000_spr_f006.grb2')
test_subset = {'W': 15, 'E': 17, 'S': 46, 'N': 48, 'resolution': 0.5}
test_info_file = {'parameter': 'tmp_2m',
                  'anal_date': '2021-04-16 00:00:00',
                  'valid_date': '2021-04-16 06:00:00',
                  'yday': 106,
                  'dayminute': 360,
                  'step': 6,
                  'latitude': [46.0, 46.5, 47.0, 47.5, 48.0],
                  'longitude': [15.0, 15.5, 16.0, 16.5, 17.0],
                  'data': [['latitude', 'longitude', 'spread', 'log_spread', 'mean'],
                           [46.0, 15.0, 0.14, -1.97, 2.44],
                           [46.0, 15.5, 0.14, -1.97, 2.92],
                           [46.0, 16.0, 0.11, -2.21, 3.47],
                           [46.0, 16.5, 0.13, -2.04, 3.2],
                           [46.0, 17.0, 0.17, -1.77, 3.18],
                           [46.5, 15.0, 0.23, -1.47, -0.09],
                           [46.5, 15.5, 0.14, -1.97, 2.21],
                           [46.5, 16.0, 0.13, -2.04, 2.43],
                           [46.5, 16.5, 0.14, -1.97, 2.89],
                           [46.5, 17.0, 0.12, -2.12, 3.0],
                           [47.0, 15.0, 0.11, -2.21, -1.42],
                           [47.0, 15.5, 0.09, -2.41, 1.83],
                           [47.0, 16.0, 0.13, -2.04, 2.53],
                           [47.0, 16.5, 0.13, -2.04, 2.74],
                           [47.0, 17.0, 0.16, -1.83, 2.79],
                           [47.5, 15.0, 0.16, -1.83, -3.0],
                           [47.5, 15.5, 0.16, -1.83, -1.68],
                           [47.5, 16.0, 0.15, -1.9, 0.48],
                           [47.5, 16.5, 0.13, -2.04, 2.5],
                           [47.5, 17.0, 0.17, -1.77, 3.27],
                           [48.0, 15.0, 0.18, -1.71, -0.57],
                           [48.0, 15.5, 0.17, -1.77, -0.54],
                           [48.0, 16.0, 0.16, -1.83, 1.07],
                           [48.0, 16.5, 0.14, -1.97, 2.83],
                           [48.0, 17.0, 0.19, -1.66, 2.89]]
                  }


# Convert Parsed Dicts
TEST_ARGSINFO = {
    'modeltype': True,
    'available_modeltype': ['avg', 'spr', 'ens'],
    'begin': True,
    'begindate': True,
    'date': True,
    'end': True,
    'enddate': True,
    'folder': True,
    'available_folder': ['suedtirol', 'lwd', 'zamg'],
    'parameter': True,
    'available_parameter': ['tmp_2m', 'rh_2m'],
    'resolution': True,
    'available_resolution': [0.5, 1],
    'script': True,
    'available_script': ['get_lwd_data', 'pre_processing_prediction']}

TEST_ARGS_OK = ['--modeltype', 'avg', '--begin', '10', '--begindate', '2021-01-10', '--date', '2021-02-10',
                '--end', '11', '--enddate', '2021-01-11', '--folder', 'suedtirol', '--parameter', 'tmp_2m',
                '--resolution', '0.5', '--script', 'get_lwd_data']
TEST_PARSED_DICT_OK = {'modeltype': 'avg',
                       'begin': 10,
                       'begindate': '20210110',
                       'date': '20210210',
                       'end': 11,
                       'enddate': '20210111',
                       'folder': 'suedtirol',
                       'parameter': 'tmp_2m',
                       'resolution': 0.5,
                       'script': 'get_lwd_data',
                       }


class TestSpatialUtil(unittest.TestCase):
    '''pytest for spatial_util'''

    def test_gribfile_to_json_ok(self):
        '''This test should return valid data from a *.grb2 file'''
        json_file = spatial_util.gribfile_to_json(
            test_avg_gribfile, test_spr_gribfile, 'tmp_2m', 'avg', test_subset)
        self.assertDictEqual(test_info_file, json_file)

    def test_spatial_parser_value_in_list_ok(self):
        '''The test checks whether a value from a dict can be assigned.'''
        parsed_args = spatial_parser.spatial_parser_value_in_list(
            TEST_ARGSINFO, 'modeltype', Namespace(modeltype='avg'), {})
        self.assertDictEqual({'modeltype': 'avg'}, parsed_args)

    def test_spatial_parser_value_in_list_fail(self):
        '''The test checks raises an error because the key is not in a the available list.'''
        with self.assertRaises(RuntimeError):
            spatial_parser.spatial_parser_value_in_list(
                TEST_ARGSINFO, 'modeltype', Namespace(modeltype='moon'), {})

    def test_spatial_parser_ok(self):
        '''The test parse valid input data'''
        parsed_args = spatial_parser.spatial_parser(
            TEST_ARGS_OK, TEST_ARGSINFO)
        self.assertDictEqual(TEST_PARSED_DICT_OK, parsed_args)


if __name__ == '__main__':
    unittest.main(exit=False)
