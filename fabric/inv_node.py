#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""The collection is needed for node."""

import logging
from invoke import task, Collection
from . import inv_base
from . import inv_logging

@task
def build(c):
    """This task is used to build the Javascript components"""
    inv_logging.task(build.__name__)
    user, group = inv_base.uid_gid(c)
    inv_base.docker_compose(c, f"run -u {user}:{group} node yarn build", pty=True)
    logging.info("The Javascript components were built, minified and zipped.")
    inv_logging.success(build.__name__)


@task
def lint(c):
    """This task is used to embellish the code"""
    inv_logging.task(lint.__name__)
    user, group = inv_base.uid_gid(c)
    inv_base.docker_compose(c, f"run -u {user}:{group} node yarn lint", pty=True)
    inv_logging.success(lint.__name__)


@task
def yarn(c, cmd):
    """This task is used to respond to the packet manager yarn, for example: yarn add date-fns"""
    inv_logging.task(yarn.__name__)
    user, group = inv_base.uid_gid(c)
    inv_logging.cmd(cmd)
    inv_base.docker_compose(c, f"run -u {user}:{group} node yarn {cmd}", pty=True)
    inv_logging.success(yarn.__name__)


NODE_NS = Collection("node")
NODE_NS.add_task(build)
NODE_NS.add_task(lint)
NODE_NS.add_task(yarn)
