#!/usr/bin/python
# -*- coding: utf-8 -*-

"""A management command for deleting the spatialMos predictions from the database."""

import sys
from django.db import connection, transaction
from django.core.management.base import BaseCommand
from predictions.models import SpatialMosRun, SpatialMosStep, SpatialMosPoint
from datetime import datetime, timedelta

class Command(BaseCommand):
    """A management command for deleting the spatialMos predictions from the database."""
    help = "With this management command old model runs can be removed from the database. Options: --parameter ['tmp_2m', 'rh_2m', 'wind_10m'] --days 5"

    def add_arguments(self, parser):
        """Adding additional arguments"""
        parser.add_argument('parameter', type=str)
        parser.add_argument('days', type=int)


    def handle(self, *args, **options):
        parameter = options['parameter']
        days = options['days']
        vacuum_database = False


        line = "-----------------------------"
        newest_imported_spatialmos_run = SpatialMosRun.objects.filter(complete=True, parameter=parameter).latest('anal_date')
        oldest_imported_spatialmos_run = SpatialMosRun.objects.filter(complete=True, parameter=parameter).latest('-anal_date')
        msg = f"{parameter:6} | Oldest model run in the database: -  {oldest_imported_spatialmos_run}" 
        self.stdout.write(msg)

        timedelta_newest_imported_spatialmos_run = newest_imported_spatialmos_run.anal_date - timedelta(days=days)
        print(timedelta_newest_imported_spatialmos_run)
        selection_spatialmos_run = SpatialMosRun.objects.filter(parameter=parameter, anal_date__lte=timedelta_newest_imported_spatialmos_run).order_by('anal_date')
        spatialmos_run_count = SpatialMosRun.objects.filter(parameter=parameter).count()
        msg = f"{parameter:6} | Available model runs before deleting: {spatialmos_run_count}"
        self.stdout.write(msg)

        i = 1
        for spatialmos_run in selection_spatialmos_run:
            starttime = datetime.now()
            spatialmos_run.delete()
            timedifference = (datetime.now() - starttime).total_seconds()
            msg = f"{parameter:6} | [{i}/{selection_spatialmos_run}] The following selection was deleted from the database in {timedifference:3.1f} seconds - {spatialmos_run}"
            self.stdout.write(msg)
            vacuum_database = True
            i=i+1
        self.stdout.write(line)

        spatialmos_run_count = SpatialMosRun.objects.filter(parameter=parameter).count()
        msg = f"{parameter:6} | Available model runs before deleting: {spatialmos_run_count}"
        self.stdout.write(msg)
        self.stdout.write(line)


        if vacuum_database is True:
            starttime = datetime.now()
            cursor = connection.cursor()
            cursor.execute("vacuum")
            transaction.commit()
            timedifference = (datetime.now() - starttime).total_seconds()
            msg = f"{parameter:6} | The execution of vaccum Database took {timedifference} seconds."
            self.stdout.write(msg)
