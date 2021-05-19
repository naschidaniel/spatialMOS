#!/usr/bin/env python
# coding: utf-8

'''Unittest for the get_lwd_data modules'''

import csv
import unittest
import json
import tempfile
from pathlib import Path
import shutil
from py_spatialmos import get_lwd_data

class TestExitCodes(unittest.TestCase):
    '''pytest for get_lwd_data'''

    def test_fetch_lwd_data_ok(self):
        '''This test should complete successfully if all the data from lwd could be downloaded.'''
        data_path = Path(tempfile.mkdtemp())
        ogd_path = Path(tempfile.mkdtemp())
        get_lwd_data.fetch_lwd_data(data_path, ogd_path)

        try:
            for csv_file in data_path.glob('*.csv'):
                with open(csv_file) as f:
                    csv_data = list(csv.reader(f, delimiter=';'))
                self.assertEqual(len(csv_data) >= 50, True)
        finally:
            shutil.rmtree(data_path)

        try:
            for ogd_file in ogd_path.glob('*.geojson'):
                with open(ogd_file) as f:
                    ogd_data = dict(json.load(f))
                self.assertEqual(['features', 'type'], list(ogd_data.keys()))
        finally:
            shutil.rmtree(ogd_path)

if __name__ == '__main__':
    unittest.main(exit=False)
