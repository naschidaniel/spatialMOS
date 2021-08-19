FROM python:3.9-buster

ENV PYTHONUNBUFFERED 1

ENV TZ=Europe/Berlin

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update

RUN apt-get install gdal-bin libeccodes0 libgdal-dev libproj-dev proj-bin proj-data libgeos-dev -y

RUN apt-get clean all

WORKDIR /usr/src/app

COPY . /usr/src/app/

RUN python -m pip install --upgrade pip

RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt

RUN pip3 install cartopy
