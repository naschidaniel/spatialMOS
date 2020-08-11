#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""The middleware is used to parse input for spatialMOS."""

import argparse
import sys
import logging
from datetime import datetime


def spatial_parser(modeltype=False, name_modeltype="", begin=False, begindate=False, date=False, end=False, enddate=False, folder=False, name_folder="", host=False, name_host="", parameter=False, name_parameter="", resolution=False, name_resolution=""):
    """A function to proceed some parsed Arguments."""
    parser = argparse.ArgumentParser(description="All required arguments for spatialMOS are captured and the input is checked.")
    parser.add_argument("--modeltype", dest="modeltype", help=f"Enter the GFSE Mean or Spread: {name_modeltype}", default="avg", type=str)
    parser.add_argument("--begin", dest="begin", help="Enter a number for one day in the calendar year: e.g. 1", default=1, type=int)
    parser.add_argument("--begindate", dest="begindate", help="Enter the begindate in the format YYYY-MM-DD.", default="", type=str)
    parser.add_argument("--date", dest="date", help="Enter the begindate in the format YYYY-MM-DD.", default="", type=str)
    parser.add_argument("--end", dest="end", help="Enter a number for one day in the calendar year: e.g. 1", default=365, type=int)
    parser.add_argument("--enddate", dest="enddate", help="Enter the enddate in the format YYYY-MM-DD.", default="", type=str)
    parser.add_argument("--folder", dest="folder", help=f"Enter a folder: {name_folder}", default="", type=str)
    parser.add_argument("--host", dest="host", help=f"Specify the host: {name_host}", default="moses.tirol", type=str)
    parser.add_argument("--parameter", dest="parameter", help=f"Enter a parameter from the list: {name_parameter}", default="", type=str)
    parser.add_argument("--resolution", dest="resolution", help=f"Model initialization hour: {name_resolution}", default=1, type=int)

    options = parser.parse_args()


    if modeltype is True:
        if options.modeltype in name_modeltype:
            modeltype = options.modeltype
            logging.info("PARSER | {:>20} | {}".format("--modeltype", modeltype))
        else:
            logging.error("PARSER | {:>20} | {}".format("--modeltype", name_modeltype))
            sys.exit(1)
    else:
        modeltype = None

    if begin is True:
        if isinstance(options.begin, str):
            begin = options.begin
            logging.info("PARSER | {:>20} | {}".format("--begin", enddate))
        else:
            logging.error("PARSER | {:>20} | {}".format("--begin", options.begin))
            sys.exit(1)
    else:
        begin = None

    if begindate is True:
        try:
            begindate = datetime.strptime(options.begindate, "%Y-%m-%d")
            begindate = datetime.strftime(begindate, "%Y%m%d")
            logging.info("PARSER | {:>20} | {}".format("--begindate", begindate))
        except ValueError:
            logging.error("PARSER | {:>20} | {}".format("--begindate", options.begindate))
            raise ValueError("The begindate is not entered in the correct format: YYYY-MM-DD")
    else:
        begindate = None

    if date is True:
        try:
            date = datetime.strptime(options.date, "%Y-%m-%d")
            date = datetime.strftime(date, "%Y%m%d")
            logging.info("PARSER | {:>20} | {}".format("--date", date))
        except ValueError:
            logging.error("PARSER | {:>20} | {}".format("--date", options.date))
            raise ValueError("The date is not entered in the correct format: YYYY-MM-DD")
    else:
        date = None

    if end is True:
        if isinstance(options.end, int):
            end = options.end
            logging.info("PARSER | {:>20} | {}".format("--end", end))
        else:
            logging.error("PARSER | {:>20} | {}".format("--end", options.end))
            sys.exit(1)
    else:
        end = None


    if enddate is True:
        try:
            enddate = datetime.strptime(options.enddate, "%Y-%m-%d")
            enddate = datetime.strftime(enddate, "%Y%m%d")
            logging.info("PARSER | {:>20} | {}".format("--enddate", enddate))
        except ValueError:
            logging.error("PARSER | {:>20} | {}".format("--enddate", options.enddate))
            raise ValueError("The date is not entered in the correct format: YYYY-MM-DD")
    else:
        enddate = None

    if folder is True:
        logging.info("PARSER | {:>20} | {}".format(
            "name_folder options", name_folder))
        if options.folder in name_folder:
            folder = options.folder
            logging.info("PARSER | {:>20} | {}".format("--folder", folder))
        else:
            logging.error("--folder | Enter a folder from the list: {}".format(name_folder))
            sys.exit(1)
    else:
        folder = None

    if host is True:
        if options.host in name_host:
            host = options.host
            logging.info("PARSER | {:>20} | {}".format("--host", host))
        else:
            logging.error("--host | Enter a host from the list: {}".format(name_host))
            sys.exit(1)
    else:
        host = None

    if parameter is True:
        logging.info("PARSER | {:>20} | {}".format(
            "name_parameter options", name_parameter))
        if options.parameter in name_parameter:
            parameter = options.parameter
            logging.info("PARSER | {:>20} | {}".format("--parameter", parameter))
        else:
            logging.error("--parameter | Enter a parameter from the list: {}".format(name_parameter))
            sys.exit(1)
    else:
        parameter = None

    if resolution is True:
        logging.info("PARSER | {:>20} | {}".format("name_resolution options", name_resolution))
        if options.resolution in name_resolution:
            if isinstance(options.resolution, int):
                resolution = options.resolution
                logging.info("PARSER | {:>20} | {}".format("--resolution", resolution))
            else:
                logging.error("PARSER | {:>20} | {}".format("--resolution", options.resolution))
                sys.exit(1)
        else:
            logging.error("--resolution | Enter a resolution from the list: {}".format(name_resolution))
            sys.exit(1)
    else:
        resolution = None

    parser_dict = {"modeltype": modeltype,
                   "begin": begin,
                   "begindate": begindate,
                   "date": date,
                   "end": end,
                   "enddate": enddate,
                   "folder": folder,
                   "host": host,
                   "parameter": parameter,
                   "resolution": resolution
                   }
    return parser_dict
