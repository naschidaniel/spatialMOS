#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""This collection is used to deploy spatialMOS to a server."""

from invoke import task
import inv_logging
import inv_docker
import inv_django
import inv_docker
import inv_install
import inv_rsync


@task
def check_upstream(c):
    """Check master """
    print("Do you really want to run on production? [y/N]")
    answer = input()

    if answer.upper() not in ("Y", "YES", "JA", "J"):
        sys.exit(1)

    if c.run("git rev-parse --abbrev-ref HEAD", hide=True).stdout.strip() != "master":
        logging.error("You are not in the master branch. Only the master branch can be uploaded onto the server.")
        sys.exit(1)

    c.run("git fetch origin master", hide=True)
    if c.run("git diff origin/master", hide=True).stdout.strip() != "":
        logging.error("Your local branch differs from upstream master (run git diff)")
        sys.exit(1)

    if c.run("git status --short", hide=True).stdout.strip() != "":
        logging.error("You have a dirty working directory (run git status)")
        sys.exit(1)


@task(pre=[inv_base.check_upstream])
@task
def deploy(c):
    """Everything you need to deploy"""
    inv_logging.task(deploy.__name__)
    #c.run("./task.py local.node.build")
    c.run("./task.py local.django.collectstatic")
    inv_docker.stop(c)
    inv_rsync.push(c, "sourcefiles")
    inv_rsync.push(c, "staticfiles")
    inv_rsync.push(c, "climatologies")
    inv_install.setproductionenvironment(c)
    inv_docker.rebuild(c)
    inv_django.migrate(c)
    inv_docker.start(c)
    inv_logging.success(deploy.__name__)
