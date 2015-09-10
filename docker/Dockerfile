# based on a blog article of michal karzynski
# http://michal.karzynski.pl/blog/2015/04/19/packaging-django-applications-as-docker-container-images/

FROM debian:jessie

MAINTAINER Martin Schröder


# Set env variables used in this Dockerfile (add a unique prefix, such as DOCKYARD)
# Local directory with project source
ENV DOCKYARD_SRC=PyScadaServer
# Directory in container for all project files
ENV DOCKYARD_SRVHOME=/srv
# Directory in container for project source files
ENV DOCKYARD_SRVPROJ=/srv/PyScadaServer
#
ENV PYSCADA_VERSION 0.6.b12

# add the user to use
RUN adduser app_user --disabled-password


# install all packages
RUN apt-get update && apt-get install -y --no-install-recommends \
  python \
  python-mysqldb \
  python-pip \
  gunicorn \

RUN pip install mysqlclient django">=1.7,<1.8" pyscada=="$PYSCADA_VERSION"

FROM nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Create application subdirectories
WORKDIR $DOCKYARD_SRVHOME
RUN mkdir media static logs run
VOLUME ["$DOCKYARD_SRVHOME/media/", "$DOCKYARD_SRVHOME/logs/"]

# Copy application source code to SRCDIR
COPY $DOCKYARD_SRC $DOCKYARD_SRVPROJ

# Copy entrypoint script into the image
WORKDIR $DOCKYARD_SRVPROJ
COPY ./docker-entrypoint.sh /
RUN chmod u+x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

# open the http port
EXPOSE 80
