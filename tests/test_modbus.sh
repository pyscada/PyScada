#!/bin/bash

mkdir test
cd test
python3 -m virtualenv ./.env
source ./.env/bin/activate

pip install ../../
pip install ../../../PyScada-Modbus/
pip install ../../../PyScada-Onewire/
pip install ../../../PyScada-Phant/
pip install ../../../PyScada-VISA/
pip install ../../../PyScada-SMBus/
pip install ../../../PyScada-SystemStat/

django-admin startproject PyScadaServer  --template ./../project_template_with_plugins_modbus.zip
cd PyScadaServer/
mkdir log
python3 manage.py migrate
python3 manage.py collectstatic
python3 manage.py loaddata color
python3 manage.py loaddata units
python3 manage.py pyscada_daemon init
export DJANGO_SUPERUSER_PASSWORD="test"
python3 manage.py createsuperuser --username pyscada --email pyscada@pyscada.org --noinput
