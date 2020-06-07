import json
import sys
import os
import logging
import copy


def manage_py(c, cmd, **kwargs):
    """The function executes the django manage.py command."""
    user, group = uid_gid(c)
    docker_compose(c, f"run -u {user}:{group} django python3 /www/site/manage.py {cmd}", pty=True)


def read_settings(what):
    """A function to read the settings file."""
    settings_file = os.path.join(os.path.join(
        os.getcwd(), "settings.json"))

    if what not in ["development", "test", "production"]:
        logging.error(
            f"No settings could be found in the file {settings_file} for your input: {what}")
        sys.exit(1)

    if os.path.exists(settings_file):
        with open(settings_file) as f:
            settings = json.load(f)
    else:
        fabric_folder = os.path.join(os.getcwd(), "fabric")
        logging.error(
            f"There is no {settings_file} file available. Edit the settings.example.json file in the {fabric_folder} folder and save it in the main folder.")
        sys.exit(1)

    if what == "test":
        settings["test"]["docker"]["INSTALLFOLDER"] = os.getcwd()
    return settings[what]


def uid_gid(c):
    if c.config["collection"] == "production":
        uid = c.config["docker"]["USERID"]
        gid = c.config["docker"]["GROUPID"]
    else:
        uid = os.getuid()
        gid = os.getgid()
    return uid, gid


def docker_environment(c):
    """The function generates the docker environment variables."""
    settings = read_settings(c.config["collection"])
    docker_environment = settings["docker"]
    if c.config["collection"] in ["development", "test"]:
        uid, gid = uid_gid(c)
        docker_environment["USERID"] = f"{uid}"
        docker_environment["GROUPID"] = f"{gid}"
    return docker_environment


def dockerdaemon(c, cmd, **kwargs):
    """A function to start the docker daemon."""
    command = ["docker"]
    command.append(cmd)
    return c.run(" ".join(command), env=docker_environment(c), **kwargs)


def docker_compose(c, cmd, **kwargs):
    """A function to start docker-compose."""
    command = ["docker-compose"]
    for config_file in c.docker_compose_files:
        command.append("-f")
        command.append(config_file)
    command.append(cmd)
    return c.run(" ".join(command), env=docker_environment(c), **kwargs)
