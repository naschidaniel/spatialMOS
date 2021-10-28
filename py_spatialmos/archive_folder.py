#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''A script to archive csv files.'''

import os
import logging
from  pathlib import Path, PurePath
from datetime import datetime as dt
from typing import Dict, Tuple, Any

def generate_folders(folder: str) -> Tuple[Path, Path]:
    '''folders returns the destination and source folder'''
    archive_path = Path('./data/archive/')
    os.makedirs(archive_path, exist_ok=True)
    data_path = Path('./data/get_available_data/').joinpath(folder)
    return (archive_path, data_path)

def archive_folder(archive_path, data_path):
    '''archive_folder tar an order into an archive folder'''
    if not os.path.exists(data_path):
        raise RuntimeError(f'There is no folder \'{data_path}\' for archiving.')

    foldername = PurePath(data_path)
    tarfile = os.path.join(archive_path, f"{foldername.name}_{dt.utcnow().strftime('%Y-%m-%d_%H_%M_%S')}.tar.gz")
    logging.info('%s files were compressed with tar into the file \'%s\'.', len(list(Path(data_path).glob('*'))), tarfile)
    system_run = os.system(f'tar -czvf {tarfile} -C {data_path} .')

    if system_run != 0:
        raise RuntimeError(f'The archive file \'{tarfile}\' could not be created.')
    return tarfile

def run_archive_folder(parser_dict: Dict[str, Any]):
    '''run_archive_folder tar an order into an archive folder'''
    archive_path, data_path = generate_folders(parser_dict['folder'])
    tarfile = archive_folder(archive_path, data_path)
    logging.info('The archive file \'%s\' was successfully created.', tarfile)
    os.system(f"rm -rf {Path(data_path).joinpath('*')}")
    logging.info('The data in the folder \'%s\' was successfully deleted.', data_path)

def run_untar_archive_files(parser_dict: Dict[str, Any]):
    '''untar_archive_folder extracts a tar file to the data folder'''
    archive_path, data_path = generate_folders(parser_dict['folder'])
    untar_archive_files(archive_path, data_path, parser_dict['folder'])

def untar_archive_files(archive_path: Path, data_path: Path, file_prefix):
    '''untar_archive_folder extracts a tar file to the data folder'''
    for tarfile in archive_path.glob(f'{file_prefix}*.tar.gz'):
        print(tarfile)
        print(data_path)
        logging.info('The file \'%s\' will be decompressed  to \'%s\'.', tarfile, data_path)
        system_run = os.system(f'tar -xvzf {tarfile} -C {data_path}')
        if system_run != 0:
            raise RuntimeError(f'The archive file \'{archive_path}\' could not be unpacked.')
