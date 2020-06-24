FROM continuumio/anaconda3

ENV PYTHONUNBUFFERED 1

ENV TZ=Europe/Berlin

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ADD ./requirements.txt .

RUN conda install -c conda-forge --file requirements.txt

WORKDIR /usr/src/app
