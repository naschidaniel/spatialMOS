#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Ein Programm zu zum erstellen von Datentables für eine spatiale Klimatologie. Die Klimatologien können mithilfe der Statistiksoftware R berechnet werden
"""
import csv
import optparse
import os
import sys
import threading

import dateutil
import numpy as np
import pandas as pd

# Lokale Files
sys.path.insert(0, os.getcwd())
from PyspatialMOS.datamanipulation.grib_files_to_stations import scandir


# Functions
def log_spread(spread):
    if spread == float(0):
        log_spread_val = np.log(0.001)
    else:
        log_spread_val = np.log(spread)
    return round(log_spread_val, 3)


def kfold(datum, k):
    """Funktion zum erstellen eines Dict zur Crossvalidation auf basis eines Datumsvektors.
    datum = list; k = int()
    """
    kfold = []
    for j in np.arange(1, k + 1):
        for i in np.arange(0, len(datum) / k):
            kfold.append(j)
    kfold = kfold[0:len(datum)]
    kfold_dictonary = dict(zip(datum, kfold))
    return (kfold_dictonary)


def combine_df_csvfiles(df, csvfiles_sorted, name_parm, station_parm):
    ''''Worker Funktion zum erstellen von Klimatologien für die weitere statistische Datenaufarbeitung in R.
    df = pd.Dataframe() .... Datenframe mit den Beobachtungen
    csvfiles_sorted = list() ... Gespeicherte CSV Files mit den Interpolierten Stationswerten.
    name_parm = str()
    station_parm = str()
    '''
    df_grib = None
    for file in csvfiles_sorted:
        df_grib_new = pd.read_csv(file, sep=';', quoting=csv.QUOTE_NONNUMERIC)
        if df_grib is None:
            df_grib = df_grib_new
        else:
            df_grib = df_grib.append(df_grib_new)

    try:
        obstime_grib_no_tz = df_grib['validDate'].apply(
            lambda x: dateutil.parser.parse(x))  # obstimeformat is str('%Y-%m-%d %H:%M') no timezoneinfo
    except TypeError:
        print("df_grib: {} | name_parm: {} | Datum: {}".format(df_grib, name_parm, df['datum']))

    # Typenumwanldung für GAMLSS
    df_grib['utctimestamp'] = obstime_grib_no_tz.dt.tz_localize('UTC', ambiguous='NaT')
    df_grib.insert(0, 'datum', df_grib['utctimestamp'].dt.strftime("%Y-%m-%d"))
    df_grib.insert(1, 'yday', df_grib['utctimestamp'].dt.dayofyear)
    df_grib.insert(2, 'hour', df_grib['utctimestamp'].dt.hour)
    df_grib.insert(3, 'minute', df_grib['utctimestamp'].dt.minute)
    df_grib.insert(4, 'dayminute', df_grib['utctimestamp'].dt.hour * 60 + df_grib['utctimestamp'].dt.minute)

    # Umwandlung in log(spread) wichtig, damit nur postive Werte simuliert werden
    log_spread_col = [log_spread(s) for s in df_grib['spread']]
    df_grib.insert(15, 'log_spread', log_spread_col)

    # TODO Typenumwandlung unnötig machen :)
    df['alt'] = df['alt'].astype(int)
    df_grib['alt'] = df_grib['alt'].astype(int)

    # Merge Dataframe von Messungen und Gribfiles
    df = pd.merge(df, df_grib, on=['datum', 'yday', 'minute', 'dayminute', 'hour', 'alt', 'lon', 'lat', 'station'])
    df[['datum', 'analDate', 'validDate', 'station']] = df[['datum', 'analDate', 'validDate', 'station']].astype(
        str)  # .astype('|S')
    df[['alt', 'step', 'yday', 'hour', 'minute', 'dayminute']] = df[
        ['alt', 'step', 'yday', 'hour', 'minute', 'dayminute']].astype(int)
    df[['lon', 'lat', station_parm, 'mean', 'log_spread']] = df[
        ['lon', 'lat', station_parm, 'mean', 'log_spread']].astype(float)

    # Save Format für R für alle Parameter
    stepstr = df['step'][0]
    df = df[['yday', 'kfold', 'dayminute', 'alt', 'lon', 'lat', station_parm, 'mean', 'log_spread']]
    df.columns = ['yday', 'kfold', 'dayminute', 'alt', 'lon', 'lat', 'obs', 'mean', 'log_spread']
    df.to_csv('./data/GAM/{}/klima_nwp/{}_{:03d}.csv'.format(name_parm, name_parm, stepstr), sep=';', index=False,
              quoting=csv.QUOTE_NONNUMERIC)
    print("Thread mit Step {:03d} fertiggestellt".format(stepstr))
    return (df)


# Main
# Parser Input Argumente
if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-p', '--parm',
                      action="store", dest="name_parm",
                      help="tmp_2m | apcp_sfc | rh_2m | wind_10m", default="")
    options, args = parser.parse_args()
    name_parm = options.name_parm

    if name_parm in ['tmp_2m', 'rh_2m', 'apcp_sfc', 'wind_10m']:
        # Interpolierte Gribfiles im CSV Format
        path_csvfiles = str('./data/grib/gfs_interpolated_grib_files/{}/'.format(name_parm))
        # Zuweisung von name_parm (verwendung in Gribfiles) und station_parm (verwendung an den Messstationen)
        if name_parm == 'tmp_2m':
            station_parm = 't'
        elif name_parm == 'rh_2m':
            station_parm = 'rf'
        elif name_parm == 'apcp_sfc':
            station_parm = 'regen'
        elif name_parm == 'wind_10m':
            station_parm = 'wg'

        # Erstellung Ordner für Klimatologien
        if not os.path.exists("./data/GAM"):
            os.mkdir("./data/GAM")
        if not os.path.exists("./data/GAM/{}".format(name_parm)):
            os.mkdir("./data/GAM/{}".format(name_parm))
        if not os.path.exists("./data/GAM/{}/klima_nwp".format(name_parm)):
            os.mkdir("./data/GAM/{}/klima_nwp".format(name_parm))

        # Interpolierte Gribfiles einlesen und vorbereitung für Multithreading
        csvfiles = scandir(path_csvfiles, name_parm)

        # Alle verfügbaren Steps von den Interpoliereten Grib Files
        step_ending = [s[-7:] for s in csvfiles]
        step_ending = list(dict.fromkeys(step_ending))

        csvfiles_sorted = []
        for files in step_ending:
            csvfiles_step = [s for s in csvfiles if files in s]
            csvfiles_sorted.append(csvfiles_step)

        # Einlesen der Datei aus dem Programm data_table | Die Datei beinhaltet alle Stationswerte von allen Parametern
        try:
            df_h5 = pd.read_hdf('./data/klima/alle_stationswerte_zlib.h5', 'table')
        except Exception as e:
            print('Die Datei alle_stationswerte.h5 wurde noch nicht erstellt. | data_table.py wurde noch nicht ausgeführt? | Error: {}'.format(e))
            sys.exit()

        # Building von Obsdataframe
        df = df_h5[['datum', 'yday', 'hour', 'minute', 'dayminute', 'alt', 'lon', 'lat', 'station', station_parm]]
        df = df[df['minute'] == 0]
        df = df.dropna(axis=0).reset_index(drop=True)

        # Building up the Crossvalidation
        datum_series = df_h5['datum'].drop_duplicates(keep='first')
        datum_series = datum_series.to_list()
        kfold_dictonary = kfold(datum_series, k=10)
        kfold_entry = [int(kfold_dictonary[r]) for r in df['datum']]
        df.insert(1, 'kfold', kfold_entry)

        # Multithreading
        for i in np.arange(0, len(csvfiles_sorted), 1, int):
            thread = threading.Thread(target=combine_df_csvfiles,
                                      args=(df, csvfiles_sorted[i], name_parm, station_parm))
            thread.start()

        # Save Format für R für alle Parameter
        df_save = df[['yday', 'kfold', 'dayminute', 'alt', 'lon', 'lat', station_parm]]
        df_save.columns = ['yday', 'kfold', 'dayminute', 'alt', 'lon', 'lat', 'obs']
        df_save.to_csv('./data/GAM/{}/{}_alle_stationswerte.csv'.format(name_parm, name_parm), sep=';', index=False,
                       quoting=csv.QUOTE_NONNUMERIC)
    else:
        print("Der eingegebene Parameter ist falsch. | --help für mehr Infos")
        sys.exit(1)