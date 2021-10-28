#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
'''This collection is used to ensure data exchange between local PC and server.'''

import subprocess
import logging
from itertools import chain, repeat
from invoke import task, Collection
from . import inv_logging
from . import util

def str2bool(string):
    '''A function to convert strings of the settings file to Bool variables'''
    if string not in ['True', 'False']:
        raise ValueError('Check the typo (True || False) of ignore-existing in the settings file.')

    return bool(string == 'True')


def exclude_include_ignore(settings, rsync_direction, rsync_task):
    '''A function to process include and exclude arguments.'''
    if 'include' in settings[rsync_direction][rsync_task]:
        include = settings[rsync_direction][rsync_task]['include']
    else:
        include = None

    if 'exclude' in settings[rsync_direction][rsync_task]:
        exclude = settings[rsync_direction][rsync_task]['exclude']
    else:
        exclude = None

    if 'exclude-from' in settings[rsync_direction][rsync_task]:
        exclude_from = settings[rsync_direction][rsync_task]['exclude-from']
    else:
        exclude_from = None

    if 'ignore-existing' in settings[rsync_direction][rsync_task]:
        ignore_existing = str2bool(settings[rsync_direction][rsync_task]['ignore-existing'])
    else:
        ignore_existing = False

    logging.info('The settings %s from the settings.json file are used for the production.', rsync_task)
    return (include, exclude, exclude_from, ignore_existing)

def ssh(remote_user, remote_host, cmd):
    '''This function executes the ssh command on the server'''
    ssh_cmd = ['ssh', f'{remote_user}@{remote_host}', f'{cmd}']
    logging.info('The following command was executed with ssh: %s', ssh_cmd)
    subprocess.run(ssh_cmd, check=True)

def scp_push(remote_user, remote_host, source_file, destination_file):
    '''This function copies localhost files to the server'''
    scp_cmd = ['scp', f'{source_file}', f'{remote_user}@{remote_host}:{destination_file}']
    logging.info('The following command was executed with scp: %s', scp_cmd)
    subprocess.run(scp_cmd, check=True)


def scp_get(remote_user, remote_host, source_file, destination_file):
    '''This function pulls server files to the localhost'''
    scp_cmd = ['scp', f'{remote_user}@{remote_host}:{source_file}', f'{destination_file}']
    logging.info('The following command was executed with scp: %s', scp_cmd)
    subprocess.run(scp_cmd, check=True)


def rsync_push(remote_user, remote_host, local_dir, remote_dir, include=None, exclude=None, exclude_from=None, ignore_existing=False): # pylint: disable=R0913
    '''The function synchronizes local files with the server'''
    return _rsync(remote_user, remote_host, local_dir, remote_dir, include, exclude, exclude_from, ignore_existing, push_to_server=True)


def rsync_get(remote_user, remote_host, local_dir, remote_dir, include=None, exclude=None, exclude_from=None, ignore_existing=False): # pylint: disable=R0913
    '''The function synchronizes remote files with the local machine'''
    return _rsync(remote_user, remote_host, local_dir, remote_dir, include, exclude, exclude_from, ignore_existing, push_to_server=False)


def _rsync(remote_user, remote_host, local_dir, remote_dir, include, exclude, exclude_from, ignore_existing, push_to_server=True): # pylint: disable=R0913
    if include is None:
        include = []
    include_args = list(chain(*zip(repeat('--include'), include)))

    if exclude is None:
        exclude = []
    exclude_args = list(chain(*zip(repeat('--exclude'), exclude)))

    if exclude_from is None:
        exclude_from = []
    exclude_from_args = list(chain(*zip(repeat('--exclude-from'), exclude_from)))


    ssh_str = f'{remote_user}@{remote_host}:{remote_dir}'
    if push_to_server:
        cp = [local_dir, ssh_str]
    else:
        cp = [ssh_str, local_dir]

    if ignore_existing:
        rsync_cmd = ['rsync', '-a', '--progress', '--ignore-existing', '--recursive', '--compress'] + include_args + exclude_args + exclude_from_args + cp
    else:
        rsync_cmd = ['rsync', '-a', '--progress', '--delete-before'] + include_args + exclude_args + exclude_from_args + cp
    logging.info('The following rsync command is executed: %s', rsync_cmd)
    subprocess.run(rsync_cmd, check=True)


@task
def push(c, what): # pylint: disable=W0613
    '''This task synchronizes the local folders to the server'''
    inv_logging.task(push.__name__)
    settings = util.read_settings()

    if what not in ['sourcefiles', 'climatologies', 'staticfiles']:
        raise RuntimeError(f'Your entry \'{what}\' was incorrect. Please read the Readme.md')

    rsync_direction = 'rsync_push'
    include, exclude, exclude_from, ignore_existing = exclude_include_ignore(settings, rsync_direction, what)
    rsync_push(settings['REMOTE_USER'], settings['REMOTE_HOST'], \
        settings[rsync_direction][what]['local_dir'], \
        settings[rsync_direction][what]['remote_dir'], \
        include, exclude, exclude_from, ignore_existing)
    inv_logging.success(push.__name__)


@task
def push_climatologies(c):
    '''Precalculated climatologies are loaded on the server'''
    inv_logging.task(push_climatologies.__name__)
    push(c, 'climatologies')
    inv_logging.success(push_climatologies.__name__)


@task
def get(c): # pylint: disable=W0613
    '''This task synchronizes the server to the local machine'''
    inv_logging.task(get.__name__)
    settings = util.read_settings()

    rsync_direction = 'rsync_get'
    for rsync_task in settings[rsync_direction]:
        print(rsync_task)
        include, exclude, exclude_from, ignore_existing = exclude_include_ignore(settings, rsync_direction, rsync_task)
        rsync_get(settings['REMOTE_USER'], settings['REMOTE_HOST'], \
            settings[rsync_direction][rsync_task]['local_dir'], \
            settings[rsync_direction][rsync_task]['remote_dir'], \
            include, exclude, exclude_from, ignore_existing)
    inv_logging.success(get.__name__)


RSYNC_NS = Collection('rsync')
RSYNC_NS.add_task(push)
RSYNC_NS.add_task(push_climatologies)
RSYNC_NS.add_task(get)
