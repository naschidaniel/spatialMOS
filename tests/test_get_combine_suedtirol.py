#!/usr/bin/env python
# coding: utf-8

'''Unittest for the get_suedtirol_data and combine_data modules'''

import tempfile
import os
import csv
import unittest
import shutil
from pathlib import Path
from py_spatialmos import get_suedtirol_data
from py_spatialmos import combine_data

with open(Path('./tests/testdata/test_get_combine_suedtirol/suedtirol_20210101_20210102_2021-05-13T19_00_00.csv'), 'r',  encoding='utf-8') as testdata:
    MEASUREMENTS_OK = list(csv.reader(testdata, delimiter=';'))

with open(Path('./tests/testdata/test_get_combine_suedtirol/suedtirol_20210101_20210102_2021-05-13T19_00_00_rh_2m.csv'), 'r',  encoding='utf-8') as testdata:
    MEASUREMENTS_RH_2M_OK = list(csv.reader(testdata, delimiter=';'))

with open(Path('./tests/testdata/test_get_combine_suedtirol/suedtirol_20210101_20210102_2021-05-13T19_00_00_rh_2m_stations.csv'), 'r', encoding='utf-8') as testdata:
    STATIONS_RH_2M_OK = list(csv.reader(testdata, delimiter=';'))

PARAMETERS = get_suedtirol_data.SuedtirolData.parameters()

def create_csv_tempfile():
    '''create_csv_tempfile'''
    fid, temp_source_file = tempfile.mkstemp(suffix='.csv')
    os.close(fid)
    return temp_source_file
class TestExitCodes(unittest.TestCase):
    '''pytest for spatialMOS'''

    def test_combine_data_suedtirol(self):
        '''This test checks if the data can be combined'''
        csv_files_temp_path = Path(tempfile.mkdtemp())
        get_suedtirol_data.fetch_suedtirol_data('20210101', '20210102', csv_files_temp_path)
        # All measurements
        temp_measurements_file = create_csv_tempfile()
        with open(Path(temp_measurements_file), mode='w', newline='', encoding='utf-8') as target:
            combine_data.combine_data(csv_files_temp_path, PARAMETERS, target)

        with open(Path(temp_measurements_file), mode='r', encoding='utf-8') as f:
            measurements = list(csv.reader(f, delimiter=';'))

        self.assertEqual(len(MEASUREMENTS_OK), len(measurements))
        self.assertEqual(MEASUREMENTS_OK, measurements)
        os.unlink(Path(temp_measurements_file))
        shutil.rmtree(csv_files_temp_path)

    def test_data_for_spatialmos(self):
        '''This test checks if data for the parameters can be created'''
        # All measurements for parameter
        temp_parameter_file = create_csv_tempfile()
        temp_stations_file = create_csv_tempfile()

        with open(temp_parameter_file, mode='w', newline='', encoding='ISO-8859-1') as target_parameter, open(temp_stations_file, mode='w', newline='', encoding='ISO-8859-1') as target_stations:
            combine_data.data_for_spatialmos(MEASUREMENTS_OK, PARAMETERS, 'rh_2m', target_parameter, target_stations)

        with open(Path(temp_parameter_file), 'r', encoding='ISO-8859-1') as f:
            measurements_rh_2m = list(csv.reader(f, delimiter=';'))

        self.assertEqual(MEASUREMENTS_RH_2M_OK[0:9], measurements_rh_2m[0:9])
        # All stations for a parameter
        with open(Path(temp_stations_file), 'r', encoding='ISO-8859-1') as f:
            stations_rh_2m = list(csv.reader(f, delimiter=';'))

        self.assertEqual(STATIONS_RH_2M_OK[0:9], stations_rh_2m[0:9])
        os.unlink(Path(temp_parameter_file))
        os.unlink(Path(temp_stations_file))

if __name__ == '__main__':
    unittest.main(exit=False)
