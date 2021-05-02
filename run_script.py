#!/usr/bin/python
# -*- coding: utf-8 -*-


'''
  The generic script is used to get data from the data providers.
'''

import datetime
import logging
import sys
from py_spatialmos import get_gefs_forecasts
from py_spatialmos import get_lwd_data
from py_spatialmos import get_suedtirol_data
from py_spatialmos import get_zamg_data
from py_spatialmos import spatial_logging
from py_spatialmos import spatial_parser

# Main
if __name__ == '__main__':
    try:
        STARTTIME = datetime.datetime.now()
        spatial_logging.logging_init("run_get_data.log")
        argsinfo = {'available_dataprovider': ['gefs', 'lwd', 'suedtirol', 'zamg'],
                    'dataprovider': True,
                    }
        arguments = sys.argv[1:]
        PARSER_DICT = spatial_parser.spatial_parser(arguments, argsinfo)
        dataprovider = PARSER_DICT['dataprovider']
        if dataprovider == 'gefs':
            argsinfo = {'modeltype': True,
                        'date': True,
                        'available_modeltype': ["avg", "spr", "ens"],
                        'parameter': True,
                        'available_parameter': ["tmp_2m", "rh_2m", "ugrd_10m", "vgrd_10m"],
                        'resolution': True,
                        'available_resolution': [0.5, 1],
                        }
            PARSER_DICT = spatial_parser.spatial_parser(arguments, argsinfo)
            get_gefs_forecasts.fetch_gefs_data(PARSER_DICT["modeltype"], PARSER_DICT["date"], PARSER_DICT["parameter"], PARSER_DICT["resolution"])
        elif dataprovider == 'lwd':
            logging.info('The data lwd download has started.')
            get_lwd_data.fetch_lwd_data()
        elif dataprovider == 'suedtirol':
            argsinfo = {'begindate': True,
                        'enddate': True,
                        }
            PARSER_DICT = spatial_parser.spatial_parser(arguments, argsinfo)
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
