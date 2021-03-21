#!/usr/bin/env python
# coding: utf-8

"""Unittest for the rust module suedtirol"""

import unittest
import pathlib
import sys

# spatialMOS python Scripts
py_spatialmos_path = pathlib.Path(__file__).parents[1].joinpath("py_spatialmos")
sys.path.insert(1, str(py_spatialmos_path))
get_suedtirol_data = __import__("get_suedtirol_data")


class TestExitCodes(unittest.TestCase):

    def test_fetch_suedtirol_data_ok(self):
        """This test should complete successfully if all the data could be downloaded."""
        get_suedtirol_data.fetch_suedtirol_data('20210101', '20210102')

if __name__ == '__main__':
    unittest.main(exit=False)
