#!/bin/bash

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
  echo "This script must be run as root" 1>&2
  exit 1
fi

# Choose the config method (venv or docker)
answer_config=""
echo "choose your installation"

while [[ "$answer_config" == "" ]]; do

read -p "1: venv, 2: docker : " answer_config
  case $answer_config in
    "1")
    #remove logs file if exist (to avoid appending)
    if [ -f logs_install.txt ]; then
      rm logs_install.txt
    fi

      #execute the install_venv.sh script and output error in logs file
      source install_venv.sh 2>&1 | tee -a logs_install.txt 1>&2 | { while IFS= read -r line; do echo "$line"; done; }
      ;;
    "2")
    #remove logs file if exist (to avoid appending)
    if [ -f logs_docker.txt ]; then
      rm logs_docker.txt
    fi
      source install_docker.sh 2>&1 | tee -a logs_docker.txt 1>&2  | { while IFS= read -r line; do echo "$line"; done; }
      ;;
    *)
      echo "choose a valid configuration"
      answer_config=""
      ;;
  esac
  #statements
done
