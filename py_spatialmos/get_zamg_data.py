#!/usr/bin/python
# -*- coding: utf-8 -*-
'''With this Python script data can be obtained from the ZAMG website.'''

import logging
import re
import time
import os
import datetime
from pathlib import Path
from typing import List, TextIO, Tuple
import requests
import pytz

from spatial_logging import spatial_logging
from spatial_writer import SpatialWriter

spatial_logging.logging_init(__file__)


class ZamgData:
    '''ZamgData Class'''

    # The data is loaded from the website and saved as a csv file.
    # https://www.zamg.ac.at/
    # The units are determined from the table https://www.zamg.ac.at/cms/de/wetter/wetterwerte-analysen/tirol

    @staticmethod
    def parameters() -> dict:
        '''parameters and a unit which is encapsulated in the spatialmos format.'''
        return {'date': {'name': 'date', 'unit': '[UTC]'},
                'name': {'name': 'name', 'unit': '[str]'},
                'alt': {'name': 'alt', 'unit': '[m]'},
                't': {'name': 't', 'unit': '[°C]'},
                'rf': {'name': 'rf', 'unit': '[%]'},
                'wg': {'name': 'wg', 'unit': '[km/h]'},
                'wr': {'name': 'wr', 'unit': '[str]'},
                'boe': {'name': 'boe', 'unit': '[km/h]'},
                'regen': {'name': 'regen', 'unit': '[mm]'},
                'sonne': {'name': 'sonne', 'unit': '[%]'},
                'ldred': {'name': 'ldred', 'unit': '[hPa]'}}

    @ classmethod
    def request_data(cls, state: str) -> str:
        '''request_data loads the data from the Website'''
        request_url = f'https://www.zamg.ac.at/cms/de/wetter/wetterwerte-analysen/{state}/temperatur/?mode=geo&druckang=red'
        logging.info('The web page will be loaded %s', request_url)
        try:
            request_data = requests.get(request_url)
            if request_data.status_code != 200:
                raise(RuntimeError(
                    f'The response of the Webpage \'{request_url}\' does not match 200'))
            else:
                logging.info('The URL %s was loaded successfully', request_url)
            return request_data.text
        except:
            logging.error('The request for \'%s\' failed', request_url)
            return ''


class ZamgSpatialConverter:
    '''ZamgSpatialConverter Class'''

    def __init__(self, target: TextIO):
        '''init ZamgSpatialConverter'''
        federal_state = ['burgenland', 'kaernten', 'niederoesterreich',
                         'oberoesterreich', 'salzburg', 'steiermark', 'tirol', 'vorarlberg', 'wien']
        parameters = ZamgData.parameters()
        writer = SpatialWriter(parameters, target)
        raw_text_time = None
        retry = 0
        max_retries = 3
        now_hour = int(datetime.datetime.now(
            pytz.timezone('Europe/Vienna')).strftime('%H'))
        while retry <= max_retries:
            for state in federal_state:
                raw_html_text = ZamgData.request_data(state)
                if raw_html_text == '':
                    continue

                measurements_optimized, raw_text_time = self.manipulate_html_text(
                    raw_html_text)
                # Check the data status of the website
                if now_hour == int(raw_text_time):
                    for row in measurements_optimized:
                        writer.append(row)
                    logging.info(
                        'The weather data for %s has been saved.', state)
                    federal_state = [
                        i for i in federal_state if state not in i]
                else:
                    logging.warning(
                        'The weather data for %s is not yet up to date.', state)
                time.sleep(10)

            # Check whether all federal states have been successfully loaded
            if len(federal_state) != 0:
                logging.error(
                    'No current data could be loaded for the federal state %s and retry %s/%s ', federal_state, retry, max_retries)
                logging.info('The process is repeated in 600 seconds.')
                retry += 1
                time.sleep(600)
            else:
                logging.info(
                    'All data for was downloaded from the Zamg website and saved as CSV files.')
                break
        else:
            logging.error(
                'The maximum number of retries was reached %s/%s and not all data could be saved.', retry, max_retries)

    def manipulate_html_text(self, raw_html_text: str) -> Tuple[List[List[str]], str]:
        '''manipulate_html_text changes the html text and returns the extracted information'''
        utc_now_hour = datetime.datetime.utcnow().replace(
            minute=0, second=0, microsecond=0)
        # Special character
        raw_html_text = raw_html_text.replace('&uuml;', 'ü')
        raw_html_text = raw_html_text.replace('&ouml;', 'ö')
        raw_html_text = raw_html_text.replace('&szlig;', 'ß')
        raw_html_text = raw_html_text.replace('&auml;', 'ä')
        # Units
        raw_html_text = raw_html_text.replace('km/h', '')
        raw_html_text = raw_html_text.replace('&deg;', '')
        raw_html_text = raw_html_text.replace('%', '')
        raw_html_text = raw_html_text.replace(
            '<small style="font-size:0.85em;">m</small>', '')
        raw_html_text = raw_html_text.replace(
            '<small style="font-size:0.85em;">mm</small>', '')
        raw_html_text = raw_html_text.replace(
            '<small style="font-size:0.85em;">hPa</small>', '')
        raw_html_text = raw_html_text.replace(
            '<small style="font-size:0.85em;">Windstille</small>', 'Windstille')
        # Pressure tendency
        raw_html_text = raw_html_text.replace(
            '<img src="https://www.zamg.ac.at/pict/wetter/a1.png" width="15" height="12" alt="Drucktendenz: steigend, dann stabil" title="steigend, dann stabil" /></td>', '')
        raw_html_text = raw_html_text.replace(
            '<img src="https://www.zamg.ac.at/pict/wetter/a2.png" width="15" height="12" alt="Drucktendenz: steigend" title="steigend" />', '')
        raw_html_text = raw_html_text.replace(
            '<img src="https://www.zamg.ac.at/pict/wetter/a3.png" width="15" height="12" alt="Drucktendenz: stabil, dann steigend" title="stabil, dann steigend" /></td>', '')
        raw_html_text = raw_html_text.replace(
            '<img src="https://www.zamg.ac.at/pict/wetter/a5.png" width="15" height="12" alt="Drucktendenz: fallend, dann leicht steigend" title="fallend, dann leicht steigend" />', '')
        raw_html_text = raw_html_text.replace(
            '<img src="https://www.zamg.ac.at/pict/wetter/a6.png" width="15" height="12" alt="Drucktendenz: fallend, dann stabil" title="fallend, dann stabil" />', '')
        raw_html_text = raw_html_text.replace(
            '<img src="https://www.zamg.ac.at/pict/wetter/a7.png" width="15" height="12" alt="Drucktendenz: fallend" title="fallend" />', '')
        raw_html_text = raw_html_text.replace(
            '<img src="https://www.zamg.ac.at/pict/wetter/a8.png" width="15" height="12" alt="Drucktendenz: stabil, dann fallend" title="stabil, dann fallend" />', '')
        # Incorrect values
        raw_html_text = raw_html_text.replace('n.v.', '-999')
        raw_html_text = raw_html_text.replace('k.A.', '-999')
        raw_html_text = raw_html_text.replace('*', '')

        raw_text_date_begin = raw_html_text.find(
            '<h1 id="dynPageHead">') + len('<h1 id="dynPageHead">')
        raw_text_date_end = raw_html_text.find('</h1>')
        raw_text_date = raw_html_text[raw_text_date_begin:raw_text_date_end]
        raw_text_date = raw_text_date[raw_text_date.find('-')+1:]
        raw_text_date = raw_text_date.strip()

        raw_text_time_begin = raw_html_text.find(
            'Aktuelle Messwerte der Wetterstationen von ') + len('Aktuelle Messwerte der Wetterstationen von ')
        raw_text_time_end = raw_html_text.find('Uhr</h2>')
        raw_text_time = raw_html_text[raw_text_time_begin:raw_text_time_end]
        raw_text_time = raw_text_time.replace('\n', '')

        # Extract measurements
        raw_text_measurements_begin = raw_html_text.find(
            '<tr class="dynPageTableLine1"><td class="wert">')
        raw_text_measurements_end = raw_html_text.find(
            "Die Messwerte in dieser Liste")
        raw_text_measurements = raw_html_text[raw_text_measurements_begin: raw_text_measurements_end].split(
            '\n')

        # Removing the HTML tag
        html_tag_regex = re.compile(r'.*?\>(.*?)\<')
        measurements = [re.findall(html_tag_regex, line)
                        for line in raw_text_measurements]
        measurements = [list(filter(None, stations))
                        for stations in measurements]
        measurements = [list(map(lambda x: x.strip(' ').replace(
            'Windstille', 'Windstille, 0'), stations)) for stations in measurements]

        # remove superfluous whitespaces and separate direction and wind speed
        measurements_optimized = []
        for stations in measurements:
            flat_list = [datetime.datetime.strftime(
                utc_now_hour, '%Y-%m-%d %H:%M:%S')]
            if not any(', ' in s for s in stations):
                stations.insert(5, '-999')
            for entry in stations:
                entry = entry.strip(' ')
                if ', ' in entry:
                    for i in entry.split(', '):
                        # Fix Windstille and and Direction
                        if i == 'Windstille':
                            flat_list.append('Windstille')
                        else:
                            flat_list.append(i)
                else:
                    flat_list.append(entry)
            if len(flat_list) >= 4:  # drop district lines
                measurements_optimized.append(flat_list)
        return (measurements_optimized, raw_text_time)

    @ classmethod
    def convert(cls, target: TextIO):
        '''convert the data and save it in spatialMOS CSV format'''
        cls(target)


# Functions
def fetch_zamg_data():
    '''fetch_zamg_data is used to store zamg data in csv files.'''
    utcnow_str = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H_%M_%S')
    data_path = Path('./data/get_available_data/zamg/data')
    try:
        os.makedirs(data_path, exist_ok=True)
    except:
        logging.error('The folders could not be created.')

    with open(data_path.joinpath(f'data_zamg_{utcnow_str}.csv'), 'w', newline='') as target:
        ZamgSpatialConverter.convert(target)


# Main
if __name__ == '__main__':
    try:
        STARTTIME = datetime.datetime.now()
        logging.info('The data zamg download has started.')
        fetch_zamg_data()
        DURATION = datetime.datetime.now() - STARTTIME
        logging.info('The script has run successfully in %s', DURATION)
    except Exception as ex:
        logging.exception(ex)
        raise ex
