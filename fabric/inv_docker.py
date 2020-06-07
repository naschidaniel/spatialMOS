#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
"""This function contains the most important docker commands."""

import logging
from invoke import task, Collection
import inv_base
import inv_logging
import inv_django
import inv_node

@task
def docker(c, cmd):
    """The Task can execute a Docker command including cmd: docker ps"""
    inv_logging.task(restart.__name__)
    inv_logging.cmd(cmd)
    inv_base.dockerdaemon(c, cmd)
    inv_logging.success(restart.__name__)


@task
def restart(c):
    """Restart all docker containers"""
    inv_logging.task(restart.__name__)
    inv_base.docker_compose(c, "up -d --remove-orphans")
    inv_logging.success(restart.__name__)


@task
def fullrestart(c):
    """Restart all docker containers with force"""
    inv_logging.task(fullrestart.__name__)
    inv_base.docker_compose(c, "up -d --force-recreate")
    inv_logging.success(fullrestart.__name__)


@task
def run(c, cmd):
    """Start a service from the Docker Compose file, for example: docker django"""
    inv_logging.task(run.__name__)
    user, group = inv_base.uid_gid(c)
    inv_logging.cmd(cmd)
    inv_base.docker_compose(c, f"run -u {user}:{group} {cmd}", pty=True)
    inv_logging.success(run.__name__)


@task
def rebuild(c):
    """Rebuild all docker containers"""
    inv_logging.task(rebuild.__name__)
    inv_base.docker_compose(c, "build")
    restart(c)
    inv_logging.success(rebuild.__name__)


@task
def rebuildhard(c):
    """Rebuild all containers with --no-cache"""
    inv_logging.task(rebuildhard.__name__)
    inv_base.docker_compose(c, "build --no-cache")
    fullrestart(c)
    inv_logging.success(rebuildhard.__name__)


@task
def serve(c):
    """Serve the development environment"""
    inv_logging.task(serve.__name__)
    inv_base.docker_compose(c, "up")
    inv_logging.success(serve.__name__)


@task
def start(c):
    """Start in detached Modus"""
    inv_logging.task(start.__name__)
    #inv_django.migrate(c)
    inv_base.docker_compose(c, "up -d")
    inv_logging.success(start.__name__)


@task
def stop(c):
    """Stop all running Docker Containers"""
    inv_logging.task(stop.__name__)
    inv_base.docker_compose(c, "down --remove-orphans")
    inv_logging.success(stop.__name__)


@task
def logs(c, cmd):
    """Show the log files from the Docker Services, for example: django"""
    inv_logging.task(logs.__name__)
    inv_base.docker_compose(c, 'logs -f {}'.format(cmd))
    inv_logging.cmd(cmd)
    inv_logging.success(logs.__name__)


docker_compose_development_ns = Collection("docker-compose")
docker_compose_development_ns.add_task(restart)
docker_compose_development_ns.add_task(fullrestart)
docker_compose_development_ns.add_task(rebuildhard)
docker_compose_development_ns.add_task(rebuild)
docker_compose_development_ns.add_task(start)
docker_compose_development_ns.add_task(stop)
docker_compose_development_ns.add_task(run)
docker_compose_development_ns.add_task(logs)


docker_compose_production_ns = Collection("docker-compose")
docker_compose_production_ns.add_task(restart)
docker_compose_production_ns.add_task(fullrestart)
docker_compose_production_ns.add_task(rebuildhard)
docker_compose_production_ns.add_task(rebuild)
docker_compose_production_ns.add_task(start)
docker_compose_development_ns.add_task(serve)
docker_compose_production_ns.add_task(stop)
docker_compose_production_ns.add_task(run)
docker_compose_production_ns.add_task(logs)