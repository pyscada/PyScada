.. IMPORTANT::
    This Version of PyScada is BETA software and may have serious bugs which may cause damage to your computer,
    automation hardware and data. It is not intended for use in production systems! You use this Software on your own risk!

Docker
======

This guide covers the basic setup of PyScada with `Docker <https://www.docker.com/>`_ and `Docker Compose <https://docs.docker.com/compose/>`_.

Download the necessary files
----------------------------

First of all download the docker config files for building your images.

Using Git.

::

    git clone https://github.com/clavay/PyScada.git
    cd PyScada/docker

Using wget.

::

    wget -qO- -O tmp.zip https://github.com/clavay/PyScada/archive/refs/heads/master.zip && unzip tmp.zip && rm tmp.zip
    cd PyScada-master/docker


Generating SSL Certificates
---------------------------

Generate ssl certificates for using ssl.

::

    mkdir nginx/ssl
    cd nginx/ssl
    openssl req -x509 -nodes -days 1780 -newkey rsa:2048 -keyout ./pyscada_server.key -out ./pyscada_server.crt



Build and Run the Image
-----------------------


Build the PyScada Docker Image.

::

    sudo docker-compose build

After the Images have been successfully build we need to initialize the Database and Create a superuser.

::

    sudo docker-compose run pyscada /src/pyscada/pyscada_init
    sudo docker-compose run pyscada /src/pyscada/manage.py createsuperuser

The last step is to start the Container.

::

    sudo docker-compose up -d