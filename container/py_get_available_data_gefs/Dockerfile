FROM continuumio/anaconda3

ENV PYTHONUNBUFFERED 1

ADD ./requirements.txt .

RUN conda install -c conda-forge --file requirements.txt

WORKDIR /usr/src/app
