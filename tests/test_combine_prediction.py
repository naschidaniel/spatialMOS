#!/usr/bin/env python3
# coding: utf-8

'''Unittest for the combine_predictions modules'''

import json
import unittest
from pathlib import Path
import shutil
import tempfile
from py_spatialmos import combine_predictions

 # pylint: disable=too-few-public-methods
class TestCombinePredictions(unittest.TestCase):
    '''pytest for combine_predictions'''

    def test_combine_predictions(self):
        '''This test checks if the two json files be combined'''
        parser_dict = {'parameter': 'tmp_2m', 'date': 20210803}
        data_path_spool = Path('./tests/testdata/test_prediction/')
        temp_path = Path(tempfile.mkdtemp())

        try:
            data = combine_predictions.merge_predictions(parser_dict, data_path_spool, ['006', '012', '018'])
            temp_outfile = temp_path.joinpath('20210803_predictions.json')
            combine_predictions.write_merged_predictions_file(data, temp_outfile)
            with open(Path("./tests/testdata/test_prediction/20210803_predictions.json"), 'r', encoding='utf-8') as f_ok, open(temp_outfile, 'r', encoding='utf-8') as f:
                spatialmos_merged_prediction_ok = json.load(f_ok)
                spatialmos_merged_prediction = json.load(f)
                self.assertDictEqual(spatialmos_merged_prediction_ok, spatialmos_merged_prediction)
        finally:
            shutil.rmtree(temp_path)

if __name__ == '__main__':
    unittest.main(exit=False)
