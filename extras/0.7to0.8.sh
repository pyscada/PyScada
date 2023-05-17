#!/bin/bash

# check if path is passed
if [ $# -eq 0 ]
  then
    manage_path="/var/www/pyscada/PyScadaServer"
    if test -f "$manage_path/manage.py"; then
      echo "$manage_path/manage.py found."
    else
      echo "File $manage_path/manage.py not found. Please specify the path of manage.py."
      exit 1
    fi
else
  if test -f "$1/manage.py"; then
    echo "$1/manage.py found."
    manage_path=$1
  else
    echo "File $1/manage.py not found. Please specify the path of manage.py or let empty tu use the default value : /var/www/pyscada/PyScadaServer/manage.py"
    exit 1
  fi
fi

# get the pyscada protocols with at least one device
res=$(echo -e "from pyscada.models import DeviceProtocol

for dp in DeviceProtocol.objects.all():
  if len(dp.device_set.all()) > 0:
    print(dp)
  " | python3 $manage_path/manage.py shell)


# check and install plugins
if [[ $res == *"modbus"* ]]; then
  echo "Modbus It's there!"
  pip3 install pyscada-modbus
fi
if [[ $res == *"phant"* ]]; then
  echo "phant It's there!"
  pip3 install pyscada-phant
fi
if [[ $res == *"systemstat"* ]]; then
  echo "systemstat It's there!"
  pip3 install pyscada-systemstat
fi
if [[ $res == *"visa"* ]]; then
  echo "visa It's there!"
  pip3 install pyscada-visa
fi
if [[ $res == *"smbus"* ]]; then
  echo "smbus It's there!"
  pip3 install pyscada-smbus
fi
if [[ $res == *"onewire"* ]]; then
  echo "onewire It's there!"
  pip3 install pyscada-onewire
fi

