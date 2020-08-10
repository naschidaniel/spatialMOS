#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Help functions to create the spatialMOS plots,."""

import os
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

# Functions
def plot_forecast(parameter, m, xx, yy, plotparameter, anal_date, valid_date, step, what):
    """A function to create the GEFS and spatialMOS forecast plots."""

    fig_dpi=96
    fig = plt.figure(figsize=(1200/fig_dpi, 1200/fig_dpi), dpi=fig_dpi)

    if parameter == "tmp_2m" and what == "samos_mean":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="RdBu_r")
        plot_title="2m Temperatur SAMOS MEAN [°C]"
        plt.clim(-40, 40)
    elif parameter == "tmp_2m" and what == "samos_spread":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Reds")
        plot_title="2m Temperatur SAMOS SPREAD [°C]"
        plt.clim(0, 5)
    elif parameter == "tmp_2m" and what == "nwp_mean":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="RdBu_r")
        plot_title="2m Temperatur GEFS MEAN [°C]"
        plt.clim(-40, 40)
    elif parameter == "tmp_2m" and what == "nwp_spread":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Reds")
        plot_title="2m Temperatur GEFS SPREAD [°C]"
        plt.clim(0, 5)
    elif parameter == "rh_2m" and what == "samos_mean":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="YlGn")
        plot_title="2m Relative Luftfeuchte SAMOS MEAN [%]"
        plt.clim(0, 100)
    elif parameter == "rh_2m" and what == "samos_spread":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Reds")
        plot_title="2m Relative Luftfeuchte SAMOS SPREAD [%]"
        plt.clim(0, 5)
    elif parameter == "rh_2m" and what == "nwp_mean":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="YlGn")
        plot_title="2m Relative Luftfeuchte GEFS MEAN [%]"
        plt.clim(0, 100)
    elif parameter == "rh_2m" and what == "nwp_spread":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Reds")
        plot_title="2m Relative Luftfeuchte GEFS SPREAD [%]"
        plt.clim(0, 5)
    elif parameter == "wind_10m" and what == "samos_mean":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Purples")
        plot_title="10m Windgeschwindigkeit SAMOS MEAN [km/h]"
        plt.clim(0, 10)
    elif parameter == "wind_10m" and what == "samos_spread":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Reds")
        plot_title="10m Windgeschwindigkeit SAMOS SPREAD [km/h]"
        plt.clim(0, 10)
    elif parameter == "wind_10m" and what == "nwp_mean":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Purples")
        plot_title="10m Windgeschwindigkeit GEFS MEAN [km/h]"
        plt.clim(0, 10)
    elif parameter == "wind_10m" and what == "nwp_spread":
        m.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, cmap="Reds")
        plot_title="10m Windgeschwindigkeit GEFS SPREAD [km/h]"
        plt.clim(0, 10)

    plt.title(plot_title, loc="center", fontsize=13)
    plt.title(f"Gültig für {valid_date} | Step +{step}", loc="left", fontsize=10)
    plt.title(f"GEFS Lauf {anal_date}", loc="right", fontsize=10)
    m.colorbar(location="right")

    m.readshapefile("./data/get_available_data/gadm/gadm36_AUT_shp/gadm36_AUT_0", "aut")

    parallels = np.arange(44.5, 52.5, 1.)
    m.drawparallels(parallels, labels=[False, False, False, False], fontsize=8, color="lightgrey")
    meridians = np.arange(8.5, 19.5, 1.)
    m.drawmeridians(meridians, labels=[False, False, False, False], fontsize=8, color="lightgrey")

    parallels = np.arange(45., 53., 1.)
    m.drawparallels(parallels, labels=[True, False, False, False], fontsize=8, linewidth=0.0)
    meridians = np.arange(8., 20., 1.)
    m.drawmeridians(meridians, labels=[False, False, False, True], fontsize=8, linewidth=0.0)

    filepath = "./data/spool/{}/{}/".format(parameter, what)
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    anal_date_timestamp = dt.datetime.strptime(anal_date, "%Y-%m-%d %H:%M")
    anal_date_str = anal_date_timestamp.strftime("%Y%m%d")
    filename = f"{anal_date_str}_step_{step:03d}.jpg"
    path_filename = os.path.join(filepath, filename)
    fig.savefig(path_filename, bbox_inches="tight", quality=95, optimize=True, progressive=True)
    plt.close(fig=None)
    return path_filename, filename


def reshapearea(series, array):
    """A function to adjust the shape of a Pandas Series to a numpy array."""
    data = series.values
    reshapedarea = data.reshape(array.shape)
    reshapedarea = reshapedarea[::-1]
    return reshapedarea
