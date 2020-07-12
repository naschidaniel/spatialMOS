#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A script to archive csv files."""

import os
import sys
import logging
from datetime import datetime
from py_middleware import spatial_parser
from py_middleware import logger_module


# Main
if __name__ == "__main__":
    starttime = logger_module.start_logging("get_available_data", "archive", docker=False)
    parser_dict = spatial_parser.spatial_parser(folder=True, name_folder=["gefs_forecast", "gefs_reforecast", "suedtirol", "uibk", "wetter_at", "zamg"])

    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

    # Provide folder structure.
    archive_path = "./data/archive"
    archive_path = os.path.join(basedir, archive_path)
    if not os.path.exists(f"{archive_path}"):
        os.mkdir(f"{archive_path}")

    # Folder to tar
    path_to_tar = os.path.join(basedir, "data")
    path_to_tar = os.path.join(path_to_tar, "get_available_data")
    path_to_tar = os.path.join(path_to_tar, parser_dict["folder"])
    if not os.path.exists(archive_path):
        os.makedirs(archive_path)
        logging.info("The archive folder '%s' was created.", archive_path)
    
    count_files_to_tar = 0
    if os.path.exists(path_to_tar):
        for root, dirs, files in os.walk(path_to_tar):
            count_files_to_tar += len(files)
        tarfile = os.path.join(archive_path, "{}_{}.tar.gz".format(parser_dict["folder"], datetime.utcnow().strftime("%Y-%m-%d_%H_%M_%S")))

        logging.info("Action: {:35} | Files: {} | {}".format("count_files_to_tar ", count_files_to_tar, tarfile))
        tarfileStatus = os.system(f"tar -czvf {tarfile} -C {path_to_tar} .")

        if tarfileStatus == 0:
            logging.info("The archive file '%s' was successfully created.", tarfile)
        else:
            logging.error("The archive file '%s' could not be created.", tarfile)
            sys.exit(1)
    else:
        logging.error("There is no folder '%s' for archiving.", path_to_tar)
        sys.exit(1)

    try:
        os.system("rm -rf {}".format(path_to_tar))
        logging.info("The data folder '%s' was successfully deleted.", path_to_tar)
    except:
        logging.error("The data folder '%s' could not be deleted.", path_to_tar)
        sys.exit(1)

    logger_module.end_logging(starttime)
