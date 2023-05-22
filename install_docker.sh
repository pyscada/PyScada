#!/bin/bash

# VAR

answer_db_name="PyScada_db"         # Name of the database
answer_db_user="PyScada-user"         # Username for the database (not the root)
answer_db_password="PyScada-user-password"     # Password for the database (not the root)

answer_auto_add_apps="True"   # Auto add apps or manual add (in django configuration)

answer_admin_name=""      # admin name (for the system)
answer_admin_mail=""      # admin mail (for errors output)

ssl_dir="./nginx/ssl"
key_file="$ssl_dir/pyscada_server.key"
crt_file="$ssl_dir/pyscada_server.crt"

DOCKER_COMPOSE="./docker-compose.yml"
SETTINGS_TPL="../tests/project_template_tmp/project_name/settings.py-tpl"
DOCKERFILE_SQL="./mysql/Dockerfile"

# Make sure only root can run script
if [[ $EUID -ne 0 ]]; then
  >&2 echo "This script must be run as root"
  exit -1
fi

check_exit_status() {
  local message=$1
  local exit_status=$2

  if [ $exit_status -ne 0 ]; then
    >&2 echo "$message" # >&2: stderr output
    exit -1
  fi
  wait
}

function debug(){
  message=$1
  echo ""
  echo $message 1>&2
  echo ""
}

function db_setup(){
  debug "db_setup"

  # copy clean docker-compose
  cp ./docker-compose.yml-tmp $DOCKER_COMPOSE
  check_exit_status "Unable to copy docker-compose.yml" $?
  # copy template clean mysql Dockerfile
  cp ./mysql/Dockerfile-tmp $DOCKERFILE_SQL
  check_exit_status "Unable to copy Dockerfile" $?

  # add mysql Dockerfile with db informations
  sed -i "s|PyScada_db|$answer_db_name|g"  $DOCKERFILE_SQL
  sed -i "s|PyScada-user-password|$answer_db_password|g"  $DOCKERFILE_SQL
  sed -i "s|PyScada-user|$answer_db_user|g"  $DOCKERFILE_SQL

  # modify docker-compose.yml with db informations
  sed -i "s|PyScada_db|$answer_db_name|g" $DOCKER_COMPOSE
  sed -i "s|PyScada-user-password|$answer_db_password|g" $DOCKER_COMPOSE
  sed -i "s|PyScada-user|$answer_db_user|g" $DOCKER_COMPOSE

  debug "db_setup end"
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

function questions_setup(){
  debug "questions_setup"

  admin_name_setup
  regex_mail
  project_admins=$(echo "('${answer_admin_name}', '${answer_admin_mail}' )")
  echo $project_admins
  echo $answer_db_name

  # db params
  read -p "Database name [PyScada_db]: " answer_db_name
  read -p "Database user [PyScada-user]: " answer_db_user
  read -sp "Database password (your input is hidden) [PyScada-user-password]: " answer_db_password
  echo "\n"

  if [[ "$answer_db_name" == "" ]]; then
    answer_db_name="PyScada_db"
  fi
  if [[ "$answer_db_user" == "" ]]; then
    answer_db_user="PyScada-user"
  fi
  if [[ "$answer_db_password" == "" ]]; then
    answer_db_password="PyScada-user-password"
  fi

  while true; do
    read -p "Auto add pyscada plugins ? [True/False]: " answer_auto_add_apps
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

  debug "questions_setup end"
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

function ssl_setup(){
  # Creation of openssl certificate
  debug "ssl_setup"
  if [ ! -d "$ssl_dir" ]; then
    mkdir "$ssl_dir"
    check_exit_status "Unable to create ssl directory" $?
    echo "SSL directory created"
  else
    echo "SSL directory already exist"
  fi

  if [ ! -f "$key_file" ] && [ ! -f "$crt_file" ]; then
    rm -f "$ssl_dir/*"
    openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout "$key_file" -out "$crt_file" -subj '/CN=www.mydom.com/O=My Company Name LTD./C=US'
    check_exit_status "SSL certificates creation failed." $?
    echo "SSL certificates created"
  else
    echo "SSL certificates already exist"
  fi
  debug "ssl_setup end"
}

function template_setup(){
  # add db informations to django template
  debug "template_setup"
  rm -r ../tests/project_template_tmp/
  cp -r ../tests/project_template ../tests/project_template_tmp

  # add mysql host name to the mysql container
  sed -i "/'PASSWORD': '/a \ \ \ \ \ \ \ \ 'HOST': 'db'," "$SETTINGS_TPL"

  # remove concurrent_log_handler config and use file handler
  sed -i "/ConcurrentRotatingFileHandler/c\ \ \ \ \ \ \ \ \ \ \ \ 'class': 'logging.FileHandler'," "$SETTINGS_TPL"
  sed -i '/maxBytes/d' "$SETTINGS_TPL"
  sed -i '/backupCount/d' "$SETTINGS_TPL"
  check_exit_status "add mysql HOST failed" $?

  # set up django settings file
  sed -i "s|{{ db_name }}|$answer_db_name|g"  $SETTINGS_TPL
  sed -i "s|{{ db_user }}|$answer_db_user|g"  $SETTINGS_TPL
  sed -i "s|{{ db_password }}|$answer_db_password|g"  $SETTINGS_TPL
  sed -i "s|{{ project_root }}|\/src\/pyscada\/|g"  $SETTINGS_TPL
  sed -i "s|{{ log_file_dir }}|\/src\/pyscada\/|g"  $SETTINGS_TPL
  sed -i "s|{{ project_admins\|safe }}|$project_admins|g"  $SETTINGS_TPL
  sed -i "s|{{ auto_add_apps }}|$answer_auto_add_apps|g"  $SETTINGS_TPL
  sed -i "s|{{ additional_apps }}||g"  $SETTINGS_TPL
  sed -i "s|{{ additional_settings }}||g"  $SETTINGS_TPL

  rm ./pyscada/project_template.zip
  cd ../tests/project_template_tmp
  zip -r ../../docker/pyscada/project_template.zip .
  check_exit_status "Unable to create project_template.zip" $?
  cd ../../docker

  rm ./pyscada/pyscada.zip
  zip -r ./pyscada/pyscada.zip .. -x "../docs/*" "../.git/*" "../tests/*" "../docker/*" "../__pycache__/*"

  debug "template_setup end"
}

# Verify if docker-compose is installed
if ! command -v docker-compose >/dev/null 2>&1; then
  >&2 echo "Docker Compose is not installed."
  exit -1
fi

systemctl is-active docker.service
check_exit_status "docker service is not running. Start it using : sudo systemctl start docker.service" $?

echo "The installation may take some time"
sleep 0

command -v zip >/dev/null 2>&1
check_exit_status "Zip is not installed, install it with : sudo apt install zip" $?

# Execute commands from ./docker
cd docker
check_exit_status "The docker directory is missing." $?

ssl_setup
wait

questions_setup
wait

db_setup

template_setup
wait

# Build the image with the --no-cache argument
docker-compose build --no-cache
check_exit_status "The image build failed." $?

# Execute pyscada init in the docker container
docker-compose run pyscada /src/pyscada/pyscada_init
check_exit_status "pyscada_init failed." $?

# Execute docker-compose up in the background
docker-compose up -d
sleep 10

# Execute into the container the superuseer creation

echo "Create admin account for the web interface : "
docker-compose run pyscada python3 /src/pyscada/manage.py createsuperuser
check_exit_status "Superuser creation failed." $?

# Verify if the containers are running
if docker ps | grep "pyscada" >/dev/null; then
  echo "PyScada installed"
  echo "Connect to http://127.0.0.1 using admin account created previously"
else
  >&2 echo "docker-compose up failed."
  exit -1
fi
