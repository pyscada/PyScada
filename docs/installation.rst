Installation
============

Dependencies
------------


Debian 7
^^^^^^^^

::

	sudo -i
	apt-get update
	apt-get -y upgrade
	apt-get -y install mysql-server python-mysqldb python-pip libhdf5-7 libhdf5-dev python-dev nginx gunicorn
	pip install cython
	pip install numpy
	pip install h5py


Debian 8/ Raspeian
^^^^^^^^^^^^^^^^^^

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


Fedora 22/23
^^^^^^^^^^^^

::
	
	sudo -i
	dnf install libjpeg-turbo-devel-1.4.1-2.fc23 nginx mysql-server mysql-devel
	pip install cython
	pip install numpy
	pip install h5py
	pip install gunicorn
	pip install MySQL-python



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

	# for VISA
	pip install pyvisa pyvisapy
	# for 1-Wire
	pip install pyownet
	# for smbus 
	pip install smbus
	# systemstat
	pip install psaux
	


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

::
	
	
	

	
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
	


see :doc:`django_settings` for all nessesary adjustments to the django settings.py and urls.py.


Initialize Database And Copy Static Files
-----------------------------------------

::


	cd /var/www/pyscada/PyScadaServer # linux
	sudo -u pyscada python manage.py migrate
	sudo -u pyscada python manage.py collectstatic
	
	# load fixures with default configuration
	sudo -u pyscada python manage.py loaddata color
	sudo -u pyscada python manage.py loaddata units
	
	
	

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


after editing, enable the configuration and restart nginx, optionaly remove the default configuration

::
	
	# debian
	sudo ln -s /etc/nginx/sites-available/pyscada.conf /etc/nginx/sites-enabled/
	sudo rm /etc/nginx/sites-enabled/default

now it's time to [re]start nginx.

::

	# systemd (Debian 8, Fedora, Ubuntu > XX.XX)
	systemctl enable nginx.service # enable autostart on boot
	sudo systemctl restart nginx

	# SysV-Init (Debian 7, Ubuntu <= XX.XX, [Debian 8])
	sudo service nginx restart
	


for Fedora you have to allow nginx to serve the static and media folder.

::
	
	sudo chcon -Rt httpd_sys_content_t /var/www/pyscada/http/



Start PyScada
-------------






Windows (experimantal)
----------------------


 - Python 2.7 for Windows https://www.python.org/downloads/windows/
 - Microsoft Visual C++ Comiler for Python 2.7 https://www.microsoft.com/en-us/download/details.aspx?id=44266
 - h5py https://pypi.python.org/pypi/h5py/2.5.0
 - h5py for 64bit Windows http://www.lfd.uci.edu/~gohlke/pythonlibs/#h5py

Open a Shell (cmd.exe) and install the folowing packages via pip.

::

	pip install gunicorn
	pip install django">=1.11,<1.12"
	pip install numpy
	pip install python-daemon
	pip install pyscada
	cd C:/Users/_YOUR_USERNAME_/
	mkdir www
	cd www
	python django-admin startproject PyScadaServer
	

::
	
	python manage.py migrate
	python manage.py collectstatic
	
	# load fixures with default configuration
	python manage.py loaddata color
	python manage.py loaddata units
	
	# create a admin user 
	python manage.py createsuperuser



Start the Django Development Server on Windows (optional, experimental)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open a Windows Command-line (cmd.exe) and start the Django Development Server.

::


	cd C:/Users/_YOUR_USERNAME_/www/PyScadaServer # Windows
	python manage.py runserver --insecure

	
Add/Start the PyScada Services on Windows (optional, experimental)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Using pyscada background daemons in Windows is currently not supported, to start the daemons in foreground open a Windows Command-line (cmd.exe) for every daemon and start it with the following command.

::

	cd C:/Users/_YOUR_USERNAME_/www/PyScadaServer
	python manage.py PyScadaWindowsDaemonHandler daemon_name


It is also posible to register the modbus daemon as an windows service, to do this download the registratioen skript from https://raw.githubusercontent.com/trombastic/PyScada/dev/0.7.x/extras/service/windows/register_windows_service_modbus.py and copy it to the project root folder.

::
	
	
	cd C:/Users/_YOUR_USERNAME_/www/PyScadaServer
	python register_windows_service_modbus.py




The installation of PyScada 0.7.x on `Debian 7/8 <https://www.debian.org/>`_ based Linux systems using `MySQL <https://www.mysql.de/>`_  as Database, `Gunicorn <http://gunicorn.org/>`_ as WSGI HTTP Server and `nginx <http://nginx.org/>`_ as HTTP Server.

The installation of PyScada 0.7.x on `Fedora 22/23 <https://www.fedoraproject.org/>`_ based Linux systems using `MySQL <https://www.mysql.de/>`_  as Database, `Gunicorn <http://gunicorn.org/>`_ as WSGI HTTP Server and `nginx <http://nginx.org/>`_ as HTTP Server.

The installation of PyScada 0.7.x on `Raspbian <https://www.raspbian.org/>`_ Linux systems using `SQLite <https://www.sqlite.org/>`_  as Database, `Gunicorn <http://gunicorn.org/>`_ as WSGI HTTP Server and `nginx <http://nginx.org/>`_ as HTTP Server.

The installation of PyScada 0.7.x on `Microsoft Windows <https://www.microsoft.com/>`_ systems using `SQLite <https://www.sqlite.org/>`_  as Database and the the Django Development Server as HTTP/WSGI Server.

