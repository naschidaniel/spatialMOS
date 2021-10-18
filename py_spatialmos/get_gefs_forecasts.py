#!/usr/bin/python
# -*- coding: utf-8 -*-
'''The script was developed by Reto Stauffer and extended by Daniel Naschberger.

The sourcecode of Reto Stauffer can be found at :
https://github.com/retostauffer/GEFS_Downloader_Simple'''


import os
import sys
import re
import logging
from datetime import datetime
import pathlib
import requests

class IdxEntry():
    '''A small helper class to handle index entries.'''

    def __init__(self, args):
        '''IdxEntry(args)

        A small helper class to handle index entries.

        Parameters
        ----------
        args : list
            list with three entries (bytes start, param name, param level)
        '''
        self._byte_start = int(args[0])
        self._var = str(args[1])
        self._lev = str(args[2])
        self._byte_end = False

    def add_end_byte(self, x):
        '''add_end_byte(x)

        Appends the ending byte.
        '''
        self._byte_end = x

    def end_byte(self):
        '''end_byte()

        Returns end byte.
        '''
        return getattr(self, '_byte_end')


    def start_byte(self):
        '''start_byte()

        Returns start byte.
        '''
        return getattr(self, '_byte_start')

    def key(self):
        '''key()

        Returns
        -------
        Returns a character string '<param name>:<param level>'.
        '''
        var = getattr(self, '_var')
        lev = getattr(self, '_lev')
        return f'{var}:{lev}'

    def range(self):
        '''range()

        Returns
        -------
        Returns the byte range for curl.
        '''
        try:
            start = getattr(self, '_byte_start')
            end = getattr(self, '_byte_end')
        except AttributeError as ex:
            logging.exception(ex)
            raise AttributeError from ex
        end = '' if end is None else f'{end}'

        return f'{start}-{end}'

    def __repr__(self):
        if isinstance(self._byte_end, bool):
            end = 'UNKNOWN'
        elif self._byte_end is None:
            end = 'end of file'
        else:
            end = f'{self._byte_end}'
        return f'IDX ENTRY: {self._byte_start:10d}-{end:>10s}, \'{self.key()}\''



def get_file_names(data_path_gribfile, baseurl, date, mem, step, modeltype, resolution):
    '''With this function the file names from the server are preprocessed.'''

    if modeltype in ['avg', 'spr']:
        if resolution == 0.5:
            # Create URL for geavg.t00z.pgrb2a.0p50.f000.idx
            filename = f'ge{modeltype}.t{date.strftime("%H")}z.pgrb2a.0p50.f{step:03d}'
        elif resolution == 1:
            # since UPDATE of noa server depraced 2020-09-27
            # Create URL for geavg.t00z.pgrb2af00.idx
            filename = f'ge{modeltype}.t{date.strftime("%H")}z.pgrb2af{step:02d}' if step < 100 else f'{step:03d}'
        else:
            logging.error('The resolution %d ist not supported', resolution)
            sys.exit(1)

        gribfile = os.path.join(date.strftime(baseurl), filename)
        gribfile_path = f"{date.strftime('GFEE_%Y%m%d_%H00')}_{modeltype}_f{step:03d}.grb2"
    else:
        # UPDATE NAMES 2020-09-27
        # Create URL for gec00.t00z.pgrb2a.0p50.f000.idx
        # Create URL for gep01.t00z.pgrb2a.0p50.f000.idx
        gribfile = os.path.join(date.strftime(baseurl), f"ge{'c' if mem == 0 else 'p'}{mem:02d}.t{date.strftime('%H')}z.pgrb2a.0p50.f{step:03d}")
        gribfile_path = f"date.strftime('GEFS_%Y%m%d_%H00')_{mem:02d}_f{step:03d}.grb2"
    return {'grib': gribfile,
            'idx': f'{gribfile}.idx',
            'gribfile_path': os.path.join(data_path_gribfile, gribfile_path)}


def parse_index_file(idxfile, params):
    '''A function for processing the GEFS idx files'''
    try:
        logging.info('The index file is going to be downloaded: %s', idxfile)
        req = requests.get(idxfile)
        data = req.text.split('\n')
    except requests.exceptions.HTTPError as ex:
        logging.error('Problems downloading index file ... %s ... return None', idxfile)
        logging.exception(ex)
        return None
    except requests.exceptions.Timeout as ex:
        logging.exception(ex)
        return None

    # List to store the required index message information
    idx_entries = []

    comp = re.compile(r'^\d+:(\d+):d=\d{10}:([^:.*]*):([^:.*]*)')
    for line in data:
        if len(line) == 0:
            continue
        match = re.findall(comp, line)
        if not match:
            raise Exception(f'whoops, pattern mismatch \'{line}\'')
        # Else crate the variable hash
        idx_entries.append(IdxEntry(match[0]))

    for k, _ in enumerate(idx_entries):
        if (k + 1) == len(idx_entries):
            idx_entries[k].add_end_byte(None)
        else:
            idx_entries[k].add_end_byte(idx_entries[k+1].start_byte() - 1)

    res = []
    for x in idx_entries:
        if x.key() in params:
            res.append(x.range())
    return res


def download_grib(grib, gribfile_path, required):
    '''A function to download GRIB files.'''
    headers = {'Range': f"bytes={','.join(required)}"}
    req_grib = requests.get(grib, headers=headers)

    try:
        with open(gribfile_path, 'wb') as f:
            f.write(req_grib.content)
            f.close()
        return True
    except OSError as ex:
        logging.error(
            'The Grbifile \'%s\' could not be loaded and saved in \'%s\'', grib, gribfile_path)
        logging.exception(ex)
        return False


def select_params(p):
    '''A function to select a parameter'''
    available_params = {
        'tmp_2m': 'TMP:2 m above ground',
        'rh_2m': 'RH:2 m above ground',
        'ugrd_10m': 'UGRD:10 m above ground',
        'vgrd_10m': 'VGRD:10 m above ground',
    }
    return available_params.get(p, None)


def fetch_gefs_data(modeltype, date, parameter, resolution):
    '''Function for downloading gribfiles from the GEFS NCEP server.'''

    # A failure variable if an error occurs
    exit_with_error = False

    params = select_params(parameter)

    # runhour is in [0, 6, 12, 18]
    runhour = 0
    date = datetime.strptime(f'{date} {runhour:02d}:00:00', '%Y%m%d %H:%M:%S')

    # Steps/members. The +1 is required to get the required sequence!
    steps = range(6, 300+1, 6)

    logging.info('-------------------------------------------------------------------------------------------------')

    # https://www.nco.ncep.noaa.gov/pmb/products/gens/
    if modeltype in ['avg', 'spr']:
        members = range(0, 1, 1)
        logging.info('Downloading members: %s', modeltype)
        if resolution == 1:
            data_path = pathlib.Path(f'./data/get_available_data/gefs_avgspr_forecast_p1/{parameter}')
            # url exchanged on 2020-09-23 response with a 404 error
            baseurl = 'https://www.ftp.ncep.noaa.gov/data/nccf/com/gens/prod/gefs.%Y%m%d/%H/pgrb2a/'
        elif resolution == 0.5:
            data_path = pathlib.Path(f'./data/get_available_data/gefs_avgspr_forecast_p05/{parameter}')
            # baseurl = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.%Y%m%d/%H/pgrb2ap5/' # url exchanged on 2020-09-23 response with a 404 error
            baseurl = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.%Y%m%d/%H/atmos/pgrb2ap5/'
    else:
        data_path = pathlib.Path(f'./data/get_available_data/gefs_ens_forecast_p05/{parameter}')
        members = range(0, 30+1, 1)
        logging.info('Downloading members: {%s}', ', '.join([f'{x:d}' for x in members]))
        # url exchanged on 2020-09-23 response with a 404 error
        #baseurl = ' http://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.%Y%m%d/%H/pgrb2/'
        baseurl = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.%Y%m%d/00/atmos/pgrb2ap5/'


    steps_str = ', '.join([f'{x:d}' for x in steps])
    logging.info('Downloading steps: %s', steps_str)
    logging.info('For date/model initialization %s', date.strftime('%Y-%m-%d %H:%M UTC'))
    logging.info('Base url: %s', date.strftime(baseurl))
    logging.info('-------------------------------------------------------------------------------------------------')

    # Looping over the different members first
    for mem in members:
        # Looping over forecast lead times
        for step in steps:
            logging.info('-------------------------------------------------------------------------------------------------')
            if modeltype in ['avg', 'spr']:
                logging.info('Processing +%sh forecast %s', f'{step:03d}', modeltype)
            else:
                logging.info('Processing +%sh forecast, member %s', f'{step:03d}', f'{mem:02d}')

            # Specify and create output directory if necessary
            data_path_gribfile = data_path.joinpath(date.strftime('%Y%m%d%H%M'))
            os.makedirs(data_path_gribfile, exist_ok=True)


            files = get_file_names(
                data_path_gribfile, baseurl, date, mem, step, modeltype, resolution)
            if os.path.isfile(files['gribfile_path']):
                logging.info('gribfile_path file exists, skip: %s', files['gribfile_path'])
                logging.info('-------------------------------------------------------------------------------------------------')
                continue

            logging.info('Grib file: %s', files['grib'])
            logging.info('Index file: %s', files['idx'])
            logging.info('gribfile_path file: %s', files['gribfile_path'])

            # Read/parse index file (if possible)
            required = parse_index_file(files['idx'], params)

            # If no messages found: continue
            if required is None or len(required) == 0:
                exit_with_error = True
                continue

            download_grib_success = download_grib(
                files['grib'], files['gribfile_path'], required)

            if not download_grib_success:
                exit_with_error = True
                continue

            logging.info('-------------------------------------------------------------------------------------------------')
    if exit_with_error:
        raise RuntimeError('Not all gribfiles could be loaded.')
