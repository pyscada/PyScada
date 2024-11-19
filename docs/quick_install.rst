.. IMPORTANT::
    This Version of PyScada is BETA software and may have serious bugs which may cause damage to your computer,
    automation hardware and data. It is not intended for use in production systems! You use this Software on your own risk!

Installation
============

This installation guide covers the installation of PyScada for `Debian 10/11 <https://www.debian.org/>`_ ,
`Raspberry Pi OS <https://www.raspberrypi.com/software/>`_ based Linux systems
using `MariaDB <https://mariadb.com/>`_ as Database,
`Gunicorn <http://gunicorn.org/>`_ as WSGI HTTP Server and `nginx <http://nginx.org/>`_ as HTTP Server.

Scripts available
-----------------

The script ``install.sh`` let you choose between 2 installation type : system or docker and create a log file of the installation.

Then it call the script ``install_system.sh`` or ``install_docker.sh`` depending on your choice.

Automatic installation on Debian and derivatives
------------------------------------------------

1. Choose a method to download PyScada (you need write rights in the current directory) :

  - by cloning the repository :

  .. code-block:: shell

      sudo apt install git
      git clone https://github.com/pyscada/PyScada.git
      cd PyScada


  - by downloading the zip file and extracting it :

  .. code-block:: shell

      sudo apt install wget
      wget https://github.com/pyscada/PyScada/archive/refs/heads/main.zip -O PyScada-main.zip
      sudo apt install unzip
      unzip ./PyScada-main.zip
      rm ./PyScada-main.zip
      cd PyScada-main

2. Install PyScada

  .. IMPORTANT::
      For a new installation, make sure to answer "no" to the question "Update only".

  You will have to choose :

  * if you want to install PyScada on the system or in a docker container.
  * if the system date is correct (system install only)
  * if you want to use a proxy (system install only)
  * if you want to install channels and redis to speed up communications inter pyscada processes (system install only)
  * if you want to update only, if not :

    * the DB name, user and password
    * admin name and mail to send error logs (need further django email configuration in settings.py)
    * the first pyscada user credentials
    * if you want installed pyscada plugins to be automatically loaded

  Run :

  .. code-block:: shell

      sudo ./install.sh

Troubleshooting
---------------

If you already installed PyScada using docker, you need to delete the ``db_data`` docker volume using :

.. code-block:: shell

    docker volume rm docker_dbdata
