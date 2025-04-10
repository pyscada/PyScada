#!/bin/bash

# todo : add inputs for django admin name, password

# check if the script is run from script directory
SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

if [[ "$DIR" != "$PWD" ]]; then
  echo "You must run this script from $DIR"
  exit 1
fi

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root"
  exit 1
fi


# PATHS CONST
INSTALL_ROOT=/var/www/pyscada # files will be installed here
log_file_dir="/var/log/pyscada/" # log files will be here
SERVER_ROOT=$INSTALL_ROOT/PyScadaServer # django project root
pyscada_home=/home/pyscada
pyscada_venv=$pyscada_home/.venv

# VAR
answer_date=""            # Is the date correct
answer_proxy=""           # Setup of proxy
answer_config=""          # Will it be install on docker or on venv

answer_db_name=""         # Name of the database
answer_db_user=""         # Username for the database (not the root)
answer_db_password=""     # Password for the database (not the root)

answer_channels=""        # Install or not channels and redis
answer_update=""          # The installation is just an update or not
answer_auto_add_apps=""   # Auto add apps or manual add (in django configuration)

answer_admin_name=""      # admin name (for errors output)
answer_admin_mail=""      # admin mail (for errors output)

answer_web_name=""        # web interface admin name
answer_web_password=""    # web interface admin password

echo -e "\nPyScada python packages will be installed in the virtual environment $pyscada_venv"

function debug(){
  message=$1
  echo ""
  echo $message 1>&2
  echo ""
}

# called in questions_setup
function regex_proxy(){
  echo "regex_proxy" 1>&2
  regex='^(https?|ftp)://[0-9a-zA-Z.-]+:[0-9]+$';
  while true; do
    read -p "Use proxy? [http://proxy:port or n]: " answer_proxy
    if [[ $answer_proxy == "n" || $answer_proxy =~ $regex ]]; then
      break
    else
      echo "Choose a valid proxy"
    fi
  done
  echo "regex_proxy end" 1>&2
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

# called in questions_clean_inst_setup
function regex_mail(){
  debug "regex_mail"

  regex='^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$';
  while true; do
    read -p "admin mail ? " answer_admin_mail
    if [[ $answer_admin_mail =~ $regex ]]; then
      break
    else
      echo "Choose a valid mail"
    fi
  done

  debug "regex_mail end"
}

# called in questions_clean_inst_setup
function admin_name_setup(){
  debug "admin_name_setup"

  while true; do
    read -p "admin name ? " answer_admin_name
    if [[ "$answer_admin_name" == "" ]]; then
      echo "Choose a valid name"
    else
      break
    fi
  done

  debug "admin_name_setup end"
}

# called in questions_setup
function questions_clean_install_setup(){
  debug "questions_clean_install_setup"

  read -p "DB name ? [PyScada_db]: " answer_db_name
  read -p "DB user ? [PyScada-user]: " answer_db_user
  read -sp "DB password ? [PyScada-user-password]: " answer_db_password
  echo ""

  admin_name_setup
  regex_mail
  project_admins=$(echo "('${answer_admin_name}', '${answer_admin_mail}' )")
  echo $project_admins
  echo $answer_db_name

  read -p "web interface admin name [pyscada]: " answer_web_name
  read -p "web interface admin password [password]: " answer_web_password

  if [[ "$answer_db_name" == "" ]]; then
    answer_db_name="PyScada_db"
  fi
  if [[ "$answer_db_user" == "" ]]; then
    answer_db_user="PyScada-user"
  fi
  if [[ "$answer_db_password" == "" ]]; then
    answer_db_password="PyScada-user-password"
  fi

  if [[ "$answer_web_name" == "" ]]; then
    answer_web_name="pyscada"
  fi
  if [[ "$answer_web_password" == "" ]]; then
    answer_web_password="password"
  fi

  while true; do
    read -p "Auto load pyscada plugins installed ? If False, you need to edit the settings.py file manually to load a plugin. [True/False]: " answer_auto_add_apps
    if [[ "$answer_auto_add_apps" == "True" ]]; then
      echo 'You need to restart pyscada and gunicorn after (un)installing any pyscada plugin.'
      break;
    elif [[ "$answer_auto_add_apps" == "False" ]]; then
      echo 'You need manually add a plugin to the django project settings and restart pyscada and gunicorn after (un)installing any pyscada plugin.'
      break;
    else
      echo "Please answer True or False."
    fi
  done

  debug "questions_clean_install_setup end"
}

# called in the core of the script
function questions_setup(){
  debug "questions_setup"

  # Date verification
  echo 'date :'
  echo $(date)
  read -p "Is the date and time correct ? [y/n]: " answer_date
  if [[ "$answer_date" != "y" ]]; then
    echo "please set the date correctly or enter 'y'"
    exit 1
  fi

  # Proxy setup
  regex_proxy

  # Channels and redis
  read -p "Install channels and redis to speed up inter pyscada process communications ? [y/n]: " answer_channels

  # Clean installation or not
  while true; do
    read -p "Update only : if 'y' it will not create DB, superuser, copy services, settings and urls... On a fresh install you should answer 'n' ? [y/n]: " answer_update
    if [[ "$answer_update" == "y" ]]; then
      break
    elif [[ "$answer_update" == "n" ]]; then
      break
    else
      echo "Please answer y or n."
    fi
  done

  if [[ "$answer_update" == "n" ]]; then
    questions_clean_install_setup
  fi

  debug "questions_setup end"
}

# called in the core of the script
function install_dependences(){
  debug "install_dependences"

  apt_proxy install -y python3-pip
  echo 'Some python3 packages installed:'
  # Install prerequisites
  DEB_TO_INSTALL="
    libatlas-base-dev
    libopenblas-dev
    libffi-dev
    libhdf5-dev
    libjpeg-dev
    libmariadb-dev
    libopenjp2-7
    mariadb-server
    nginx
    python3-dev
    python3-mysqldb
    python3-pip
    python3-venv
    zlib1g-dev
    pkg-config
  "
  apt_proxy install -y $DEB_TO_INSTALL

  # Create virtual environment
  sudo -u pyscada python3 -m venv $pyscada_venv
  # activate
  source $pyscada_venv/bin/activate

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

  debug "install_dependences end"
}

# called in pyscada_init
function web_setup(){
  debug "web_setup"

  (
    cd $SERVER_ROOT
  sudo -u pyscada -E env PATH=${PATH} python3 manage.py shell << EOF
try:
  from django.contrib.auth import get_user_model
  from django.db.utils import IntegrityError
  User = get_user_model()
  User.objects.create_superuser('$answer_web_name',
                                'team@pyscada.org',
                                '$answer_web_password')
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
      echo "Creating symcolic link to gunicorn" ;
      ln -s /usr/bin/gunicorn /usr/local/bin/gunicorn;
  fi

  debug "web_setup end"
}

# called in the core of the script
function install_channel_redis(){
  debug "install_channel_redis"

  apt_proxy -y install redis-server
  if grep -R "Raspberry Pi 3"  "/proc/device-tree/model" ; then
    echo "Don't install Rust for RPI3"
    pip3_proxy_not_rust install --upgrade channels channels-redis asgiref
  else
    pip3_proxy install --upgrade cryptography==3.4.6 channels channels-redis asgiref
  fi

  debug "install_channel_redis end"
}

# called in the core of the script
function pyscada_init(){
  debug "pyscada_init"

  (
      cd $SERVER_ROOT
      # Migration and static files
      sudo -u pyscada -E env PATH=${PATH} python3 manage.py migrate
      sudo -u pyscada -E env PATH=${PATH} python3 manage.py collectstatic --noinput

      # Load fixtures with default configuration for chart lin colors and units
      sudo -u pyscada -E env PATH=${PATH} python3 manage.py loaddata color
      sudo -u pyscada -E env PATH=${PATH} python3 manage.py loaddata units

      # Initialize the background service system of pyscada
      sudo -u pyscada -E env PATH=${PATH} python3 manage.py pyscada_daemon init
  )

  if [[ "$answer_update" == "n" ]]; then
    web_setup
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
    echo "username : $answer_web_name"
    echo "password : $answer_web_password"
  else
    echo "PyScada updated"
  fi

  debug "pyscada_init end"
}

# called in the core of the script
function db_setup(){
  debug "db_setup"

  # Create DB
  mysql << EOF
    CREATE DATABASE IF NOT EXISTS ${answer_db_name}
      CHARACTER SET utf8;
    GRANT ALL PRIVILEGES ON ${answer_db_name}.*
      TO '${answer_db_user}'@'localhost'
      IDENTIFIED BY '${answer_db_password}';
EOF

  debug "db_setup end"
}

#called in the core of the script
function template_setup(){
  debug "template_setup"

  # add db informations to django template
  rm -r ./tests/project_template_tmp/
  cp -r ./tests/project_template ./tests/project_template_tmp/
  chmod a+w ./tests/project_template_tmp/project_name/settings.py-tpl
  sudo -u pyscada -E env PATH=${PATH} python3 << EOF
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
                "pyscada_home": "${pyscada_home}",
                "log_file_dir": "${log_file_dir}",
                "project_admins": "${project_admins}",
                "auto_add_apps": "${answer_auto_add_apps}",
                "additional_apps": "",
                "additional_settings": "",
                })
  f.seek(0)
  f.write(template.render(context))
  f.truncate()
EOF

  sudo -u pyscada mkdir -p $SERVER_ROOT
  sudo -u pyscada -E env PATH=${PATH} django-admin startproject PyScadaServer $SERVER_ROOT --template ./tests/project_template_tmp
  rm -rf ./tests/project_template_tmp

  debug "template_setup end"
}

# called in the core of the script
function user_setup(){
  debug "user_setup"

  # Create pyscada user
  echo "Creating system user pyscada..."
  useradd -r pyscada
  mkdir -p $pyscada_home
  chown -R pyscada:pyscada $pyscada_home
  mkdir -p $INSTALL_ROOT
  chown -R pyscada:pyscada $INSTALL_ROOT
  mkdir -p $pyscada_home/measurement_data_dumps
  chown -R pyscada:pyscada $pyscada_home/measurement_data_dumps

  mkdir ${log_file_dir}
  chown pyscada:pyscada ${log_file_dir}
  touch ${log_file_dir}pyscada_{daemon,debug}.log
  chown pyscada:pyscada ${log_file_dir}pyscada_{daemon,debug}.log

  # Add rights for usb, i2c and serial
  adduser www-data pyscada
  adduser pyscada dialout

  debug "user_setup end"
}

# stop pyscada and show some python3 packages installed
function stop_pyscada(){
  debug "stop_pyscada"

  echo "Stopping PyScada"
  systemctl stop pyscada gunicorn gunicorn.socket
  sleep 1 # Give systemd time to shutdown
  systemctl --quiet is-active pyscada
  if [ $? == 0 ] ; then
    echo "Can't stop pyscada systemd service. Aborting."
    exit 1
  fi
  echo "PyScada stopped"

  debug "stop_pyscada end"
}

# install process: * means depending on the user answer
: <<'END'
- questions_setup
  - regex_proxy
  - *questions_clean_install_setup
    - admin_name_setup
    - regex_mail
- stop_pyscada
- user_setup
- install_dependences
  - apt_proxy
  - pip3_proxy
- pyscada install
- *install_channel_redis
  - apt_proxy
  - pip3_proxy_not_rust
  - pip3_proxy
- *db_setup
- *template_setup
- pyscada_init
  - *web_setup
END

questions_setup

stop_pyscada

user_setup

install_dependences

# Install PyScada
pip3_proxy install --upgrade .


if [[ "$answer_channels" == "y" ]]; then
  install_channel_redis
fi

if [[ "$answer_update" == "n" ]]; then
  db_setup
  template_setup
fi

pyscada_init

# fix owner in /home/pyscada
chown -R pyscada:pyscada $pyscada_home
