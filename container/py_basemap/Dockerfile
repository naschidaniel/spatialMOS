FROM continuumio/anaconda3

ENV PYTHONUNBUFFERED 1

ENV TZ=Europe/Berlin

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /usr/src/app

RUN conda update conda

RUN conda config --set channel_priority strict

RUN conda create -n spatialmos -c conda-forge python

ADD requirements.txt /usr/src/app/requirements.txt

RUN conda install -n spatialmos -c conda-forge --file /usr/src/app/requirements.txt

RUN conda init bash

RUN echo "source activate spatialmos" > ~/.bashrc

ENV PATH /opt/conda/envs/env/bin:$PATH