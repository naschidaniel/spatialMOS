
#!/usr/bin/env python
# coding: utf-8

'''Unittest for the interpolate_gribfile functions'''

import csv
import os
from pathlib import Path
import unittest
import tempfile
from py_spatialmos import interpolate_gribfiles
from py_spatialmos.spatial_util.spatial_writer import SpatialWriter
from . import test_spatial_util

DATA_OK = [['anal_data', 'valid_data', 'yday', 'step', 'lon', 'lat', 'mean', 'mean'],
           ['[UTC]', '[UTC]', '[Integer]', '[Integer]',
           '[angle Degree]', '[angle Degree]', '[Degree C]', '[Degree C]'],
           ['2021-04-16 00:00:00', '2021-04-16 06:00:00', '106', '6', '15.0', '46.0', '0.14', '2.44'],
           ['2021-04-16 00:00:00', '2021-04-16 06:00:00', '106', '6', '15.5', '46.5', '0.14', '2.21'],
           ['2021-04-16 00:00:00', '2021-04-16 06:00:00', '106', '6', '16.3', '46.2', '0.13', '3.07']]

STATION_LOCATIONS = [[15.0, 46.0], [15.5, 46.5], [16.3, 46.2]]


class TestExitCodes(unittest.TestCase):
    '''pytest for spatialMOS'''

    def test_interpolate_gribfiles(self):
        '''test_interpolate_gribfiles tests the output of the data'''
        gribdata = test_spatial_util.test_info_file
        fid, temp_source_file = tempfile.mkstemp(suffix='.csv')
        os.close(fid)
        target = Path(temp_source_file)
        with open(target, mode='w') as f:
            csv_writer = SpatialWriter(interpolate_gribfiles.PARAMETERS, f)
            interpolate_gribfiles.interpolate_gribfiles(gribdata, csv_writer, STATION_LOCATIONS)

        try:
            with open(target) as f:
                data = list(csv.reader(f, delimiter=';'))
        finally:
            self.assertEqual(DATA_OK, data)
            os.unlink(target)

if __name__ == '__main__':
    unittest.main(exit=False)
