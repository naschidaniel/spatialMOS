#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
  The generic script is used to get data from the data providers.
'''

import datetime
import logging
from py_spatialmos import get_lwd_data
from py_spatialmos import get_suedtirol_data
from py_spatialmos import get_zamg_data
from py_spatialmos import spatial_logging
from py_spatialmos.py_middleware import spatial_parser

# Main
if __name__ == '__main__':
    try:
        STARTTIME = datetime.datetime.now()
        spatial_logging.logging_init("run_get_data.log")
        PARSER_DICT = spatial_parser.spatial_parser(dataprovider=True, available_dataprovider=['lwd', 'suedtirol', 'zamg'])
        dataprovider = PARSER_DICT['dataprovider']
        if dataprovider == 'lwd':
            logging.info('The data lwd download has started.')
            get_lwd_data.fetch_lwd_data()
        elif dataprovider == 'suedtirol':
            PARSER_DICT = spatial_parser.spatial_parser(begindate=True, enddate=True)
            logging.info('The data suedtirol download from \'%s\' to \'%s\' has started.', PARSER_DICT['begindate'], PARSER_DICT['enddate'])
            get_suedtirol_data.fetch_suedtirol_data(PARSER_DICT['begindate'], PARSER_DICT['enddate'])
        elif dataprovider == 'zamg':
            logging.info('The data zamg download has started.')
            get_zamg_data.fetch_zamg_data()

        DURATION = datetime.datetime.now() - STARTTIME
        logging.info('The script has run successfully in %s', DURATION)
    except Exception as ex:
        logging.exception(ex)
        raise ex
