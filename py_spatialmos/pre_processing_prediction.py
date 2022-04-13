#!/usr/bin/env python3
# coding: utf-8
""" With this Python script gribfiles can be converted into json files."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict
from .spatial_util import spatial_util


def combine_gribfiles(parser_dict: Dict[str, Any]):
    """combine_gribfiles combines the previously downloaded gribfiles from the datafolder into one json file"""
    subset = {"W": 9, "E": 20, "S": 45, "N": 53, "resolution": 0.5}

    if parser_dict["resolution"] == 0.5:
        folder = "gefs_avgspr_forecast_p05"
    else:
        folder = "gefs_avgspr_forecast_p1"

    gribfiles_path = Path(
        f"./data/get_available_data/{folder}/{parser_dict['parameter']}/{parser_dict['date']}0000/"
    )
    spr_files = sorted(gribfiles_path.glob("*spr*.grb2"))
    exit_with_error = False
    for avg_gribfile in sorted(gribfiles_path.glob("*avg*.grb2")):
        logging.info("The avg file '%s' is processed", avg_gribfile)
        if "_subset.grb2" in avg_gribfile.name:
            step = f"{avg_gribfile.name[-16:-12]}"
        else:
            step = f"{avg_gribfile.name[-9:-5]}"

        is_spr_gribfile = False
        for spr_gribfile in spr_files:
            if spr_gribfile.match(f"*{step}*"):
                is_spr_gribfile = True
                logging.info(
                    "The spr file '%s' was found and will be processed", spr_gribfile
                )
                json_file = gribfiles_path.joinpath(
                    f"./GFSE_{parser_dict['date']}_0000_{step}.json"
                )
                logging.info("The data are written to '%s'.", json_file)
                with open(Path(json_file), mode="w", encoding="utf-8") as f:
                    json.dump(
                        spatial_util.gribfiles_to_json(
                            avg_gribfile, spr_gribfile, parser_dict["parameter"], subset
                        ),
                        f,
                    )
                break

        if not is_spr_gribfile:
            logging.error("No spr_gribfile could be found for '%s'.", avg_gribfile)
            exit_with_error = True

    for file in gribfiles_path.glob("**/*"):
        if ".json" not in file.name and file.is_file():
            logging.info("The file '%s' will bee deleted.", file)
            os.remove(file)

    if exit_with_error:
        raise RuntimeError("Not all gribfiles could be combined.")
