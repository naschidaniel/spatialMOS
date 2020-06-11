#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Ein Script zum erstellen archivieren von Downloads
Erstellt am: 07.09.2019
Autor: Daniel Naschberger
"""

import os
import sys
from datetime import datetime

# Lokale Files
sys.path.insert(0, os.getcwd())
import PyspatialMOS.misc.spatialLogging as spatialLogging
import PyspatialMOS.misc.spatialParser as spatialParser

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

########### MAIN #################
if __name__ == "__main__":
    #Logger
    logger, startTime = spatialLogging.setupLogging('log', 'misc__archiv.log', append=True)

    #Parser
    parserDict = spatialParser.parser(logger, name_folder=['uibk', 'grib', 'zamg_page'], folder=True)

    #Archivfolder
    archivfolder = './data/archiv'
    archivfolder = os.path.join(basedir, archivfolder)

    #Folder
    zipfolder = os.path.join(basedir, 'data')
    zipfolder = os.path.join(zipfolder, parserDict['folder'])

    #Zipfile
    zipfile = os.path.join(archivfolder, '{}_{}.7z'.format(parserDict['folder'], datetime.utcnow().strftime('%Y-%m-%d_%H_%M_%S')))
    print(zipfile)
    #Ordnerstruktur
    if not os.path.exists(archivfolder):
        os.makedirs(archivfolder)
        logger.info('Action: {:35} | {}'.format('osmkdirs', archivfolder))

    #Ordnerstruktur
    countFiles = 0
    if os.path.exists(zipfolder):
        for root, dirs, files in os.walk(zipfolder):
            countFiles += len(files)
        logger.info('Action: {:35} | Files: {} | {}'.format('countFiles ', countFiles, zipfile))

        zipFileStatus = os.system("7z a {} {}".format(zipfile, zipfolder))
        logger.info('Action: {:35} | {}'.format('7z file erstellt', zipfile))

        if zipFileStatus == 0:
            logger.info('Action: {:35} | {}'.format('7z: Everything is OK', zipfile))
        else:
            logger.error('Action: {:35} | {}'.format('7z: Something went wrong', zipfile))
            sys.exit(1)
    else:
        logger.error('Action: {:35} | {}'.format('kein Ordner zum zippen vorhanden', zipfolder))
        sys.exit(1)

    try:
        os.system("rm -rf {}".format(zipfolder))
        logger.info('Action: {:35} | {}'.format('rm - rf ... erfolgreich', zipfolder))
    except:
        logger.error('Action: {:35} | {}'.format('rm - rf ... fehlgeschlagen', zipfolder))

    spatialLogging.endLoggingMSG(logger, startTime)