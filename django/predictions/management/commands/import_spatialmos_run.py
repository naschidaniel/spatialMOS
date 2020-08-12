#!/usr/bin/python
# -*- coding: utf-8 -*-

"""A management command for importing the spatialMos predictions into the database."""

import os
import sys
import json
import logging
import datetime as dt
import pytz
from django.core.management.base import BaseCommand
from predictions.models import SpatialMosRun, SpatialMosStep, SpatialMosPoint
from django.core.files import File


class Command(BaseCommand):
    """A management command for importing the spatialMos predictions into the database."""
    help = "Import the pre-processed forecast into the database. Options: --parameter ['tmp_2m', 'rh_2m', 'wind_10m'] --date '2020-08-02'"

    def add_arguments(self, parser):
        """Adding additional arguments"""
        parser.add_argument('date', type=str)
        parser.add_argument('parameter', type=str)

    def handle(self, *args, **options):
        """Main Function"""
        global available_fields
        available_fields = ['nwp_mean', 'nwp_mean_sm', 'nwp_spread', 'nwp_spread_sm', 'samos_mean', 'samos_mean_sm', 'samos_spread', 'samos_spread_sm']

        def create_SpatialMosRun(anal_date_aware, parameter):
            """A function to create an entry in the table of the model SpatialMosRun"""
            spatialmos_run = SpatialMosRun(anal_date=anal_date_aware, parameter=parameter)
            spatialmos_run.save()
            return spatialmos_run

        def create_SpatialMosStep(prediction_json_file, spatialmos_run, valid_date_aware):
            """A function to create an entry in the table of the model SpatialMosStep"""
            def filename_figure(prediction_json_file, what):
                spool_path_filename = os.path.join("/www/", prediction_json_file['SpatialMosStep'][f'path_filename_{what}'])
                django_path = os.path.join(f"./predictions/{prediction_json_file['SpatialMosRun']['parameter']}/{what}")
                binary_file = File(open(spool_path_filename, 'rb'))
                django_path_filename = os.path.join(django_path, prediction_json_file['SpatialMosStep'][f'filename_{what}'])
                return django_path_filename, binary_file

            spatialmos_step = SpatialMosStep(spatialmos_run=spatialmos_run, valid_date=valid_date_aware, step=prediction_json_file['SpatialMosStep']['step'])

            for what in available_fields:
                filename, file = filename_figure(prediction_json_file, what)
                spatialmos_step.__dict__[f'filename_{what}'].save(filename, file)

            spatialmos_step.save()
            return spatialmos_step

        def create_SpatialMosPoint(spatialmos_point_dict, spatialmos_step):
            """A function to create an entry in the table of the model SpatialMosPoint"""

            insert_list = []
            for item in spatialmos_point_dict:
                newrecord = SpatialMosPoint(spatialmos_step=spatialmos_step, **item)
                insert_list.append(newrecord)

            if len(insert_list) > 0:
                SpatialMosPoint.objects.bulk_create(insert_list)

        parameter = options['parameter']
        date_timestamp = dt.datetime.strptime(options['date'], "%Y-%m-%d")
        date = date_timestamp.strftime("%Y%m%d")

        # Read status file of the spatialMOS model run
        filename_spatialmos_run_status = os.path.join("/www", f"./data/spool/{parameter}/samos/{date}_run.json")
        if os.path.isfile(filename_spatialmos_run_status):
            with open(filename_spatialmos_run_status, 'r') as f:
                spatialmos_run_status = json.load(f)
        else:
            logging.error("No status file could be found for the parameter '%s' and date '%s'.", parameter, date)
            sys.exit(1)

        spatialmos_run = None
        for step in spatialmos_run_status:
            if spatialmos_run_status[step]['status'] != "ok":
                logging.error("The run '%s' for the parameter '%s' and date '%s' was not imported.", step, parameter, date)
                continue

            filename_spatialmos_step = os.path.join("/www", f"{spatialmos_run_status[step]['prediction_json_file']}")
            if os.path.isfile(filename_spatialmos_step):
                with open(filename_spatialmos_step, 'r') as f:
                    prediction_json_file = json.load(f)

                timezone = pytz.timezone('UTC')
                anal_date = dt.datetime.strptime(prediction_json_file['SpatialMosRun']['anal_date'], '%Y-%m-%d %H:%M:%S')
                anal_date_aware = timezone.localize(anal_date)
                valid_date = dt.datetime.strptime(prediction_json_file['SpatialMosStep']['valid_date'], '%Y-%m-%d %H:%M:%S')
                valid_date_aware = timezone.localize(valid_date)

                if spatialmos_run is None:
                    spatialmos_run = create_SpatialMosRun(anal_date_aware, prediction_json_file['SpatialMosRun']['parameter'])
                    logging.info('parameter: {:9} | anal_date: {} | Modelllauf erstellt'.format(prediction_json_file['SpatialMosRun']['parameter'], prediction_json_file['SpatialMosRun']['anal_date']))

                step = create_SpatialMosStep(prediction_json_file, spatialmos_run, valid_date_aware)
                logging.info('parameter: {:9} | anal_date: {} | valid_date: {} | Step: {:03d}'.format(prediction_json_file['SpatialMosRun']['parameter'], prediction_json_file['SpatialMosRun']['anal_date'], prediction_json_file['SpatialMosStep']['valid_date'], prediction_json_file['SpatialMosStep']['step']))
                create_SpatialMosPoint(prediction_json_file['SpatialMosPoint'], step)
                logging.info('parameter: {:9} | datum: {} | The spatialMos run was successfully imported. {}'.format(parameter, date, filename_spatialmos_step))

                os.remove(os.path.join("/www/", prediction_json_file['SpatialMosStep']['path_filename_SpatialMosStep']))
                for what in available_fields:
                    os.remove(os.path.join("/www/", prediction_json_file['SpatialMosStep'][f'path_filename_{what}']))

                logging.info('parameter: {:9} | anal_date: {} | There are no files available in the spool directory'.format(prediction_json_file['SpatialMosRun']['parameter'], prediction_json_file['SpatialMosRun']['anal_date']))

            else:
                logging.error('parameter: {:9} | datum: {} | No files could be found. {}'.format(parameter, date, filename_spatialmos_step))
                continue
            
        if spatialmos_run is not None:
            spatialmos_run.complete = True
            spatialmos_run.save()
            os.remove(filename_spatialmos_run_status)
            logging.info('parameter: {:9} | anal_date: {} | Complete'.format(prediction_json_file['SpatialMosRun']['parameter'], prediction_json_file['SpatialMosRun']['anal_date']))
