#!/usr/bin/python
# -*- coding: utf-8 -*-
'''A script to archive csv files.'''

import os
import logging
import pathlib
from datetime import datetime


def run_archive_folder(parser_dict):
    '''run_archive_folder tar an order into an archive folder'''

    archive_path = pathlib.Path('./data/archive/')
    os.makedirs(archive_path, exist_ok=True)

    path_to_tar = pathlib.Path(
        './data/get_available_data/').joinpath(parser_dict['folder'])

    count_files_to_tar = 0
    if os.path.exists(path_to_tar):
        for _, _, files in os.walk(path_to_tar):
            count_files_to_tar += len(files)
        utc_now_str = datetime.utcnow().strftime('%Y-%m-%d_%H_%M_%S')
        tarfile = os.path.join(archive_path, f"{parser_dict['folder']}_{utc_now_str}.tar.gz")
        logging.info('%s files were compressed with tar into the file \'%s\'.', count_files_to_tar, tarfile)
        system_run = os.system(f'tar -czvf {tarfile} -C {path_to_tar} .')

        if system_run != 0:
            raise RuntimeError(
                'The archive file \'%s\' could not be created.' % tarfile)
        logging.info('The archive file \'%s\' was successfully created.', tarfile)
    else:
        raise RuntimeError(
            'There is no folder \'%s\' for archiving.' % path_to_tar)

    os.system(f"rm -rf {pathlib.Path(path_to_tar).joinpath('*')}")
    logging.info(
        'The data in the folder \'%s\' was successfully deleted.', path_to_tar)
