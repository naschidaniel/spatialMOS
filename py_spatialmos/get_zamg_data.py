#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This program is used to load data from the ZAMG website."""

import csv
import logging
import sys
import re
import time
import os
import datetime
from pathlib import Path
from typing import Iterable, TextIO

import pandas as pd
import requests
import pytz

from spatial_logging import spatial_logging

spatial_logging.logging_init(Path(f"/log/{__file__}.log"))

class ZamgData:
    """ZamgData Class"""

    @staticmethod
    def federal_state() -> Iterable[str]:
        return ["burgenland", "kaernten", "niederoesterreich", "oberoesterreich", "salzburg", "steiermark", "tirol", "vorarlberg", "wien"]

    @staticmethod
    def parameters() -> Iterable[str]:
        return ["timestamp", "timestamp_download", "station", "alt", "t", "rf", "wg", "wr", "wsg", "regen", "sonne", "ldred"]

    @classmethod
    def request_data(cls, state: str) -> str:
        request_url = f"https://www.zamg.ac.at/cms/de/wetter/wetterwerte-analysen/{state}/temperatur/?mode=geo&druckang=red"
        logging.info("The web page will be loaded %s", request_url)
        try:
            request_data = requests.get(request_url)
            if request_data.status_code != 200:
                raise(RuntimeError("The response of the Webpage '%s' does not match 200", request_url))
            return request_data.text
        except:
            logging.error("The request for '%s' failed", request_url)


class ZamgSpatialConverter:
    def __init__(self):
        federal_state = ZamgData.federal_state()
        raw_text_time = None
        retry = 0
        max_retrys = 3
        now_hour = int(datetime.datetime.now(pytz.timezone("Europe/Vienna")).strftime("%H"))
        while now_hour != raw_text_time:
            if retry <= max_retrys:
                file_counter = 0
                for state in federal_state:
                    raw_html_text = ZamgData.request_data(state)
                    df_red, raw_text_time = self.manipulate_html_text(raw_html_text)

                    # Merging of the two dataframes and reorder
                    df = df[["timestamp", "timestamp_download", "station", "alt", "t", "rf", "wg", "wr", "wsg", "regen", "sonne", "ldred", "ldstat"]]

                    # Check the data status of the website
                    if now_hour == raw_text_time:
                        file_counter = file_counter + 1
                        timestamp_save = datetime.now().strftime("%Y-%m-%d")
                        csvfile = f"{data_path}/{timestamp_save}_{raw_text_time}_ZAMG_PAGE_{state}.csv"
                        df.to_csv(csvfile, index=False,
                                quoting=csv.QUOTE_NONNUMERIC)
                        logging.info("{:18} | Uhrzeit Text {} | Zeit {}".format(
                            state, raw_text_time, now_hour))
                    else:
                        logging.warning("{:18} | Uhrzeit Text {} | Zeit {}".format(
                            state, raw_text_time, now_hour))

                    time.sleep(10)

                # Check whether all federal states have been successfully loaded
                if file_counter != 9:
                    logging.error(
                        "Not all federal states could be downloaded successfully. The process is repeated. | Retry %s/%s ", retry, max_retrys)
                    retry = retry + 1
                    file_counter = 0
                    logging.info("The process is repeated in 600 seconds.")
                    time.sleep(600)
                else:
                    logging.info(
                        "All data was downloaded from the Zamg website and saved as CSV files.")

            else:
                logging.error(
                    "The maximum number of retries was reached and not all data could be saved. %s/%s", retry, max_retrys)


    def manipulate_html_text(self, raw_html_text):

        # Text manipulations of the HTML Raw file
        # Special character
        raw_html_text = raw_html_text.replace('&uuml;', 'ü')
        raw_html_text = raw_html_text.replace('&ouml;', 'ö')
        raw_html_text = raw_html_text.replace('&szlig;', 'ß')
        raw_html_text = raw_html_text.replace('&auml;', 'ä')
        # Units
        raw_html_text = raw_html_text.replace('km/h', '')
        raw_html_text = raw_html_text.replace('&deg;', '')
        raw_html_text = raw_html_text.replace('%', '')
        raw_html_text = raw_html_text.replace('Windstille', '')
        raw_html_text = raw_html_text.replace(
            '<small style="font-size:0.85em;">m</small>', '')
        raw_html_text = raw_html_text.replace(
            '<small style="font-size:0.85em;">mm</small>', '')
        raw_html_text = raw_html_text.replace(
            '<small style="font-size:0.85em;">hPa</small>', '')
        raw_html_text = raw_html_text.replace(
            '<small style="font-size:0.85em;">Windstille</small>', '')
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


        raw_text_date_begin = re.search(
            '<h1 id="dynPageHead">', raw_html_text).end()
        raw_text_date_end = re.search("</h1>", raw_html_text).start()
        raw_text_date = raw_html_text[raw_text_date_begin:raw_text_date_end]
        raw_text_date = raw_text_date[re.search("-", raw_text_date).end():]
        raw_text_date = raw_text_date.strip()

        raw_text_time_begin = re.search(
            "Aktuelle Messwerte der Wetterstationen von ", raw_html_text).end()
        raw_text_time_end = re.search("Uhr</h2>", raw_html_text).start()
        raw_text_time = raw_html_text[raw_text_time_begin:raw_text_time_end]
        raw_text_time = int(raw_text_time.replace("\n", ""))

        raw_text_timestamp = f"{raw_text_date}T{raw_text_time}"

        # Extract measurements
        raw_text_measurements_begin = re.search('<tr class="dynPageTableLine1"><td class="wert">', raw_html_text).start()
        raw_text_measurements_end = re.search('Die Messwerte in dieser Liste', raw_html_text).start()
        raw_text_measurements = raw_html_text[raw_text_measurements_begin: raw_text_measurements_end].split("\n")

        # Removing the HTML tag
        html_tag_regex = re.compile(r".*?\>(.*?)\<")
        measurements = [re.findall(html_tag_regex, line) for line in raw_text_measurements]
        measurements = [list(filter(None, stations)) for stations in measurements]

        print(measurements)
        # remove superfluous columns
        text_filter = []
        for to_filter in measurements:
            text_filter.append(list(filter(None, to_filter)))
        text_filter = list(filter(None, text_filter))

        # Creating the Pandas Dataframe
        df = pd.DataFrame(text_filter, columns=[
                        "station", "alt", "t", "rf", "wg", "wsg", "regen", "sonne", "ldred"])
        df = df.dropna()

        # Data manipulation
        # Timestamp of the download
        df.insert(1, "timestamp", raw_text_timestamp)
        timestamp_download = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df.insert(2, "timestamp_download", timestamp_download)

        # Wind direction and wind speed in format: Süd, 19
        df["wr"] = [re.sub(r"[0-9,]", "", string) for string in df["wg"]]
        df["wr"] = [string.strip() for string in df["wr"]]
        df["wg"] = [re.sub(r"[a-zA-Züäö,]", "", string) for string in df["wg"]]
        df["wg"] = [string.strip() for string in df["wg"]]
        df["wg"][df["wr"] == "Windstille"] = 0

        df[["wg", "alt", "t", "rf", "wsg", "regen", "sonne", "ldred"]] = df[[
            "wg", "alt", "t", "rf", "wsg", "regen", "sonne", "ldred"]].astype(float)

        return df, raw_text_time

    @classmethod
    def convert(cls, target: TextIO):
        cls()
        pass


# Functions
def fetch_zamg_data():
    """fetch_zamg_data is used to store zamg data in csv files."""

    utcnow_str = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H_%M_%S")
    data_path = Path("./data/get_available_data/zamg/data")
    try:
        os.makedirs(data_path, exist_ok=True)
    except:
        raise OSError("The folder could not be created.")
    
    with open(data_path.joinpath(f"data_zamg_{utcnow_str}.csv"), "w", newline='') as target:
        ZamgSpatialConverter.convert(target)
    



# Main
if __name__ == "__main__":
    try:
        STARTTIME = datetime.datetime.now()
        logging.info("The data lwd download has started.")
        fetch_zamg_data()
        DURATION = datetime.datetime.now() - STARTTIME
        logging.info(DURATION)
    except Exception as ex:
        logging.exception(ex)
        raise ex
