#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""The collection is needed for node."""

import logging
from invoke import task, Collection
import inv_base
import inv_logging
import inv_docker

@task
def build(c):
    """This task is used to build the Javascript components"""
    inv_logging.task(build.__name__)
    user, group = inv_base.uid_gid(c)
    inv_base.docker_compose(c, f"run -u {user}:{group} node npm run build", pty=True)
    logging.info("The Javascript components were built, minified and zipped.")
    inv_logging.success(build.__name__)


@task
def lint(c):
    """This task is used to embellish the code"""
    inv_logging.task(lint.__name__)
    user, group = inv_base.uid_gid(c)
    inv_base.docker_compose(c, f"run -u {user}:{group} node npm run lint", pty=True)
    inv_logging.success(lint.__name__)


@task
def npm(c, cmd):
    """This task is used to respond to the packet manager npm, for example: npm install date-fns"""
    inv_logging.task(npm.__name__)
    user, group = inv_base.uid_gid(c)
    inv_logging.cmd(cmd)
    inv_base.docker_compose(c, f"run -u {user}:{group} node npm {cmd}", pty=True)
    inv_logging.success(npm.__name__)

@task
def npx(c, cmd):
    """This task is used to respond to the packet manager npx, for example: npx install date-fns"""
    inv_logging.task(npx.__name__)
    user, group = inv_base.uid_gid(c)
    inv_logging.cmd(cmd)
    inv_base.docker_compose(c, f"run -u {user}:{group} node npx {cmd}", pty=True)
    inv_logging.success(npx.__name__)

NODE_NS = Collection("node")
NODE_NS.add_task(build)
NODE_NS.add_task(lint)
NODE_NS.add_task(npm)
NODE_NS.add_task(npx)
