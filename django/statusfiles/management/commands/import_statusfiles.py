#!/usr/bin/python
# -*- coding: utf-8 -*-

"""A management command for importing the statusfiles from fabric commands into the database."""

import os
import json
import logging
import re
import sys
import datetime as dt
import pytz
from django.core.management.base import BaseCommand
from statusfiles.models import StatusChecks, StatusFiles

class Command(BaseCommand):
    """A management command for importing the statusfiles from fabric commands into the database."""
    help = "Import statusfiles form the ./data/spool/statusfiles directory"

    def handle(self, *args, **options):
        """Main Function"""

        def select_StatusCheck(statusfile, cmd_regex):
            """A function to create a new statuscheck"""
            statuscheck = StatusChecks.objects.filter(taskname=statusfile["taskname"], cmd_regex=cmd_regex)
            if not statuscheck:
                statuscheck_entry = StatusChecks(taskname=statusfile["taskname"], cmd_regex=cmd_regex, name=statusfile["taskname"])
                statuscheck_entry.save()
                logging.info("A statuscheck was created. taskname: %s; cmd_regex = %s", statusfile["taskname"], cmd_regex)
            else:
                statuscheck_entry = statuscheck[0]
            return statuscheck_entry

        def create_StatusFileEntry(statuscheck_entry, statusfile):
            """A function to create an entry in the table of the model StatusFiles"""
            timezone = pytz.timezone('Europe/Vienna')
            task_finished_time = dt.datetime.strptime(statusfile['task_finished_time'], '%Y-%m-%dT%H:%M:%S')
            task_finished_time_aware = timezone.localize(task_finished_time)
            statusfile_entry = StatusFiles.objects.filter(task_finished_time=task_finished_time_aware, cmd=statusfile["cmd"])
            if not statusfile_entry:
                statusfile_entry = StatusFiles(check_name=statuscheck_entry, task_finished_time=task_finished_time_aware, cmd=statusfile["cmd"])
                statusfile_entry.save()
                return True
            else:
                logging.warning("The task is allready in the database.")
                return True

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
                    f.close()
                
                date_regexp = "(\d{4})[/.-](\d{2})[/.-](\d{2})"
                cmd_regex = re.sub(date_regexp, "YYYY-MM-DD", statusfile["cmd"])
                statuscheck_entry = select_StatusCheck(statusfile, cmd_regex)
                file_imported = create_StatusFileEntry(statuscheck_entry, statusfile)
                if file_imported:
                    os.replace(os.path.join(data_path, filename), os.path.join(data_path_done, filename))
                    logging.info("The statusfile %s was imported and was moved to the done folder.", filename)
                else:
                    logging.error("The statusfile %s could not be imported.", filename)
