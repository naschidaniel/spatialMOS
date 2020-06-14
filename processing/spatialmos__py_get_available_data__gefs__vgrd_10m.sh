#!/bin/bash
#$ -cwd
#$ -M daniel@naschi.at

INSTALLFOLDER=$(grep INSTALLFOLDER .env | cut -d '=' -f 2-)
HOST=$(grep HOST .env | cut -d '=' -f 2-)
d=`date +%Y-%m-%d`
parameter='vgrd_10m'


# - Starting the job here
cd $INSTALLFOLDER
./task.py $HOST.spatialmos.py-get-available-data--gefs "--date $d --runhour 0 --parameter $parameter --avgspr avg"
./task.py $HOST.spatialmos.py-get-available-data--gefs "--date $d --runhour 0 --parameter $parameter --avgspr spr"
