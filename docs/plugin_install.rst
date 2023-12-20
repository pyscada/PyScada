PyScada plugin installation
===========================

1. Choose a method to download  the PyScada plugin (exemple using PyScada-Modbus) :

  - by cloning the repository :

  .. code-block:: shell

      sudo apt install git
      git clone https://github.com/pyscada/PyScada-Modbus.git
      cd PyScada-Modbus


  - by downloading the zip file and extracting it :

  .. code-block:: shell

      sudo apt install wget
      wget https://github.com/pyscada/PyScada-Modbus/archive/refs/heads/main.zip -O PyScada-Modbus-main.zip
      sudo apt install unzip
      unzip ./PyScada-Modbus-main.zip
      rm ./PyScada-Modbus-main.zip
      cd PyScada-Modbus-main

2. Install the PyScada plugin

  Run :

  .. code-block:: shell

      # activate the PyScada virtual environment
      source /home/pyscada/.venv/bin/activate
      # install the plugin
      sudo -u pyscada -E env PATH=${PATH} pip3 install .
      # run migrations
      python /var/www/pyscada/PyScadaServer/manage.py migrate
      # copy static files
      python /var/www/pyscada/PyScadaServer/manage.py collectstatic --no-input
      # restart gunicorn and PyScada
      sudo systemctl restart gunicorn pyscada


List PyScada plugin installed
-----------------------------

.. code-block:: shell

    # activate the PyScada virtual environment
    source /home/pyscada/.venv/bin/activate
    pip3 list | grep cada


Uninstall a plugin
----------------------

To uninstall a plugin

.. code-block:: shell
    
    sudo -u pyscada -E env PATH=${PATH} pip uninstall yourPlugin