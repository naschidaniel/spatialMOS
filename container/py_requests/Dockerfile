FROM python:3.7-buster

ENV PYTHONUNBUFFERED 1

ENV TZ=Europe/Berlin

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip3 install --no-cache-dir -r /usr/src/app/requirements.txt
