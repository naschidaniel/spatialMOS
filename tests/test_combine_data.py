#!/usr/bin/env python
# coding: utf-8

'''Unittest for the get_data modules'''

import tempfile
import os
import csv
import unittest
from pathlib import Path
from py_spatialmos import get_suedtirol_data
from py_spatialmos import combine_data

with open(Path('./tests/testdata/suedtirol_20210101_20210102_2021-05-13T19_00_00.csv')) as testdata:
    DATA_OK = list(csv.reader(testdata, delimiter=';'))


class TestExitCodes(unittest.TestCase):
    '''pytest for spatialMOS'''

    def test_combine_data_suedtirol(self):
        '''This test checks if the data can be combined'''
        #get_suedtirol_data.fetch_suedtirol_data('20210101', '20210102')
        parameters = get_suedtirol_data.SuedtirolData.parameters()

        csv_files_path = Path("./data/get_available_data/suedtirol/data")

        fid, temp_source_file = tempfile.mkstemp(suffix='.csv')
        os.close(fid)
        with open(Path(temp_source_file), mode='w') as target:
            combine_data.combine_data(csv_files_path, parameters, target)

        with open(Path(temp_source_file)) as f:
            data = list(csv.reader(f, delimiter=';'))
        os.unlink(Path(temp_source_file))

        self.assertEqual(DATA_OK, data)


if __name__ == '__main__':
    unittest.main(exit=False)
