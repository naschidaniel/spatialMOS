#!/usr/bin/env python
# coding: utf-8

'''Unittest for the prediction modules'''

import json
import unittest
import tempfile
from py_spatialmos import prediction
from pathlib import Path
class TestRustModules(unittest.TestCase):
    '''Test spatialMOS Rust library'''

    def test_spatial_prediction(self):

        parser_dict = {'parameter': 'tmp_2m', 'resolution': 0.5, 'date': 20210803}
        data_path_spool = Path(tempfile.mkdtemp())

        alt_file = Path("./tests/testdata/test_prediction/spatial_alt_area.csv")
        alt_area_file = Path("./tests/testdata/test_prediction/spatial_alt_area.json")
        spatialmos_run_status = dict()
        with open(Path("./tests/testdata/test_prediction/GFSE_20210803_0000_f006.json")) as f:
            gribfiles_data = json.load(f)

        # Check if climatologies files are available
        climate_spatialmos_file = Path("./tests/testdata/test_prediction/yday_215_dayminute_360.csv")
        climate_spatialmos_nwp_file = Path("./tests/testdata/test_prediction/yday_215_dayminute_360_step_006.csv")
        spatialmos_coef_file = Path("./tests/testdata/test_prediction/spatialmos_coef_tmp_2m_006.csv")

        # Check if spatialmos coefficients are available
        prediction.spatial_prediction(alt_file, alt_area_file, climate_spatialmos_file, climate_spatialmos_nwp_file, data_path_spool, gribfiles_data, spatialmos_coef_file, spatialmos_run_status, parser_dict)
        prediction.write_spatialmos_run_file(data_path_spool, gribfiles_data["anal_date"], spatialmos_run_status)

        with open(Path("./tests/testdata/test_prediction/20210803_run.json")) as f_ok, open(data_path_spool.joinpath("20210803_run.json")) as f:
            spatialmos_run_status_ok = json.load(f_ok)
            spatialmos_run_status = json.load(f)
        self.assertDictEqual(spatialmos_run_status_ok, spatialmos_run_status)

        with open(Path("./tests/testdata/test_prediction/20210803_step_006.json")) as f_ok, open(data_path_spool.joinpath("20210803_step_006.json")) as f:
            spatialmos_prediction_ok = json.load(f_ok)
            spatialmos_prediction = json.load(f)
        self.assertDictEqual(spatialmos_prediction_ok, spatialmos_prediction)


if __name__ == '__main__':
    unittest.main(exit=False)
