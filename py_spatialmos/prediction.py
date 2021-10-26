#!/usr/bin/python
# -*- coding: utf-8 -*-
'''A script for generating surface forecasts based on GEFS predictions and GAMLSS climatologies.'''

import os
import json
import csv
import logging
import datetime as dt
from pathlib import Path
import numpy as np
import pandas as pd
import pytz
from scipy.interpolate import griddata
from .spatial_util import spatial_plots


# Functions
def write_spatialmos_run_file(data_path_media, spatialmos_run_status, parameter):
    '''A function to create an Info File'''
    filename_spatialmos_run = os.path.join(data_path_media, f'spatialmosrun_{parameter}.json')
    with open(filename_spatialmos_run, mode='w', encoding='utf-8') as f:
        json.dump(spatialmos_run_status, f)
    logging.info('The Info File \'%s\' for the spatialMOS run was written.', filename_spatialmos_run)


def run_spatial_predictions(parser_dict):
    '''A run_spatial_predictions runs the main function'''
    steps = [f'{s:03d}' for s in range(6, 192+1, 6)]
    data_path = Path(f"./data/get_available_data/gefs_avgspr_forecast_p05/{parser_dict['parameter']}/{parser_dict['date']}0000/")
    json_files = [f for step in steps for f in sorted(data_path.glob(f'*{step}.json'))]
    data_path_media = Path(f"./data/media/{parser_dict['parameter']}/")

    alt_file = Path('./data/get_available_data/gadm/spatial_alt_area.csv')
    alt_area_file = Path('./data/get_available_data/gadm/spatial_alt_area.json')

    gadm36_shape_file = Path('./data/get_available_data/gadm/gadm36_AUT_shp/gadm36_AUT_0.shp')

    spatial_alt_area_file = Path('./data/get_available_data/gadm/spatial_alt_area_df.csv')
    spatialmos_run_status = []
    for json_file in json_files:
        with open(json_file, mode='r', encoding='utf-8') as f:
            gribfiles_data = json.load(f)

        # Check if climatologies files are available
        climate_spatialmos_file = Path(f"./data/spatialmos_climatology/gam/{parser_dict['parameter']}/climate_spatialmos/yday_{gribfiles_data['yday']:03d}_dayminute_{gribfiles_data['dayminute']}.csv")
        climate_spatialmos_nwp_file = Path(f"./data/spatialmos_climatology/gam/{parser_dict['parameter']}/climate_spatialmos_nwp/yday_{gribfiles_data['yday']:03d}_dayminute_{gribfiles_data['dayminute']}_step_{gribfiles_data['step']:03d}.csv")
        spatialmos_coef_file = Path(f"./data/spatialmos_climatology/gam/{parser_dict['parameter']}/spatialmos_coef/spatialmos_coef_{parser_dict['parameter']}_{gribfiles_data['step']:03d}.csv")

        if not os.path.exists(climate_spatialmos_file) or not os.path.exists(climate_spatialmos_nwp_file) or not os.path.exists(spatialmos_coef_file):
            logging.warning("For the parameter '%s', step '%03d' and yday '%03d' the required climatologies or coefficients are missing.", parser_dict['parameter'], gribfiles_data['step'], gribfiles_data['yday'])

            # Write info file to spool directory
            if not os.path.exists(climate_spatialmos_file):
                logging.error('File %s is missing', climate_spatialmos_file)
            if not os.path.exists(climate_spatialmos_nwp_file):
                logging.error('File %s is missing',
                              climate_spatialmos_nwp_file)
            if not os.path.exists(spatialmos_coef_file):
                logging.error('File %s is missing', spatialmos_coef_file)

            spatialmos_run_status.append({'status': 'failed', 'step': f"{gribfiles_data['step']:03d}"})
            continue

        # Check if spatialmos coefficients are available
        spatialmos_run_status = spatial_prediction(alt_file, alt_area_file, climate_spatialmos_file, climate_spatialmos_nwp_file,
                                                   data_path_media, gribfiles_data, spatial_alt_area_file, spatialmos_coef_file, spatialmos_run_status, parser_dict, gadm36_shape_file)
        write_spatialmos_run_file(data_path_media, spatialmos_run_status, parser_dict['parameter'])


def spatial_prediction(alt_file, alt_area_file, climate_spatialmos_file, climate_spatialmos_nwp_file, data_path_spool, gribfiles_data, spatial_alt_area_file, spatialmos_coef_file, spatialmos_run_status, parser_dict, gadm36_shape_file):
    '''spatial_prediction creates the plot and predictions for North and South Tyrol'''

    alt = pd.read_csv(alt_file, header=None)
    with open(alt_file, newline='', mode='r', encoding='utf-8') as f:
        alt_new = list(csv.reader(f, delimiter=','))

    with open(alt_area_file, mode='r', encoding='utf-8') as f:
        alt_area = json.load(f)

    # Consider Timezone
    timezone = pytz.timezone('UTC')
    anal_date_aware = timezone.localize(dt.datetime.strptime(
        gribfiles_data['anal_date'], '%Y-%m-%d %H:%M:%S'))
    valid_date_aware = timezone.localize(dt.datetime.strptime(
        gribfiles_data['valid_date'], '%Y-%m-%d %H:%M:%S'))

    # Create required grids for NWP
    latlon_correction = 0.25 / gribfiles_data['resolution']

    # Create meshgrid and add M + 1, N + 1
    # https://matplotlib.org/3.3.0/gallery/images_contours_and_fields/pcolormesh_grids.html
    # shading='auto'
    gribfiles_data['longitude'].append(
        gribfiles_data['longitude'][-1] + gribfiles_data['resolution'])
    gribfiles_data['latitude'].append(
        gribfiles_data['latitude'][-1] + gribfiles_data['resolution'])
    lons = [x - latlon_correction for x in gribfiles_data['longitude']]
    lats = [x - latlon_correction for x in gribfiles_data['latitude']]
    xx_nwp, yy_nwp = np.meshgrid(lons, lats)

    # Create required meshgrid for spatialMOS
    lons_spatialmos = np.linspace(alt_area['min_lon'], alt_area['max_lon'], len(alt_new[0]))
    lats_spatialmos = np.linspace(alt_area['max_lat'], alt_area['min_lat'], len(alt_new))
    xx_spatialmos, yy_spatialmos = np.meshgrid(lons_spatialmos, lats_spatialmos)

    # Read in preprocessed NWP CSV file with the predictions
    nwp_df = pd.DataFrame(gribfiles_data['data'], columns=gribfiles_data['data_columns'], dtype=float)

    # Interpolation of NWP forecasts
    mean_interpolation = griddata(nwp_df[['longitude', 'latitude']], nwp_df['mean'], (xx_spatialmos, yy_spatialmos), method='linear')
    log_spread_interpolation = griddata(nwp_df[['longitude', 'latitude']], nwp_df['log_spread'], (xx_spatialmos, yy_spatialmos), method='linear')
    mean_interpolation_spatial_area = np.ma.masked_where(np.isnan(alt), mean_interpolation)
    log_spread_interpolation_spatial_area = np.ma.masked_where(np.isnan(alt), log_spread_interpolation)

    # Read in GAMLSS climatologies
    climate_spatialmos = pd.read_csv(climate_spatialmos_file, header=0, index_col=0)
    climate_spatialmos_nwp = pd.read_csv(climate_spatialmos_nwp_file, header=0, index_col=0)
    spatialmos_coef = pd.read_csv(spatialmos_coef_file, sep=';', quoting=csv.QUOTE_NONNUMERIC)

    # Set dytypes to float
    cols = climate_spatialmos.select_dtypes(exclude=['float']).columns
    climate_spatialmos[cols] = climate_spatialmos[cols].apply(pd.to_numeric, downcast='float', errors='coerce')

    cols_nwp = climate_spatialmos_nwp.select_dtypes(exclude=['float']).columns
    climate_spatialmos_nwp[cols_nwp] = climate_spatialmos_nwp[cols_nwp].apply(
        pd.to_numeric, downcast='float', errors='coerce')

    # Set index of climate dataframes to lat, lon
    climate_spatialmos = climate_spatialmos.set_index(['lat', 'lon'])
    climate_spatialmos_nwp = climate_spatialmos_nwp.set_index(['lat', 'lon'])

    spatial_alt_area = pd.read_csv(spatial_alt_area_file, header=0, index_col=0)
    cols_spatialmos = spatial_alt_area.select_dtypes(exclude=['float']).columns
    spatial_alt_area[cols_spatialmos] = spatial_alt_area[cols_spatialmos].apply(pd.to_numeric, downcast='float', errors='coerce')
    spatial_alt_area = spatial_alt_area.set_index(['lat', 'lon'])

    # Concate altitude and NWP und spatialMOS Dataframes to one big Dataframe
    spatialmos = pd.concat([spatial_alt_area, climate_spatialmos], axis=1, sort=True)
    spatialmos = pd.concat([spatialmos, climate_spatialmos_nwp], axis=1, sort=True)
    spatialmos = spatialmos.loc[:, ~spatialmos.columns.duplicated()]

    # Reshape dataframe
    climate_fit = spatial_plots.reshapearea(spatialmos['climate_fit'], alt)
    climate_sd = spatial_plots.reshapearea(spatialmos['climate_sd'], alt)
    mean_fit = spatial_plots.reshapearea(spatialmos['mean_fit'], alt)
    mean_sd = spatial_plots.reshapearea(spatialmos['mean_sd'], alt)
    log_spread_fit = spatial_plots.reshapearea(spatialmos['log_spread_fit'], alt)
    log_spread_sd = spatial_plots.reshapearea(spatialmos['log_spread_sd'], alt)

    # Generate anomalies
    nwp_anom = (mean_interpolation_spatial_area.data - mean_fit) / mean_sd
    log_spread_nwp_anom = (log_spread_interpolation_spatial_area.data - log_spread_fit) / log_spread_sd

    # Generate spatialmos spatial predictions
    spatialmos_coef = spatialmos_coef.apply(pd.to_numeric)
    spatialmos_anom = spatialmos_coef['intercept'][0] + spatialmos_coef['mean_anom'][0] * nwp_anom
    spatialmos_mean = spatialmos_anom * climate_sd + climate_fit
    spatialmos_log_anom_spread = spatialmos_coef['intercept_log_spread'][0] + spatialmos_coef['log_spread_anom'][0] * log_spread_nwp_anom
    spatialmos_spread = np.exp(spatialmos_log_anom_spread) * climate_sd

    # Round predicted values
    spatialmos_mean = np.round(spatialmos_mean, decimals=2)
    spatialmos_spread = np.round(spatialmos_spread, decimals=5)

    # Create filename for the plots for NWP and spatialMOS forecast maps
    data_path_spool_images = data_path_spool.joinpath('images')
    os.makedirs(data_path_spool_images, exist_ok=True)

    plot_filenames = []
    for what in ['nwp_mean', 'nwp_spread', 'spatialmos_mean', 'spatialmos_spread']:
        if what in ['nwp_mean', 'nwp_spread']:
            xx = xx_nwp
            yy = yy_nwp
        else:
            xx = xx_spatialmos
            yy = yy_spatialmos

        plotparameter = {
            'nwp_mean': gribfiles_data['values_avg'],
            'nwp_spread': gribfiles_data['values_spr'],
            'spatialmos_mean': spatialmos_mean,
            'spatialmos_spread': spatialmos_spread
        }
        plot_filename = data_path_spool_images.joinpath(f"{what}_{anal_date_aware.strftime('%Y%m%d')}_step_{gribfiles_data['step']:03d}.jpg")
        spatial_plots.plot_forecast(plot_filename, parser_dict['parameter'], xx, yy, plotparameter.get(what), gribfiles_data, gadm36_shape_file, what)
        plot_filenames.append(plot_filename)

    # Point Forecasts for North and South Tyrol without consideration of values outside the borders
    spatialmos_point = pd.DataFrame({'lat': yy_spatialmos.flatten().tolist(), 'lon': xx_spatialmos.flatten().tolist(), 'spatialmos_mean': spatialmos_mean.flatten().tolist(), 'spatialmos_spread': spatialmos_spread.flatten().tolist()})
    spatialmos_point = spatialmos_point.dropna()
    spatialmos_point_dict = spatialmos_point.to_dict('records')

    # Declare Unit
    if parser_dict['parameter'] == 'tmp_2m':
        unit = '° C'
    else:
        unit = '%'

    # Exchange file for spatialMOS Run in JSON format. This file is imported into the database.
    filename_spatialmos_step = f"{anal_date_aware.strftime('%Y%m%d')}_step_{gribfiles_data['step']:03d}.json"
    prediction_json_file = {'SpatialMosRun':
                            {
                                'anal_date': anal_date_aware.strftime('%Y-%m-%d %H:%M:%S'),
                                'parameter': parser_dict['parameter'],
                                'unit': unit,
                            },
                            'SpatialMosStep':
                                {'filename_SpatialMosStep': filename_spatialmos_step,
                                 'valid_date': valid_date_aware.strftime('%Y-%m-%d %H:%M:%S'),
                                 'step': gribfiles_data['step'],
                                 'filename_nwp_mean': f"/media/{parser_dict['parameter']}/images/{plot_filenames[0].name}",
                                 'filename_nwp_spread': f"/media/{parser_dict['parameter']}/images/{plot_filenames[1].name}",
                                 'filename_spatialmos_mean': f"/media/{parser_dict['parameter']}/images/{plot_filenames[2].name}",
                                 'filename_spatialmos_spread': f"/media/{parser_dict['parameter']}/images/{plot_filenames[3].name}",
                                 },
                            'SpatialMosPoint': spatialmos_point_dict
                            }

    with open(data_path_spool.joinpath(filename_spatialmos_step), mode='w', encoding='utf-8') as f:
        json.dump(prediction_json_file, f)
        f.close()

    logging.info('parameter: %9s | anal_date: %s | valid_date: %s | step: %03d | %s',
                 prediction_json_file['SpatialMosRun']['parameter'], prediction_json_file['SpatialMosRun']['anal_date'],
                 prediction_json_file['SpatialMosStep']['valid_date'], prediction_json_file['SpatialMosStep']['step'], filename_spatialmos_step)

    spatialmos_run_status.append({'status': 'ok',
                                  'step': str(gribfiles_data['step']),
                                  'anal_date': anal_date_aware.strftime('%Y-%m-%d %H:%M:%S'),
                                  'valid_date': valid_date_aware.strftime('%Y-%m-%d %H:%M:%S'),
                                  'parameter': parser_dict['parameter'],
                                  'unit': unit,
                                  'prediction_json_file': filename_spatialmos_step,
                                  'filename_nwp_mean': f"/media/{parser_dict['parameter']}/images/{plot_filenames[0].name}",
                                  'filename_nwp_spread': f"/media/{parser_dict['parameter']}/images/{plot_filenames[1].name}",
                                  'filename_spatialmos_mean': f"/media/{parser_dict['parameter']}/images/{plot_filenames[2].name}",
                                  'filename_spatialmos_spread': f"/media/{parser_dict['parameter']}/images/{plot_filenames[3].name}",
                                  })
    return spatialmos_run_status
