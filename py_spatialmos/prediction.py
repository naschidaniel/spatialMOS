#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Ein Script zum erstellen von spatialMOS Forcasts auf Basis von GFSE-Forcasts
Erstellt am: 15.03.2019
Autor: Daniel Naschberger
"""

########### MAIN #################
# Forcast Grib Files
import os
import json
import sys
import csv
import pytz
from datetime import datetime
import numpy as np
import numpy.ma as ma
import pandas as pd
from scipy.interpolate import griddata
from mpl_toolkits.basemap import Basemap
from osgeo import gdal


# Lokale Files
from py_middleware import logger_module
from py_middleware import spatial_parser
from py_middleware import spatial_parser

import PyspatialMOS.datamanipulation.modelklimatologies as modelklimatologies
import PyspatialMOS.prediction.predictionfunktionen as pf

os.environ['PROJ_LIB'] = '/usr/share/proj/'

if __name__ == "__main__":
    #Logger
    logger, startTime = spatialLogging.setupLogging('log', 'prediction__point_prediction.log', append=True)

    #Parser
    parserDict = spatialParser.parser(logger, name_parm=['tmp_2m', 'rh_2m', 'wind_10m'], datum=True, parm=True)
    modellauf = None
    filepath = "./data/DGM/SPATIAL_ALT_area.grd"
    # TODO einheitlihe avalible_steps in RspatialMOS und PyspatialMOS
    avalible_steps = np.arange(6, 193, 6, int)

    # Ofnen des spatialen Env
    raster = gdal.Open(filepath)
    alt = raster.ReadAsArray()
    gt = raster.GetGeoTransform()
    width = raster.RasterXSize
    height = raster.RasterYSize
    gt = raster.GetGeoTransform()
    minx = gt[0]
    miny = gt[3] + width * gt[4] + height * gt[5]
    maxx = gt[0] + width * gt[1] + height * gt[2]
    maxy = gt[3]
    x_center = (minx + maxx) / 2
    y_center = (miny + maxy) / 2

    # Basemaps für NWP (Grob aufgelöst) und SAMOS (Fein aufgelöst)
    m_nwp = Basemap(llcrnrlon=9, urcrnrlon=18, llcrnrlat=46, urcrnrlat=50, resolution='c', ellps='WGS84')
    m_samos = Basemap(llcrnrlon=10, urcrnrlon=13, llcrnrlat=miny, urcrnrlat=48, ellps='WGS84', lat_0=y_center, lon_0=x_center)

    # Datein für U und V
    if parserDict['parm'] in ['wind_10m']:
        nwp_gribfiles_avalibel_u_mean_steps, nwp_gribfiles_avalibel_u_spread_steps = pf.nwp_gribfiles_avalibel_steps(logger, 'ugrd_10m', parserDict['datum'], avalible_steps)
        nwp_gribfiles_avalibel_v_mean_steps, nwp_gribfiles_avalibel_v_spread_steps = pf.nwp_gribfiles_avalibel_steps(logger, 'vgrd_10m', parserDict['datum'], avalible_steps)

        nwpFiles = zip(nwp_gribfiles_avalibel_u_mean_steps, nwp_gribfiles_avalibel_u_spread_steps, nwp_gribfiles_avalibel_v_mean_steps, nwp_gribfiles_avalibel_v_spread_steps)
        for u_mean_file, u_spread_file, v_mean_file, v_spread_file in nwpFiles:
            u_mean, analDate_u_mean, validDate_u_mean = pf.pygribOpen(u_mean_file)
            u_spread, analDate_u_spread, validDate_u_spread = pf.pygribOpen(u_spread_file)
            v_mean, analDate_v_mean, validDate_v_mean = pf.pygribOpen(v_mean_file)
            v_spread, analDate_v_spread, validDate_v_spread = pf.pygribOpen(v_spread_file)

            wind_10m = u_mean
            wind_10m_spread = wind_10m

            wind_10m['values'] = np.sqrt(u_mean['values'] ** 2 + v_mean['values'] ** 2)
            wind_10m_spread['values'] = np.sqrt(u_spread['values'] ** 2 + v_spread['values'] ** 2)

            wind_mean_file = u_mean_file[u_mean_file.rfind('/')+1:]
            wind_spread_file = u_spread_file[u_spread_file.rfind('/')+1:]

            path_nwp_forcasts = './data/grib/gfs_forcast/{}/{}0000/'.format('wind_10m', parserDict['datum'])
            if not os.path.exists(path_nwp_forcasts):
                os.makedirs(path_nwp_forcasts)
            else:
                pass

            wind_10m_mean = wind_10m.tostring()
            wind_10m_spread = wind_10m_spread.tostring()

            file_mean = os.path.join(path_nwp_forcasts, wind_mean_file)
            file_spread = os.path.join(path_nwp_forcasts, wind_spread_file)

            grbout_mean = open(file_mean, 'wb')
            grbout_mean.write(wind_10m_mean)
            grbout_mean.close()

            grbout_spread = open(file_spread, 'wb')
            grbout_spread.write(wind_10m_spread)
            grbout_spread.close()
    else:
        pass

    # Dateneinleseroutine für die NWP Forcasts
    nwp_gribfiles_avalibel_mean_steps, nwp_gribfiles_avalibel_spread_steps = pf.nwp_gribfiles_avalibel_steps(logger, parserDict['parm'], parserDict['datum'] , avalible_steps)

    # MainLOOP
    for nwp_gribfiles_mean_step, nwp_gribfiles_spread_step in zip(nwp_gribfiles_avalibel_mean_steps, nwp_gribfiles_avalibel_spread_steps):
        # Öffen der Gribfiles und Basis Configuration
        grb_avg, analDate_avg, validDate_avg = pf.pygribOpen(nwp_gribfiles_mean_step)
        grb_spr, analDate_spr, validDate_spr = pf.pygribOpen(nwp_gribfiles_mean_step)

        yday = grb_avg.validDate.timetuple().tm_yday
        dayminute = grb_avg.validDate.timetuple().tm_hour * 60
        step = grb_avg.startStep

        # Meshgrid von SAMOS
        ##NWP
        lons = np.linspace(float(grb_avg['longitudeOfFirstGridPointInDegrees']),
                           float(grb_avg['longitudeOfLastGridPointInDegrees']), int(grb_avg['Ni']))
        lats = np.linspace(float(grb_avg['latitudeOfFirstGridPointInDegrees']),
                           float(grb_avg['latitudeOfLastGridPointInDegrees']), int(grb_avg['Nj']))
        xx_nwp, yy_nwp = m_nwp(*np.meshgrid(lons - 0.5, lats - 0.5))

        ##SAMOS
        lons_linespace = np.linspace(minx, maxx, alt.shape[1])
        lats_linespace = np.linspace(maxy, miny, alt.shape[0])

        xx_samos, yy_samos = m_samos(*np.meshgrid(lons_linespace, lats_linespace))

        #Korrturen am Mean Wert
        if parserDict['parm'] == 'tmp_2m':
            konstante = 273.15
        elif parserDict['parm'] == 'rh_2m':
            konstante = 0
        elif parserDict['parm'] == 'wind_10m':
            konstante = 0
        else:
            konstante = 0

        df = []
        for x in lons:
            for y in lats:
                mean = grb_avg.data(lat1=y, lon1=x)
                mean = round(mean[0][0][0] - konstante, 2)
                spread = grb_spr.data(lat1=y, lon1=x)
                log_spread = modelklimatologies.log_spread(spread[0][0][0]) ### von Kelvin in Celsius
                df.append([mean, log_spread, x, y])

        nwp_df = pd.DataFrame(df, columns=['mean', 'log_spread', 'lon', 'lat'])

        # NWP Interpolationen
        mean_interpolation = griddata(nwp_df[["lon", "lat"]], nwp_df["mean"], (xx_samos, yy_samos), method='linear')
        log_spread_interpolation = griddata(nwp_df[["lon", "lat"]], nwp_df["log_spread"], (xx_samos, yy_samos), method='linear')
        mean_interpolation_spatial_area = ma.masked_where(np.isnan(alt) == True, mean_interpolation)
        log_spread_interpolation_spatial_area = ma.masked_where(np.isnan(alt) == True, log_spread_interpolation)

        # Einlesen von Klimadaten und umwandlung in float Format; Setindex lat, lon für pd.concat
        klima_samos_file = './data/GAM/{}/klima_samos/yday_{:03d}_dayminute_{}.feather'.format(parserDict['parm'], yday, dayminute)
        try:
            klima_samos = pd.read_feather(klima_samos_file)
        except:
            logger.error('parm: {:9} | Step: {:03d} | NO klima_samos_file: {}'.format(parserDict['parm'], step, klima_samos_file))
            continue

        klima_samos_nwp_file = './data/GAM/{}/klima_samos_nwp/yday_{:03d}_dayminute_{}_step_{:03d}.feather'.format(parserDict['parm'], yday, dayminute, step)
        try:
            klima_samos_nwp = pd.read_feather(klima_samos_nwp_file)
        except:
            logger.error('parm: {:9} | Step: {:03d} | NO klima_samos_nwp_file: {}'.format(parserDict['parm'], step, klima_samos_nwp_file))
            continue

        cols = klima_samos.select_dtypes(exclude=['float']).columns
        klima_samos[cols] = klima_samos[cols].apply(pd.to_numeric, downcast='float', errors='coerce')
        klima_samos = klima_samos.set_index(['lat', 'lon'])

        cols_nwp = klima_samos_nwp.select_dtypes(exclude=['float']).columns
        klima_samos_nwp[cols_nwp] = klima_samos_nwp[cols_nwp].apply(pd.to_numeric, downcast='float', errors='coerce')
        klima_samos_nwp = klima_samos_nwp.set_index(['lat', 'lon'])

        SAMOS = pd.read_feather('./data/DGM/SPATIAL_ALT_area_df.feather')
        cols_samos = SAMOS.select_dtypes(exclude=['float']).columns
        SAMOS[cols_samos] = SAMOS[cols_samos].apply(pd.to_numeric, downcast='float', errors='coerce')
        SAMOS = SAMOS.set_index(['lat', 'lon'])
        ## PD.concat der Datensätze
        SAMOS = pd.concat([SAMOS, klima_samos], axis=1, sort=True)
        SAMOS = pd.concat([SAMOS, klima_samos_nwp], axis=1, sort=True)
        SAMOS = SAMOS.loc[:, ~SAMOS.columns.duplicated()]

        # SAMOS Predictions
        ##Anpassung des Shapes fürs SAMOS
        klima_fit = pf.reshapearea(SAMOS['klima_fit'], alt)
        klima_sd = pf.reshapearea(SAMOS['klima_sd'], alt)
        mean_fit = pf.reshapearea(SAMOS['mean_fit'], alt)
        mean_sd = pf.reshapearea(SAMOS['mean_sd'], alt)
        log_spread_fit = pf.reshapearea(SAMOS['log_spread_fit'], alt)
        log_spread_sd = pf.reshapearea(SAMOS['log_spread_sd'], alt)
        ## ANOMALIE
        nwp_anom = (mean_interpolation_spatial_area.data - mean_fit) / mean_sd
        log_spread_nwp_anom = (log_spread_interpolation_spatial_area.data - log_spread_fit) / log_spread_sd

        ##SAMOS Prediction
        SAMOS_coef_file = './data/GAM/{}/SAMOS_coef/SAMOS_coef_{}_{:03d}.csv'.format(parserDict['parm'], parserDict['parm'], step)
        try:
            SAMOS_coef = pd.read_csv(SAMOS_coef_file, sep=';', quoting=csv.QUOTE_NONNUMERIC)
        except:
            logger.error('parm: {:9} | Step: {:03d} | NO SAMOS_coef_file: {}'.format(parserDict['parm'], step, SAMOS_coef_file))
            continue

        SAMOS_coef = SAMOS_coef.apply(pd.to_numeric)
        samos_anom = SAMOS_coef['intercept'][0] + SAMOS_coef['mean_anom'][0] * nwp_anom
        samos_pred = samos_anom * klima_sd + klima_fit
        samos_log_anom_spread = SAMOS_coef['intercept_log_spread'][0] + SAMOS_coef['log_spread_anom'][0] * log_spread_nwp_anom
        samos_pred_spread = np.exp(samos_log_anom_spread) * klima_sd

        # Roundigs
        samos_pred = np.round(samos_pred, decimals=2)
        samos_pred_spread = np.round(samos_pred_spread, decimals=5)

        # Plot von den Vorhersagekarten
        ##NWP
        figname_nwp = pf.plot_forcast(parserDict['parm'], m_nwp, xx_nwp, yy_nwp, grb_avg.values - konstante, analDate_avg, validDate_avg, grb_avg.analDate, step, what='nwp_mean')
        figname_nwp_sd = pf.plot_forcast(parserDict['parm'], m_nwp, xx_nwp, yy_nwp, grb_spr.values, analDate_avg, validDate_avg, grb_avg.analDate, step, what='nwp_spread')

        figname_samos = pf.plot_forcast(parserDict['parm'], m_samos, xx_samos, yy_samos, samos_pred, analDate_avg, validDate_avg, grb_avg.analDate, step, what='samos_mean')
        figname_samos_sd = pf.plot_forcast(parserDict['parm'], m_samos, xx_samos, yy_samos, samos_pred_spread, analDate_avg, validDate_avg, grb_avg.analDate, step, what='samos_spread')

        timezone = pytz.timezone("UTC")
        analDate_aware = timezone.localize(grb_avg.analDate)
        validDate_aware = timezone.localize(grb_avg.validDate)

        jsonFile = {
                    "Modellauf": {"analDate": analDate_aware.strftime("%Y-%m-%d %H:%M"),
                                  "parm": parserDict['parm']},
                    "VorhersageStep": {"validDate": validDate_aware.strftime("%Y-%m-%d %H:%M"),
                                       "step": step,
                                       "fig_nwp": figname_nwp,
                                       "fig_nwp_sd": figname_nwp_sd,
                                       "fig_samos": figname_samos,
                                       "fig_samos_sd": figname_samos_sd
                                       },
                    "points": {'lat': yy_samos.flatten().tolist(),
                               'lon': xx_samos.flatten().tolist(),
                               'samos_mean': samos_pred.flatten().tolist(),
                               'samos_spread': samos_pred_spread.flatten().tolist()}
                    }

        filepath = './spool/{}/samos/'.format(parserDict['parm'])
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        filename = os.path.join(filepath, '{}_step_{:03d}.json'.format(analDate_aware.strftime("%Y%m%d%H%M"), step))
        with open(filename, 'w') as fp:
            json.dump(jsonFile, fp)
        logger.info('parm: {:9} | analDate: {} | validDate: {} | Step: {:03d} | {}'.format(jsonFile['Modellauf']['parm'], jsonFile['Modellauf']['analDate'], jsonFile['VorhersageStep']['validDate'], jsonFile['VorhersageStep']['step'], filename))

    spatialLogging.endLoggingMSG(logger, startTime)