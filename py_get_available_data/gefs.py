#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The script was developed by Reto Stauffer and extended by Daniel Naschberger.

The sourcecode of Reto Stauffer can be found at :
https://github.com/retostauffer/GEFS_Downloader_Simple"""


import os
import re
import sys
import argparse
import logging
from datetime import datetime
import subprocess as sub
import numpy as np
import requests
from py_middleware import spatial_parser
from py_middleware import logger_module

# Functions
def get_file_names(filedir, baseurl, date, mem, step, avgspr):
    """get_file_names(filedir, baseurl, date, mem, step)

    Generates the file names (remote and local).

    Parameters
    ----------
    filedir : str
        name of the directory where to create the file "local"
    baseurl : str
        base url, used to format the data (can contain %Y%m%d or similar)
    date : datetime.
        defines model initialization date and time
    mem : int
        member number
    step : int
        forecast step (in hours)

    Returns
    -------
    Returns a dict with three entries for the indexfile ("idx"), the grib file ("grib"),
    and the local file name ("local"), plus the file name of the local subset. Only
    used if subset is defined and wgrib2 is available (see main script).
    """

    # Create URL  	geavg.t00z.pgrb2af00.idx
    if avgspr in ['avg', 'spr']:
        gribfile = os.path.join(date.strftime(baseurl),
                            "ge{:s}.t{:s}z.pgrb2af{:s}".format(avgspr, date.strftime("%H"),
                            "{:02d}".format(step) if step < 100 else "{:03d}".format(step)))
        local = date.strftime("GFEE_%Y%m%d_%H00") + "_{:s}_f{:03d}.grb2".format(avgspr, step)
        subset = date.strftime("GFSE_%Y%m%d_%H00") + "_{:s}_f{:03d}_subset.grb2".format(avgspr, step)
    else:
        gribfile = os.path.join(date.strftime(baseurl),
                            "ge{:s}{:02d}.t{:s}z.pgrb2f{:s}".format(
                            "c" if mem == 0 else "p", mem, date.strftime("%H"),
                            "{:02d}".format(step) if step < 100 else "{:03d}".format(step)))
        local    = date.strftime("GEFS_%Y%m%d_%H00") + "_{:02d}_f{:03d}.grb2".format(mem, step)
        subset   = date.strftime("GEFS_%Y%m%d_%H00") + "_{:02d}_f{:03d}_subset.grb2".format(mem, step)
    return {"grib"   : gribfile,
            "idx"    : "{:s}.idx".format(gribfile), 
            "local"  : os.path.join(filedir, local),
            "subset" : os.path.join(filedir, subset)}


# -------------------------------------------------------------------
# -------------------------------------------------------------------
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
        except:
            raise Error("whoops, _byte_end attribute not found.")
        return x 

    def start_byte(self):
        """start_byte()

        Returns start byte.
        """
        try:
            x = getattr(self, "_byte_start")
        except:
            raise Error("whoops, _byte_start attribute not found.")
        return x 

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

# -------------------------------------------------------------------
# -------------------------------------------------------------------
def parse_index_file(idxfile, params):
    """A function for processing the GEFS idx files"""

    try:
        logging.info("The index file is going to be downloaded: %s", idxfile)
        req  = requests.get(idxfile)
        data = req.text.split("\n")
    except Exception as e:
        logging.error("Problems reading index file ... %s ... return None", idxfile)
        return None

    # List to store the required index message information
    idx_entries = []

    # Parsing data (extracting message starting byte,
    # variable name, and variable level)

    comp = re.compile("^\d+:(\d+):d=\d{10}:([^:.*]*):([^:.*]*)")
    for line in data:
        if len(line) == 0: continue
        mtch = re.findall(comp, line)
        if not mtch:
            raise Exception("whoops, pattern mismatch \"{:s}\"".format(line))
        # Else crate the variable hash
        idx_entries.append(idx_entry(mtch[0]))

    # Now we know where the message start (bytes), but we do not
    # know where they end. Append this information.
    for k in range(0, len(idx_entries)):
        if (k + 1) == len(idx_entries):
            idx_entries[k].add_end_byte(None)
        else:
            idx_entries[k].add_end_byte(idx_entries[k+1].start_byte() - 1)
    #    print(idx_entries[k])

    # Go trough the entries to find the messages we request for.
    res = []
    for x in idx_entries:
        if x.key() in params: res.append(x.range())
        
    # Return ranges to be downloaded
    return res

# -------------------------------------------------------------------
def download_grib(grib, local):
    req_grib = requests.get(grib)

    with open(local, 'wb') as f:
        f.write(req_grib.content)
        f.close()
    return True



def fetch_gefs_data(avgspr, date, parameter, runhour):
    if parameter == 'tmp_2m':
        params = ["TMP:2 m above ground"]
    elif parameter == 'rh_2m':
        params = ["RH:2 m above ground"]
    elif parameter == 'ugrd_10m':
        params = ["UGRD:10 m above ground"]
    elif parameter == 'vgrd_10m':
        params = ["VGRD:10 m above ground"]

    # Config
        # Provide folder structure.
    data_path = "/get_available_data/gefs"
    if not os.path.exists(f"{data_path}"):
        os.mkdir(f"{data_path}")

    if not os.path.exists(f"{data_path}/data/"):
        os.mkdir(f"{data_path}/data/")

    outdir = "/get_available_data/gefs/data/gfs_forcast/{}".format(parameter)
    baseurl_avgspr = "https://www.ftp.ncep.noaa.gov/data/nccf/com/gens/prod/gefs.%Y%m%d/%H/pgrb2a/"
    baseurl_ens = "http://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.%Y%m%d/%H/pgrb2/"
    # Subset (requires wgrib2), can also be None.
    # Else a dict with N/S/E/W in degrees (0-360!)
    subset = {"E": 20, "W": 8, "S": 45, "N": 53}


    # Crate date arg
    print(date)
    date = datetime.strptime("{:s} {:02d}:00:00".format(date, runhour), "%Y%m%d %H:%M:%S")

    # Steps/members. The +1 is required to get the required sequence!
    steps = np.arange(6, 300+1, 6, dtype = int)

    logging.info("{:s}".format("".join(["-"]*70)))
    if avgspr in ['avg', 'spr']:
        members = np.arange(0, 1, 1, dtype = int)
        print("Downloading members:\n  {:s}:  ".format(avgspr))
        baseurl = baseurl_avgspr
    else:
        members = np.arange(0, 20+1, 1, dtype=int)
        print("Downloading members:\n  {:s}".format(", ".join(["{:d}".format(x) for x in members])))
        baseurl = baseurl_ens


    print("Downloading steps:\n  {:s}".format(", ".join(["{:d}".format(x) for x in steps])))
    print("For date/model initialization\n  {:s}".format(date.strftime("%Y-%m-%d %H:%M UTC")))
    print("Base url:\n  {:s}".format(date.strftime(baseurl)))
    logging.info("{:s}".format("".join(["-"]*70)))

    # Looping over the different members first
    for mem in members:
        # Looping over forecast lead times
        for step in steps:
            logging.info("{:s}".format("".join(["-"]*70)))
            if avgspr in ['avg', 'spr']:
                print("Processing +{:03d}h forecast, {:s}".format(step, avgspr))
            else:
                print("Processing +{:03d}h forecast, member {:02d}".format(step, mem))

            # Specify and create output directory if necessary
            filedir = "{:s}/{:s}".format(outdir, date.strftime("%Y%m%d%H%M"))
            if not os.path.isdir(filedir):
                try:
                    os.makedirs(filedir)
                except:
                    raise Exception("Cannot create directory {:s}!".format(filedir))

            # Getting file names
            files = get_file_names(filedir, baseurl, date, mem, step, avgspr)
            print(files)
            if os.path.isfile(files["subset"]):
                print("- Local subset exists, skip")
                logging.info("{:s}".format("".join(["-"]*70)))
                continue
            if os.path.isfile(files["local"]):
                print("- Local file exists, skip")
                logging.info("{:s}".format("".join(["-"]*70)))
                continue


            # Else start download
            print (f"- Grib file: {files['grib']}\n- Index file: {files['idx']}\n - Local file: {files['local']}\n- Subset file: {files['subset']}")

            # Downloading the data
            download_grib(files["grib"], files["local"])

            # If wgrib2 exists: crate subset (small_grib)
            if not subset is None:
                WE  = "{:.2f}:{:.2f}".format(subset["W"], subset["E"])
                SN  = "{:.2f}:{:.2f}".format(subset["S"], subset["N"])
                cmd = ["wgrib2", files["local"], "-small_grib", WE, SN, files["subset"]]
                print("- Subsetting: {:s}".format(" ".join(cmd)))
                p = sub.Popen(cmd, stdout = sub.PIPE, stderr = sub.PIPE) 
                out, err = p.communicate()

                if p.returncode == 0:
                    print("- Subset created, delete global file")
                    os.remove(files["local"])
                else:
                    print("[!] Problem with subset, do not delete global grib2 file.")


            # Else post-processing the data
            logging.info("{:s}".format("".join(["-"]*70)))

# Main
if __name__ == "__main__":
    starttime = logger_module.start_logging("get_available_data", "suedtirol")
    parser_dict = spatial_parser.spatial_parser(avgspr=True, date=True, name_avgspr=[None, "avg", "spr"], parameter=True, name_parameter=["tmp_2m", "rh_2m", "ugrd_10m", "vgrd_10m"], runhour=True, name_runhour=[0, 6, 12, 18])
    fetch_gefs_data(parser_dict["avgspr"], parser_dict["date"], parser_dict["parameter"], parser_dict["runhour"])
    logger_module.end_logging(starttime)
 