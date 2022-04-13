#!/usr/bin/env python3
# coding: utf-8

"""Unittest for the interpolate_gribfile functions"""

import os
import unittest
import tempfile
from typing import Tuple
from pathlib import Path
import shutil
from py_spatialmos import archive_folder


def generate_temp_data() -> Tuple[Path, Path]:
    """A helper function to create temporary direcotries and files."""
    archive_path = Path(tempfile.mkdtemp())
    fid, temp_source_file = tempfile.mkstemp(prefix="testdata", suffix=".csv")
    os.close(fid)
    data_path = Path(tempfile.mkdtemp())
    shutil.move(Path(temp_source_file), data_path)
    return (archive_path, data_path)


class TestExitCodes(unittest.TestCase):
    """pytest for archive_folder"""

    def test_archive_folder(self):
        """test_archive_folder"""
        archive_dir_path, data_path = generate_temp_data()
        try:
            tarfile = archive_folder.archive_folder(archive_dir_path, data_path)
            self.assertEqual(True, Path(tarfile).is_file())
        finally:
            shutil.rmtree(archive_dir_path)
            shutil.rmtree(data_path)

    def test_archive_folder_not_exist(self):
        """test_archive_folder"""
        archive_dir_path, data_path = generate_temp_data()
        try:
            shutil.rmtree(data_path)
            with self.assertRaises(RuntimeError):
                archive_folder.archive_folder(archive_dir_path, data_path)
        finally:
            shutil.rmtree(archive_dir_path)

    def test_untar_folder(self):
        """test_untar_folder extracts a tar file"""
        archive_dir_path, data_path = generate_temp_data()
        try:
            archive_folder.archive_folder(archive_dir_path, data_path)

            archive_folder.untar_archive_files(archive_dir_path, data_path, "tmp")
            self.assertEqual(1, len(list(Path(data_path).glob("*.csv"))))
        finally:
            shutil.rmtree(archive_dir_path)
            shutil.rmtree(data_path)


if __name__ == "__main__":
    unittest.main(exit=False)
