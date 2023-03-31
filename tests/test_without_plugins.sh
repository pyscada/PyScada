#!/bin/bash

mkdir test
cd test
python3 -m virtualenv ./.env
source ./.env/bin/activate

pip install ../../

django-admin startproject PyScadaServer  --template ./../project_template_stand-alone.zip
cd PyScadaServer/
mkdir log
python3 manage.py migrate
python3 manage.py collectstatic
python3 manage.py loaddata color
python3 manage.py loaddata units
python3 manage.py pyscada_daemon init
export DJANGO_SUPERUSER_PASSWORD="test"
python3 manage.py createsuperuser --username pyscada --email pyscada@pyscada.org --noinput
python3 manage.py runserver --insecure
deactivate
cd ../../
rm -rf test
