#!/bin/bash

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

INSTALL_ROOT=/var/www/pyscada

# todo : add inputs for mysql root pwd, db name, username, user pwd

function validate_url(){
  if [[ `wget_proxy -S --spider $1  2>&1 | grep 'HTTP/1.1 200 OK'` ]]; then
    return 0
  else
    return 1
  fi
}

function add_line_if_not_exist(){
  grep -qF "$1" "$2"  || echo "$1" | tee --append "$2"
}

function pip3_proxy(){
  if [[ "$answer_proxy" == "n" ]]; then
    pip3 $*
  else
    echo "pip3 using" $answer_proxy "for" $* > /dev/tty
    pip3 --proxy=$answer_proxy $*
  fi
}

function pip3_proxy_not_rust(){
  if [[ "$answer_proxy" == "n" ]]; then
    CRYPTOGRAPHY_DONT_BUILD_RUST=1 pip3 install cryptography==3.4.6 --no-cache-dir
    pip3 $*
  else
    echo "pip3 using" $answer_proxy "for" $* > /dev/tty
    CRYPTOGRAPHY_DONT_BUILD_RUST=1 pip3 --proxy=$answer_proxy install cryptography==3.4.6 --no-cache-dir
    pip3 --proxy=$answer_proxy $*
  fi
}

function apt_proxy(){
  if [[ "$answer_proxy" == "n" ]]; then
    apt-get $*
  else
    echo "apt using" $answer_proxy "for" $* > /dev/tty
    export http_proxy=$answer_proxy
    apt-get $*
    unset http_proxy
  fi
}

function wget_proxy(){
  if [[ "$answer_proxy" == "n" ]]; then
    echo "wget no proxy" $* > /dev/tty
    wget --no-proxy $*
  else
    echo "wget using" $answer_proxy "for" $* > /dev/tty
    http_proxy=$answer_proxy https_proxy=$answer_proxy ftp_proxy=$answer_proxy wget $*
  fi
}

echo 'date :'
echo $(date)
read -p "Is the date and time correct ? [y/n]: " answer_date
if [[ "$answer_date" == "n" ]]; then
  echo "please set the date correctly"
  exit 1
fi

read -p "Use proxy ? [http://proxy:port or n]: " answer_proxy
if [[ "answer_proxy" == "" ]]; then
  echo "please select 'n' or enter a valid proxy"
  exit 1
fi

apt_proxy install -y python3-pip
echo 'Some python3 packages installed:'
pip3 list | grep -i -E 'pyscada|channels|asgiref'

read -p "Update only (don't create db, user, copy services, settings and urls...) ? [y/n]: " answer_update
read -p "Install channels and redis ? [y/n]: " answer_channels

if [[ "$answer_update" == "n" ]]; then
  read -p "DB name ? [PyScada_db]: " answer_db_name
fi
if [[ "$answer_db_name" == "" ]]; then
  answer_db_name="PyScada_db"
fi
echo $answer_db_name

echo "Stopping PyScada"
systemctl stop pyscada gunicorn gunicorn.socket
sleep 1 # Give systemd time to shutdown
systemctl --quiet is-active pyscada
if [ $? == 0 ] ; then
    echo "Can't stop pyscada systemd service. Aborting." > /dev/stderr
    exit 1
fi
echo "PyScada stopped"

# Install prerequisites
DEB_TO_INSTALL="
	libatlas-base-dev
	libffi-dev
	libhdf5-103
	libhdf5-dev
	libjpeg-dev
	libmariadb-dev
	libopenjp2-7
	mariadb-server
	nginx
	python3-dev
	python3-mysqldb
	python3-pip
	zlib1g-dev
"
apt_proxy install -y $DEB_TO_INSTALL

PIP_TO_INSTALL="
	cffi
	Cython
	docutils
	gunicorn
	lxml
	mysqlclient
	numpy
"
pip3_proxy install --upgrade $PIP_TO_INSTALL

# Install PyScada
pip3_proxy install --upgrade .


if [[ "$answer_channels" == "y" ]]; then
  apt_proxy -y install redis-server
  if grep -R "Raspberry Pi 3"  "/proc/device-tree/model" ; then
    echo "Don't install Rust for RPI3"
    pip3_proxy_not_rust install --upgrade channels channels-redis asgiref
  else
    pip3_proxy install --upgrade cryptography==3.4.6 channels channels-redis asgiref
  fi
fi

log_file_dir="/var/log/pyscada/"

if [[ "$answer_update" == "n" ]]; then
  # Create pyscada user
  echo "Creating system user pyscada..."
  useradd -r pyscada
  mkdir -p /home/pyscada
  chown -R pyscada:pyscada /home/pyscada
  mkdir -p $INSTALL_ROOT/http
  chown -R pyscada:pyscada $INSTALL_ROOT

  touch ${log_file_dir}pyscada_{daemon,debug}.log
  chown pyscada:pyscada ${log_file_dir}pyscada_{daemon,debug}.log

  # Add rights for usb, i2c and serial
  add_line_if_not_exist 'SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", MODE="0664", GROUP="pyscada"' /etc/udev/rules.d/10-usb.rules
  add_line_if_not_exist 'KERNEL=="ttyS[0-9]", GROUP="dialout", MODE="0777"' /etc/udev/rules.d/10-usb.rules
  adduser www-data pyscada
  adduser pyscada dialout
  adduser pyscada i2c
fi

SERVER_ROOT=$INSTALL_ROOT/PyScadaServer
answer_db_user="PyScada-user"
answer_db_password="PyScada-user-password"
if [[ "$answer_update" == "n" ]]; then
    # Create DB
    mysql <<-EOF
	CREATE DATABASE IF NOT EXISTS ${answer_db_name}
		CHARACTER SET utf8;
	GRANT ALL PRIVILEGES ON ${answer_db_name}.*
		TO '${answer_db_user}'@'localhost'
		IDENTIFIED BY '${answer_db_password}';
EOF

# add db infor to django template 
mkdir ./tests/project_template_tmp
cp -r ./tests/project_template/* ./tests/project_template_tmp/
python3 <<-EOF
import django
from django.conf import settings
from django.template.loader import render_to_string

settings.configure(
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['./'],  # script dir
	'OPTIONS': {'string_if_invalid': '{{ %s }}'}, # prevents the other template tags to be replaced by ''
    }]
)

django.setup()
from django.template import Template, Context
with open("./tests/project_template_tmp/project_name/settings.py-tpl", "r+") as f:
    template = Template(f.read())
    context = Context({
                   "db_name": "${answer_db_name}",
                   "db_user": "${answer_db_user}",
                   "db_password": "${answer_db_password}",
                   "project_root": "${INSTALL_ROOT}",
                   "log_file_dir": "${log_file_dir}",
                   "additional_apps": "",
                   "additional_settings": "",
	           })
    f.seek(0)
    f.write(template.render(context))
    f.truncate()
EOF

    sudo -u pyscada mkdir -p $SERVER_ROOT
    sudo -u pyscada django-admin startproject PyScadaServer $SERVER_ROOT --template ./tests/project_template_tmp

fi

(
    cd $SERVER_ROOT
    # Migration and static files
    sudo -u pyscada python3 manage.py migrate
    sudo -u pyscada python3 manage.py collectstatic --noinput

    # Load fixtures with default configuration for chart lin colors and units
    sudo -u pyscada python3 manage.py loaddata color
    sudo -u pyscada python3 manage.py loaddata units

    # Initialize the background service system of pyscada
    sudo -u pyscada python3 manage.py pyscada_daemon init
)

if [[ "$answer_update" == "n" ]]; then
    (
	cd $SERVER_ROOT
	python3 manage.py shell <<-EOF
try:
  from django.contrib.auth import get_user_model
  from django.db.utils import IntegrityError
  User = get_user_model()
  User.objects.create_superuser('pyscada',
                                'team@pyscada.org',
                                'password')
except IntegrityError:
  print('User pyscada already exist')
EOF
    )
    # Nginx
    cp extras/nginx_sample.conf /etc/nginx/sites-available/pyscada.conf
    ln -sf ../sites-available/pyscada.conf /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    mkdir -p /etc/nginx/ssl
    # the certificate will be valid for 5 Years,
    openssl req -x509 -nodes -days 1780 -newkey rsa:2048 -keyout /etc/nginx/ssl/pyscada_server.key -out /etc/nginx/ssl/pyscada_server.crt -subj '/CN=www.mydom.com/O=My Company Name LTD./C=US'
    systemctl enable nginx.service # enable autostart on boot
    systemctl restart nginx

    # Gunicorn and PyScada as systemd units
    cp extras/service/systemd/{gunicorn.{socket,service},pyscada_daemon.service} /etc/systemd/system
    # Rename PyScada service file
    mv /etc/systemd/system/pyscada_daemon.service /etc/systemd/system/pyscada.service

    # Fix if gunicorn installed in /usr/bin and not /usr/local/bin -> create symbolic link
    if [[ $(which gunicorn) != /usr/local/bin/gunicorn ]] && [[ ! -f /usr/local/bin/gunicorn ]] && [[ -f /usr/bin/gunicorn ]]; then
        echo "Creating symcolic link to gunicorn";
        ln -s /usr/bin/gunicorn /usr/local/bin/gunicorn;
    fi
fi

# enable the services for autostart
systemctl enable gunicorn
systemctl restart gunicorn
systemctl enable pyscada
systemctl restart pyscada
sleep 1
systemctl --quiet is-active pyscada
if [ $? != 0 ] ; then
    echo "Can't start pyscada systemd service." > /dev/stderr
    exit 1
fi

if [[ "$answer_update" == "n" ]]; then
  echo "PyScada installed"
  echo "Connect to http://127.0.0.1 using :"
  echo "username : pyscada"
  echo "password : password"
else
  echo "PyScada updated"
fi
