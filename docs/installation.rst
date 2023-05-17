
.. IMPORTANT::
    This Version of PyScada is BETA software and may have serious bugs which may cause damage to your computer,
    automation hardware and data. It is not intended for use in production systems! You use this Software on your own risk!



Installation
============

This installation guide covers the installation of PyScada for `Debian 10/11 <https://www.debian.org/>`_ ,
`Raspberry Pi OS <https://www.raspberrypi.com/software/>`_, `Fedora 22/23 <https://www.fedoraproject.org/>`_ based Linux systems
using `MySQL <https://www.mysql.com/>`_ / `MariaDB <https://mariadb.com/>`_ or `SQLite <https://www.sqlite.org/>`_ as Database,
`Gunicorn <http://gunicorn.org/>`_ as WSGI HTTP Server and `nginx <http://nginx.org/>`_ as HTTP Server.

Automatic installation using a script
-------------------------------------

On the Raspberry Pi with internet connection run :

::

    wget https://raw.githubusercontent.com/clavay/PyScada-Laborem/master/extras/install.sh -O install.sh
    sudo chmod a+x install.sh
    sudo ./install.sh


Dependencies
------------

.. js:autofunction:: toggle_timeline
   :short-name:

.. autofunction:: pyscada.models.Device.__str__


Debian 9, Raspbian
^^^^^^^^^^^^^^^^^^

::

    sudo -i
    apt-get update
    apt-get -y upgrade
    # if you use MariaDB/MySQL as Database system (recommend)
    apt-get -y install mariadb-server python3-mysqldb
    apt-get install -y python3-pip libhdf5-103 libhdf5-dev python3-dev nginx

    pip3 install gunicorn
    pip3 install pyserial
    pip3 install docutils


macOS
^^^^^

 - `MySQL Server <https://www.mysql.de/>`
 - HDF5 TODO	


::

        brew install python
        export PATH=$PATH:/usr/local/mysql/bin
        pip install MySQL-python


all
^^^^

::

    sudo -i
    pip3 install https://github.com/pyscada/PyScada/archive/master.zip

    # for VISA Protocol
    pip3 install pyvisa pyvisa-py
    # for 1Wire Protocol
    apt-get install owfs #
    pip3 install pyownet
    # for smbus Protocol, install libffi-dev first!
    apt-get install libffi-dev
    pip3 install smbus-cffi




Add a new system-user for Pyscada (optional, recommend)
-------------------------------------------------------

Add a dedicated user for the pyscada server instance and add a directory for `static`/`media` files.


Linux
^^^^^

::

    sudo -i
    useradd -r pyscada
    mkdir -p /var/www/pyscada/http
    chown -R pyscada:pyscada /var/www/pyscada
    mkdir -p /home/pyscada
    chown -R pyscada:pyscada /home/pyscada


macOS
^^^^^

::

    sudo -i
    dscl . -create /Users/pyscada IsHidden 1
    dscl . -create /Users/pyscada NFSHomeDirectory /Users/pyscada
    LastID=`dscl . -list /Users UniqueID | awk '{print $2}' | sort -n | tail -1`
    NextID=$((LastID + 1))
    dscl . create /Users/pyscada UniqueID $NextID
    dscl . create /Users/pyscada PrimaryGroupID 20
    mkdir -p /var/www/pyscada/http
    chown -R pyscada:staff /var/www/pyscada/



Create a MySql Database
-----------------------

Create the Database and grand the nessesery permission. Replace `PyScada_db`, `PyScada-user` and `PyScada-user-password` as you like.

::

    mysql -uroot -p -e "CREATE DATABASE PyScada_db CHARACTER SET utf8;GRANT ALL PRIVILEGES ON PyScada_db.* TO 'PyScada-user'@'localhost' IDENTIFIED BY 'PyScada-user-password';"



Create a new Django Project
---------------------------

::

    # Linux/OSX
    cd /var/www/pyscada/
    sudo -u pyscada django-admin startproject PyScadaServer



see :doc:`django_settings` for all necessary adjustments to the django settings.py and urls.py.


Initialize Database And Copy Static Files
-----------------------------------------

::


    cd /var/www/pyscada/PyScadaServer # linux
    sudo -u pyscada python3 manage.py migrate
    sudo -u pyscada python3 manage.py collectstatic

    # load fixtures with default configuration for chart lin colors and units
    sudo -u pyscada python3 manage.py loaddata color
    sudo -u pyscada python3 manage.py loaddata units

    # initialize the background service system of pyscada
    sudo -u pyscada python3 manage.py pyscada_daemon init



Add a Admin User To Your Django Project
---------------------------------------

::

    cd /var/www/pyscada/PyScadaServer
    sudo -u pyscada python3 manage.py createsuperuser


Setup the Webserver (nginx, gunicorn)
-------------------------------------


::


    # debian
    sudo wget https://raw.githubusercontent.com/pyscada/PyScada/master/extras/nginx_sample.conf -O /etc/nginx/sites-available/pyscada.conf

    # Fedora
    sudo wget https://raw.githubusercontent.com/pyscada/PyScada/master/extras/nginx_sample.conf -O /etc/nginx/conf.d/pyscada.conf


after editing, enable the configuration and restart nginx, optionally remove the default configuration

to use ssl (https, recommend)
-----------------------------

generate ssl certificates.


::

        # for Debian, Ubuntu, Raspian
        sudo mkdir /etc/nginx/ssl
        # the certificate will be valid for 5 Years,
        sudo openssl req -x509 -nodes -days 1780 -newkey rsa:2048 -keyout /etc/nginx/ssl/pyscada_server.key -out /etc/nginx/ssl/pyscada_server.crt

::

    # debian
    sudo ln -s /etc/nginx/sites-available/pyscada.conf /etc/nginx/sites-enabled/
    sudo rm /etc/nginx/sites-enabled/default

now it's time to [re]start nginx.

::

    # systemd (Debian 8, Fedora, Ubuntu > XX.XX)
    sudo systemctl enable nginx.service # enable autostart on boot
    sudo systemctl restart nginx

    # SysV-Init (Debian 7, Ubuntu <= XX.XX, [Debian 8])
    sudo service nginx restart



for Fedora you have to allow nginx to serve the static and media folder.

::

    sudo chcon -Rt httpd_sys_content_t /var/www/pyscada/http/


add gunicorn and pyscada unit files:

::

    # systemd
    sudo wget https://raw.githubusercontent.com/pyscada/PyScada/master/extras/service/systemd/gunicorn.socket -O /etc/systemd/system/gunicorn.socket
    sudo wget https://raw.githubusercontent.com/pyscada/PyScada/master/extras/service/systemd/gunicorn.service -O /etc/systemd/system/gunicorn.service
    sudo wget https://raw.githubusercontent.com/pyscada/PyScada/master/extras/service/systemd/pyscada_daemon.service -O /etc/systemd/system/pyscada.service

    # in some installations gunicorn is not at /usr/local/bin/gunicorn but at /usr/bin/gunicorn
    # in this case you have to change the pat in the file /etc/systemd/system/gunicorn.service accordingly

    # enable the services for autostart
    sudo systemctl enable gunicorn
    sudo systemctl start gunicorn
    sudo systemctl enable pyscada


Start PyScada
-------------

::

    sudo systemctl start pyscada


