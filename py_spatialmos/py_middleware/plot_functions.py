#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Help functions to create the spatialMOS plots,."""

import os
import sys
import logging
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from PIL import Image

# Functions
def resize_plot(path_filename, filepath, newwidth, ending):
    """A function to resize prediction plots"""
    try:
        im = Image.open(path_filename)
        oldsize = im.size
        ratio = float(oldsize[0]) / float(newwidth)
        newsize = (newwidth, int(round(oldsize[1] / ratio)))
        im.thumbnail(newsize, Image.ANTIALIAS)
        file, ext = os.path.splitext(os.path.basename(path_filename))
        filename_resize = f"{file}_{ending}{ext}"
        path_filename_resize = os.path.join(filepath, filename_resize)
        im.save(path_filename_resize, "JPEG")
        logging.info("The prediction '%s' plot with the new width of %d was created.", path_filename_resize, newwidth)
    except IOError:
        logging.error("The new file with the new width of %d from '%s' could not be created.", newwidth, path_filename)
        sys.exit(1)
        
    plot_filenames = {}
    plot_filenames[f"path_filename_{ending}"] = path_filename_resize
    plot_filenames[f"filename_{ending}"] = filename_resize
    return plot_filenames

def plot_forecast(parameter, erc, xx, yy, plotparameter, gribfile_info, what):
    """A function to create the GEFS and spatialMOS forecast plots."""

    anal_date = gribfile_info["anal_date_avg"]
    valid_date = gribfile_info["valid_date_avg"]
    step = gribfile_info["step"]

    fig_dpi=72
    fig = plt.figure(figsize=(1400/fig_dpi, 1400/fig_dpi), dpi=fig_dpi)

    plot_title = ""
    if parameter == "tmp_2m" and what == "spatialmos_mean":
        fig.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, transform=erc, cmap="RdBu_r")
        plot_title="2m Temperatur spatialmos MEAN [°C]"
        plt.clim(-40, 40)
    elif parameter == "tmp_2m" and what == "spatialmos_spread":
        fig.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, transform=erc, cmap="Reds")
        plot_title="2m Temperatur spatialmos SPREAD [°C]"
        plt.clim(0, 5)
    elif parameter == "tmp_2m" and what == "nwp_mean":
        fig.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, transform=erc, cmap="RdBu_r")
        plot_title="2m Temperatur GEFS MEAN [°C]"
        plt.clim(-40, 40)
    elif parameter == "tmp_2m" and what == "nwp_spread":
        fig.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, transform=erc, cmap="Reds")
        plot_title="2m Temperatur GEFS SPREAD [°C]"
        plt.clim(0, 5)
    elif parameter == "rh_2m" and what == "spatialmos_mean":
        fig.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, transform=erc, cmap="YlGn")
        plot_title="2m Relative Luftfeuchte spatialmos MEAN [%]"
        plt.clim(0, 100)
    elif parameter == "rh_2m" and what == "spatialmos_spread":
        fig.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, transform=erc, cmap="Reds")
        plot_title="2m Relative Luftfeuchte spatialmos SPREAD [%]"
        plt.clim(0, 5)
    elif parameter == "rh_2m" and what == "nwp_mean":
        fig.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, transform=erc, cmap="YlGn")
        plot_title="2m Relative Luftfeuchte GEFS MEAN [%]"
        plt.clim(0, 100)
    elif parameter == "rh_2m" and what == "nwp_spread":
        fig.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, transform=erc, cmap="Reds")
        plot_title="2m Relative Luftfeuchte GEFS SPREAD [%]"
        plt.clim(0, 5)
    elif parameter == "wind_10m" and what == "spatialmos_mean":
        fig.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, transform=erc, cmap="Purples")
        plot_title="10m Windgeschwindigkeit spatialmos MEAN [km/h]"
        plt.clim(0, 10)
    elif parameter == "wind_10m" and what == "spatialmos_spread":
        fig.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, transform=erc, cmap="Reds")
        plot_title="10m Windgeschwindigkeit spatialmos SPREAD [km/h]"
        plt.clim(0, 10)
    elif parameter == "wind_10m" and what == "nwp_mean":
        fig.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, transform=erc, cmap="Purples")
        plot_title="10m Windgeschwindigkeit GEFS MEAN [km/h]"
        plt.clim(0, 10)
    elif parameter == "wind_10m" and what == "nwp_spread":
        fig.pcolormesh(xx, yy, plotparameter, shading="flat", latlon=True, transform=erc, cmap="Reds")
        plot_title="10m Windgeschwindigkeit GEFS SPREAD [km/h]"
        plt.clim(0, 10)

    plt.title(plot_title, loc="center", fontsize=20)
    plt.title(f"Gültig für {valid_date} | Step +{step}", loc="left", fontsize=15)
    plt.title(f"GEFS Lauf {anal_date} UTC", loc="right", fontsize=15)
    m.colorbar(location="right")

    m.readshapefile("./data/get_available_data/gadm/gadm36_AUT_shp/gadm36_AUT_0", "aut")

    m.drawparallels(gribfile_info["lats"], labels=[False, False, False, False], fontsize=10, color="lightgrey")
    meridians = np.arange(8.5, 19.5, 1.)
    m.drawmeridians(gribfile_info["lons"], labels=[False, False, False, False], fontsize=10, color="lightgrey")

    m.drawparallels(gribfile_info["lats"], labels=[True, False, False, False], fontsize=10, color="lightgrey")
    m.drawmeridians(gribfile_info["lons"], labels=[False, False, False, True], fontsize=10, linewidth=0.0)

    filepath = f"./data/spool/{parameter}/images/"
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    anal_date_timestamp = dt.datetime.strptime(anal_date, "%Y-%m-%d %H:%M")
    anal_date_str = anal_date_timestamp.strftime("%Y%m%d")
    filename = f"{what}_{anal_date_str}_step_{step:03d}.jpg"
    path_filename = os.path.join(filepath, filename)
    fig.savefig(path_filename, bbox_inches="tight", quality=70, optimize=True, progressive=True)
    plt.close(fig=None)
    logging.info("The prediction plot '%s' was created.", path_filename)
    
    # Create a small Version of the plot
    plot_filenames_sm = resize_plot(path_filename, filepath, 640, "sm")
    plot_filenames_md = resize_plot(path_filename, filepath, 1024, "md")
    plot_filenames_lg = resize_plot(path_filename, filepath, 1200, "lg")

    # Remove Plot from filesystem
    os.remove(path_filename)

    # Create a dict with all information
    plot_filenames = plot_filenames_sm
    plot_filenames.update(plot_filenames_md)
    plot_filenames.update(plot_filenames_lg)
    return plot_filenames


def reshapearea(series, array):
    """A function to adjust the shape of a Pandas Series to a numpy array."""
    data = series.values
    reshapedarea = data.reshape(array.shape)
    reshapedarea = reshapedarea[::-1]
    return reshapedarea
