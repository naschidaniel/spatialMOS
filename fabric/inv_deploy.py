#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""This collection is used to deploy spatialMOS to a server."""

import logging
import sys
from invoke import task
from . import inv_logging
from . import inv_node
from . import inv_docker
from . import inv_rsync

@task
def check_upstream(c):
    """Check main"""
    inv_logging.task(check_upstream.__name__)
    print("Do you really want to run on production? [y/N]")
    answer = input()

    if answer.upper() not in ("Y", "YES", "JA", "J"):
        sys.exit(1)

    if c.run("git rev-parse --abbrev-ref HEAD", hide=True).stdout.strip() != "main":
        logging.error("You are not in the main branch. Only the main branch can be uploaded onto the server.")
        sys.exit(1)

    c.run("git fetch origin main", hide=True)
    if c.run("git diff origin/main", hide=True).stdout.strip() != "":
        logging.error("Your local branch differs from upstream main (run git diff)")
        sys.exit(1)

    if c.run("git status --short", hide=True).stdout.strip() != "":
        logging.error("You have a dirty working directory (run git status)")
        sys.exit(1)
    inv_logging.success(check_upstream.__name__)


@task(pre=[check_upstream])
@task
def deploy(c):
    """Everything you need to deploy"""
    inv_logging.task(deploy.__name__)
    inv_docker.run_maturin_build(c)
    inv_node.build(c)
    inv_rsync.push(c, "sourcefiles")
    inv_rsync.push(c, "staticfiles")
    inv_logging.success(deploy.__name__)

@task
def push_climatologies(c):
    """Precalculated climatologies are loaded on the server"""
    inv_logging.task(deploy.__name__)
    inv_rsync.push(c, "climatologies")
    inv_logging.success(deploy.__name__)
