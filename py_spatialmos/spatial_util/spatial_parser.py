#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
'''The util is used to parse input for spatialMOS.'''

import argparse
from datetime import datetime as dt
from typing import Any, Dict, List


def spatial_parser_value_in_list(argsinfo: Dict[str, Any], key: str, options: argparse.Namespace, parsed_args) -> Dict[str, Any]:
    '''spatial_parser_value_in_list checks if the value is in a available list.'''
    option = getattr(options, key)
    if option in argsinfo[f'available_{key}']:
        parsed_args[key] = option
    else:
        raise RuntimeError('PARSERERROR --%s \'%s\' is not in %s' %
                           (key, option, argsinfo[f'available_{key}']))
    return parsed_args


def spatial_parser(args: List[str], argsinfo: Dict[str, Any]) -> Dict[str, Any]:
    '''A function to proceed some parsed Arguments.'''
    argsinfo_default = {
        'modeltype': False,
        'available_modeltype': [],
        'begin': False,
        'begindate': False,
        'date': False,
        'end': False,
        'enddate': False,
        'folder': False,
        'available_folder': [],
        'parameter': False,
        'available_parameter': [],
        'resolution': False,
        'available_resolution': [],
        'script': True,
        'available_script': [],
        }

    argsinfo = {**argsinfo_default, **argsinfo}
    parser = argparse.ArgumentParser(
        description='All required arguments for spatialMOS are captured and the input is checked.')
    parser.add_argument('--modeltype', dest='modeltype',
                        help=f"Enter the GFSE Mean or Spread: {argsinfo['available_modeltype']}", default='avg', type=str)
    parser.add_argument('--begin', dest='begin',
                        help='Enter a number for one day in the calendar year: e.g. 1', default=1, type=int)
    parser.add_argument('--begindate', dest='begindate',
                        help='Enter the begindate in the format YYYY-MM-DD.', default='', type=str)
    parser.add_argument('--date', dest='date',
                        help='Enter the begindate in the format YYYY-MM-DD.', default='', type=str)
    parser.add_argument(
        '--end', dest='end', help='Enter a number for one day in the calendar year: e.g. 1', default=365, type=int)
    parser.add_argument('--enddate', dest='enddate',
                        help='Enter the enddate in the format YYYY-MM-DD.', default='', type=str)
    parser.add_argument('--folder', dest='folder',
                        help=f"Enter a folder: {argsinfo['available_resolution']}", default='', type=str)
    parser.add_argument('--parameter', dest='parameter',
                        help=f"Enter a parameter from the list: {argsinfo['available_parameter']}", default='', type=str)
    parser.add_argument('--resolution', dest='resolution',
                        help=f"Model initialization hour: {argsinfo['available_resolution']}", default=0.5, type=float)
    parser.add_argument('--script', dest='script',
                        help=f"Enter a script from the list: {argsinfo['available_script']}", default='', type=str)

    options = parser.parse_args(args)
    parsed_args: Dict[str, Any] = {}
    if argsinfo['modeltype']:
        parsed_args = spatial_parser_value_in_list(
            argsinfo, 'modeltype', options, parsed_args)

    if argsinfo['begin']:
        parsed_args['begin'] = getattr(options, 'begin')

    if argsinfo['begindate']:
        parsed_args['begindate'] = dt.strftime(
            dt.strptime(options.begindate, '%Y-%m-%d'), '%Y%m%d')

    if argsinfo['date']:
        parsed_args['date'] = dt.strftime(
            dt.strptime(options.date, '%Y-%m-%d'), '%Y%m%d')


    if argsinfo['end']:
        parsed_args['end'] = getattr(options, 'end')

    if argsinfo['enddate']:
        parsed_args['enddate'] = dt.strftime(
            dt.strptime(options.enddate, '%Y-%m-%d'), '%Y%m%d')

    if argsinfo['folder']:
        parsed_args = spatial_parser_value_in_list(
            argsinfo, 'folder', options, parsed_args)

    if argsinfo['parameter']:
        parsed_args = spatial_parser_value_in_list(
            argsinfo, 'parameter', options, parsed_args)

    if argsinfo['resolution']:
        parsed_args = spatial_parser_value_in_list(
            argsinfo, 'resolution', options, parsed_args)

    if argsinfo['script']:
        parsed_args = spatial_parser_value_in_list(
            argsinfo, 'script', options, parsed_args)
    return parsed_args
