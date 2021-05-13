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
    MEASUREMENTS_OK = list(csv.reader(testdata, delimiter=';'))

with open(Path('./tests/testdata/suedtirol_20210101_20210102_2021-05-13T19_00_00_rh_2m.csv')) as testdata:
    MEASUREMENTS_RH_2M_OK = list(csv.reader(testdata, delimiter=';'))

with open(Path('./tests/testdata/suedtirol_20210101_20210102_2021-05-13T19_00_00_rh_2m_stations.csv')) as testdata:
    STATIONS_RH_2M_OK = list(csv.reader(testdata, delimiter=';'))

def create_csv_tempfile():
    '''create_csv_tempfile'''
    fid, temp_source_file = tempfile.mkstemp(suffix='.csv')
    os.close(fid)
    return temp_source_file
class TestExitCodes(unittest.TestCase):
    '''pytest for spatialMOS'''

    def test_combine_data_suedtirol(self):
        '''This test checks if the data can be combined'''
        get_suedtirol_data.fetch_suedtirol_data('20210101', '20210102')
        parameters = get_suedtirol_data.SuedtirolData.parameters()

        csv_files_path = Path("./data/get_available_data/suedtirol/data")

        # All measurements
        temp_measurements_file = create_csv_tempfile()
        with open(Path(temp_measurements_file), mode='w') as target:
            combine_data.combine_data(csv_files_path, parameters, target)

        with open(Path(temp_measurements_file)) as f:
            measurements = list(csv.reader(f, delimiter=';'))
        self.assertEqual(MEASUREMENTS_OK, measurements)

        # All measurements for parameter
        temp_parameter_file = create_csv_tempfile()
        temp_stations_file = create_csv_tempfile()

        with open(temp_parameter_file, mode='w') as target_parameter, open(temp_stations_file, mode='w') as target_stations:
            combine_data.data_for_spatialmos(temp_measurements_file, parameters, 'rh_2m', target_parameter, target_stations)

        with open(Path(temp_parameter_file)) as f:
            measurements_rh_2m = list(csv.reader(f, delimiter=';'))

        self.assertEqual(MEASUREMENTS_RH_2M_OK, measurements_rh_2m)
        # All stations for a parameter
        with open(Path(temp_stations_file)) as f:
            stations_rh_2m = list(csv.reader(f, delimiter=';'))

        self.assertEqual(STATIONS_RH_2M_OK, stations_rh_2m)
        os.unlink(Path(temp_measurements_file))
        os.unlink(Path(temp_parameter_file))
        os.unlink(Path(temp_stations_file))

if __name__ == '__main__':
    unittest.main(exit=False)
