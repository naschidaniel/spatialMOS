#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from typing import List, Union

def nwp_gribfiles_avalibel_steps(parameter, date, available_steps):
    """Eine Funktion zum durchsuchen der zur Verfügung stehenden NWP forecasts
    """
    import os
    path_nwp_forecasts = f"./data/get_available_data/gefs_forecast/{parameter}/{date}0000/"
    
    def mainfunktion(path_nwp_forecasts, avg_spr):
        nwp_gribfiles_available_steps: List[Union[bytes, str]] = []
        for dirpath, subdirs, files in os.walk(path_nwp_forecasts):
            for file in files:
                for step in available_steps:
                    searchstring = None
                    if avg_spr == "mean":
                        searchstring = "_avg_f{:03d}".format(step)
                    elif avg_spr == "spread":
                        searchstring = "_spr_f{:03d}".format(step)

                    if searchstring in file:
                        nwp_gribfiles_available_steps.append(os.path.join(dirpath, file))
                    else:
                        continue

        if nwp_gribfiles_available_steps == []:
            logging.error("parameter: {:8} | available Files: {} | {} | {}".format(parameter, len(nwp_gribfiles_available_steps), avg_spr, path_nwp_forecasts))
        else:
            logging.info("parameter: {:8} | available Files: {} | {} | {}".format(parameter, len(nwp_gribfiles_available_steps), avg_spr, path_nwp_forecasts))

        return (sorted(nwp_gribfiles_available_steps))
    return mainfunktion(path_nwp_forecasts, "mean"), mainfunktion(path_nwp_forecasts, "spread")


def open_gribfile(file):
    import pygrib
    file = pygrib.open(file)
    file = file.select()[0]
    analDate = file.analDate.strftime("%Y-%m-%d %H:%M")
    validDate = file.validDate.strftime("%Y-%m-%d %H:%M")

    return file, analDate, validDate


def plot_forecast(name_parameter, m, xx, yy, plotparameter, analDate, validDate, grb_analDate, step, what):
    """Plotfunktion für forecast Grafiken
        m = Object vom type BASEMAP
        xx, yy = BASEMAP.meshgrid
        plotparameter = numpy.ndarray
        analDate, validDate, analDate_save_format, = string
        step = integer
        what, parameter = string
    """
    import io
    import os
    import matplotlib.pyplot as plt
    import numpy as np
    import requests

    fig = plt.figure(figsize=(15, 15), dpi=96)

    if name_parameter == "tmp_2m" and what == "samos_mean":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="RdBu_r")
        plt.title("2m Temperatur SAMOS MEAN [°C]", loc="center")
        plt.clim(-40, 40)
    elif name_parameter == "tmp_2m" and what == "samos_spread":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Reds")
        plt.title("2m Temperatur SAMOS SPREAD [°C]", loc="center")
        plt.clim(0, 5)
    elif name_parameter == "tmp_2m" and what == "nwp_mean":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="RdBu_r")
        plt.title("2m Temperatur GFS MEAN [°C]", loc="center")
        plt.clim(-40, 40)
    elif name_parameter == "tmp_2m" and what == "nwp_spread":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Reds")
        plt.title("2m Temperatur GFS SPREAD [°C]", loc="center")
        plt.clim(0, 5)
    elif name_parameter == "rh_2m" and what == "samos_mean":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="YlGn")
        plt.title("2m Relative Luftfeuchte SAMOS MEAN [%]", loc="center")
        plt.clim(0, 100)
    elif name_parameter == "rh_2m" and what == "samos_spread":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Reds")
        plt.title("2m Relative Luftfeuchte SAMOS SPREAD [%]", loc="center")
        plt.clim(0, 5)
    elif name_parameter == "rh_2m" and what == "nwp_mean":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="YlGn")
        plt.title("2m Relative Luftfeuchte GFS MEAN [%]", loc="center")
        plt.clim(0, 100)
    elif name_parameter == "rh_2m" and what == "nwp_spread":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Reds")
        plt.title("2m Relative Luftfeuchte GFS SPREAD [%]", loc="center")
        plt.clim(0, 5)
    elif name_parameter == "wind_10m" and what == "samos_mean":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Purples")
        plt.title("10m Windgeschwindigkeit SAMOS MEAN [km/h]", loc="center")
        plt.clim(0, 10)
    elif name_parameter == "wind_10m" and what == "samos_spread":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Reds")
        plt.title("10m Windgeschwindigkeit SAMOS SPREAD [km/h]", loc="center")
        plt.clim(0, 10)
    elif name_parameter == "wind_10m" and what == "nwp_mean":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Purples")
        plt.title("10m Windgeschwindigkeit GFS MEAN [km/h]", loc="center")
        plt.clim(0, 10)
    elif name_parameter == "wind_10m" and what == "nwp_spread":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Reds")
        plt.title("10m Windgeschwindigkeit GFS SPREAD [km/h]", loc="center")
        plt.clim(0, 10)


    plt.title("Gültig für {} | Step +{}".format(validDate, step), loc="left")
    plt.title("GFS Lauf {}".format(analDate), loc="right")
    m.colorbar(location="right")
    
    gadm36_AUT_shp = "./data/get_available_data/gadm/gadm36_AUT_shp"
    if not os.path.exists(gadm36_AUT_shp):
        req_shapefile = requests.get("https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_AUT_shp.zip", stream=True)
        if req_shapefile.status_code == 200:
            with open("./data/get_available_data/gadm/gadm36_AUT_shp.zip", mode="wb") as f:
                for chunk in req_shapefile.iter_content(chunk_size=128):
                    f.write(chunk)

    m.readshapefile("./data/get_available_data/gadm/gadm36_AUT_shp/gadm36_AUT_0", "aut")

    parallels = np.arange(44.5, 52.5, 1.)
    m.drawparallels(parallels, labels=[False, False, False, False], fontsize=8, color="lightgrey")
    meridians = np.arange(8.5, 19.5, 1.)
    m.drawmeridians(meridians, labels=[False, False, False, False], fontsize=8, color="lightgrey")

    parallels = np.arange(45., 53., 1.)
    m.drawparallels(parallels, labels=[True, False, False, False], fontsize=8, linewidth=0.0)
    meridians = np.arange(8., 20., 1.)
    m.drawmeridians(meridians, labels=[False, False, False, True], fontsize=8, linewidth=0.0)

    filepath = "./spool/{}/{}/".format(name_parameter, what)
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    figname = "{}_step_{:03d}.png".format(grb_analDate.strftime("%Y%m%d%H%M"), step)
    file = os.path.join(filepath, figname)
    fig.savefig(file, bbox_inches="tight")
    plt.close(fig=None)
    return figname


def reshapearea(column, alt):
    """Eine Funktion zum reshapen von Pandas Dataframe Clumns
    column = pd.Dataframe.Column
    alt = np.ndarray"""
    data = column.values
    reshapedarea = data.reshape(alt.shape)
    reshapedarea = reshapedarea[::-1]
    return reshapedarea


def avaliblelSteps(parameter, date, available_steps):
    import sys
    import os

    path_nwp_forecasts = f"./data/get_available_data/gefs_forecast/{parameter}/{date}0000/"
    nwp_gribfiles_avalibel_mean_steps = nwp_gribfiles_avalibel_steps(path_nwp_forecasts, "mean", available_steps)
    nwp_gribfiles_avalibel_spread_steps = nwp_gribfiles_avalibel_steps(path_nwp_forecasts, "spread", available_steps)

    if nwp_gribfiles_avalibel_mean_steps is [] or nwp_gribfiles_avalibel_spread_steps is []:
        logging.error("There are no predictions in the folder %s for the entered date %s | {}", path_nwp_forecasts, date)

    return nwp_gribfiles_avalibel_mean_steps, nwp_gribfiles_avalibel_spread_steps