#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""The collection is needed for postgresql."""

import os
import datetime
import logging
from invoke import task, Collection
import inv_base
import inv_logging
import inv_docker
import inv_rsync
import inv_django

def delete_db_dump(c, host, postgres_backup_folder, file):
    """A function to delete the las db dump."""
    cmd = f"rm {postgres_backup_folder}/{file}.out"
    if host == "moses":
        inv_rsync.ssh(c, c.config["REMOTE_USER"], c.config["REMOTE_HOST"], cmd)
    else:
        c.run(cmd)
    logging.info("The uncompressed database dump was deleted: '%s/%s.out'", postgres_backup_folder, file)


def create_backup(c, host="local"):
    """A function for the database dump."""
    inv_docker.stop(c)
    inv_docker.start(c)
    settings = c.config

    if settings["collection"] == "production":
        postgres_backup_folder = f"{settings['docker']['INSTALLFOLDER']}{settings['postgres_backup_folder']}"
    else:
        postgres_backup_folder = f"{settings['postgres_backup_folder']}"

    user, group = inv_base.uid_gid(c)
    file = f"postgres_{settings['collection']}_backup_{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
    inv_base.docker_compose(c, f"run -u {user}:{group} --rm postgres bash -c 'pg_dumpall -c -U postgres -h postgres > /var/backup/{file}.out'", pty=True)
    logging.info("A database dump was saved in the file: '%s/%s.out", postgres_backup_folder, file)

    cmd = f"tar -czf {postgres_backup_folder}/{file}.tar.gz -C {postgres_backup_folder} {file}.out"
    if settings["collection"] == "production":
        inv_rsync.ssh(c, settings["REMOTE_USER"], settings["REMOTE_HOST"], cmd)
    else:
        c.run(cmd)

    logging.info("A database dump was saved in the file: '%s/%s.tar.gz'", postgres_backup_folder, file)

    delete_db_dump(c, host, postgres_backup_folder, file)

    inv_docker.stop(c)
    inv_docker.start(c)
    return postgres_backup_folder, file, settings


def read_backup(c, host="local"):
    """A function to read the database dump into the database."""
    inv_docker.stop(c)
    inv_docker.start(c)
    settings = c.config
    postgres_backup_folder = settings["postgres_backup_folder"]
    user, group = inv_base.uid_gid(c)
    postgresdata_backup_files = os.popen(f"ls {postgres_backup_folder}").read().strip().split("\n")
    file = postgresdata_backup_files[-1]
    file = file[:file.rfind(".tar.gz")]
    logging.info("The last database dump archive will be unpacked.: '%s/%s.tar.gz'", postgres_backup_folder, file)

    command = f"tar -xzf {postgres_backup_folder}/{file}.tar.gz -C {postgres_backup_folder}"
    if host == "moses":
        inv_rsync.ssh(c, settings["REMOTE_USER"], settings["REMOTE_HOST"], command)
    else:
        c.run(command)

    logging.info("The database dump is unpacked.: '%s/%s.out'", postgres_backup_folder, file)
    inv_base.docker_compose(c, f"run -u {user}:{group} --rm postgres bash -c 'psql -h postgres -U postgres -f /var/backup/{file}.out --quiet'")
    delete_db_dump(c, host, postgres_backup_folder, file)
    inv_docker.stop(c)
    inv_docker.start(c)


@task
def dump_backup(c):
    """Create a *.tar.gz local database dump """
    inv_logging.task(dump_backup.__name__)
    create_backup(c, "local")
    inv_logging.success(dump_backup.__name__)

@task
def dump_moses_backup(c):
    """Create a *.tar.gz moses database dump from localhost"""
    inv_logging.task(dump_backup.__name__)
    create_backup(c, "moses")
    inv_logging.success(dump_backup.__name__)

@task
def import_last_backup(c):
    """Import a *.tar.gz database dump into the postgres database"""
    inv_logging.task(import_last_backup.__name__)
    read_backup(c)
    inv_logging.success(import_last_backup.__name__)

@task
def import_last_moses_backup(c):
    """Import a *.tar.gz database dump into the moses postgres database from localhost"""
    inv_logging.task(import_last_moses_backup.__name__)
    read_backup(c, "moses")
    inv_logging.success(import_last_moses_backup.__name__)

@task
def reset_db(c):
    """Resets postgres database and migrate django migrations."""
    inv_logging.task(reset_db.__name__)
    inv_docker.stop(c)
    inv_base.manage_py(c, "flush")
    inv_docker.start(c)
    inv_django.makemigrations(c)
    inv_django.migrate(c)
    inv_logging.success(reset_db.__name__)

POSTGRESQL_DEVELOPMENT_NS = Collection("postgres")
POSTGRESQL_DEVELOPMENT_NS.add_task(dump_backup)
POSTGRESQL_DEVELOPMENT_NS.add_task(import_last_backup)
POSTGRESQL_DEVELOPMENT_NS.add_task(reset_db)

POSTGRESQL_PRODUCTION_NS = Collection("postgres")
POSTGRESQL_PRODUCTION_NS.add_task(dump_backup)
#POSTGRESQL_DEVELOPMENT_NS.add_task(dump_moses_backup)
POSTGRESQL_PRODUCTION_NS.add_task(import_last_backup)
#POSTGRESQL_DEVELOPMENT_NS.add_task(import_last_moses_backup)
