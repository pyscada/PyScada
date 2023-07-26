#!/bin/bash
sudo python3 /var/www/pyscada/PyScadaServer/manage.py collectstatic --no-input --clear
sudo systemctl restart gunicorn
sudo systemctl restart pyscada
