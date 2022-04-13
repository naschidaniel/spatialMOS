#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
"""The collection is needed for node."""

from invoke import task, Collection
from . import inv_docker
from . import inv_logging


@task
def build(c):
    """This task is used to build the Javascript components"""
    inv_logging.task(build.__name__)
    cmd = ["yarn", "build"]
    inv_docker.run_node(c, cmd)
    inv_logging.success(build.__name__)


@task
def dev(c):
    """This task is used for development"""
    inv_logging.task(build.__name__)
    cmd = ["yarn", "dev"]
    inv_docker.run_node(c, cmd)
    inv_logging.success(build.__name__)


@task
def lint(c):
    """This task is used to embellish the code"""
    inv_logging.task(lint.__name__)
    cmd = ["yarn", "lint"]
    inv_docker.run_node(c, cmd)
    inv_logging.success(lint.__name__)


@task
def yarn(c, cmd):
    """This task is used to respond to the packet manager yarn, for example: yarn add date-fns"""
    inv_logging.task(yarn.__name__)
    command = ["yarn", cmd]
    inv_docker.run_node(c, command)
    inv_logging.success(yarn.__name__)


NODE_NS = Collection("node")
NODE_NS.add_task(build)
NODE_NS.add_task(dev)
NODE_NS.add_task(lint)
NODE_NS.add_task(yarn)
