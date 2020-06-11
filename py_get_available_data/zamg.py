#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This program is used to load data from the ZAMG website."""

import csv
import logging
import sys
import re
import time
import os
from datetime import datetime
import pandas as pd
import requests
import pytz
from py_middleware import logger_module


# Functions
def fetch_zamg_data():
    """This function is used to store zamg data in csv files."""
    # Provide folder structure.
    data_path = "/get_available_data/zamg"
    if not os.path.exists(f"{data_path}"):
        os.mkdir(f"{data_path}")

    data_path = os.path.join(data_path, "data")
    if not os.path.exists(f"{data_path}"):
        os.mkdir(f"{data_path}")

    timezone = pytz.timezone("Europe/Vienna")
    federal_state = ["burgenland", "kaernten", "niederoesterreich",
                     "oberoesterreich", "salzburg", "steiermark", "tirol", "vorarlberg", "wien"]

    raw_text_time = None
    retry = 0
    max_retrys = 3
    now_hour = int(datetime.now(timezone).strftime("%H"))
    while now_hour != raw_text_time:
        if retry <= max_retrys:
            file_counter = 0
            for state in federal_state:
                # Station values and current pressure at station level
                df_stat, raw_text_time = download_zamg_page_data(
                    data_path, state, "stat")
                # Station values and current pressure at sea level
                df_red, raw_text_time = download_zamg_page_data(
                    data_path, state, "red")
                df_red = df_red[["station", "ldred"]]

                # Merging of the two dataframes and reorder
                df = df_stat.merge(df_red, on=["station"])
                df = df[["timestamp", "timestamp_download", "station", "alt", "t", "rf", "wg", "wr", "wsg", "regen", "sonne",
                         "ldred", "ldstat"]]

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
                    "Not all federal states could be downloaded successfully. The process is repeated. | Retry {}/{} ".format(retry, max_retrys))
                retry = retry + 1
                file_counter = 0
                logging.info("The process is repeated in 600 seconds.")
                time.sleep(600)
            else:
                logging.info(
                    "All data was downloaded from the Zamg website and saved as CSV files.")

        else:
            logging.error(
                "The maximum number of retries was reached and not all data could be saved. {}/{}".format(retry, max_retrys))
            sys.exit(1)


def download_zamg_page_data(data_path, state, pressure):
    """A function to download the current values from the website of ZAMG."""
    url_page = f"https://www.zamg.ac.at/cms/de/wetter/wetterwerte-analysen/{state}/temperatur/?mode=geo&druckang={pressure}"
    req_page = requests.get(url_page)

    if req_page.status_code == 200:
        # Text manipulations of the HTML Raw file
        raw_text = req_page.text
        # Special character
        raw_text = raw_text.replace('&uuml;', 'ü')
        raw_text = raw_text.replace('&ouml;', 'ö')
        raw_text = raw_text.replace('&szlig;', 'ß')
        raw_text = raw_text.replace('&auml;', 'ä')
        # Units
        raw_text = raw_text.replace('km/h', '')
        raw_text = raw_text.replace('&deg;', '')
        raw_text = raw_text.replace('%', '')
        raw_text = raw_text.replace('Windstille', '')
        raw_text = raw_text.replace(
            '<small style="font-size:0.85em;">m</small>', '')
        raw_text = raw_text.replace(
            '<small style="font-size:0.85em;">mm</small>', '')
        raw_text = raw_text.replace(
            '<small style="font-size:0.85em;">hPa</small>', '')
        raw_text = raw_text.replace(
            '<small style="font-size:0.85em;">Windstille</small>', '')
        # Pressure tendency
        raw_text = raw_text.replace(
            '<img src="https://www.zamg.ac.at/pict/wetter/a1.png" width="15" height="12" alt="Drucktendenz: steigend, dann stabil" title="steigend, dann stabil" /></td>', '')
        raw_text = raw_text.replace(
            '<img src="https://www.zamg.ac.at/pict/wetter/a2.png" width="15" height="12" alt="Drucktendenz: steigend" title="steigend" />', '')
        raw_text = raw_text.replace(
            '<img src="https://www.zamg.ac.at/pict/wetter/a3.png" width="15" height="12" alt="Drucktendenz: stabil, dann steigend" title="stabil, dann steigend" /></td>', '')
        raw_text = raw_text.replace(
            '<img src="https://www.zamg.ac.at/pict/wetter/a5.png" width="15" height="12" alt="Drucktendenz: fallend, dann leicht steigend" title="fallend, dann leicht steigend" />', '')
        raw_text = raw_text.replace(
            '<img src="https://www.zamg.ac.at/pict/wetter/a6.png" width="15" height="12" alt="Drucktendenz: fallend, dann stabil" title="fallend, dann stabil" />', '')
        raw_text = raw_text.replace(
            '<img src="https://www.zamg.ac.at/pict/wetter/a7.png" width="15" height="12" alt="Drucktendenz: fallend" title="fallend" />', '')
        raw_text = raw_text.replace(
            '<img src="https://www.zamg.ac.at/pict/wetter/a8.png" width="15" height="12" alt="Drucktendenz: stabil, dann fallend" title="stabil, dann fallend" />', '')
        # Incorrect values
        raw_text = raw_text.replace('n.v.', '-999')
        raw_text = raw_text.replace('k.A.', '-999')
        raw_text = raw_text.replace('*', '')

        timezone = pytz.timezone("Europe/Vienna")
        now = int(datetime.now(timezone).strftime("%Y%m%d%H%M"))
        tempfile = os.path.join(data_path, f"{state}_{now}.html.tmp")
        with open(tempfile, "w") as f:
            f.write(raw_text)
            f.close()

        raw_text_date_begin = re.search(
            '<h1 id="dynPageHead">', raw_text).end()
        raw_text_date_end = re.search("</h1>", raw_text).start()
        raw_text_date = raw_text[raw_text_date_begin:raw_text_date_end]
        raw_text_date = raw_text_date[re.search("-", raw_text_date).end():]
        raw_text_date = raw_text_date.strip()

        raw_text_time_begin = re.search(
            "Aktuelle Messwerte der Wetterstationen von ", raw_text).end()
        raw_text_time_end = re.search("Uhr</h2>", raw_text).start()
        raw_text_time = raw_text[raw_text_time_begin:raw_text_time_end]
        raw_text_time = int(raw_text_time.replace("\n", ""))

        raw_text_timestamp = f"{raw_text_date}T{raw_text_time}"

        # trim data
        measured_values_begin = re.search(
            '<tr class="dynPageTableLine1"><td class="wert">', raw_text).start()
        measured_values_end = re.search(
            'Die Messwerte in dieser Liste', raw_text).start()
        measured_values = raw_text[measured_values_begin: measured_values_end]

        with open(tempfile, "w") as f:
            f.write(measured_values)
            f.close()

        # Data manipulation of the tempfile
        lines = [line.rstrip("\n") for line in open(tempfile)]
        os.remove(tempfile)

        # Removing the HTML tag
        text_list = []
        for line in lines:
            html_tag_regex = re.compile(".*?\>(.*?)\<")
            result = re.findall(html_tag_regex, line)
            text_list.append(result)

        # remove superfluous columns
        text_filter = []
        for to_filter in text_list:
            text_filter.append(list(filter(None, to_filter)))
        text_filter = list(filter(None, text_filter))

        # Creating the Pandas Dataframe
        ld_name = "ld" + pressure
        df = pd.DataFrame(text_filter, columns=[
                          "station", "alt", "t", "rf", "wg", "wsg", "regen", "sonne", ld_name])
        df = df.dropna()

        # Data manipulation
        # Timestamp of the download
        df.insert(1, "timestamp", raw_text_timestamp)
        timestamp_download = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df.insert(2, "timestamp_download", timestamp_download)

        # Wind direction and wind speed in format: Süd, 19
        df["wr"] = [re.sub(r"[0-9,]", "", string) for string in df["wg"]]
        df["wr"] = [string.strip() for string in df["wr"]]
        df["wg"] = [re.sub(r"[a-zA-Züäö,]", "", string) for string in df["wg"]]
        df["wg"] = [string.strip() for string in df["wg"]]
        df["wg"][df["wr"] == "Windstille"] = 0

        df[["wg", "alt", "t", "rf", "wsg", "regen", "sonne", ld_name]] = df[[
            "wg", "alt", "t", "rf", "wsg", "regen", "sonne", ld_name]].astype(float)

        return (df, raw_text_time)
    else:
        logging.error(
            f"The request for the URL '{url_page}' returned the status code 404")
        df = None
        raw_text_time = None
        return(df, raw_text_time)


# Main
if __name__ == "__main__":
    starttime = logger_module.start_logging("get_available_data", "zamg")
    fetch_zamg_data()
    logger_module.end_logging(starttime)
