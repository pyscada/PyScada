Installation
============


Debian like Systems
-------------------


The installation of PyScada 0.6.x on `Debian <https://www.debian.org/>`_ based Linux systems using `MySQL <https://www.mysql.de/>`_  as Database, `Gunicorn <http://gunicorn.org/>`_ as WSGI HTTP Server and `nginx <http://nginx.org/>`_ as HTTP Server.

Install Dependencies
^^^^^^^^^^^^^^^^^^^^


::

	sudo apt-get update
	sudo apt-get upgrade
	sudo apt-get install mysql-server python-mysqldb
	sudo apt-get install python-pip libhdf5-7 libhdf5-dev python-dev
	sudo apt-get install nginx
	sudo pip install gunicorn
	sudo pip install django">=1.7,<1.8"
	sudo pip install cython
	sudo pip install numpy
	sudo pip install h5py
	sudo pip install python-daemon


Install PyScada
^^^^^^^^^^^^^^^


::

	cd ~/
	sudo pip install git+https://github.com/trombastic/PyScada.git@stable/0.6.x


Create a Database
^^^^^^^^^^^^^^^^^

Create the Database and grand the nessesery permission. Replace `PyScada_db`, `PyScada-user` and `PyScada-user-password`.

::

	mysql -uroot -p -e "CREATE DATABASE PyScada_db CHARACTER SET utf8;"
	mysql -uroot -p -e "GRANT ALL PRIVILEGES ON PyScada_db.* TO 'PyScada-user'@'localhost' IDENTIFIED BY 'PyScada-user-password';"


Create a new Django Project
^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

	cd ~/
	mkdir www
	cd www
	django-admin.py startproject PyScadaServer


Edit urls.py And settings.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open the urls configuration file and add the nesseary rewrite rule to the django URL dispatcher.

::

	nano ~/www/PyScadaServer/PyScadaServer/urls.py


::

	...
		url(r'^admin/', include(admin.site.urls)),
		url(r'^', include('pyscada.urls')),
	...


Open the django settings file and make the following modifications. See also the `django documentation <https://docs.djangoproject.com/en/1.8/ref/settings/>`_ for more Information.

::

	nano ~/www/PyScadaServer/PyScadaServer/settings.py


First deaktivate the debuging, if debuging is active django will keep all SQL queries in the ram, the dataaquasition runs many queries so your system will run fast out of memory. Keep in mind to restart guinicorn and all dataaquasion daemons after you change the debuging state.

::

	DEBUG = False
	TEMPLATE_DEBUG = DEBUG


Add the host/domain of your machine, is this case every url that point to a ip of the machine is allowed.

::

	ALLOWED_HOSTS = ['*']


Add the PyScada and the subapps to the installed apps list.

::

	INSTALLED_APPS = (
		...
		'pyscada',
		'pyscada.modbus',
		'pyscada.hmi',
		'pyscada.systemstat'
	)

Fill in the database, the user and password as selected in the *create Database section*.

::

	DATABASES = {
		'default': {
			'ENGINE': 		'django.db.backends.mysql',
			'NAME': 				'PyScada_db',
			'USER': 				'PyScada-user',
			'PASSWORD': 'PyScada-user-password'
		}
	}


Set the static file and media dir as followes.

::

	...
	# Static files (CSS, JavaScript, Images)
	# https://docs.djangoproject.com/en/1.6/howto/static-files/

	STATIC_URL = '/static/'

	STATIC_ROOT = BASE_DIR + '/static/'

	MEDIA_URL = '/media/'

	MEDIA_ROOT = BASE_DIR + '/media/'


Add all PyScada specific settings

::

	# PyScada settings
	# https://github.com/trombastic/PyScada

	# folder were the daemon pid files are stored
	PID_ROOT = BASE_DIR + '/run/'

	# list of available client Protocols
	#
	PYSCADA_CLIENTS = (
		('modbus','Modbus Client',),
		('systemstat','Monitor Local System',),
	)

	# parameters for the Modbus Client
	# 	polling_interval 	how often the modbus client requests data
	#						from devices and write to the cache
	#
	#	recording_intervall how often the data is written to the database
	#
	# 	pid_file			file were the daemon pid is stored

	PYSCADA_MODBUS = {
		'polling_interval':5,
		'recording_interval':5,
		'pid_file_name': 'daemon-modbus.pid'
	}

	PYSCADA_SYSTEMSTAT = {
		'polling_interval':5,
		'recording_interval':5,
		'pid_file_name': 'daemon-sysstat.pid'
	}


Initialize Database And Copy Static Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

	cd ~/www/PyScadaServer
	python manage.py migrate
	python manage.py collectstatic


if the migration fails just run the migration command twice.

Add a Admin User To Your Django Project
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

	cd ~/www/PyScadaServer
	./manage.py createsuperuser


Configuration of Nginx
^^^^^^^^^^^^^^^^^^^^^^

::

	sudo nano /etc/nginx/sites-available/pyscada.conf

add the following and adjust the server, /media, /static location

::

	# pyscada.conf

	# the upstream component nginx needs to connect to
	upstream django {
		server unix:/home/www-user/www/PyScadaServer/run/gunicorn.sock fail_timeout=0; # for a file socket
	}

	# configuration of the server
	server {
		# the port your site will be served on
		listen      80;
		# the domain name it will serve for
		server_name .example.com; # substitute your machine's IP address or FQDN
		charset     utf-8;

		# max upload size
		client_max_body_size 75M;   # adjust to taste

		# Django media
		location /media  {
			alias /home/www-user/www/PyScadaServer/media;  # your Django project's media files - amend as required
		}

		location /static {
			alias /home/www-user/www/PyScadaServer/static; # your Django project's static files - amend as required
		}

			# an HTTP header important enough to have its own Wikipedia entry:
			#   http://en.wikipedia.org/wiki/X-Forwarded-For
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

			# enable this if and only if you use HTTPS, this helps Rack
			# set the proper protocol for doing redirects:
			# proxy_set_header X-Forwarded-Proto https;

			# pass the Host: header from the client right along so redirects
			# can be set properly within the Rack application
			proxy_set_header Host $http_host;

			# we don't want nginx trying to do something clever with
			# redirects, we set the Host: header above already.
			proxy_redirect off;

			# set "proxy_buffering off" *only* for Rainbows! when doing
			# Comet/long-poll stuff.  It's also safe to set if you're
			# using only serving fast clients with Unicorn + nginx.
			# Otherwise you _want_ nginx to buffer responses to slow
			# clients, really.
			# proxy_buffering off;

			# Try to serve static files from nginx, no point in making an
			# *application* server like Unicorn/Rainbows! serve static files.
			if (!-f $request_filename) {
				proxy_pass http://django;
				break;
			}
		}
	}


after editing, enable the configuration and restart nginx, optionaly remove the default configuration

::

	sudo rm /etc/nginx/sites-enabled/default


::

	sudo ln -s /etc/nginx/sites-available/pyscada.conf /etc/nginx/sites-enabled/pyscada.conf
	sudo service nginx restart


Add Init.d Scripts
^^^^^^^^^^^^^^^^^^


To start the Dataaquasition daemon(s) and guinicorn, there are two example scripts in the git repository. Copy them to the init.d path of your machine and make them executible.

::

	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/stable/0.6.x/pyscada_daemon -O /etc/init.d/pyscada_daemon
	sudo wget https://raw.githubusercontent.com/trombastic/PyScada/stable/0.6.x/gunicorn_django -O /etc/init.d/gunicorn_django
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
		'modbus	/home/www-user/www/PyScadaServer/'
	)
	RUN_AS='www-user'


Edit the gunicorn init.d script.

::

	sudo nano /etc/default/gunicorn_django


Also fill in the path to your django project dir and replace the four spaces between the django projectname (PyScadaserver) the project path and the number of workers (10) with tabs.

::

	#!/bin/sh
	#/etc/default/gunicorn_django
	SERVERS=(
		'PyScadaServer	/home/www-user/www/PyScadaServer	10'
	)
	RUN_AS='www-user'


(optinal) install System-V style init script links

::

	sudo update-rc.d pyscada_daemon defaults
	sudo update-rc.d gunicorn_django defaults



Raspberry Pi (RASPBIAN)
-----------------------

The installation of Version 0.6.x is not recommend for the Raspberry Pi, please use the 0.7.x release instead.
