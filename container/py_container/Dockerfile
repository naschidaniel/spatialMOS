FROM ubuntu:focal

ENV PYTHONUNBUFFERED 1

ENV TZ=Europe/Berlin

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update

RUN apt-get install software-properties-common -y

RUN add-apt-repository ppa:ubuntugis/ppa -y

RUN apt-get update

RUN apt-get install gdal-bin -y

RUN apt-get install libgdal-dev -y

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal

ENV C_INCLUDE_PATH=/usr/include/gdal

#RUN add-apt-repository ppa:deadsnakes/ppa -y

RUN apt-get update

#RUN apt install python3.9 -y

RUN apt-get install python3-dev -y

RUN apt install python3-distutils -y

RUN apt-get install curl gdal-bin libeccodes0 libgdal-dev libproj-dev proj-bin proj-data libgeos-dev -y

RUN apt-get install libgeos++-dev -y

RUN apt-get install libproj-dev -y

RUN apt install build-essential -y

RUN apt-get clean all

RUN apt-get update

RUN ln -sf /usr/bin/python3 /usr/bin/python

WORKDIR /usr/src/app

COPY . /usr/src/app/

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

RUN python get-pip.py

RUN pip3 --version

RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt

RUN apt-get install python3-dev -y

RUN apt-get install python3-cartopy -y

RUN pip3 install osgeo

RUN pip3 install gdal