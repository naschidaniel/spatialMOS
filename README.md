# spatialMOSv2

A Live Perview about the current development status of the repository can be viewed at [http://moses.tirol](http://moses.tirol)

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
Past measured values are obtained via the API interfaces of [http://at-wetter.tk/](http://at-wetter.tk/) and [http://wetter.provinz.bz.it/](http://wetter.provinz.bz.it/).

```
./task.py *TODO*
```

Current values from the ZAMG web page as well as from the UIBK API interface can be done with the two program calls.

```
./task.py production.spatialmos.py-get-available-data--uibk
./task.py production.spatialmos.py-get-available-data--zamg
```


#### GEFS Weather Forecast Archive

Previous mean and spread ensemble forecasts of the GEFS weather model can be downloaded free of charge from the FTP in a resolution of 1° x 1°. To load the data the program [PyGFSV2](https://github.com/retostauffer/PyGFSV2) is required.

The data is stored in order *TODO*.


#### GEFS Weather Forecasts

Current Ensemble weather forecasts can be obtained from the FTP server. Please use today's date

```
./task.py production.spatialmos.py-get-available-data--gefs "--date 2020-06-18 --runhour 0 --parameter tmp_2m --avgspr avg"
./task.py production.spatialmos.py-get-available-data--gefs "--date 2020-06-18 --runhour 0 --parameter tmp_2m --avgspr spr"
./task.py production.spatialmos.py-get-available-data--gefs "--date 2020-06-18 --runhour 0 --parameter rh_2m --avgspr avg"
./task.py production.spatialmos.py-get-available-data--gefs "--date 2020-06-18 --runhour 0 --parameter rh_2m --avgspr spr"
./task.py production.spatialmos.py-get-available-data--gefs "--date 2020-06-18 --runhour 0 --parameter vgrd_10m --avgspr avg"
./task.py production.spatialmos.py-get-available-data--gefs "--date 2020-06-18 --runhour 0 --parameter vgrd_10m --avgspr spr"
./task.py production.spatialmos.py-get-available-data--gefs "--date 2020-06-18 --runhour 0 --parameter ugrd_10m --avgspr avg"
./task.py production.spatialmos.py-get-available-data--gefs "--date 2020-06-18 --runhour 0 --parameter ugrd10m --avgspr spr"
```


#### GEFS Weather Forecast Archive

Previous mean and spread ensemble forecasts of the GEFS weather model can be downloaded free of charge from the FTP in a resolution of 1° x 1°. To load the data the program [PyGFSV2](https://github.com/retostauffer/PyGFSV2) is required.

The data is stored in order *TODO*.


### Raw data processing for further statistical processing

Based on the raw data and the modelling software [gamlss](http://www.gamlss.com/), climatologies for the forecast area are created. The raw data must be converted into a general format for this purpose.

```
.\task.py *TODO*
```


### Climatologies for the daily calculation of forecasts

The required daily climatologies are created with the statistics software R.

```
.\task.py *TODO*
```

### Statistically corrected weather forecasts
The current forecasts and the climatologies created are used to produce corrected weather forecasts for temperature, relative humidity and wind. 

```
.\task.py *TODO*
```

The calculated predictions are available in the exchange folder spool. A provision of the data is done via the framework python django.


### Website

The online presence was implemented with the web framework django from python. The calculated predictions are stored in a PostgreSQL database. For each address in Tyrol, predictions can thus be made. The API of openstreetmap is used for the address query.

#### Data import from spool directory to PostgreSQL database

```
.\task.py *TODO*
```

#### Live Demo

Visit the Live Demo Page for current forecasts for North and South Tyrol.

[http://moses.tirol](http://moses.tirol)


## Contribution

Please make sure to read the [Contributing Guide](./CONTRIBUTING.md) before making a pull request.



## Changelog

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
