#!/usr/bin/env python3
# coding: utf-8

'''Unittest for the combine_climatology module'''


import csv
import unittest
from pathlib import Path
import shutil
import tempfile
from py_spatialmos import combine_climatology


# pylint: disable=too-few-public-methods
class TestCombinePredictions(unittest.TestCase):
    '''pytest for combine_predictions'''

    def test_combine_nwp_climatology(self):
        '''This test checks if a nwp climatology for gamlss can be created'''
        gfse_file = Path('./tests/testdata/test_combine_climatology/GFSE_f006.csv')
        measurements_files = Path('./tests/testdata/test_combine_climatology/all_measurements_tmp_2m.csv')
        temp_path = Path(tempfile.mkdtemp())
        temp_outfile = temp_path.joinpath('tmp_2m_006.csv')

        try:
            combine_climatology.combine_nwp_climatology(gfse_file, measurements_files, temp_outfile)
            with open(Path("./tests/testdata/test_combine_climatology/tmp_2m_006.csv"), 'r', encoding='utf-8') as f_ok, open(temp_outfile, 'r', encoding='utf-8') as f:
                expected = list(csv.reader(f_ok))
                result = list(csv.reader(f))
                self.assertEqual(result, expected)
        finally:
            shutil.rmtree(temp_path)


if __name__ == '__main__':
    unittest.main(exit=False)
