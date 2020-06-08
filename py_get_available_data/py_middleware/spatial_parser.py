#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
"""The middleware is used to parse input for spatialMOS."""

import argparse
import sys
import logging
from datetime import datetime


def spatial_parser(beginn=False, beginndate=False, date=False, end=False, enddate=False, folder=False, name_folder="", host=False, name_host="", param=False, name_param=""):
    """A function to proceed some parsed Arguments."""
    parser = argparse.ArgumentParser(description="All required arguments for spatialMOS are captured and the input is checked.")
    parser.add_argument("--beginn", dest="beginn", help="Enter a number for one day in the calendar year: e.g. 1", default=1, type=int)
    parser.add_argument("--beginndate", dest="beginndate", help="Enter the beginndate in the format YYYY-MM-DD.", default="", type=str)
    parser.add_argument("--date", dest="date", help="Enter the beginndate in the format YYYY-MM-DD.", default="", type=str)
    parser.add_argument("--end", dest="end", help="Enter a number for one day in the calendar year: e.g. 1", default=365, type=int)
    parser.add_argument("--enddate", dest="enddate", help="Enter the enddate in the format YYYY-MM-DD.", default="", type=str)
    parser.add_argument("--folder", dest="folder", help="Enter a folder", default="", type=str)
    parser.add_argument("--host", dest="host", help="Specify the host: example.com", default="moses.tirol", type=str)
    parser.add_argument("--param", dest="param", help="Enter a parameter from the list: [tmp_2m | rh_2m | wind_10m]", default="", type=str)

    options = parser.parse_args()

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
            beginndate = datetime.strptime(options.date, "%Y-%m-%d")
            beginndate = datetime.strftime(date, "%Y%m%d")
            logging.info("PARSER | {:>20} | {}".format("--beginndate", beginndate))
        except ValueError:
            logging.error("PARSER | {:>20} | {}".format(
                "--beginndate", options.beginndate))
            raise ValueError("The date is not entered in the correct format: YYYY-MM-DD")
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
            logging.error("PARSER | {:>20} | {}".format(
                "--end", options.end))
            sys.exit(1)
    else:
        end = None


    if enddate is True:
        try:
            enddate = datetime.strptime(options.date, "%Y-%m-%d")
            enddate = datetime.strftime(date, "%Y%m%d")
            logging.info("PARSER | {:>20} | {}".format("--enddate", enddate))
        except ValueError:
            logging.error("PARSER | {:>20} | {}".format("--enddate", options.enddate))
            raise ValueError("The date is not entered in the correct format: YYYY-MM-DD")
    else:
        enddate = None

    if folder is True:
        logging.info("PARSER | {:>20} | {}".format(
            "name_parm options", name_folder))
        if options.parm in name_param:
            folder = options.folder
            logging.info("PARSER | {:>20} | {}".format("--parm", folder))
        else:
            print("--folder | Enter a folder from the list: {}".format(name_folder))
            logging.error("PARSER | {:>20} | {}".format("--folder", options.folder))
            sys.exit(1)
    else:
        folder = None

    if host is True:
        if options.host in name_host:
            host = options.host
            logging.info("PARSER | {:>20} | {}".format("--host", host))
        else:
            print("--host | Enter a host from the list: {}".format(name_host))
            logging.error("PARSER | {:>20} | {}".format("--host", options.host))
            sys.exit(1)
    else:
        host = None

    if param is True:
        logging.info("PARSER | {:>20} | {}".format(
            "name_param options", name_param))
        if options.param in name_param:
            param = options.param
            logging.info("PARSER | {:>20} | {}".format("--param", param))
        else:
            print("--param | Enter a host from the list: {}".format(name_param))
            logging.error("PARSER | {:>20} | {}".format(
                "--param", options.param))
            sys.exit(1)
    else:
        param = None

    parser_dict = {"beginn": beginn,
                   "beginndate": beginndate,
                   "date": date,
                   "end": end,
                   "enddate": enddate,
                   "folder": folder,
                   "host": host,
                   "param": param
                   }
    return parser_dict
