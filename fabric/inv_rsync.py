#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
"""This collection is used to ensure data exchange between local PC and server."""

import os
import sys
import subprocess
import logging
from itertools import chain, repeat
from invoke import task, Collection
import inv_base
import inv_logging
import inv_install

def ssh(c, remote_user, remote_host, cmd):
    """This function executes the ssh command on the server"""
    ssh_cmd = ["ssh", f"{remote_user}@{remote_host}", f"{cmd}"]
    logging.info(f"The following command was executed with ssh: {ssh_cmd}")
    subprocess.run(ssh_cmd, check=True)

def scp_push(c, remote_user, remote_host, source_file, destination_file):
    """This function copies server files to the localhost"""
    scp_cmd = ["scp", f"{source_file}", f"{remote_user}@{remote_host}:{destination_file}"]
    logging.info(f"The following command was executed with scp: {scp_cmd}")
    subprocess.run(scp_cmd, check=True)


def scp_get(c, remote_user, remote_host, source_file, destination_file):
    """This function copies local files to the server"""
    scp_cmd = ["scp", f"{remote_user}@{remote_host}:{source_file}", f"{destination_file}"]
    logging.info(f"The following command was executed with scp: {scp_cmd}")
    subprocess.run(scp_cmd, check=True)


def rsync_push(c, remote_user, remote_host, local_dir, remote_dir, include=None, exclude=None):
    """The function synchronizes local files with the server"""
    return _rsync(c, remote_user, remote_host, local_dir, remote_dir, include, exclude, push=True)


def rsync_get(c, remote_user, remote_host, local_dir, remote_dir, include=None, exclude=None):
    """The function synchronizes remote files with the local machine"""
    return _rsync(c, remote_user, remote_host, local_dir, remote_dir, include, exclude, push=False)


def _rsync(c, remote_user, remote_host, local_dir, remote_dir, include=None, exclude=None, push=True):
    if include is None:
        include = []
    include_args = list(chain(*zip(repeat('--include'), include)))
    
    if exclude is None:
        exclude = []
    exclude_args = list(chain(*zip(repeat('--exclude'), exclude)))

    ssh_str = f"{remote_user}@{remote_host}:{remote_dir}"
    if push:
        cp = [local_dir, ssh_str]
    else:
        cp = [ssh_str, local_dir]

    rsync_cmd = ["rsync", "-a", "--progress", "--delete-before"] + include_args + exclude_args + cp
    logging.info(f"The following rsync command is executed: {rsync_cmd}")
    subprocess.run(rsync_cmd, check=True)


@task(inv_install.check_upstream)
def push(c):
    """This task synchronizes the local folders to the server"""
    inv_logging.task(push.__name__)
    settings = inv_base.read_settings("production")

    for rsync_task in settings["rsync_push"]:
        if "include" in settings["rsync_push"][rsync_task]:
            include = settings["rsync_push"][rsync_task]["include"]
        else:
            include = None

        if "exclude" in settings["rsync_push"][rsync_task]:
            exclude = settings["rsync_push"][rsync_task]["exclude"]
        else:
            exclude = None
        
        logging.info(
            f"The settings {rsync_task} from the settings.json file are used for the production.")
        rsync_push(c, settings["REMOTE_USER"], settings["REMOTE_HOST"], settings["rsync_push"][rsync_task]
                ["local_dir"], settings["rsync_push"][rsync_task]["remote_dir"], include, exclude)
    
    inv_logging.success(push.__name__)

@task
def get(c):
    """This task synchronizes the server to the local machine"""
    inv_logging.task(get.__name__)
    settings = inv_base.read_settings("production")

    for rsync_task in settings["rsync_get"]:
        if "include" in settings["rsync_get"][rsync_task]:
            include = settings["rsync_get"][rsync_task]["include"]
        else:
            include = None

        if "exclude" in settings["rsync_get"][rsync_task]:
            exclude = settings["rsync_get"][rsync_task]["exclude"]
        else:
            exclude = None

        logging.info(
            f"The settings {rsync_task} from the settings.json file are used for the production.")
        rsync_get(c, settings["REMOTE_USER"], settings["REMOTE_HOST"], settings["rsync_get"][rsync_task]
                ["local_dir"], settings["rsync_get"][rsync_task]["remote_dir"], include, exclude)
    
    inv_logging.success(get.__name__)


rsync_ns = Collection("rsync")
rsync_ns.add_task(push)
rsync_ns.add_task(get)