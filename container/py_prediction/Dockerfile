FROM continuumio/anaconda3

ENV PYTHONUNBUFFERED 1

ENV TZ=Europe/Berlin

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update -y

RUN apt-get install gdal-bin libgdal-dev libproj-dev proj-bin -y

RUN apt-get clean all

ADD ./requirements.txt .

RUN conda config --set allow_conda_downgrades true

RUN conda create -n spatialmos python=3.6 

RUN conda init bash

RUN conda install -n spatialmos -c conda-forge --file requirements.txt

WORKDIR /usr/src/app

RUN echo "source activate spatialmos" > ~/.bashrc

ENV PATH /opt/conda/envs/env/bin:$PATH