#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
"""The collection is needed for postgresql."""

import os
import sys
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
    command = f"rm {postgres_backup_folder}/{file}.out"
    if host == "development":
        c.run(command)
    elif host == "production":
        settings = inv_base.read_settings(host)
        inv_rsync.ssh(c, settings["REMOTE_USER"], settings["REMOTE_HOST"], command)

def dump_backup(c, host):
    """A function for the database dump."""
    inv_docker.stop(c)
    inv_docker.start(c)
    settings = inv_base.read_settings(host)

    if host == "development":
        postgres_backup_folder = f"{settings['postgres_backup_folder']}"
    elif host == "production":
        postgres_backup_folder = f"{settings['docker']['INSTALLFOLDER']}{settings['postgres_backup_server_folder']}"

    user, group = inv_base.uid_gid(c)
    file = f"postgres_{host}_backup_{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
    inv_base.docker_compose(c, f"run -u {user}:{group} --rm postgres bash -c 'pg_dumpall -c -U postgres -h postgres > /var/backup/{file}.out'", pty=True)
    logging.info(f"A database dump was saved in the file: '{postgres_backup_folder}/{file}.out")
    
    command = f"tar -czf {postgres_backup_folder}/{file}.tar.gz -C {postgres_backup_folder} {file}.out"
    if host == "development":
        c.run(command)
    elif host == "production":
        inv_rsync.ssh(c, settings["REMOTE_USER"], settings["REMOTE_HOST"], command)  
    logging.info(f"A database dump was saved in the file: '{postgres_backup_folder}/{file}.tar.gz'")
    
    delete_db_dump(c, host, postgres_backup_folder, file)

    logging.info(f"The uncompressed database dump was deleted: '{postgres_backup_folder}/{file}.out'")

    inv_docker.stop(c)
    inv_docker.start(c)
    return postgres_backup_folder, file, settings

def read_backup(c, folder, docker_volume, host):
    """A function to read the database dump into the database."""
    inv_docker.stop(c)
    inv_docker.start(c)
    settings = inv_base.read_settings("development")
    postgres_backup_folder = settings[folder]
    user, group = inv_base.uid_gid(c)
    postgresdata_backup_server_files = os.popen(f"ls {postgres_backup_folder}").read().strip().split("\n")
    file = postgresdata_backup_server_files[-1]
    file = file[:file.rfind(".tar.gz")]
    logging.info(f"The database dump archive is unpacked.: '{postgres_backup_folder}/{file}.tar.gz'")

    command = f"tar -xzf {postgres_backup_folder}/{file}.tar.gz -C {postgres_backup_folder}"
    if host == "development":
        c.run(command)
    elif host == "production":
        inv_rsync.ssh(c, settings["REMOTE_USER"], settings["REMOTE_HOST"], command)
    
    logging.info(f"The database dump was unpacked.: '{postgres_backup_folder}/{file}.out'")
    inv_base.docker_compose(c, f"run -u {user}:{group} --rm postgres bash -c 'psql -h postgres -U postgres -f {docker_volume}/{file}.out --quiet'")
    delete_db_dump(c, host, postgres_backup_folder, file)
    inv_docker.stop(c)
    inv_docker.start(c)

@task
def dump_development_backup(c):
    """With this task the development database can be dumped into a tar.gz file."""
    inv_logging.task(dump_development_backup.__name__)
    dump_backup(c, host="development")
    inv_logging.success(dump_development_backup.__name__)

@task
def dump_production_backup(c):
    """With this task the production database can be dumped into a tar.gz file."""
    inv_logging.task(dump_production_backup.__name__)
    dump_backup(c, host="production")
    inv_logging.success(dump_production_backup.__name__)

@task 
def import_last_development_backup(c):
    """With this task the last development database dump can be imported from a tar.gz file."""
    inv_logging.task(import_last_development_backup.__name__)
    read_backup(c, "postgres_backup_folder", "/var/backup", "development")
    inv_logging.success(import_last_development_backup.__name__)

@task
def import_last_production_backup_into_local_db(c):
    """With this task the last production database dump can be imported from a tar.gz file into the local database."""
    inv_logging.task(import_last_production_backup_into_local_db.__name__)
    read_backup(c, "postgres_backup_server_folder", "/var/backup_server", "development")
    inv_logging.success(import_last_production_backup_into_local_db.__name__)

@task 
def import_last_production_backup(c):
    """With this task the last production database dump can be imported from a tar.gz file."""
    inv_logging.task(import_last_production_backup.__name__)
    read_backup(c, "postgres_backup_server_folder", "/var/backup", "production")
    inv_logging.success(import_last_production_backup.__name__)

@task
def get_last_production_backup(c):
    """With this task the last database dump can be downloaded from the server."""
    inv_logging.task(get_last_production_backup.__name__)
    settings_development = inv_base.read_settings("development")
    settings_production = inv_base.read_settings("production")
    postgres_backup_server_folder = f"{settings_production['docker']['INSTALLFOLDER']}{settings_production['postgres_backup_server_folder']}"
    remote_postgresdata_backup_server_files = os.popen(f"ssh {settings_production['REMOTE_USER']}@{settings_production['REMOTE_HOST']} ls {postgres_backup_server_folder}").read().strip().split("\n")
    backup_file = f"{remote_postgresdata_backup_server_files[-1]}"
    inv_rsync.scp_get(c, settings_production["REMOTE_USER"], settings_production["REMOTE_HOST"], f"{postgres_backup_server_folder}/{backup_file}", f"{settings_development['postgres_backup_server_folder']}/{backup_file}")
    inv_logging.success(get_last_production_backup.__name__)

@task
def reset_db(c):
    """Resets postgres database and migrate django migrations."""
    inv_logging.task(reset_db.__name__)
    inv_docker.stop(c)
    inv_base.manage_py(c, "reset_db")
    inv_docker.start(c)
    inv_django.makemigrations(c)
    inv_django.migrate(c)
    inv_logging.success(reset_db.__name__)

postgresql_development_ns = Collection("postgres")
postgresql_development_ns.add_task(dump_development_backup)
postgresql_development_ns.add_task(import_last_development_backup)
postgresql_development_ns.add_task(import_last_production_backup_into_local_db)
postgresql_development_ns.add_task(get_last_production_backup)
postgresql_development_ns.add_task(reset_db)

postgresql_production_ns = Collection("postgres")
postgresql_production_ns.add_task(dump_production_backup)
postgresql_production_ns.add_task(import_last_production_backup)