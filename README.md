![[maturin]](https://github.com/naschidaniel/spatialmos/actions/workflows/maturin.yml/badge.svg?name=maturin) 
![[mypy]](https://github.com/naschidaniel/spatialmos/actions/workflows/mypy.yml/badge.svg?name=mypy) 
![[rsaudit]](https://github.com/naschidaniel/spatialmos/actions/workflows/rsaudit.yml/badge.svg?name=rsaudit) 
![[rstest]](https://github.com/naschidaniel/spatialmos/actions/workflows/rstest.yml/badge.svg?name=rstest)
![[build webpage]](https://github.com/naschidaniel/spatialmos/actions/workflows/website.yml/badge.svg?name=website)

# spatialMOS

spatialMOS is currently being completely redesigned. In section [CHANGELOG](#CHANGELOG) the already implemented program parts and functionalities are listed. The website is available online again and can be reached at [https://moses.tirol](https://moses.tirol).

## Warning
Since 2020-09-23, the GEFS 1 x 1 ° predictions are no longer provided on the Files Server of [noaa ncep](https://www.ftp.ncep.noaa.gov/). Since then it is no longer possible to post-process the 1 x 1 ° predictions. The 0.5 x 0.5 ° GEFS forecasts are now used for the predictions. The underlying climatology still corresponds to the 1 x 1 ° grid.


## Introduction
With spatialMOS weather forecasts of the global weather model GEFS (1 x 1° Grid) can be improved for the regions North- and South Tyrol. Based on past station observations and past predictions, future predictions are post-processed with statistical methods. 
The spatial resolution of the statistically post-processed predictions corresponds to the grid of the SRTM Data (Further information can be obtained from [https://gadm.org](https://gadm.org)). The resolution of the spatial post-processed forecasts is 90 x 90 m. With spatialMOS temperature, relative humidity and wind forecasts can be made at ground level.

A detailed description of the statistical method to correct spatial predictions at ground level can be found in the master these [Flächenhafte Vorhersagen von Temperatur und relativer Luftfeuchte im Flachland](http://diglib.uibk.ac.at/urn:nbn:at:at-ubi:1-16130).

## Dependencies
You will need [python](https://www.python.org/) **version 3.7+**, [invoke](http://www.pyinvoke.org/installing.html) **version 1.4+**, [docker](https://www.docker.com/), [docker-compose](https://docs.docker.com/compose/), [rsync](https://rsync.samba.org/) and [tar](https://www.gnu.org/software/tar/).


## Usage
A list for spatialMOS implemented invoke commands: 

```
./task.py
```


## Configuration and Installation
Copy the `fabric/settings.example.json` to `./settings.json` and adapt the file to your individual needs. Two environments are provided in the file: `development` and `production`. For local development, only the dictionary `development` must be edited. The `production` dictionary entries are optional and only relevant for the server.

To install spatialMOS, the necessary folder structures and to set the environment variables the following command can be used:

```
./task.py local.install.quickinstallation
./task.py local.install.createsuperuser
./task.py local.install.loadexampledata
```

### Data basis

***For statistical post-processing of weather forecasts, past values of at least two years are required.***


#### Digital Ground Model and Shapefiles for North- and South Tyrol

The required shapefiles are prepared for further processing with the help of the R libraries rgdal and raster. For the topography the GADM topography of North and South Tyrol is used. For the predictions, which are generated in python, the required [GADM](https://gadm.org/) files are downloaded and unpacked using unzip. The will be downloaded from the website  and stored in folder `./data/get_available_data/gadm`. 

```
./task.py local.spatialmos.spatialmos--init-topography
```

#### Meteorological station values
Past measured values are obtained via the API interfaces of [http://wetter.provinz.bz.it/](http://wetter.provinz.bz.it/).

```
./task.py local.spatialmos.py-spatialmos--get-suedtirol --begindate 2018-01-01 --enddate 2019-12-31
```

Current values from the ZAMG web page, from lwd, or from the UIBK API interface can be done with the two fabric commands.

```
./task.py local.spatialmos.py-spatialmos--get-lwd
./task.py local.spatialmos.py-spatialmos--get-zamg
```


#### GEFS Weather Reforecasts (Forecast Archive)

Previous mean and spread ensemble forecasts of the GEFS weather model can be downloaded free of charge from a FTP of the [NOAA](https://weather.gov) in a resolution of 1° x 1°. To load the data the program [retostauffer/PyGFSV2](https://github.com/retostauffer/PyGFSV2) is required.
A forked version can be downloaded under [naschidaniel/PyGFSV2](https://github.com/naschidaniel/PyGFSV2). With `sh GFSV2_bulk.sh` the archive GEFS Reforecasts can be downloaded. The program creates folders based on the year numbers. These folders can be stored directly in `./data/get_available_data/gefs_reforecast/nwp` for further statistical processing. 


#### GEFS Weather Forecasts

Current Ensemble weather forecasts can be obtained from the a FTP of the [NOAA](https://weather.gov) server. Please use today's date. The downloaded files are automatically pre-processed for the prediction task.

```
./task.py local.spatialmos.py-spatialmos--get-gefs-forecasts --date 2020-07-03 --parameter tmp_2m 
./task.py local.spatialmos.py-spatialmos--get-gefs-forecasts --date 2020-07-03 --parameter rh_2m 
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
# Required pre calculated parameters: tmp_2m, spfh_2m, pres_sfc
./task.py local.spatialmos.py-spatialmos--pre-processing-reforecasts --parameter rh_2m 

# Required pre calculated parameters: ugrd_10m, vgrd_10m
./task.py local.spatialmos.py-spatialmos--pre-processing-reforecasts --parameter wind_10m 
```


#### Combination of GEFS Reforecasts and Station Observations

For further statistical processing a data set with past station observations and past forecasts for at least two years are required. All values are stored in one h5 data set file.

```
./task.py local.spatialmos.py-spatialmos--pre-processing-observations-and-reforecasts-to-stations
```

#### Pre Processing for further statistical calculations

The observations and the GEFS Reforecasts still need to be pre-processed. The observations and the GEFS Reforecasts will be combined. From these files the area-wide valid climatologies are generated.

```
./task.py local.spatialmos.py-spatialmos--pre-processing-gamlss-crch-climatologies --parameter tmp_2m
./task.py local.spatialmos.py-spatialmos--pre-processing-gamlss-crch-climatologies --parameter rh_2m
```

### Statistical processing for spatial of the spatially valid climatologies


#### Climatologies for the daily calculation of forecasts

Based on the pre processed data and the modelling software [gamlss](http://www.gamlss.com/), climatologies for the forecast area are created. 

```
./task.py local.spatialmos.r-spatialmos--gamlss-crch-model --validation False --parameter tmp_2m
./task.py local.spatialmos.r-spatialmos--gamlss-crch-model --validation False --parameter rh_2m
```

#### Create daily climatologies for post processing of GEFS forecasts

For the statistical processing of the Direct Model Output, climatologies for the relevant day and model step must be created. 

##### GEFS Forecast climatologies for the day of the year and model step 
```
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-nwp --begin 192 --end 195 --parameter tmp_2m 
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-nwp --begin 192 --end 195 --parameter rh_2m
```

##### Observation climatologies for the day
```
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-obs --begin 192 --end 195 --parameter tmp_2m
./task.py local.spatialmos.r-spatialmos--spatial-climatologies-obs --begin 192 --end 195 --parameter rh_2m
```


### Statistically corrected weather forecasts

The current forecasts and the climatologies created are used to produce corrected weather forecasts for temperature, relative humidity and wind. 

For this step, current forecasts ([GEFS Weather Forecasts](#GEFS-Weather-Forecasts)) and calculated climatologies ([Create daily climatologies for post processing of GEFS forecasts](#Create-daily-climatologies-for-post-processing-of-GEFS-forecasts)) must be available.


```
./task.py local.spatialmos.py-spatialmos--prediction --date 2020-07-22 --parameter tmp_2m 
./task.py local.spatialmos.py-spatialmos--prediction --date 2020-07-22 --parameter rh_2m
```

The calculated predictions are available in the exchange folder `./data/spool`. The presentation of the data is made with the help of django. 


### Archive downloaded files

The downloaded files in the folders can be archived with `tar`. The archived files are located under `./data/archive`.

```
./task.py local.spatialmos.py-spatialmos--archive-available-data --folder gefs_avgspr_forecast_p05
./task.py local.spatialmos.py-spatialmos--archive-available-data --folder lwd
./task.py local.spatialmos.py-spatialmos--archive-available-data --folder suedtirol
./task.py local.spatialmos.py-spatialmos--archive-available-data --folder zamg
```

### Website

The online presence was implemented with the web framework [https://www.djangoproject.com/](django) written in python. The calculated predictions are stored in a PostgreSQL database. For each address in North- and South Tyrol, predictions can thus be made.

#### Start and Stop a local development Webserver

A web server can be started or stopped in dedatched modus for the local test environment.

```
./task.py local.docker-compose.start

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


#### Predictions for addresses and coordinates

For the prediction of addresses and coordinates in North- and South Tyrol the API interface of [nominatim.openstreetmap.org](https://nominatim.openstreetmap.org) is used. The [github.com/osm-search/Nominatim](https://github.com/osm-search/Nominatim) is licensed under [GPLv2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html).



#### Live Demo

Visit the Live Demo Page [https://moses.tirol](https://moses.tirol) for current forecasts for North and South Tyrol. 




### Deployment

### Source files and spatial climatologies exchange with the server

With the help of `rsync` and `scp` data can be exchanged between server and local computer. In the file `settings.json` the necessary settings are made.

The files are synchronized using the fabric command:

```
./task.py deploy
```

The precalculated climatologies can be uploaded using the following fabric command:

```
./task.py rsync.push-climatologies
```


## Generate Climatologies for R GAMLSS

```
./task.py combine-data --folder lwd
./task.py combine-data --folder suedtirol
./task.py combine-data --folder zamg
./task.py combine-measurements
./task.py interpolate-gribfiles --parameter tmp_2m
./task.py interpolate-gribfiles --parameter rh_2m
./task.py combine_gamlss_climatology --parameter tmp_2m
./task.py combine_gamlss_climatology --parameter rh_2m
```

## Contribution

Please make sure to read the [Contributing Guide](./CONTRIBUTING.md) before making a pull request.


## Station- and forecast data
* [Land Tirol - data.tirol.gv.at](https://www.data.gv.at/katalog/dataset/bb43170b-30fb-48aa-893f-51c60d27056f)
* [noaa ncep](https://www.ftp.ncep.noaa.gov/)
* [South Tyrolean weather service](http://wetter.provinz.bz.it/)
* [ZAMG](https://www.zamg.ac.at/)

## License

[GPL-3.0](./LICENSE)

Copyright (c) 2019-present, Daniel Naschberger
