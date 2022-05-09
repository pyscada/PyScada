FROM python:3.6
LABEL maintainer="PyScada | Martin Schröder"
ENV DEBIAN_FRONTEND noninteractive

#RUN apt-get -y update && \
#    apt-get -y upgrade && \
#    apt-get -y install python3-mysqldb libmysqlclient-dev && \
#    apt-get purge && \
#    apt-get clean && \
#    rm -rf /var/lib/apt/lists/*

ENV LANG C.UTF-8

COPY project_template.zip /src/pyscada/
COPY pyscada /src/pyscada/
COPY pyscada_init /src/pyscada/
WORKDIR /src/pyscada

RUN pip3 install gunicorn
RUN pip3 install mysqlclient
RUN pip3 install https://github.com/pyscada/PyScada/tarball/master
RUN django-admin startproject PyScadaServer /src/pyscada/ --template /src/pyscada/project_template.zip
RUN chmod +x /src/pyscada/pyscada
RUN chmod +x /src/pyscada/pyscada_init
CMD ["/src/pyscada/pyscada"]