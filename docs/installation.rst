Installation
============

This installation guide covers the installation of PyScada for `Debian 7/8 <https://www.debian.org/>`_ , `Raspbian <https://www.raspbian.org/>`_, `Fedora 22/23 <https://www.fedoraproject.org/>`_ based Linux systems using `MySQL <https://www.mysql.de/>`_ or `SQLite <https://www.sqlite.org/>`_ as Database, `Gunicorn <http://gunicorn.org/>`_ as WSGI HTTP Server and `nginx <http://nginx.org/>`_ as HTTP Server.


Dependencies
------------


Debian 7
^^^^^^^^

::

	sudo -i
	apt-get update
	apt-get -y upgrade
	# if you use MySQL as Database system (recommend)
	apt-get -y install mysql-server python-mysqldb
	apt-get -y python-pip libhdf5-7 libhdf5-dev python-dev nginx gunicorn
	pip install cython
	pip install numpy
	pip install h5py


Debian 8/ Raspeian
^^^^^^^^^^^^^^^^^^

::

	sudo -i
	apt-get update
	apt-get -y upgrade
	# if you use MariaDB/MySQL as Database system (recommend)
	apt-get -y install mariadb-server python-mysqldb
	apt-get install -y python-pip libhdf5-100 libhdf5-dev python-dev nginx gunicorn
	pip install cython
	pip install numpy
	
	# for 64bit 
	export HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial/ 
	# for 32 bit
	export HDF5_DIR=/usr/lib/x86_32-linux-gnu/hdf5/serial/ 
	# for ARM (Raspberry Pi)
	export HDF5_DIR=/usr/lib/arm-linux-gnueabihf/hdf5/serial/
	
	pip install h5py


Fedora 22/23
^^^^^^^^^^^^

::
	
	sudo -i
	dnf install libjpeg-turbo-devel-1.4.1-2.fc23 nginx

	# if you use MySQL as Database system (recommend)
	dnf install mysql-server mysql-devel
	pip install MySQL-python

	pip install cython
	pip install numpy
	pip install h5py
	pip install gunicorn




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
	
	
	pip install https://github.com/trombastic/PyScada/archive/dev/0.7.x.zip

	# for VISA Protocol
	pip install pyvisa pyvisa-py
	# for 1Wire Protocol
	pip install pyownet
	# for smbus Protocol, install libffi-dev first!
	pip install smbus-cffi
	# systemstat (monitor system statistics)
	pip install psutil
	


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
	sudo -u pyscada python manage.py migrate
	sudo -u pyscada python manage.py collectstatic
	
	# load fixtures with default configuration for chart lin colors and units
	sudo -u pyscada python manage.py loaddata color
	sudo -u pyscada python manage.py loaddata units
	
	# initialize the background service system of pyscada
	sudo -u pyscada python manage.py pyscada_daemon init

	

Add a Admin User To Your Django Project
---------------------------------------

::

	cd /var/www/pyscada/PyScadaServer
	python manage.py createsuperuser


Setup the Webserver (nginx, gunicorn)
-------------------------------------


::
	
	
	# debian
	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/nginx_sample.conf -O /etc/nginx/sites-available/pyscada.conf
	
	# Fedora
	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/nginx_sample.conf -O /etc/nginx/conf.d/pyscada.conf


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


add gunicorn:

::

    # systemd
    sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/gunicorn.socket -O /etc/systemd/system/gunicorn.socket
    sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/gunicorn.service -O /etc/systemd/system/gunicorn.service

    # enable the services for autostart
    sudo systemctl enable gunicorn
    sudo systemctl start gunicorn


Start PyScada
-------------

::

	cd /var/www/pyscada/PyScadaServer
	# start the background daemon for daq, mail, events
	sudo -u pyscada python manage.py pyscada_daemon start


