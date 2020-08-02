#!/usr/bin/python
# -*- coding: utf-8 -*-

"""A management command for importing the spatialMos predictions into the database."""

import os
import sys
import json
import logging
import datetime as dt
import pytz
import numpy as np
import pandas as pd
from django.db import connection, transaction
from django.core.management.base import BaseCommand, CommandError
from predictions.models import SpatialMosRun, SpatialMosStep, SpatialMosPoint
from datetime import datetime, timedelta
from django.core.files import File


class Command(BaseCommand):
    help = "Import the pre-processed forecast into the database. Options: --parameter ['tmp_2m', 'rh_2m', 'wind_10m'] --date '2020-08-02'"

    def add_arguments(self, parser):
        """Adding additional arguments"""
        parser.add_argument('parameter', type=str)
        parser.add_argument('date', type=str)

    def handle(self, *args, **options):
        """Main Function"""
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

            filename_nwp_mean, file_nwp_mean = filename_figure(prediction_json_file, 'nwp_mean')
            filename_samos_spread, file_nwp_spread = filename_figure(prediction_json_file, 'nwp_spread')
            filename_samos_mean, file_samos_mean = filename_figure(prediction_json_file, 'samos_mean')
            filename_nwp_spread, file_samos_spread = filename_figure(prediction_json_file, 'samos_spread')

            spatialmos_step.filename_nwp_mean.save(filename_nwp_mean, file_nwp_mean)
            spatialmos_step.filename_nwp_spread.save(filename_nwp_spread, file_nwp_spread)
            spatialmos_step.filename_spatialmos_mean.save(filename_samos_mean, file_samos_mean)
            spatialmos_step.filename_spatialmos_spread.save(filename_samos_spread, file_samos_spread)
            spatialmos_step.save()
            return spatialmos_step

        def create_SpatialMosPoint(spatialmos_point_entrys, spatialmos_step):
            """A function to create an entry in the table of the model SpatialMosPoint"""
            df = pd.DataFrame.from_dict(spatialmos_point_entrys)
            df = df.dropna()
            insert_list = []
            for item in df.to_dict('records'):
                newrecord = SpatialMosPoint(spatialmos_step=spatialmos_step, **item)
                insert_list.append(newrecord)

            if len(insert_list) > 0:
                SpatialMosPoint.objects.bulk_create(insert_list)

        parameter = options['parameter']
        date_timestamp = dt.datetime.strptime(options['date'], "%Y-%m-%d")
        date = date_timestamp.strftime("%Y%m%d")
       
        spatialmos_run = None
        available_steps = np.arange(6, 193, 6, int)
        for step in available_steps:
            filename_spatialmos_step = os.path.join("/www", f"./data/spool/{parameter}/samos/{date}_step_{step:03d}.json")
            if os.path.isfile(filename_spatialmos_step):
                with open(filename_spatialmos_step, 'r') as f:
                    prediction_json_file = json.load(f)

                timezone = pytz.timezone('UTC')
                anal_date = datetime.strptime(prediction_json_file['SpatialMosRun']['anal_date'], '%Y-%m-%d %H:%M:%S')
                anal_date_aware = timezone.localize(anal_date)
                valid_date = datetime.strptime(prediction_json_file['SpatialMosStep']['valid_date'], '%Y-%m-%d %H:%M:%S')
                valid_date_aware = timezone.localize(valid_date)

                if spatialmos_run is None:
                    spatialmos_run = create_SpatialMosRun(anal_date_aware, prediction_json_file['SpatialMosRun']['parameter'])
                    logging.info('parameter: {:9} | anal_date: {} | Modelllauf erstellt'.format(prediction_json_file['SpatialMosRun']['parameter'], prediction_json_file['SpatialMosRun']['anal_date']))

                step = create_SpatialMosStep(prediction_json_file, spatialmos_run, valid_date_aware)
                logging.info('parameter: {:9} | anal_date: {} | valid_date: {} | Step: {:03d}'.format(prediction_json_file['SpatialMosRun']['parameter'], prediction_json_file['SpatialMosRun']['anal_date'], prediction_json_file['SpatialMosStep']['valid_date'], prediction_json_file['SpatialMosStep']['step']))
                create_SpatialMosPoint(prediction_json_file['SpatialMosPoint'], step)

            else:
                logging.error('parameter: {:9} | datum: {} | No files could be found. {}'.format(parameter, date, filename_spatialmos_step))
                continue
    
        if spatialmos_run is not None:
            spatialmos_run.complete = True
            spatialmos_run.save()
            logging.info('parameter: {:9} | anal_date: {} | Complete'.format(prediction_json_file['SpatialMosRun']['parameter'], prediction_json_file['SpatialMosRun']['anal_date']))

            os.remove(prediction_json_file['SpatialMosStep']['filename_SpatialMosStep'])
            os.remove(prediction_json_file['SpatialMosStep']['filename_nwp_mean'])
            os.remove(prediction_json_file['SpatialMosStep']['filename_nwp_spread'])
            os.remove(prediction_json_file['SpatialMosStep']['path_filename_samos_mean'])
            os.remove(prediction_json_file['SpatialMosStep']['path_filename_samos_spread'])

            logging.info('parameter: {:9} | anal_date: {} | There are no files available in the spool directory'.format(prediction_json_file['SpatialMosRun']['parameter'], prediction_json_file['SpatialMosRun']['anal_date']))