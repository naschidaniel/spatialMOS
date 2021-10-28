#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A module for reading local filenames"""
import os
import logging
import sys

def scandir(data_path, parameter=None, ending=None):
    """A function to browse a directory"""

    if parameter is None and ending is None:
        logging.error("Enter either a parameter or a ending.")
        sys.exit(1)

    file_list = []
    for main_folder, sub_folder, files in os.walk(data_path):
        for file in files:
            if os.path.splitext(file)[1] in [".tmp", ".idx"]:
                continue
            else:
                file_list.append(os.path.join(main_folder, file))


    if parameter is not None:
        file_list = [entry for entry in file_list if parameter in entry]

        if file_list == []:
            logging.error("There are not files in the folder %s", data_path)
            sys.exit(1)
    
    if ending is not None:
        file_list = [entry for entry in file_list if ending in entry]

        if file_list == []:
            logging.error("There are not files with the ending '%s' in the folder %s", ending, data_path)
            sys.exit(1)

    return sorted(file_list)
