# spatialMOSv2

spatialMOSv2 is currently being completely redesigned. In section [CHANGELOG](#CHANGELOG) the already implemented program parts and functionalities are listed.


## Introduction
With spatialMOSv2 weather forecasts of the global weather model GEFS (1 x 1° Grid) can be improved for the regions North- and South Tyrol. Based on past station observations and past predictions, future predictions are corrected with statistical methods. 
The spatial resolution of the statistically corrected predictions corresponds to the SRTM Data (Further information can be obtained from [https://gadm.org](https://gadm.org)), with leads to a of 90 x 90 m. With spatialMOSv2 temperature, relative humidity and wind forecasts can be made at ground level.

A detailed description of the method can be found in the master thesis [Flächenhafte Vorhersagen von Temperatur und relativer Luftfeuchte im Flachland](http://diglib.uibk.ac.at/urn:nbn:at:at-ubi:1-16130).

## Dependencies
You will need [python](https://www.python.org/) **version 3.7+**, [invoke](http://www.pyinvoke.org/installing.html) **version 1.4+**, [docker](https://www.docker.com/), [docker-compose](https://docs.docker.com/compose/), [rsync](https://rsync.samba.org/) and [tar](https://www.gnu.org/software/tar/).


## Configuration and Installation
Copy the `fabric/settings.example.json` to `./settings.json` and adapt the file to your individual needs. Two environments are provided in the file: `development` and `production`. For local operation, only the dictionary `development` must be edited. The `production` dictionary entries are optional and only relevant for the server.

spatialMOSv2 can be installed locally using the command:

```
./task.py local.install.quickinstallation
```

The required folder structure and environment variables are set.


## Usage

A list for spatialMOSv2 implemented invoke commands: 

```
./task.py
```


### Data basis

***For statistical postprocessing of weather forecasts, past values of at least two years are required.***


#### Meteorological station values
Past measured values are obtained via the API interfaces of [http://wetter.provinz.bz.it/](http://wetter.provinz.bz.it/) and [http://at-wetter.tk/](http://at-wetter.tk/). The required stations.csv file for [http://at-wetter.tk/](http://at-wetter.tk/) is downloaded from moses.tirol.

```
./task.py local.spatialmos.py-spatialmos--get-suedtirol 2018-01-01 2019-12-31
./task.py local.spatialmos.py-spatialmos--get-wetter-at 2018-01-01 2019-12-31
```

Current values from the ZAMG web page or from the UIBK API interface can be done with the two fabric commands.

```
./task.py local.spatialmos.py-spatialmos--get-uibk
./task.py local.spatialmos.py-spatialmos--get-zamg
```


#### GEFS Weather Reforecasts (Forecast Archive)

Previous mean and spread ensemble forecasts of the GEFS weather model can be downloaded free of charge from the FTP in a resolution of 1° x 1°. To load the data the program [retostauffer/PyGFSV2](https://github.com/retostauffer/PyGFSV2) is required.
A forked version can be downloaded under [naschidaniel/PyGFSV2](https://github.com/naschidaniel/PyGFSV2). With `sh GFSV2_bulk.sh` the archive GEFS Reforecasts can be downloaded. The program creates folders based on the year numbers. These folders can be stored directly in `./data/get_available_data/gefs_reforecast/nwp` for further statistical processing. 


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


#### Bilinear interpolation of GEFS Weather Reforecasts to station locations

The Global Weather Model data from the GEFS Model is bilinear interpolated to the station location. The predictions are saved per model run and step in CSV-Format. The data is stored under `./data/get_available_data/gefs_reforecast/interpolated_station_reforecasts/*`. 

```
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforecasts tmp_2m
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforecasts spfh_2m
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforecasts pres_sfc
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforecasts apcp_sfc
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforecasts ugrd_10m
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforecasts vgrd_10m
```

The data for relative humidity and wind are calculated from other parameters. These parameters must be interpolated in advance.

```
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforecasts rh_2m #Required parameters: tmp_2m, spfh_2m, pres_sfc
./task.py local.spatialmos.py-spatialmos--pre-proccessing-reforecasts wind_10m #Required parameters: ugrd_10m, vgrd_10m
```


#### Combination of GEFS Reforecasts and Station Observations

For further statistical processing a data set with all station observations for all parameters and forecasts of at least two past years are required. 

```
./task.py local.spatialmos.py-spatialmos--pre-proccessing-observations-and-reforecasts-to-stations
```

The observations and the GEFS Reforecasts still need to be pre-processed. The observations and the GEFS Reforecasts will be combined. From these files the area-wide valid climatologies are generated.

```
./task.py local.spatialmos.py-spatialmos--pre-processing-gamlss-crch-climatologies tmp_2m
./task.py local.spatialmos.py-spatialmos--pre-processing-gamlss-crch-climatologies rh_2m
./task.py local.spatialmos.py-spatialmos--pre-processing-gamlss-crch-climatologies wind_10m
./task.py local.spatialmos.py-spatialmos--pre-processing-gamlss-crch-climatologies apcp_sfc
```

### Statistical processing for spatial of the spatially valid climatologies

#### Digital Ground Model and Shapefiles for North- and South Tyrol

The required shapefiles are prepared for further processing with the help of the R libraries rgdal and raster. For the topography the GADM topography of North and South Tyrol is used. The will be downloaded from the website [GADM](https://gadm.org/) and stored in folder `./data/get_available_data/gadm`. 

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

For the statistical processing of the Direct Model Output, climatologies for the relevant day and model step must be created. 

##### GEFS Forecast climatologies for the day of the year and model step 
```
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-nwp mp_2m 192 195
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-nwp rh_2m 192 195
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-nwp wind_10m 192 195
```

##### Observation climatologies for the day
```
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-obs tmp_2m 192 195
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-obs rh_2m 192 195
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-obs wind_10m 192 195
```


### Statistically corrected weather forecasts

The current forecasts and the climatologies created are used to produce corrected weather forecasts for temperature, relative humidity and wind. 

For this step, current forecasts ([GEFS Weather Forecasts](#GEFS-Weather-Forecasts)) and calculated climatologies ([Create daily climatologies for post processing of GEFS forecasts](#Create-daily-climatologies-for-post-processing-of-GEFS-forecasts)) must be available.

```
./task.py *TODO*
```

The calculated predictions are available in the exchange folder `./data/spool`. The presentation of the data is made with the help of django. 


### Archive downloaded files

The downloaded files in the folders can be archived with `tar`. The archived files are located under `./data/archive`.

```
./task.py local.spatialmos.py-spatialmos--archive-available-data "gefs_forecast"
./task.py local.spatialmos.py-spatialmos--archive-available-data "gefs_reforecast"
./task.py local.spatialmos.py-spatialmos--archive-available-data "suedtirol"
./task.py local.spatialmos.py-spatialmos--archive-available-data "uibk"
./task.py local.spatialmos.py-spatialmos--archive-available-data "wetter_at"
./task.py local.spatialmos.py-spatialmos--archive-available-data "zamg"
```

### Source files and spatial climatologies exchange with the server

With the help of `rsync` and `scp` data can be exchanged between server and local computer. In the file `settings.json` the necessary settings are made.

The source files are synchronized using the fabric command:
```
./task.py production.rsync.push sourcefiles
```

The climatologies needed for the daily calculation can be uploaded using the command:
```
./task.py production.rsync.push climatologies
```

### Website

The online presence was implemented with the web framework django written in python. The calculated predictions are stored in a PostgreSQL database. For each address in North- and South Tyrol, predictions can thus be made. The API of openstreetmap is used for the address query. *TODO*

#### Data import from spool directory to PostgreSQL database

```
./task.py *TODO*
```

#### API Website interface 

The predictions can also be loaded as JSON data via the Api Rest interface.

```
API urls *TODO*
```


#### Live Demo

Visit the Live Demo Page for current forecasts for North and South Tyrol.

[https://moses.tirol](https://moses.tirol)


## Contribution

Please make sure to read the [Contributing Guide](./CONTRIBUTING.md) before making a pull request.



## Changelog

- 2020-07-10 Daily valid climatology files for tmp_2m can be created
- 2020-07-09 A spatial valid climatology file for tmp_2m can be created
- 2020-07-08 Download Shapefiles with R
- 2020-07-07 Adding R Container to project 
- 2020-07-03 Restructuring of the Docker containers, volumes and python script folder
- 2020-06-23 Added https certificates via Let´s Encrypt to nginx configuration
- 2020-06-18 Nginx configuration for moses.tirol
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
