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
    starttime = logger_module.start_logging("get_available_data", "archiv", docker=False)
    parser_dict = spatial_parser.spatial_parser(folder=True, name_folder=["uibk", "grib", "zamg"])

    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

    # Provide folder structure.
    archive_path = "./data/get_available_data/archive"
    archive_path = os.path.join(basedir, archive_path)
    if not os.path.exists(f"{archive_path}"):
        os.mkdir(f"{archive_path}")

    # Folder to tar
    path_to_tar = os.path.join(basedir, "data")
    path_to_tar = os.path.join(path_to_tar, "get_available_data")
    path_to_tar = os.path.join(path_to_tar, parser_dict["folder"])
    if not os.path.exists(archive_path):
        os.makedirs(archive_path)
        logging.info(f"The archive folder '{archive_path}' was created.")
    
    count_files_to_tar = 0
    if os.path.exists(path_to_tar):
        for root, dirs, files in os.walk(path_to_tar):
            count_files_to_tar += len(files)
        tarfile = os.path.join(archive_path, "{}_{}.tar.gz".format(parser_dict["folder"], datetime.utcnow().strftime("%Y-%m-%d_%H_%M_%S")))

        logging.info("Action: {:35} | Files: {} | {}".format("count_files_to_tar ", count_files_to_tar, tarfile))
        tarfileStatus = os.system(f"tar -czvf {tarfile} -C {path_to_tar} .")

        if tarfileStatus == 0:
            logging.info(f"The archive file '{tarfile}' was successfully created.")
        else:
            logging.error(f"The archive file '{tarfile}' could not be created.")
            sys.exit(1)
    else:
        logging.error(f"There is no folder '{path_to_tar}' for archiving.")
        sys.exit(1)

    try:
        os.system("rm -rf {}".format(path_to_tar))
        logging.info(f"The data folder '{path_to_tar}'was successfully deleted.")
    except:
        logging.error(f"The data folder '{path_to_tar}' could not be deleted.")
        sys.exit(1)

    logger_module.end_logging(starttime)
