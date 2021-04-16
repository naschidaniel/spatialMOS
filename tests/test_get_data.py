#!/usr/bin/env python
# coding: utf-8

'''Unittest for the get_data modules'''

import unittest
from py_spatialmos import get_lwd_data
from py_spatialmos import get_suedtirol_data
from py_spatialmos import get_zamg_data

class TestExitCodes(unittest.TestCase):
    '''pytest for spatialMOS'''

    @staticmethod
    def test_fetch_lwd_data_ok():
        '''This test should complete successfully if all the data from lwd could be downloaded.'''
        get_lwd_data.fetch_lwd_data()

    @staticmethod
    def test_fetch_suedtirol_data_ok():
        '''This test should complete successfully if all the data from suedtirol could be downloaded.'''
        get_suedtirol_data.fetch_suedtirol_data('20210101', '20210102')

    @staticmethod
    def test_fetch_zamg_data_ok():
        '''This test should complete successfully if all the data from zamg could be downloaded.'''
        get_zamg_data.fetch_zamg_data()

if __name__ == '__main__':
    unittest.main(exit=False)
