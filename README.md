# spatialMOS

spatialMOS is currently being completely redesigned. In section [CHANGELOG](#CHANGELOG) the already implemented program parts and functionalities are listed.


## Introduction
With spatialMOS weather forecasts of the global weather model GEFS (1 x 1° Grid) can be improved for the regions North- and South Tyrol. Based on past station observations and past predictions, future predictions are corrected with statistical methods. 
The spatial resolution of the statistically corrected predictions corresponds to the SRTM Data (Further information can be obtained from [https://gadm.org](https://gadm.org)), with leads to a of 90 x 90 m. With spatialMOS temperature, relative humidity and wind forecasts can be made at ground level.

A detailed description of the method can be found in the master thesis [Flächenhafte Vorhersagen von Temperatur und relativer Luftfeuchte im Flachland](http://diglib.uibk.ac.at/urn:nbn:at:at-ubi:1-16130).

## Dependencies
You will need [python](https://www.python.org/) **version 3.7+**, [invoke](http://www.pyinvoke.org/installing.html) **version 1.4+**, [docker](https://www.docker.com/), [docker-compose](https://docs.docker.com/compose/), [rsync](https://rsync.samba.org/) and [tar](https://www.gnu.org/software/tar/).


## Configuration and Installation
Copy the `fabric/settings.example.json` to `./settings.json` and adapt the file to your individual needs. Two environments are provided in the file: `development` and `production`. For local operation, only the dictionary `development` must be edited. The `production` dictionary entries are optional and only relevant for the server.

spatialMOS can be installed locally using the command:

```
./task.py local.install.quickinstallation
```

The required folder structure and environment variables are set.


## Usage

A list for spatialMOS implemented invoke commands: 

```
./task.py
```


### Data basis

***For statistical postprocessing of weather forecasts, past values of at least two years are required.***


#### Digital Ground Model and Shapefiles for North- and South Tyrol

The required shapefiles are prepared for further processing with the help of the R libraries rgdal and raster. For the topography the GADM topography of North and South Tyrol is used. For the predictions, which are generated in python, the required [GADM](https://gadm.org/) files are downloaded and unpacked using unzip. The will be downloaded from the website  and stored in folder `./data/get_available_data/gadm`. 

```
./task.py local.spatialmos.spatialmos--init-topography
```

#### Meteorological station values
Past measured values are obtained via the API interfaces of [http://wetter.provinz.bz.it/](http://wetter.provinz.bz.it/) and [http://at-wetter.tk/](http://at-wetter.tk/). The required stations.csv file for [http://at-wetter.tk/](http://at-wetter.tk/) is downloaded from moses.tirol.

```
./task.py local.spatialmos.py-spatialmos--get-suedtirol --begindate 2018-01-01 --enddate 2019-12-31
./task.py local.spatialmos.py-spatialmos--get-wetter-at --begindate 2018-01-01 --enddate 2019-12-31
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
./task.py local.spatialmos.py-spatialmos--get-gefs --date 2020-07-03 --runhour 0 --parameter tmp_2m --modeltype avg
./task.py local.spatialmos.py-spatialmos--get-gefs --date 2020-07-03 --runhour 0 --parameter tmp_2m --modeltype spr
./task.py local.spatialmos.py-spatialmos--get-gefs --date 2020-07-03 --runhour 0 --parameter rh_2m --modeltype avg
./task.py local.spatialmos.py-spatialmos--get-gefs --date 2020-07-03 --runhour 0 --parameter rh_2m --modeltype spr
./task.py local.spatialmos.py-spatialmos--get-gefs --date 2020-07-03 --runhour 0 --parameter vgrd_10m --modeltype avg
./task.py local.spatialmos.py-spatialmos--get-gefs --date 2020-07-03 --runhour 0 --parameter vgrd_10m --modeltype spr
./task.py local.spatialmos.py-spatialmos--get-gefs --date 2020-07-03 --runhour 0 --parameter ugrd_10m --modeltype avg
./task.py local.spatialmos.py-spatialmos--get-gefs --date 2020-07-03 --runhour 0 --parameter ugrd_10m --modeltype spr
```

#### GEFS Weather Forecasts Pre Processing

Due to problems with dependencies it was decided to create custom containers for pygrib, basemap and gdal. The downloaded data must therefore be pre-processed for the forecasts.

```
./task.py local.spatialmos.py-spatialmos--pre-processing-gribfiles --date 2020-07-22 --parameter tmp_2m 
./task.py local.spatialmos.py-spatialmos--pre-processing-gribfiles --date 2020-07-22 --parameter rh_2m
./task.py local.spatialmos.py-spatialmos--pre-processing-gribfiles --date 2020-07-22 --parameter wind_10m
```


### Raw data pre processing for further statistical processing


#### Bilinear interpolation of GEFS Weather Reforecasts to station locations

The Global Weather Model data from the GEFS Model is bilinear interpolated to the station location. The predictions are saved per model run and step in CSV-Format. The data is stored under `./data/get_available_data/gefs_reforecast/interpolated_station_reforecasts/*`. 

```
./task.py local.spatialmos.py-spatialmos--pre-processing-reforecasts --parameter tmp_2m
./task.py local.spatialmos.py-spatialmos--pre-processing-reforecasts --parameter spfh_2m
./task.py local.spatialmos.py-spatialmos--pre-processing-reforecasts --parameter pres_sfc
./task.py local.spatialmos.py-spatialmos--pre-processing-reforecasts --parameter apcp_sfc
./task.py local.spatialmos.py-spatialmos--pre-processing-reforecasts --parameter ugrd_10m
./task.py local.spatialmos.py-spatialmos--pre-processing-reforecasts --parameter vgrd_10m
```

The data for relative humidity and wind are calculated from other parameters. These parameters must be interpolated in advance.

```
./task.py local.spatialmos.py-spatialmos--pre-processing-reforecasts --parameter rh_2m #Required pre calculated parameters: tmp_2m, spfh_2m, pres_sfc
./task.py local.spatialmos.py-spatialmos--pre-processing-reforecasts --parameter wind_10m #Required pre calculated parameters: ugrd_10m, vgrd_10m
```


#### Combination of GEFS Reforecasts and Station Observations

For further statistical processing a data set with all station observations for all parameters and forecasts of at least two past years are required. 

```
./task.py local.spatialmos.py-spatialmos--pre-processing-observations-and-reforecasts-to-stations
```

The observations and the GEFS Reforecasts still need to be pre-processed. The observations and the GEFS Reforecasts will be combined. From these files the area-wide valid climatologies are generated.

```
./task.py local.spatialmos.py-spatialmos--pre-processing-gamlss-crch-climatologies --parameter tmp_2m
./task.py local.spatialmos.py-spatialmos--pre-processing-gamlss-crch-climatologies --parameter rh_2m
./task.py local.spatialmos.py-spatialmos--pre-processing-gamlss-crch-climatologies --parameter wind_10m
./task.py local.spatialmos.py-spatialmos--pre-processing-gamlss-crch-climatologies --parameter apcp_sfc
```

### Statistical processing for spatial of the spatially valid climatologies


#### Climatologies for the daily calculation of forecasts

Based on the pre processed data and the modelling software [gamlss](http://www.gamlss.com/), climatologies for the forecast area are created. 

```
./task.py local.spatialmos.r-spatialmos--gamlss-crch-model --parameter tmp_2m --validation False
./task.py local.spatialmos.r-spatialmos--gamlss-crch-model --parameter rh_2m --validation False
./task.py local.spatialmos.r-spatialmos--gamlss-crch-model --parameter wind_10m --validation False
```

#### Create daily climatologies for post processing of GEFS forecasts

For the statistical processing of the Direct Model Output, climatologies for the relevant day and model step must be created. 

##### GEFS Forecast climatologies for the day of the year and model step 
```
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-nwp --parameter tmp_2m --begin 192 --end 195
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-nwp --parameter rh_2m --begin 192 --end 195
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-nwp --parameter wind_10m --begin 192 --end 195
```

##### Observation climatologies for the day
```
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-obs --parameter tmp_2m --begin 192 --end 195
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-obs --parameter rh_2m --begin 192 --end 195
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-obs --parameter wind_10m --begin 192 --end 195
```


### Statistically corrected weather forecasts

The current forecasts and the climatologies created are used to produce corrected weather forecasts for temperature, relative humidity and wind. 

For this step, current forecasts ([GEFS Weather Forecasts](#GEFS-Weather-Forecasts)) and calculated climatologies ([Create daily climatologies for post processing of GEFS forecasts](#Create-daily-climatologies-for-post-processing-of-GEFS-forecasts)) must be available.


```
./task.py local.spatialmos.py-spatialmos--prediction --parameter tmp_2m --date 2020-07-22
./task.py local.spatialmos.py-spatialmos--prediction --parameter rh_2m --date 2020-07-22
./task.py local.spatialmos.py-spatialmos--prediction --parameter wind_10m --date 2020-07-22
```

The calculated predictions are available in the exchange folder `./data/spool`. The presentation of the data is made with the help of django. 


### Archive downloaded files

The downloaded files in the folders can be archived with `tar`. The archived files are located under `./data/archive`.

```
./task.py local.spatialmos.py-spatialmos--archive-available-data --folder gefs_forecast
./task.py local.spatialmos.py-spatialmos--archive-available-data --folder gefs_reforecast
./task.py local.spatialmos.py-spatialmos--archive-available-data --folder suedtirol
./task.py local.spatialmos.py-spatialmos--archive-available-data --folder uibk
./task.py local.spatialmos.py-spatialmos--archive-available-data --folder wetter_at
./task.py local.spatialmos.py-spatialmos--archive-available-data --folder zamg
```

### Source files and spatial climatologies exchange with the server

With the help of `rsync` and `scp` data can be exchanged between server and local computer. In the file `settings.json` the necessary settings are made.

The source files are synchronized using the fabric command:
```
./task.py production.rsync.push --what sourcefiles
```

The source files are synchronized using the fabric command:
```
./task.py production.rsync.push --what staticfiles
```

The climatologies needed for the daily calculation can be uploaded using the command:
```
./task.py production.rsync.push --what climatologies
```

### Website

The online presence was implemented with the web framework django written in python. The calculated predictions are stored in a PostgreSQL database. For each address in North- and South Tyrol, predictions can thus be made. The API of openstreetmap is used for the address query. *TODO*


#### TODO

```
./task.py *TODO* setenvironment
./task.py serve ... start ... quickinstall
```

#### Urls for local development

A web server is started and the project is accessible under the following URLS:

[http://localhost/](http://localhost/)

[http://localhost/admin](http://localhost/admin)



#### Data import from spool directory to PostgreSQL database

```
./task.py local.spatialmos.py-spatialmos--django-import-spatialmos-run --date 2020-07-22 --parameter tmp_2m
```


#### API Website interface 

The predictions can also be loaded as JSON data via the Api Rest interface.

[http://localhost/api/spatailmosrun/](http://localhost/api/spatailmosrun/)

[http://localhost/api/spatialmosrun/last/tmp_2m/](http://localhost/api/spatialmosrun/last/tmp_2m/)

[http://localhost/api/spatialmosstep/last/tmp_2m/](http://localhost/api/spatialmosstep/last/tmp_2m/)

[http://localhost/api/spatialmospoint/last/tmp_2m/47.26266/11.394/](http://localhost/api/spatialmospoint/last/tmp_2m/47.26266/11.394/)


#### Delete model runs from the PostgreSQL database

With this managing command model runs older than 5 days are removed from the database.

```
./task.py local.spatialmos.py-spatialmos--django-delete-spatialmos_runs --parameter tmp_2m --days 5
```


#### Live Demo

Visit the Live Demo Page for current forecasts for North and South Tyrol.

[https://moses.tirol](https://moses.tirol)


## Contribution

Please make sure to read the [Contributing Guide](./CONTRIBUTING.md) before making a pull request.



## Changelog

- 2020-08-10 Prettier Django docstrings and remarks.
- 2020-08-09 The Django website was put online on [moses.tirol](https://moses.tirol).
- 2020-08-05 Data in JSON format can be obtained from the API interface.
- 2020-07-30 Django was added to the project and tested locally.
- 2020-07-29 The new version was installed on the server. Daily two meter Temperature spatialMOS forecasts are now generated.
- 2020-07-28 The python dependencies gdal, basemap, pygrib and pyarrow caused problems. The prediction script was split and three docker containers were created
- 2020-07-22 The fabric commands for spatialMOS has been improved
- 2020-07-20 The codestyle embellishments were tested and merged
- 2020-07-19 Embellish codestyle with prettier
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
