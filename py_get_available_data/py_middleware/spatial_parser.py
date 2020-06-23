#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""The middleware is used to parse input for spatialMOS."""

import argparse
import sys
import logging
from datetime import datetime


def spatial_parser(avgspr=False, name_avgspr="", beginn=False, beginndate=False, date=False, end=False, enddate=False, folder=False, name_folder="", host=False, name_host="", parameter=False, name_parameter="", runhour=False, name_runhour=""):
    """A function to proceed some parsed Arguments."""
    parser = argparse.ArgumentParser(description="All required arguments for spatialMOS are captured and the input is checked.")
    parser.add_argument("--avgspr", dest="avgspr", help=f"Enter the GFSE Mean or Spread: {name_avgspr}", default="avg", type=str)
    parser.add_argument("--beginn", dest="beginn", help="Enter a number for one day in the calendar year: e.g. 1", default=1, type=int)
    parser.add_argument("--beginndate", dest="beginndate", help="Enter the beginndate in the format YYYY-MM-DD.", default="", type=str)
    parser.add_argument("--date", dest="date", help="Enter the beginndate in the format YYYY-MM-DD.", default="", type=str)
    parser.add_argument("--end", dest="end", help="Enter a number for one day in the calendar year: e.g. 1", default=365, type=int)
    parser.add_argument("--enddate", dest="enddate", help="Enter the enddate in the format YYYY-MM-DD.", default="", type=str)
    parser.add_argument("--folder", dest="folder", help=f"Enter a folder: {name_folder}", default="", type=str)
    parser.add_argument("--host", dest="host", help=f"Specify the host: {name_host}", default="moses.tirol", type=str)
    parser.add_argument("--parameter", dest="parameter", help=f"Enter a parameter from the list: {name_parameter}", default="", type=str)
    parser.add_argument("--runhour", dest="runhour", help=f"Model initialization hour: {name_runhour}", default=0, type=int)

    options = parser.parse_args()


    if avgspr is True:
        if options.avgspr in name_avgspr:
            avgspr = options.avgspr
            logging.info("PARSER | {:>20} | {}".format("--avgspr", avgspr))
        else:
            logging.error("--avgspr | Enter a avgspr from the list: {}".format(name_avgspr))
            sys.exit(1)
    else:
        avgspr = None

    if beginn is True:
        if isinstance(options.beginn, str):
            beginn = options.beginn
            logging.info("PARSER | {:>20} | {}".format("--beginn", enddate))
        else:
            logging.error("PARSER | {:>20} | {}".format(
                "--beginn", options.beginn))
            sys.exit(1)
    else:
        beginn = None

    if beginndate is True:
        try:
            beginndate = datetime.strptime(options.beginndate, "%Y-%m-%d")
            beginndate = datetime.strftime(beginndate, "%Y%m%d")
            logging.info("PARSER | {:>20} | {}".format("--beginndate", beginndate))
        except ValueError:
            logging.error("PARSER | {:>20} | {}".format(
                "--beginndate", options.beginndate))
            raise ValueError("The beginndate is not entered in the correct format: YYYY-MM-DD")
    else:
        beginndate = None

    if date is True:
        try:
            date = datetime.strptime(options.date, "%Y-%m-%d")
            date = datetime.strftime(date, "%Y%m%d")
            logging.info("PARSER | {:>20} | {}".format("--date", date))
        except ValueError:
            logging.error("PARSER | {:>20} | {}".format(
                "--date", options.date))
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

    if runhour is True:
        logging.info("PARSER | {:>20} | {}".format("name_runhour options", name_runhour))
        if options.runhour in name_runhour:
            if isinstance(options.runhour, int):
                runhour = options.runhour
                logging.info("PARSER | {:>20} | {}".format("--runhour", runhour))
            else:
                logging.error("PARSER | {:>20} | {}".format("--runhour", options.runhour))
                sys.exit(1)
        else:
            logging.error("--runhour | Enter a runhour from the list: {}".format(name_runhour))
            sys.exit(1)
    else:
        runhour = None

    parser_dict = {"avgspr": avgspr,
                   "beginn": beginn,
                   "beginndate": beginndate,
                   "date": date,
                   "end": end,
                   "enddate": enddate,
                   "folder": folder,
                   "host": host,
                   "parameter": parameter,
                   "runhour": runhour
                   }
    return parser_dict
