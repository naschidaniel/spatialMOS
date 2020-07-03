#!/usr/bin/python
# -*- coding: utf-8 -*-

"""A module for reading local filenames"""
import os
import logging
import sys

def scandir(data_path, parameter):
    """A function to browse a directory"""
    file_list = []
    for main_folder, sub_folder, files in os.walk(data_path):
        for x in files:
            if parameter in x:
                if '.tmp' not in x[-4:]:
                    file_list.append(os.path.join(main_folder, x))
                else:
                    continue
            else:
                continue
    
    file_list = sorted(file_list)
    
    if file_list == []:
        logging.error("There is no data in the %s folder.", data_path)
        sys.exit(1)
    
    return file_list
