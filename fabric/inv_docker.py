#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
'''This function contains the most important docker commands.'''

import logging
from invoke import task, Collection
from . import inv_logging
from . import util

@task
def prune_container(c):
    '''prune all quit containers'''
    inv_logging.task(prune_container.__name__)
    command = ['docker', 'container', 'prune', '--force']
    command = ' '.join(command)
    logging.info('The following command has entered: \'%s\'', command)
    c.run(command)
    util.write_statusfile_and_success_logging(prune_container.__name__)

@task
def run_node(c, cmd):
    '''run_r_base will run a command in r_base'''
    inv_logging.task(run_r_base.__name__)
    user, group = util.uid_gid()
    command = ['docker', 'run', '--rm', f'-u {user}:{group}', '-v $(pwd):/www', '-p 3000:3000', 'node_container']
    command.extend(cmd)
    command = ' '.join(command)
    logging.info('The following command has entered: \'%s\'', command)
    c.run(command)
    inv_logging.success(run_r_base.__name__)


@task
def run_py_container(c, cmd):
    '''run_py_container will run a command in py_container'''
    inv_logging.task(run_py_container.__name__)
    user, group = util.uid_gid()
    command = ['docker', 'run', '--rm', f'-u {user}:{group}', '-v $(pwd):/usr/src/app', 'py_container']
    command.extend(cmd)
    command = ' '.join(command)
    logging.info('The following command has entered: \'%s\'', command)
    c.run(command)
    inv_logging.success(run_py_container.__name__)


@task
def run_maturin_build(c):
    '''Build the Rust libraries for Spatialmos'''
    inv_logging.task(run_maturin_build.__name__)
    user, group = util.uid_gid()
    command = ['docker', 'run', '--rm', '-v $(pwd):/io', 'konstin2/maturin', 'build', '--manylinux', 'off']
    command = ' '.join(command)
    c.run(command)
    c.run(f'sudo chown {user}:{group} -R target') # TODO rm sudo # pylint: disable=fixme
    c.run('mv ./target/wheels/*.whl ./container/py_container/')
    inv_logging.success(run_maturin_build.__name__)


@task
def rebuild(c):
    '''Rebuild all docker containers'''
    inv_logging.task(rebuild.__name__)
    run_maturin_build(c)
    c.run('docker build --no-cache -t node_container ./website/')
    c.run('docker build --no-cache -t r_base ./container/r_base/')
    c.run('docker build --no-cache -t py_container ./container/py_container/')
    c.run('docker save node_container | gzip > ./container/node_container.tar.gz')
    c.run('docker save py_container | gzip > ./container/py_container.tar.gz')
    c.run('docker save r_base | gzip > ./container/r_base.tar.gz')
    inv_logging.success(rebuild.__name__)


@task
def run_r_base(c, cmd):
    '''run_r_base will run a command in r_base'''
    inv_logging.task(run_r_base.__name__)
    user, group = util.uid_gid()
    command = ['docker', 'run', '--rm', f'-u {user}:{group}', '-v $(pwd):/usr/src/app', 'r_base']
    command.extend(cmd)
    command = ' '.join(command)
    logging.info('The following command has entered: \'%s\'', command)
    c.run(command)
    inv_logging.success(run_r_base.__name__)


@task
def stop(c):
    '''Stop all running Docker Containers'''
    inv_logging.task(stop.__name__)
    c.run('docker stop node_container')
    inv_logging.success(stop.__name__)



DOCKER_NS = Collection('docker')
DOCKER_NS.add_task(prune_container)
DOCKER_NS.add_task(run_maturin_build)
DOCKER_NS.add_task(rebuild)
DOCKER_NS.add_task(stop)
