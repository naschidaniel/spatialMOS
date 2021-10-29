#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
'''This base functions of the spatialMOS to project.'''

import json
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from . import inv_logging


def check_upstream(c):
    '''Check main'''
    print('Should the diff between origin/main and the current branch be checked? [yes/no]')
    answer = input()

    if answer.upper() not in ('J', 'JA', 'N', 'NEIN', 'NO', 'Y', 'YES'):
        raise ValueError(f'The input \'{answer}\' cannot be processed')
    
    if answer.upper() in ('N', 'NEIN', 'NO'):
        logging.warning('The dff between origin/main and current branch is not checked.')
    else:
        if c.run('git rev-parse --abbrev-ref HEAD', hide=True).stdout.strip() != 'main':
            raise RuntimeError('You are not in the main branch. Only the main branch can be uploaded onto the server.')

        c.run('git fetch origin main', hide=True)
        if c.run('git diff origin/main', hide=True).stdout.strip() != '':
            raise RuntimeError('Your local branch differs from upstream main (run git diff)')

        if c.run('git status --short', hide=True).stdout.strip() != '':
            raise RuntimeError('You have a dirty working directory (run git status)')


def create_folders(c):
    '''This task is used to create the folder structure'''
    inv_logging.task(create_folders.__name__)
    for folder in c.config['initFolders']:
        folder = Path('./').joinpath(folder)
        logging.info('The folder %s has been created.', folder)
        os.makedirs(folder, exist_ok=True)
    inv_logging.success(create_folders.__name__)


def read_settings():
    '''A function to read the settings file.'''
    settings_file = Path(os.getcwd()).joinpath('settings.json')

    if os.path.exists(settings_file):
        with open(settings_file, mode='r', encoding='UTF-8') as f:
            settings = json.load(f)
    else:
        raise RuntimeError(
            f'There is no {settings_file} file available. Edit the settings.example.json file from the ./fabric folder and save it in the main folder.')
    return settings


def uid_gid():
    '''return userid and groupid'''
    uid = os.getuid()
    gid = os.getgid()
    return uid, gid


def write_statusfile_and_success_logging(taskname):
    '''Write statusfile and write out the final logging msg for the task'''

    settings = read_settings()
    max_age = 60
    if taskname in settings['systemChecks'].keys():
        max_age = int(settings['systemChecks'][taskname])

    status = {
        'taskName': taskname,
        'taskFinishedTime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'taskMaxAgeTime': (datetime.now() + timedelta(minutes=max_age)).strftime('%Y-%m-%dT%H:%M:%S'),
        'maxAge': max_age,
        }

    # Provide folder structure.
    data_path = Path('./data/spool/statusfiles')
    os.makedirs(data_path, exist_ok=True)

    statusfile = data_path.joinpath(f'{taskname}.json')

    try:
        with open(statusfile, 'w', encoding='UTF-8') as f:
            json.dump(status, f)
        logging.info('The status file %s has been written.', statusfile)
    except OSError:
        logging.error('The infofile could not be written.')
    logging.info('The task \'%s\' has run successfull.', taskname)
