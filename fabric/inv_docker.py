#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""This function contains the most important docker commands."""

from invoke import task, Collection
from . import inv_base
from . import inv_logging

@task
def docker(c, cmd):
    """The Task can execute a Docker command including cmd: docker ps"""
    inv_logging.task(docker.__name__)
    inv_logging.cmd(cmd)
    inv_base.dockerdaemon(c, cmd)
    inv_logging.success(docker.__name__)


@task
def restart(c, cmd):
    """Restart a single docker container"""
    inv_logging.task(restart.__name__)
    inv_logging.cmd(cmd)
    inv_base.docker_compose(c, f"restart -t 10 {cmd}", pty=True)
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
    fullrestart(c)
    inv_logging.success(rebuild.__name__)


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
    inv_base.docker_compose(c, "up -d")
    inv_logging.success(start.__name__)


@task
def stop(c):
    """Stop all running Docker Containers"""
    inv_logging.task(stop.__name__)
    inv_base.docker_compose(c, "down --remove-orphans")
    inv_logging.success(stop.__name__)



DOCKER_COMPOSE_DEVELOPMENT_NS = Collection("docker-compose")
DOCKER_COMPOSE_DEVELOPMENT_NS.add_task(restart)
DOCKER_COMPOSE_DEVELOPMENT_NS.add_task(fullrestart)
DOCKER_COMPOSE_DEVELOPMENT_NS.add_task(rebuild)
DOCKER_COMPOSE_DEVELOPMENT_NS.add_task(serve)
DOCKER_COMPOSE_DEVELOPMENT_NS.add_task(start)
DOCKER_COMPOSE_DEVELOPMENT_NS.add_task(stop)
DOCKER_COMPOSE_DEVELOPMENT_NS.add_task(run)


DOCKER_COMPOSE_PRODUCTION_NS = Collection("docker-compose")
DOCKER_COMPOSE_PRODUCTION_NS.add_task(restart)
DOCKER_COMPOSE_PRODUCTION_NS.add_task(rebuild)
DOCKER_COMPOSE_PRODUCTION_NS.add_task(start)
DOCKER_COMPOSE_PRODUCTION_NS.add_task(stop)
DOCKER_COMPOSE_PRODUCTION_NS.add_task(run)
