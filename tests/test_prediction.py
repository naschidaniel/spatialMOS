#!/usr/bin/env python
# coding: utf-8

'''Unittest for the prediction modules'''

import json
import unittest
from pathlib import Path
import tempfile
from py_spatialmos import prediction

# pylint: disable=too-few-public-methods
class TestRustModules(unittest.TestCase):
    '''Test spatialMOS Rust library'''

    def test_spatial_prediction(self):
        '''test_spatial_prediction checks if the predictions are ok'''
        parser_dict = {'parameter': 'tmp_2m', 'resolution': 0.5, 'date': 20210803}
        data_path_spool = Path(tempfile.mkdtemp())

        alt_file = Path("./tests/testdata/test_prediction/spatial_alt_area.csv")
        alt_area_file = Path("./tests/testdata/test_prediction/spatial_alt_area.json")
        spatialmos_run_status = []
        with open(Path("./tests/testdata/test_prediction/GFSE_20210803_0000_f006.json"), 'r', encoding='utf-8') as f:
            gribfiles_data = json.load(f)

        # Check if climatologies files are available
        climate_spatialmos_file = Path("./tests/testdata/test_prediction/yday_215_dayminute_360.csv")
        climate_spatialmos_nwp_file = Path("./tests/testdata/test_prediction/yday_215_dayminute_360_step_006.csv")
        spatialmos_coef_file = Path("./tests/testdata/test_prediction/spatialmos_coef_tmp_2m_006.csv")
        spatial_alt_area_file = Path("./tests/testdata/test_prediction/spatial_alt_area_df.csv")
        gadm36_shape_file = Path('./tests/testdata/test_prediction/gadm36_AUT_shp/gadm36_AUT_0.shp')

        # Check if spatialmos coefficients are available
        prediction.spatial_prediction(alt_file, alt_area_file, climate_spatialmos_file, climate_spatialmos_nwp_file, data_path_spool, gribfiles_data, spatial_alt_area_file, spatialmos_coef_file, spatialmos_run_status, parser_dict, gadm36_shape_file)
        prediction.write_spatialmos_run_file(data_path_spool, spatialmos_run_status, parser_dict['parameter'])

        with open(Path("./tests/testdata/test_prediction/spatialmosrun_tmp_2m.json"), 'r', encoding='utf-8') as f_ok, open(data_path_spool.joinpath("spatialmosrun_tmp_2m.json"), 'r', encoding='utf-8') as f:
            spatialmos_run_status_ok = json.load(f_ok)
            spatialmos_run_status = json.load(f)
        self.assertEqual(spatialmos_run_status_ok, spatialmos_run_status)

        with open(Path("./tests/testdata/test_prediction/20210803_step_006.json"), 'r', encoding='utf-8') as f_ok, open(data_path_spool.joinpath("20210803_step_006.json"), 'r', encoding='utf-8') as f:
            spatialmos_prediction_ok = json.load(f_ok)
            spatialmos_prediction = json.load(f)
        self.assertDictEqual(spatialmos_prediction_ok, spatialmos_prediction)


if __name__ == '__main__':
    unittest.main(exit=False)
