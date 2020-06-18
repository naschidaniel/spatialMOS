# spatialMOSv2

A Live Perview about the current development status of the repository can be viewed at [http://moses.tirol](http://moses.tirol)

spatialMOSv2 is currently being completely redesigned. In the file [CHANGELOG](#CHANGELOG) the already implemented program parts and functionalities are listed.


## Introduction
With spatialMOSv2 weather forecasts of the global weather model GEFS (1 x 1°) can be improved for the regions North Tyrol and South Tyrol. Based on past measurements and past predictions, future predictions are statistically corrected. 
The spatial resolution of the statistically corrected predictions corresponds to a resolution of 30 x 30 m. With spatialMOSv2 temperature, relative humidity and wind forecasts can be made at ground level.

A detailed description of the method can be found in the master thesis [Flächenhafte Vorhersagen von Temperatur und relativer Luftfeuchte im Flachland](http://diglib.uibk.ac.at/urn:nbn:at:at-ubi:1-16130).

## Dependencies
The following dependencies must be installed to access the docker container using invoke. tar is used to archive files.

* docker
* docker-compose
* python 3.7+
* pip install invoke
* rsync
* tar

## Configuration and Installation
Copy the `fabric/settings.example.json` to `./settings.json` and adapt the file to your individual needs. Three development environments are provided in the file: `development`, `test` and `production`. For local operation, only the dictionary `development` must be edited.

spatialMOSv2 is operated in docker containers. The docker containers and the dependencies are built with:

```
./task.py local.install.setenvironment development
./task.py local.install.folders
./task.py local.docker-compose.rebuild
```

## Changelog

- 2020-06-16 Landing page set up for moses.tirol
- 2020-06-16 Productive use of fabric commands with crontab
- 2020-06-16 Domain Moses.tirol was redirected to the new server
- 2020-06-14 Implementing processing and cronjobs for servers
- 2020-06-14 Download GEFS predictions from NCEP NOAA FTP Server
- 2020-06-11 Parse HTML file from ZAMG
- 2020-06-11 Fetch data from API of http://at-wetter.tk/
- 2020-06-09 Fetch data from the University of Innsbruck API
- 2020-06-09 Fetch data from the South Tyrolean weather service  
- 2020-06-07 Init Repository 