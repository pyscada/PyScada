# based on a blog article of Arnab Kumar Shil(Ruddra)
# http://ruddra.com/2016/08/14/docker-django-nginx-postgres/

FROM python:2
ENV PYTHONUNBUFFERED 1
RUN mkdir /config
ADD /config/requirements.pip /config/
RUN pip install -r /config/requirements.pip
RUN pip install https://github.com/trombastic/PyScada/archive/dev/0.7.x.zip
RUN mkdir /src
RUN mkdir /http
ADD /src/ /src
WORKDIR /src
MAINTAINER Martin Schröder
