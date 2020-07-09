# spatialMOSv2

spatialMOSv2 is currently being completely redesigned. In the file [CHANGELOG](#CHANGELOG) the already implemented program parts and functionalities are listed.


## Introduction
With spatialMOSv2 weather forecasts of the global weather model GEFS (1 x 1°) can be improved for the regions North Tyrol and South Tyrol. Based on past measurements and past predictions, future predictions are statistically corrected. 
The spatial resolution of the statistically corrected predictions corresponds to a resolution of 30 x 30 m. With spatialMOSv2 temperature, relative humidity and wind forecasts can be made at ground level.

A detailed description of the method can be found in the master thesis [Flächenhafte Vorhersagen von Temperatur und relativer Luftfeuchte im Flachland](http://diglib.uibk.ac.at/urn:nbn:at:at-ubi:1-16130).

## Dependencies
You will need [python](https://www.python.org/) **version 3.7+**, [invoke](http://www.pyinvoke.org/installing.html) **version 1.4+**, [docker](https://www.docker.com/), [docker-compose](https://docs.docker.com/compose/), [rsync](https://rsync.samba.org/) and [tar](https://www.gnu.org/software/tar/).


## Configuration and Installation
Copy the `fabric/settings.example.json` to `./settings.json` and adapt the file to your individual needs. Three development environments are provided in the file: `development`, `test` and `production`. For local operation, only the dictionary `development` must be edited.

spatialMOSv2 is operated in docker containers. The docker containers and the dependencies are built with:

```
./task.py local.install.setenvironment development
./task.py local.install.folders
./task.py local.docker-compose.rebuild
```


## Usage

A list for spatialMOSv2 implemented invoke commands: 

```
./task.py
```


### Data basis

For the calculation of weather forecasts, past values of at least two years are required.


#### Meteorological station values
Past measured values are obtained via the API interfaces of [http://wetter.provinz.bz.it/](http://wetter.provinz.bz.it/) and [http://at-wetter.tk/](http://at-wetter.tk/). The station file for further processing is loaded from the moses.tirol page.

```
./task.py local.spatialmos.py-spatialmos--get-suedtirol 2019-01-01 2019-12-31
./task.py local.spatialmos.py-spatialmos--get-wetter-at 2019-01-01 2019-12-31
```

Current values from the ZAMG web page as well as from the UIBK API interface can be done with the two program calls.

```
./task.py local.spatialmos.py-spatialmos--get-uibk
./task.py local.spatialmos.py-spatialmos--get-zamg
```


#### GEFS Weather Reforcasts (Forecast Archive)

Previous mean and spread ensemble forecasts of the GEFS weather model can be downloaded free of charge from the FTP in a resolution of 1° x 1°. To load the data the program [retostauffer/PyGFSV2](https://github.com/retostauffer/PyGFSV2) is required.
A forked version can be downloaded under [naschidaniel/PyGFSV2](https://github.com/naschidaniel/PyGFSV2). With `sh GFSV2_bulk.sh` the archive gfse forcasts can be downloaded. The data must be stored in this project in the folder `./data/get_available_data/gefs_reforcast/nwp` for further processing.


#### GEFS Weather Forecasts

Current Ensemble weather forecasts can be obtained from the FTP server. Please use today's date

```
./task.py local.spatialmos.py-spatialmos--get-gefs "--date 2020-07-03 --runhour 0 --parameter tmp_2m --avgspr avg"
./task.py local.spatialmos.py-spatialmos--get-gefs "--date 2020-07-03 --runhour 0 --parameter tmp_2m --avgspr spr"
./task.py local.spatialmos.py-spatialmos--get-gefs "--date 2020-07-03 --runhour 0 --parameter rh_2m --avgspr avg"
./task.py local.spatialmos.py-spatialmos--get-gefs "--date 2020-07-03 --runhour 0 --parameter rh_2m --avgspr spr"
./task.py local.spatialmos.py-spatialmos--get-gefs "--date 2020-07-03 --runhour 0 --parameter vgrd_10m --avgspr avg"
./task.py local.spatialmos.py-spatialmos--get-gefs "--date 2020-07-03 --runhour 0 --parameter vgrd_10m --avgspr spr"
./task.py local.spatialmos.py-spatialmos--get-gefs "--date 2020-07-03 --runhour 0 --parameter ugrd_10m --avgspr avg"
./task.py local.spatialmos.py-spatialmos--get-gefs "--date 2020-07-03 --runhour 0 --parameter ugrd_10m --avgspr spr"
```



### Raw data pre processing for further statistical processing


#### Bilinear interpolation of GEFS Weather Reforcasts to station locations

The Global Weather Model data from the GEFS Model is bilinear interpolated to the station location. The predictions are saved per model run and step in CSV-Format. The data is stored under `./data/get_available_data/gefs_reforcast/interpolated_station_reforcasts/*`. 

```
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforcasts "tmp_2m"
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforcasts "spfh_2m"
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforcasts "pres_sfc"
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforcasts "apcp_sfc"
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforcasts "ugrd_10m"
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforcasts "vgrd_10m"
```

The data for relative humidity and wind are calculated from other parameters. These parameters must be interpolated in advance.

```
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforcasts "rh_2m" #Required parameters: tmp_2m, spfh_2m, pres_sfc
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforcasts "wind_10m" #Required parameters: ugrd_10m, vgrd_10m
```


#### Combination of GEFS Reforcasts and Station Observations

For further statistical processing a data set with all station observations and forecasts of the past years is required. In this file all observations for all parameters and predictions are combined.

```
./task.py local.spatialmos.py-spatialmos--pre-proccessing-observations-and-reforcasts-to-stations
```

The observations and the GEFS Reforcasts still need to be pre-processed. The observations and the GEFS Reforcasts will be combined. From these files the area-wide valid climatologies are generated.

```
./task.py local.spatialmos.py-spatialmos--pre-processing-gamlss-crch-climatologies "tmp_2m"
./task.py local.spatialmos.py-spatialmos--pre-processing-gamlss-crch-climatologies "rh_2m"
./task.py local.spatialmos.py-spatialmos--pre-processing-gamlss-crch-climatologies "wind_10m"
./task.py local.spatialmos.py-spatialmos--pre-processing-gamlss-crch-climatologies "apcp_sfc"
```

### Statistical processing for spatial of the spatially valid climatologies

#### Digital Ground Model and National Shapefiles

The required shapefiles are prepared for further processing with the help of the libraries rgdal and raster. For the topography the GADM topography of North and South Tyrol is used. The will be downloaded from the website [GADM](https://gadm.org/) and stored in folder `./data/get_available_data/gadm`. 

```
./task.py local.spatialmos.r-spatialmos--gam-init-shapefiles
```


#### Climatologies for the daily calculation of forecasts

Based on the pre processed data and the modelling software [gamlss](http://www.gamlss.com/), climatologies for the forecast area are created. 

```
./task.py local.spatialmos.r-spatialmos--gamlss-crch-model tmp_2m False
./task.py local.spatialmos.r-spatialmos--gamlss-crch-model rh_2m False
./task.py local.spatialmos.r-spatialmos--gamlss-crch-model wind_10m False
```

#### Create daily climatologies for post processing of GEFS forecasts

##### climatologies for GEFS Reforcasts
```
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-nwp mp_2m 192 195
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-nwp rh_2m 192 195
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-nwp wind_10m 192 195
```

##### climatologies for Observations
```
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-obs tmp_2m 192 195
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-obs rh_2m 192 195
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-obs wind_10m 192 195
```


### Statistically corrected weather forecasts

The current forecasts and the climatologies created are used to produce corrected weather forecasts for temperature, relative humidity and wind. 

```
./task.py *TODO*
```

The calculated predictions are available in the exchange folder `./data/spool`. The presentation of the data is made with the help of django. 


### Archive downloaded files

The downloaded files in the folders can be archived with `tar`. The archived files are located under `./data/archive`.

```
./task.py local.spatialmos.py-spatialmos--archive-available-data "gefs_forcast"
./task.py local.spatialmos.py-spatialmos--archive-available-data "gefs_reforcast"
./task.py local.spatialmos.py-spatialmos--archive-available-data "suedtirol"
./task.py local.spatialmos.py-spatialmos--archive-available-data "uibk"
./task.py local.spatialmos.py-spatialmos--archive-available-data "wetter_at"
./task.py local.spatialmos.py-spatialmos--archive-available-data "zamg"
```


### Website

The online presence was implemented with the web framework django from python. The calculated predictions are stored in a PostgreSQL database. For each address in Tyrol, predictions can thus be made. The API of openstreetmap is used for the address query.

#### Data import from spool directory to PostgreSQL database

```
./task.py *TODO*
```

#### Live Demo

Visit the Live Demo Page for current forecasts for North and South Tyrol.

[https://moses.tirol](https://moses.tirol)


## Contribution

Please make sure to read the [Contributing Guide](./CONTRIBUTING.md) before making a pull request.



## Changelog

- 2020-07-09 create climatologies for gamlss
- 2020-07-08 download Shapefiles with R
- 2020-07-07 adding R Container to project 
- 2020-07-03 Restructuring of the Docker containers, volumes and python script folder
- 2020-06-23 added https certificates via Let´s Encrypt to nginx configuration
- 2020-06-18 nginx configuration for moses.tirol
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


## License

[GPL-3.0](./LICENSE)

Copyright (c) 2019-present, Daniel Naschberger
