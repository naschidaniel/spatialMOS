#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A script to combine data from get_lwd_data, get_suedtirol_data and get_zamg_data"""

import csv
import logging
import os
from pathlib import Path
from typing import Any, Dict, TextIO
from . import get_lwd_data
from . import get_suedtirol_data
from . import get_zamg_data
from .spatial_util import spatial_writer


def run_combine_data(parser_dict: Dict[str, Any]):
    """run_combine_data runs combine_data"""
    target_path = Path("./data/get_available_data/measurements/")
    os.makedirs(target_path, exist_ok=True)
    if parser_dict["folder"] == "lwd":
        parameters = get_lwd_data.LwdData.parameters()
    elif parser_dict["folder"] == "suedtirol":
        parameters = get_suedtirol_data.SuedtirolData.parameters()
    else:
        parameters = get_zamg_data.ZamgData.parameters()
    targetfile = Path(target_path).joinpath(
        f"{parser_dict['folder']}_measurements_all.csv"
    )
    with open(targetfile, mode="w", newline="", encoding="utf-8") as target:
        csv_files_path = Path(f"./data/get_available_data/{parser_dict['folder']}")
        combine_data(csv_files_path, parameters, target)


def combine_data(
    csv_files_path: Path, parameters: Dict[str, Dict[str, str]], target: TextIO
):
    """combine_data creates one csv file with all the data from one dataprovider"""
    parameters_keys = [parameters[k]["name"] for k in parameters]
    parameters_units = [parameters[k]["unit"] for k in parameters]

    writer = spatial_writer.SpatialWriter(parameters, target)
    for csv_file in sorted(csv_files_path.glob("**/*.csv")):
        logging.info("The file %s is added to %s", csv_file, target)
        with open(csv_file, mode="r", encoding="utf-8") as f:
            data = list(csv.reader(f, delimiter=";"))

        if len(data) <= 3:
            logging.warning(
                "There is no data so the csv file '%s' will be skiped.", csv_file
            )
            continue

        if data[0] != parameters_keys and data[1] != parameters_units:
            logging.error("Header Keys expected: %s", parameters_keys)
            logging.error("Header Keys     File: %s", data[0])
            logging.error("Header Units Expected: %s", parameters_units)
            logging.error("Header Units     File: %s", data[1])
            raise RuntimeError(f"The header in the file {csv_file} is not supported")
        writer.appendrows(data[2:])
