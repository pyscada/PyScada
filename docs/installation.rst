Installation
============


The installation of PyScada 0.6.x on `Debian <https://www.debian.org/>`_ based Linux systems using `MySQL <https://www.mysql.de/>`_  as Database, `Gunicorn <http://gunicorn.org/>`_ as WSGI HTTP Server and `nginx <http://nginx.org/>`_ as HTTP Server.

The installation of PyScada 0.6.x on `Fedora 22/23 <https://www.fedoraproject.org/>`_ based Linux systems using `MySQL <https://www.mysql.de/>`_  as Database, `Gunicorn <http://gunicorn.org/>`_ as WSGI HTTP Server and `nginx <http://nginx.org/>`_ as HTTP Server.

The installation of PyScada 0.6.x on `Raspbian <https://www.raspbian.org/>`_ Linux systems using `SQLite <https://www.sqlite.org/>`_  as Database, `Gunicorn <http://gunicorn.org/>`_ as WSGI HTTP Server and `nginx <http://nginx.org/>`_ as HTTP Server.

The installation of PyScada 0.6.x on `Microsoft Windows <https://www.microsoft.com/>`_ systems using `SQLite <https://www.sqlite.org/>`_  as Database and the the Django Development Server as HTTP/WSGI Server.


Add a new system-user for Pyscada (optional)
--------------------------------------------

Add a dedicated user for pyscada and add the home directory for `static`/`media` files and setup a virtual environemt.

::

	sudo -i
	useradd -r pyscada
	mkdir -p /var/www/pyscada/http
	chown -R pyscada:pyscada /var/www/pyscada
	mkdir -p /home/pyscada
	chown -R pyscada:pyscada /home/pyscada
	ln -s /var/www/pyscada/ ~/www_pyscada
	cd ~/
	#virtualenv -p /usr/bin/python2.7 venv
	#source venv/bin/activate



Install Dependencies
--------------------


Debian 7
^^^^^^^^

::

	sudo apt-get update
	sudo apt-get -y upgrade
	sudo apt-get -y install mysql-server python-mysqldb python-pip libhdf5-7 libhdf5-dev python-dev nginx gunicorn
	sudo pip install cython
	sudo pip install numpy
	sudo pip install h5py
	sudo pip install git+https://github.com/trombastic/PyScada.git@dev/0.7.x


Debian 8
^^^^^^^^


::

	sudo -i
	apt-get update
	apt-get -y upgrade
	apt-get -y install mysql-server python-mysqldb python-pip libhdf5-8 libhdf5-dev python-dev nginx gunicorn
	pip install cython
	pip install numpy
	
	# for 64bit 
	export HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial/ 
	# for 32 bit
	export HDF5_DIR=/usr/lib/x86_32-linux-gnu/hdf5/serial/ 
	# for ARM (RasperyPi)
	export HDF5_DIR=/usr/lib/arm-linux-gnueabihf/hdf5/serial/
	
	pip install h5py
	pip install git+https://github.com/trombastic/PyScada.git@dev/0.7.x



Fedora 22/23 
^^^^^^^^^^^^

::
	
	# as root
	sudo dnf install libjpeg-turbo-devel-1.4.1-2.fc23 nginx mysql-server mysql-devel
	# 
	sudo pip install cython
	sudo pip install numpy
	sudo pip install h5py
	sudo pip install git+https://github.com/trombastic/PyScada.git@dev/0.7.x
	sudo pip install gunicorn
	sudo pip install MySQL-python

Raspberry Pi (RASPBIAN, Jessie)
^^^^^^^^^^^^^^^^^^^^^^^

::

	sudo -i
	apt-get update
	apt-get -y upgrade
	apt-get -y install python-pip libhdf5-dev python-dev nginx gunicorn
	pip install cython
	pip install numpy
	export HDF5_DIR=/usr/lib/arm-linux-gnueabihf/hdf5/serial/ 
	pip install h5py
	pip install git+https://github.com/trombastic/PyScada.git@dev/0.7.x


Windows 
^^^^^^^

 - Python 2.7 for Windows https://www.python.org/downloads/windows/
 - Microsoft Visual C++ Comiler for Python 2.7 https://www.microsoft.com/en-us/download/details.aspx?id=44266
 - h5py https://pypi.python.org/pypi/h5py/2.5.0
 - h5py for 64bit Windows http://www.lfd.uci.edu/~gohlke/pythonlibs/#h5py

Open a Shell (cmd.exe) and install the folowing packages via pip.

::

	pip install gunicorn
	pip install django">=1.7,<1.8"
	pip install numpy
	pip install python-daemon
	pip install pyscada



Create a MySql Database (optional)
----------------------------------

Create the Database and grand the nessesery permission. Replace `PyScada_db`, `PyScada-user` and `PyScada-user-password`.

::

	mysql -uroot -p -e "CREATE DATABASE PyScada_db CHARACTER SET utf8;"
	mysql -uroot -p -e "GRANT ALL PRIVILEGES ON PyScada_db.* TO 'PyScada-user'@'localhost' IDENTIFIED BY 'PyScada-user-password';"


Create a new Django Project
---------------------------

::
	
	# Linux/OSX
	cd /var/www/pyscada/ 
	sudo -u pyscada django-admin.py startproject PyScadaServer
	
	# Windows
	cd C:/Users/_YOUR_USERNAME_/www 
	python django-admin.py startproject PyScadaServer
	


see :doc:`django_settings`


Initialize Database And Copy Static Files
-----------------------------------------

::

	# linux
	cd /var/www/pyscada/PyScadaServer # linux
	sudo -u pyscada python manage.py migrate
	sudo -u pyscada python manage.py collectstatic
	# load fixures with default configuration
	sudo -u pyscada python manage.py loaddata color
	sudo -u pyscada python manage.py loaddata units
	# Windows
	cd C:/Users/_YOUR_USERNAME_/www/PyScadaServer 
	python manage.py migrate
	python manage.py collectstatic
	# load fixures with default configuration
	python manage.py loaddata color
	python manage.py loaddata units
	

Add a Admin User To Your Django Project
---------------------------------------

::

	cd /var/www/pyscada/PyScadaServer # linux
	cd C:/Users/_YOUR_USERNAME_/www/PyScadaServer # Windows
	# both
	python manage.py createsuperuser



Setup of Nginx
--------------

see :doc:`nginx_setup`


Add Init.d Scripts for SysV-Init (optional)
-------------------------------------------


To start the Dataaquasition daemon(s) and guinicorn, there are two example scripts in the git repository. Copy them to the init.d path of your machine and make them executible.

::

	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.6.x/extras/service/SysV-init/pyscada_daemon -O /etc/init.d/pyscada_daemon
	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.6.x/extras/service/SysV-init/gunicorn_django -O /etc/init.d/gunicorn_django
	sudo chmod +x /etc/init.d/pyscada_daemon
	sudo chmod +x /etc/init.d/gunicorn_django


add a configuration file for every script.

::

	sudo nano /etc/default/pyscada_daemon



Fill in the full path to the django project dir (were the manage.py is located). Replace the four spaces between the daemon (modbus) and the path with a tab.

::

	#!/bin/sh
	#/etc/default/pyscada_daemon
	DAEMONS=(
		'modbus	/var/www/pyscada/PyScadaServer/'
	)
	RUN_AS='pyscada'


Edit the gunicorn init.d script.

::

	sudo nano /etc/default/gunicorn_django


Also fill in the path to your django project dir and replace the four spaces between the django projectname (PyScadaserver) the project path and the number of workers (10) with tabs.

::

	#!/bin/sh
	#/etc/default/gunicorn_django
	SERVERS=(
		'PyScadaServer	/var/www/pyscada/PyScadaServer	5'
	)
	RUN_AS='pyscada'


(optinal) install System-V style init script links

::

	sudo update-rc.d pyscada_daemon defaults
	sudo update-rc.d gunicorn_django defaults


Add Init.d Scripts for systemd (optional)
-----------------------------------------

Download the sample Unit-Files for systemd.

::

	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/pyscada_daq.service -O /lib/systemd/system/pyscada_daq.service
	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/pyscada_event.service -O /lib/systemd/system/pyscada_event.service
	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/pyscada_mail.service -O /lib/systemd/system/pyscada_mail.service
	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/pyscada_export.service -O /lib/systemd/system/pyscada_export.service
	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/gunicorn.socket -O /lib/systemd/system/gunicorn.socket
	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/systemd/gunicorn.service -O /lib/systemd/system/gunicorn.service
	# enable the services
	sudo systemctl enable gunicorn
	sudo systemctl enable pyscada_daq
	sudo systemctl enable pyscada_event
	sudo systemctl enable pyscada_mail
	sudo systemctl enable pyscada_export




Start the Django Development Server on Windows (optional)
---------------------------------------------------------

Open a Windows Command-line (cmd.exe) and start the Django Development Server.

::


	cd C:/Users/_YOUR_USERNAME_/www/PyScadaServer # Windows
	python manage.py runserver --insecure

	
Add/Start the PyScada Services on Windows (optional)
----------------------------------------------------


Using pyscada background daemons in Windows is currently not supported, to start the daemons in foreground open a Windows Command-line (cmd.exe) for every daemon and start it with the following command.

::

	cd C:/Users/_YOUR_USERNAME_/www/PyScadaServer
	python manage.py PyScadaWindowsDaemonHandler daemon_name


It is also posible to register the modbus daemon as an windows service, to do this download the registratioen skript from https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/windows/register_windows_service_modbus.py and copy it to the project root folder.

::
	
	
	cd C:/Users/_YOUR_USERNAME_/www/PyScadaServer
	python register_windows_service_modbus.py
