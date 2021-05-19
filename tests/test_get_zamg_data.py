#!/usr/bin/env python
# coding: utf-8

'''Unittest for the get_zamg_data'''

import csv
import unittest
import tempfile
from pathlib import Path
import shutil
from py_spatialmos import get_zamg_data

class TestExitCodes(unittest.TestCase):
    '''pytest for get_zamg_data'''

    def test_get_zamg_stations_ok(self):
        '''This test checks if the station csv file could be parsed correctly.'''
        station_info_ok = {
            'SNA':
             {'alt': 'STATIONSHÖHE',
              'lon': 'LÄNGE DEZI',
              'lat': 'BREITE DEZI',
              'rawdata': ['SYNNR', 'NAME', 'BUNDESLAND', 'LÄNGE', 'BREITE',
                          'STATIONSHÖHE', 'BEGINNDATUM', 'ORDNUNG', 'LÄNGE DEZI', 'BREITE DEZI']
              },
             '2PA':
             {'alt': '2251',
              'lon': '11,4622221',
              'lat': '47,20888901',
              'rawdata': ['11126', 'PATSCHERKOFEL', 'TIR', '112744', '471232',
                          '2251', '19930801', 'TAWES', '11,4622221', '47,20888901']
              },
             '5IN':
             {'alt': '578',
              'lon': '11,38416672',
              'lat': '47,25999832',
              'rawdata': ['11320', 'INNSBRUCK-UNIV.', 'TIR', '112303', '471536',
                          '578', '19860501', 'TAWES', '11,38416672', '47,25999832']
              }
             }


        station_info = get_zamg_data.ZamgData.get_station_locations()
        self.assertDictEqual(station_info_ok['SNA'], station_info['SNA'])
        self.assertDictEqual(station_info_ok['2PA'], station_info['2PA'])
        self.assertDictEqual(station_info_ok['5IN'], station_info['5IN'])

    def test_fetch_zamg_data_ok(self):
        '''This test should complete successfully if all the data from zamg could be downloaded.'''
        data_path = Path(tempfile.mkdtemp())
        get_zamg_data.fetch_zamg_data(data_path)

        try:
            for csv_file in data_path.glob('*.csv'):
                with open(csv_file) as f:
                    csv_data = list(csv.reader(f, delimiter=';'))
                self.assertEqual(len(csv_data) >= 50, True)
        finally:
            shutil.rmtree(data_path)

if __name__ == '__main__':
    unittest.main(exit=False)
