FROM python:3.7

ENV PYTHONUNBUFFERED 1

ENV TZ=Europe/Berlin

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update

RUN apt-get install -y libeccodes0

WORKDIR /usr/src/app

ADD ./requirements.txt .

RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

