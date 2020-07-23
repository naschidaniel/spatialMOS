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