#!/usr/bin/python
# -*- coding: utf-8 -*-

"""A management command for importing the statusfiles from fabric commands into the database."""

import os
import sys
import json
import logging
import datetime as dt
from django.core.management.base import BaseCommand
from statusfiles.models import StatusFiles

class Command(BaseCommand):
    """A management command for importing the statusfiles from fabric commands into the database."""
    help = "Import statusfiles form the ./data/spool/statusfiles directory"

    def handle(self, *args, **options):
        """Main Function"""

        def create_StatusFileEntry(statusfile: object):
            """A function to create an entry in the table of the model StatusFiles"""
            try:
                task_finished_time = dt.datetime.strptime(statusfile['task_finished_time'], '%Y-%m-%dT%H:%M:%S')
                if StatusFiles.objects.filter(taskname=statusfile["taskname"], task_finished_time=task_finished_time, cmd=statusfile["cmd"]).count() == 0:
                    statusfile_entry = StatusFiles(taskname=statusfile["taskname"], task_finished_time=task_finished_time, cmd=statusfile["cmd"])
                    statusfile_entry.save()
                    return True
                else:
                    logging.warning("The task is allready in the database.")
                    return True
            except:
                return False

        # Read status file of the spatialMOS model run
        data_path = "/www/data/spool/statusfiles"
        data_path_done = "/www/data/spool/statusfiles/done"

        # Provide Folder Structure
        if not os.path.exists(data_path_done):
            os.mkdir(f"{data_path_done}")

        filenames = os.listdir(data_path)
        for filename in filenames:
            f_path, f_extension = os.path.splitext(filename)
            if (f_extension == ".json"):
                with open(os.path.join(data_path, filename), 'r') as f:
                    statusfile = json.load(f)
                
                success = create_StatusFileEntry(statusfile)
                if success:
                    os.replace(os.path.join(data_path, filename), os.path.join(data_path_done, filename))
                    logging.info("The statusfile %s was imported and was moved to the done folder.", filename)
                else:
                    logging.error("The statusfile %s could not be imported.", filename)
                    sys.exit(1)
