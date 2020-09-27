#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The script was developed by Reto Stauffer and extended by Daniel Naschberger.

The sourcecode of Reto Stauffer can be found at :
https://github.com/retostauffer/GEFS_Downloader_Simple"""


import os
import sys
import re
import logging
from datetime import datetime
import subprocess as sub
import numpy as np
import requests
from py_middleware import spatial_parser
from py_middleware import logger_module


# Classes
class idx_entry(object):
    def __init__(self, args):
        """idx_entry(args)

        A small helper class to handle index entries.
        
        Parameters
        ----------
        args : list
            list with three entries (bytes start, param name, param level)
        """
        self._byte_start = int(args[0])
        self._var        = str(args[1])
        self._lev        = str(args[2])
        self._byte_end   = False

    def add_end_byte(self, x):
        """add_end_byte(x)

        Appends the ending byte.
        """
        self._byte_end = x

    def end_byte(self):
        """end_byte()

        Returns end byte.
        """
        try:
            x = getattr(self, "_byte_end")
            return x 
        except:
            logging.error("whoops, _byte_end attribute not found.")

    def start_byte(self):
        """start_byte()

        Returns start byte.
        """
        try:
            x = getattr(self, "_byte_start")
            return x
        except:
            logging.error("whoops, _byte_start attribute not found.")
 

    def key(self):
        """key()

        Returns
        -------
        Returns a character string "<param name>:<param level>".
        """
        try:
            var = getattr(self, "_var")
            lev = getattr(self, "_lev")
        except Exception as e:
            raise Exception(e)

        return "{:s}:{:s}".format(var,lev)

    def range(self):
        """range()

        Returns
        -------
        Returns the byte range for curl.
        """
        try:
            start = getattr(self, "_byte_start")
            end   = getattr(self, "_byte_end")
        except Exception as e:
            raise Exception(e)
        end = "" if end is None else "{:d}".format(end)

        return "{:d}-{:s}".format(start, end)

    def __repr__(self):
        if isinstance(self._byte_end, bool):
            end = "UNKNOWN"
        elif self._byte_end is None:
            end = "end of file"
        else:
            end = "{:d}".format(self._byte_end)
        return "IDX ENTRY: {:10d}-{:>10s}, '{:s}'".format(self._byte_start,
                end, self.key())

# Functions
def get_file_names(data_path_gribfile, baseurl, date, mem, step, modeltype, resolution):
    """With this function the file names from the server are preprocessed."""

    if modeltype in ["avg", "spr"]:
        if resolution == 0.5:
            # Create URL for geavg.t00z.pgrb2a.0p50.f000.idx
            filename = "ge{:s}.t{:s}z.pgrb2a.0p50.f{:03d}".format(modeltype, date.strftime("%H"), step)
        elif resolution == 1:
            # since UPDATE of noa server depraced 2020-09-27
            # Create URL for geavg.t00z.pgrb2af00.idx
            filename = "ge{:s}.t{:s}z.pgrb2af{:s}".format(modeltype, date.strftime("%H"), "{:02d}".format(step) if step < 100 else "{:03d}".format(step))
        else:
            logging.error("The resolution %d ist not supported", resolution)
            sys.exit(1)
        
        gribfile = os.path.join(date.strftime(baseurl), filename)
        local = date.strftime("GFEE_%Y%m%d_%H00") + "_{:s}_f{:03d}.grb2".format(modeltype, step)
        subset = date.strftime("GFSE_%Y%m%d_%H00") + "_{:s}_f{:03d}_subset.grb2".format(modeltype, step)
    else:
        # UPDATE NAMES 2020-09-27
        # Create URL for gec00.t00z.pgrb2a.0p50.f000.idx
        # Create URL for gep01.t00z.pgrb2a.0p50.f000.idx
        gribfile = os.path.join(date.strftime(baseurl),
                            "ge{:s}{:02d}.t{:s}z.pgrb2a.0p50.f{:s}".format(
                            "c" if mem == 0 else "p", mem, date.strftime("%H"),
                            "{:03d}".format(step)))
        local    = date.strftime("GEFS_%Y%m%d_%H00") + "_{:02d}_f{:03d}.grb2".format(mem, step)
        subset   = date.strftime("GEFS_%Y%m%d_%H00") + "_{:02d}_f{:03d}_subset.grb2".format(mem, step)
    return {"grib"   : gribfile,
            "idx"    : "{:s}.idx".format(gribfile), 
            "local"  : os.path.join(data_path_gribfile, local),
            "subset" : os.path.join(data_path_gribfile, subset)}


def parse_index_file(idxfile, params):
    """A function for processing the GEFS idx files"""
    try:
        logging.info("The index file is going to be downloaded: %s", idxfile)
        req  = requests.get(idxfile)
        data = req.text.split("\n")
    except:
        logging.error("Problems reading index file ... %s ... return None", idxfile)
        return None

    # List to store the required index message information
    idx_entries = []

    comp = re.compile("^\d+:(\d+):d=\d{10}:([^:.*]*):([^:.*]*)")
    for line in data:
        if len(line) == 0: continue
        mtch = re.findall(comp, line)
        if not mtch:
            raise Exception("whoops, pattern mismatch \'{:s}\'".format(line))
        # Else crate the variable hash
        idx_entries.append(idx_entry(mtch[0]))

    for k in range(0, len(idx_entries)):
        if (k + 1) == len(idx_entries):
            idx_entries[k].add_end_byte(None)
        else:
            idx_entries[k].add_end_byte(idx_entries[k+1].start_byte() - 1)

    res = []
    for x in idx_entries:
        if x.key() in params: res.append(x.range())
        
    return res


def download_grib(grib, local, required):
    """A function to download GRIB files."""
    headers = {"Range": "bytes={:s}".format(",".join(required))}
    req_grib = requests.get(grib, headers=headers)

    with open(local, "wb") as f:
        f.write(req_grib.content)
        f.close()
    return True


def fetch_gefs_data(modeltype, date, parameter, resolution):
    """Function for downloading gribfiles from the GEFS NCEP server."""
    
    params = None
    if parameter == "tmp_2m":
        params = ["TMP:2 m above ground"]
    elif parameter == "rh_2m":
        params = ["RH:2 m above ground"]
    elif parameter == "ugrd_10m":
        params = ["UGRD:10 m above ground"]
    elif parameter == "vgrd_10m":
        params = ["VGRD:10 m above ground"]

    # Subset (requires wgrib2), can also be None.
    # Else a dict with N/S/E/W in degrees (0-360!)
    subset = {"E": 20, "W": 8, "S": 45, "N": 53}

    # runhour is in [0, 6, 12, 18]
    runhour = 0
    date = datetime.strptime("{:s} {:02d}:00:00".format(date, runhour), "%Y%m%d %H:%M:%S")

    # Steps/members. The +1 is required to get the required sequence!
    steps = np.arange(6, 300+1, 6, dtype = int)

    logging.info("{:s}".format("".join(["-"]*70)))
    
    # https://www.nco.ncep.noaa.gov/pmb/products/gens/
    if modeltype in ["avg", "spr"]:
        members = np.arange(0, 1, 1, dtype = int)
        logging.info("Downloading members: {:s}:  ".format(modeltype))
        if resolution == 1:
            data_path = f"./data/get_available_data/gefs_avgspr_forecast_p1/{parameter}"
            # url exchanged on 2020-09-23 response with a 404 error
            baseurl = "https://www.ftp.ncep.noaa.gov/data/nccf/com/gens/prod/gefs.%Y%m%d/%H/pgrb2a/"
        elif resolution == 0.5:
            data_path = f"./data/get_available_data/gefs_avgspr_forecast_p05/{parameter}"
            # baseurl = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.%Y%m%d/%H/pgrb2ap5/" # url exchanged on 2020-09-23 response with a 404 error
            baseurl = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.%Y%m%d/%H/atmos/pgrb2ap5/"
        else:
            logging.error("The resolution is not supported")
            sys.exit(1)
    elif modeltype in ["ens"]:
        data_path = f"./data/get_available_data/gefs_ens_forecast_p05/{parameter}"
        members = np.arange(0, 30+1, 1, dtype=int)
        logging.info("Downloading members: {:s}".format(", ".join(["{:d}".format(x) for x in members])))
        # url exchanged on 2020-09-23 response with a 404 error
        #baseurl = " http://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.%Y%m%d/%H/pgrb2/"
        baseurl = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.%Y%m%d/00/atmos/pgrb2ap5/"
    else:
        logging.info("The modeltype is not supported: %s", modeltype)
        sys.exit(1)
   

    steps_str = ", ".join(["{:d}".format(x) for x in steps])
    logging.info("Downloading steps: %s", steps_str)
    logging.info("For date/model initialization %s", date.strftime("%Y-%m-%d %H:%M UTC"))
    logging.info("Base url: %s", date.strftime(baseurl))
    logging.info("{:s}".format("".join(["-"]*70)))

    # Looping over the different members first
    for mem in members:
        # Looping over forecast lead times
        for step in steps:
            logging.info("{:s}".format("".join(["-"]*70)))
            if modeltype in ["avg", "spr"]:
                logging.info("Processing +{:03d}h forecast, {:s}".format(step, modeltype))
            else:
                logging.info("Processing +{:03d}h forecast, member {:02d}".format(step, mem))

            # Specify and create output directory if necessary
            data_path_gribfile = "{:s}/{:s}".format(data_path, date.strftime("%Y%m%d%H%M"))
            if not os.path.isdir(data_path_gribfile):
                try:
                    os.makedirs(data_path_gribfile)
                except:
                    raise Exception("Cannot create directory {:s}!".format(data_path_gribfile))

            files = get_file_names(data_path_gribfile, baseurl, date, mem, step, modeltype, resolution)
            if os.path.isfile(files["subset"]):
                logging.info("Local subset exists, skip: %s", files["subset"])
                logging.info("{:s}".format("".join(["-"]*70)))
                continue
            if os.path.isfile(files["local"]):
                logging.info("Local file exists, skip: %s", files["local"])
                logging.info("{:s}".format("".join(["-"]*70)))
                continue

            logging.info("Grib file: %s", files["grib"])
            logging.info("Index file: %s", files["idx"])
            logging.info("Local file: %s", files["local"])
            logging.info("Subset file: %s", files["subset"])

            # Read/parse index file (if possible)
            required = parse_index_file(files["idx"], params)

            # If no messages found: continue
            if required is None: continue
            if len(required) == 0: continue

            download_grib(files["grib"], files["local"], required)

            # If wgrib2 ist installed: crate subset (small_grib)
            if not subset is None:
                we_bounds = "{:.2f}:{:.2f}".format(subset["W"], subset["E"])
                sn_bounds = "{:.2f}:{:.2f}".format(subset["S"], subset["N"])
                cmd = ["wgrib2", files["local"], "-small_grib", we_bounds, sn_bounds, files["subset"]]
                logging.info("- Subsetting: {:s}".format(" ".join(cmd)))
                p = sub.Popen(cmd, stdout=sub.PIPE, stderr=sub.PIPE)
                out, err = p.communicate()

                if p.returncode == 0:
                    os.remove(files["local"])
                    logging.info("Subset created, delete global file: %s", files["local"])
                else:
                    logging.error("Problem with subset, do not delete global grib2 file.")

            logging.info("{:s}".format("".join(["-"]*70)))

# Main
if __name__ == "__main__":
    STARTTIME = logger_module.start_logging("py_spatialmos", os.path.basename(__file__))
    PARSER_DICT = spatial_parser.spatial_parser(modeltype=True, date=True, name_modeltype=["avg", "spr", "ens"], \
        parameter=True, name_parameter=["tmp_2m", "rh_2m", "ugrd_10m", "vgrd_10m"], resolution=True, name_resolution=[0.5, 1])
    fetch_gefs_data(PARSER_DICT["modeltype"], PARSER_DICT["date"], PARSER_DICT["parameter"], PARSER_DICT["resolution"])
    logger_module.end_logging(STARTTIME)
 