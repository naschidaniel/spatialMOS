FROM python:buster AS base

ENV PYTHONUNBUFFERED 1

WORKDIR /www/site

COPY ./requirements.txt /www/site/requirements.txt

RUN pip install --no-cache-dir -r /www/site/requirements.txt

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE "spatialmos.settings"

# PRODUCTION
FROM base as production

RUN pip install gunicorn

CMD gunicorn -u 1001 -c /www/site/gunicorn_config.py spatialmos.wsgi


# DEVELOPMENT
FROM base as development

CMD uvicorn --reload --host 0.0.0.0 spatialmos.asgi:application