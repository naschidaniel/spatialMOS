#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Help functions to create the spatialMOS plots,.'''

import logging
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import datetime as dt
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

# Functions
def plot_forecast(filename, parameter, xx, yy, plotparameter, gribfiles_data, gadm36_shape_file, what):
    '''A function to create the GEFS and spatialMOS forecast plots.'''
    step = gribfiles_data['step']

    if parameter not in ['tmp_2m', 'rh_2m']:
        raise RuntimeError(f'The parameter \'{parameter}\' is not supported')

    if what not in ['spatialmos_spread', 'spatialmos_mean', 'nwp_mean', 'nwp_spread']:
        raise RuntimeError(f'The parameter \'{parameter}\' is not supported', )

    fig_dpi = 72
    fig = plt.figure(figsize=(1600/fig_dpi, 1600/fig_dpi), dpi=fig_dpi)
    ax = plt.axes(projection=ccrs.PlateCarree(
        globe=ccrs.Globe(datum='WGS84', ellipse='WGS84')))

    if parameter == 'tmp_2m' and what == 'spatialmos_mean':
        im = plt.pcolormesh(xx, yy, plotparameter, cmap='RdBu_r', vmin=-40,
                            vmax=40, shading='auto', transform=ccrs.PlateCarree())
        plot_title = '2m Temperatur MEAN [°C]'
    elif parameter == 'tmp_2m' and what == 'spatialmos_spread':
        im = plt.pcolormesh(xx, yy, plotparameter, cmap='Reds', vmin=0,
                            vmax=5, shading='auto', transform=ccrs.PlateCarree())
        plot_title = '2m Temperatur SPREAD [°C]'
    elif parameter == 'tmp_2m' and what == 'nwp_mean':
        im = plt.pcolormesh(xx, yy, plotparameter, cmap='RdBu_r', vmin=-40,
                            vmax=40, shading='auto', transform=ccrs.PlateCarree())
        plot_title = '2m Temperatur GEFS MEAN [°C]'
    elif parameter == 'tmp_2m' and what == 'nwp_spread':
        im = plt.pcolormesh(xx, yy, plotparameter, cmap='Reds', vmin=0,
                            vmax=5, shading='auto', transform=ccrs.PlateCarree())
        plot_title = '2m Temperatur GEFS SPREAD [°C]'
    elif parameter == 'rh_2m' and what == 'spatialmos_mean':
        im = plt.pcolormesh(xx, yy, plotparameter, cmap='YlGn', vmin=0,
                            vmax=100, shading='auto', transform=ccrs.PlateCarree())
        plot_title = '2m relative Feuchte MEAN [%]'
    elif parameter == 'rh_2m' and what == 'spatialmos_spread':
        im = plt.pcolormesh(xx, yy, plotparameter, cmap='Reds', vmin=0,
                            vmax=15, shading='auto', transform=ccrs.PlateCarree())
        plot_title = '2m relative Feuchte SPREAD [%]'
    elif parameter == 'rh_2m' and what == 'nwp_mean':
        im = plt.pcolormesh(xx, yy, plotparameter, cmap='YlGn', vmin=0,
                            vmax=100, shading='auto', transform=ccrs.PlateCarree())
        plot_title = '2m relative Feuchte GEFS MEAN [%]'
    elif parameter == 'rh_2m' and what == 'nwp_spread':
        im = plt.pcolormesh(xx, yy, plotparameter, cmap='Reds', vmin=0,
                            vmax=15, shading='auto', transform=ccrs.PlateCarree())
        plot_title = '2m relative Feuchte  GEFS SPREAD [%]'

    plt.title(plot_title, loc='center', fontsize=20)
    anal_date_title = dt.datetime.strptime(
        gribfiles_data['anal_date'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H')
    valid_date_title = dt.datetime.strptime(
        gribfiles_data['valid_date'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H')
    plt.title(
        f'Gültig für {valid_date_title} UTC | Step +{step}', loc='left', fontsize=15)
    plt.title(f'GEFS Lauf {anal_date_title} UTC', loc='right', fontsize=15)

    # Set Colorbar and Extend
    if what in ['nwp_mean', 'nwp_spread']:
        ax.set_extent([9.5, 17.5, 46, 49.5], ccrs.PlateCarree())
        fig.colorbar(im, ax=ax, shrink=0.32)
        cities_offset = 0.05
    else:
        ax.set_extent([10, 13, 46.2, 47.9], ccrs.PlateCarree())
        fig.colorbar(im, ax=ax, shrink=0.45)
        cities_offset = 0.02

    # Add Austrian Borders
    gadm36_shape = list(shpreader.Reader(str(gadm36_shape_file)).geometries())
    ax.add_geometries(gadm36_shape, ccrs.PlateCarree(),
                      edgecolor='black', facecolor='None', alpha=0.5)

    # District capital cities
    cities = {
        'Innsbruck': {
            'pos': [47.26266, 11.39454],
            'label': 'IBK',
            'size': 7,
        },
        'Kufstein': {
            'pos': [47.58333, 12.16667],
            'label': 'KU',
            'size': 5,
        },
        'Kitzbuehel': {
            'pos': [47.44637, 12.39215],
            'label': 'KB',
            'size': 5,
        },
        'Lienz': {
            'pos': [46.8289, 12.76903],
            'label': 'LZ',
            'size': 5,
        },
        'Schwaz': {
            'pos': [47.35169, 11.71014],
            'label': 'SZ',
            'size': 5,
        },
        'Reutte': {
            'pos': [47.48333, 10.71667],
            'label': 'RE',
            'size': 5,
        },
        'Landeck': {
            'pos': [47.13988, 10.56593],
            'label': 'LA',
            'size': 5,
        },
        'Imst': {
            'pos': [47.24504, 10.73974],
            'label': 'IM',
            'size': 5,
        },
        'Bozen': {
            'pos': [46.498295, 11.354758],
            'label': 'BOZ',
            'size': 7,
        },
        'Schlanders': {
            'pos': [46.627678, 10.773689],
            'label': 'SCHL',
            'size': 5,
        },
        'Meran': {
            'pos': [46.668930, 11.163990],
            'label': 'MER',
            'size': 5,
        },
        'Sterzing': {
            'pos': [46.892673, 11.433619],
            'label': 'STE',
            'size': 5,
        },
        'Brixen': {
            'pos': [46.715858, 11.657200],
            'label': 'BX',
            'size': 5,
        },
        'Bruneck': {
            'pos': [46.796574, 11.938042],
            'label': 'BRE',
            'size': 5,
        },
    }
    for c in cities.keys():
        ax.plot(cities[c]['pos'][1], cities[c]['pos'][0],  markersize=cities[c]
                ['size'], marker='o', color='gray', transform=ccrs.PlateCarree())
        ax.text(cities[c]['pos'][1] + cities_offset, cities[c]['pos'][0] + cities_offset,
                cities[c]['label'], horizontalalignment='left', transform=ccrs.PlateCarree())

    # Add Grid
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                      linewidth=1, color='gray', alpha=0.4, linestyle='-')
    gl.top_labels = False
    gl.right_labels = False
    gl.xlocator = mticker.FixedLocator(gribfiles_data['longitude'])
    gl.ylocator = mticker.FixedLocator(gribfiles_data['latitude'])
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER

    fig.savefig(filename, bbox_inches='tight', pil_kwargs={
                'quality': 95, 'optimize': True, 'progressive': True})
    plt.close(fig=None)
    logging.info('The prediction plot \'%s\' was created.', filename)


def reshapearea(series, array):
    '''A function to adjust the shape of a Pandas Series to a numpy array.'''
    data = series.values
    reshapedarea = data.reshape(array.shape)
    reshapedarea = reshapedarea[::-1]
    return reshapedarea
